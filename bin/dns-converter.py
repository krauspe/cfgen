#!/usr/bin/env python

#TODO: check which entrys are real (installable) entrys: derive from hostname
#TODO: insert 'net' obove 'nic' tree (maybe ...?)
#TODO: create 'classes' tree and fill with values (each host or global ??)
#TODO: make a second loop to collect all hn entrys of each line and add nic entrys to each host
# "cwp10-s1": {
#                 "classes": {
#                     "main": [
#                         "nsc",
#                         "rose"
#                     ],
#                     "sub": [
#                         "cwp"
#                     ]
#                 },
#                 "hardware": "physical",
#                 "net": {
#                     "nics": {
#                         "nic0": {
#                             "dv": "eth0",
#                             "ip": "192.168.33.29",
#                             "mac": ""
#                         }
#                     }
#                 }
#             },

from __future__ import print_function
import os
import socket
import collections
import argparse
import json
import yaml
from prettyprint import pp
import re

##usage: pp(content) # where content is json

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
#tpldir = os.path.join(basedir,"tpl")
deploydir_default = os.path.join(basedir, "deployment")
dnsdir = os.path.join(confdir,"dns_hosts")
#default_hosts_file = os.path.join(dnsdir,"lx3.lgn.dfs.de.dns.hosts")
default_hosts_file = os.path.join(dnsdir,"test.dns.hosts")
tempfile = os.path.join(deploydir_default, "temp_out.txt")

# parse args
formats = ['json',]

parser = argparse.ArgumentParser(description="convert dns hosts entrys with txt records to json")
parser.add_argument("--hosts", type=str, required=False,default=default_hosts_file, help="hosts file")
parser.add_argument("-f", "--format" , type=str, required=False, default='yaml', choices=formats, help="output format")
#parser.add_argument("-d", "--deploydir" , type=str, required=False, default=deploydir_default, choices=formats, help="output format")
parser.add_argument("-d", "--deploydir" , type=str, required=False, default=os.path.join(deploydir_default,'lx3.lgn.dfs.de'), choices=formats, help="output format")
args = parser.parse_args()

infile = args.hosts
format = args.format
deploydir = args.deploydir
host_outfile = {}
HN = {}
DN = {}
ENTRY_TYPE = {}
MAIN_CLASS = {}
SUB_CLASS = {}
NIC_ENTRYS = {}
FQDNS = set([])
INSTALLABLE_HOSTS = set([])
installable_prefixes = ['psp', 'cwp', 'adc', 'sup', 'dap', 'siu', 'sim', 'iss']
installable_suffixes = ['s1', 's2']
DNS_ENTRY_LINES = set([])
MAC = {}
IP = {}
DV = {}
SN = {}
HN_ENTRYS = collections.defaultdict(list)
DESCRIPTION = {}

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

ensure_dir(deploydir)

outfile = os.path.join(deploydir, args.hosts.split('/')[-1].rstrip('.hosts') + '.' + format)

print('hosts file: {} '.format(args.hosts))
print("\ninput  file: %s" % infile)
print("output file: %s" % outfile)
print("output format: %s\n" % format)

# functions

if not os.path.exists(infile):
    print ("ERROR: %s doesn't exist !!" % infile)
    exit()

def update_nested_dict(d, u):
    for k, v in u.iteritems():
        if isinstance(d, collections.Mapping):
            if isinstance(v, collections.Mapping):
                r = update_nested_dict(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        else:
            d = {k: u[k]}
    return d

def getEntryClassification(fqdn):
    # get hostname from fqdn
    hn = fqdn.split('.')[0]
    pre_suf = hn.split('-')
    pre = pre_suf[0]
    pre = re.sub(r'[0-9]+$', "", pre)

    if len(pre_suf) == 2:
        suf = pre_suf[1]
        if pre in installable_prefixes and suf in installable_suffixes:
            entry_type = 'installable'
            main_class = 'nsc'
            sub_class  = pre
        else:
            entry_type = 'dns'
            main_class = None
            sub_class  = None
    else:
        entry_type = 'dns'
        main_class = None
        sub_class = None

    if len(pre_suf) == 1 and pre == 'nss':
        entry_type = 'installable'
        main_class = 'nss'
        sub_class = ''


    return entry_type, main_class, sub_class

# class NicEntry(object):
#     def __init__(self,nic_id,hn,**kwargs):
#         self.nic_entry = {}
#         self.nic_name = 'nic' + str(nic_id)
#         self.nic_entry[self.nic_name] = {}
#         self.set_hn(self,hn=hn)
#         for key in kwargs:
#             self.nic_entry[[self.nic_name]][key] = kwargs[key]
#
#         return self.nic_entry
#     def set_hn(self,hn):
#         self.nic_entry[[self.nic_name]]['hn'] = hn

lines = [line.rstrip('\n') for line in open(infile) if not line.startswith('#')]
lines = list(line for line in lines if line) # only non blank lines
for line in lines:
    records = line.split('#')
    # GET ip, fqdn and hn
    ip_fqdn_hn = records[0]
    l = ip_fqdn_hn.split()
    if len(l) > 2:
        ip,fqdn,hn = l[:3]
        IP[fqdn] = ip
        HN[fqdn] = hn
        FQDNS.add(fqdn)
        ENTRY_TYPE[fqdn],MAIN_CLASS[fqdn], SUB_CLASS[fqdn] , = getEntryClassification(fqdn)
    else:
        continue

#    host_outfile = os.path.join(deploydir, hn + '.' + format)
    # Create a new entry and an host_entrys_update to update host_entrys dict
#    new_entry = {}
#    host_entrys_update = {}
    description = ""

    # is there a '#" after hn AND is there a non emtpy string
    if len(records) > 1 and len(records[-1]) > 0:
        # get description from first field after '#'
        if records[1] != records[-1]:
            description = re.sub(r'^\s+',"",records[1])
            if len(description) > 0:
                DESCRIPTION[fqdn] = description

        # get string after last '#'
        t_rec_string = records[-1]
        # remove leading whitespace
        t_rec_string = re.sub(r'^\s+', "", records[-1])
        # get 'key=val' strings
        key_value_pair_strings = t_rec_string.split()
        # emtpy keys list
        keys = []
        # get keys and their values
        key = ""
        val = ""
        for key_val in key_value_pair_strings:
            # do we have a non 'emtpy' value for the key
            l = key_val.split('=')
            if len(l) == 2:
                key, val = l
            else:
                continue

            if key == 'hn':
                HN_ENTRYS[fqdn].append(val)
            elif key == 'dn':
                DN[fqdn] = val
            elif key == 'mac':
                MAC[fqdn] = val
            elif key == 'dv':
                DV[fqdn] = val
            elif key == 'sn':
                SN[fqdn] = val

for fqdn in FQDNS:
    entry_type, main_class, sub_class = getEntryClassification(fqdn)
    # debug output
    if entry_type == 'installable':
        INSTALLABLE_HOSTS.add(fqdn)
        print("{} {} main_class={} sub_class={}".format(fqdn, entry_type, main_class, sub_class))
    else:
        print("{} {}".format(fqdn, entry_type))


# - Loop ueber die Liste von fqdns und ueber hostnamen feststellen was ein installierbarer Host ist und classe
#   feststellen
# - Nicht installierbare Hosts als DNS Entrys festhalten ...??
# - Suche nach 2step-cc Eintrag: hieraus Defaults bereitstellen
# - Neue Liste aus installierbaren Hosts
# - Neue Liste aus uebrigen Hosts
# - Loop ueber die HN_ENTRYS jedes installaierbaren host:
#    - check ob ein DN[fqdn] existiert, wenn nein, Default einsetzen
#    - Dictionary (oder object ?) fuer jeden installierbaren Host mit allen seinen Eintraegen aus HN_ENTRYS un deren IPs, sn. dv etc
# - Eintraege aus HN_ENTRYS aus Liste uebriger Hosts entfernen und als DNS-Eintraege dem Host.Dictionary (oder object) zuordnen

# OUTPUT:
# - Loop ueber alle alle installierbaren hosts und Output files fuer Puppet (yaml) erzeugen
# - Aus allen DNS-Eintraegen der installierbaren hosts und der reduzierten Liste neue HOSTS Datei fuer DNS bauen
#   diese sollte keine Text-Records fuer interface Konfig enthalten , jedoch ggfs Eintraege wie "rnsc" ??



#                new_entry[key] = val

#    host_entrys_update[fqdn] = new_entry


    # with open(host_outfile, mode='w') as f:
    #     print("writing {} file {}".format(format,host_outfile))
    #
    #     if format == "json":
    #             f.write(json.dumps(new_entry, sort_keys=True, indent=2, separators=(',', ': ')))
    #     elif format == "yaml":
    #             yaml.dump(new_entry, f, default_flow_style=False)


    #host_entrys[fqdn] = new_entry
#    update_nested_dict(host_entrys,host_entrys_update)

# # Debug ouput file
# with open(tempfile,mode='w') as f:
#     for line in lines:
#         f.write (line + '\n')
#
# write output file

# with open(outfile, mode='w') as f:
#     print("writing single data {} file {}".format(format, outfile))
#
#     if format == "json":
#             f.write(json.dumps(host_entrys, sort_keys=True, indent=2, separators=(',', ': ')))
#     elif format == "yaml":
#             yaml.dump(host_entrys, f, default_flow_style=False)


#pp(host_entrys)


#!/usr/bin/env python

# - Loop ueber die Liste von fqdns und ueber hostnamen feststellen was ein installierbarer Host ist und classe
#   feststellen -> OK
# - Nicht installierbare Hosts als DNS Entrys festhalten ...? -> OK noch keine Gen von Lines oder Output
# - Suche nach 2step-cc Eintrag: hieraus Defaults bereitstellen -> OK
# - Neue Liste aus installierbaren Hosts -> OK
# - Neue Liste aus uebrigen Hosts  -> OK
# - Loop ueber die HN_ENTRYS jedes installaierbaren host:
#    - check ob ein DN[fqdn] existiert, wenn nein, Default einsetzen -> OK
#    - Dictionary (oder object ?) fuer jeden installierbaren Host mit
#       allen seinen Eintraegen aus HN_ENTRYS un deren IPs, sn. dv etc -> OK (dict bis jetzt)
# - TODO: Eintraege aus HN_ENTRYS aus Liste uebriger Hosts entfernen und als DNS-Eintraege dem Host.Dictionary (oder object) zuordnen ->

# OUTPUT:
# - Loop ueber alle alle installierbaren hosts und Output files fuer Puppet (yaml) erzeugen -> OK
# - TODO: Aus allen DNS-Eintraegen der installierbaren hosts und der reduzierten Liste neue HOSTS Datei fuer DNS bauen
# - TODO: diese sollte keine Text-Records fuer interface Konfig enthalten , jedoch ggfs Eintraege wie "rnsc" ??

# moegliche Struktur fuer allgemeine Zwecke, jedoch erst mal nur nur fuer yaml und dns output, daher siehe unten
# --------------------------------------------------------------------------------------------------------------
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
from  collections import defaultdict, Mapping
import argparse
import json
import yaml
import pretty as pp
import re

##usage: pp(content) # where content is json

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
dnsdir = os.path.join(confdir,"dns_hosts")
#tpldir = os.path.join(basedir,"tpl")
deploydir_default_base = os.path.join(basedir, "deployment")

# deploydir_default      = os.path.join(deploydir_default_base, "mu1.muc.dfs.de")
# hosts_file_default     = os.path.join(dnsdir, "mu1.muc.dfs.de.hosts")

deploydir_default      = os.path.join(deploydir_default_base, "ka1.krl.dfs.de")
hosts_file_default     = os.path.join(dnsdir, "ka1.krl.dfs.de.hosts")

# deploydir_default      = os.path.join(deploydir_default_base, "br1.bre.dfs.de")
# hosts_file_default     = os.path.join(dnsdir, "br1.bre.dfs.de.hosts")

# deploydir_default      = os.path.join(deploydir_default_base, "lx3.lgn.dfs.de")
# hosts_file_default     = os.path.join(dnsdir, "lx3.lgn.dfs.de.hosts")


tempfile = os.path.join(deploydir_default, "temp_out.txt")

# parse args
formats = ['json',]

parser = argparse.ArgumentParser(description="convert dns hosts entrys with txt records to json")
parser.add_argument("--hosts", type=str, required=False, default=hosts_file_default, help="hosts file")
parser.add_argument("-f", "--format" , type=str, required=False, default='yaml', choices=formats, help="output format")
parser.add_argument("-d", "--deploydir" , type=str, required=False, default=deploydir_default, choices=formats, help="output format")
args = parser.parse_args()

infile = args.hosts
format = args.format
deploydir = args.deploydir

host_outfile = defaultdict(str)

HN = defaultdict(str)
DN = defaultdict(str)
ENTRY_TYPE = defaultdict(str)
MAIN_CLASS = defaultdict(str)
SUB_CLASS = defaultdict(str)
NIC_ENTRYS = defaultdict(str)
MAC = defaultdict(str)
NS = defaultdict(str)
IP = defaultdict(str)
DV = defaultdict(str)
SN = defaultdict(str)
GW = defaultdict(str)
SY = defaultdict(str)
DESCRIPTION = defaultdict(str)
HN_ENTRYS = defaultdict(list)
IF_ENTRYS = defaultdict(list)

FQDNS = set([])
INSTALLABLE_FQDNS = set([])

installable_prefixes = ['psp', 'cwp', 'adc', 'sup', 'dap', 'siu', 'sim', 'iss']
installable_suffixes = ['s1', 's2']
DNS_ENTRYS = []
DNS_ENTRY_LINES = []

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

ensure_dir(deploydir)

dns_hosts_outfile = os.path.join(deploydir, args.hosts.split('/')[-1].rstrip('.hosts') + '.' + format)

print('hosts file: {} '.format(args.hosts))
print("\ninput  file: %s" % infile)
#print("output file: %s" % outfile)
print("output format: %s\n" % format)

# functions

if not os.path.exists(infile):
    print ("ERROR: %s doesn't exist !!" % infile)
    exit()

def update_nested_dict(d, u):
    for k, v in u.iteritems():
        if isinstance(d, Mapping):
            if isinstance(v, Mapping):
                r = update_nested_dict(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        else:
            d = {k: u[k]}
    return d

def getDefaultKey(fqdn):
    dn = re.sub(r'^.*?\.', "", fqdn)
    return '2step-cc.'+dn


def getEntryClassification(fqdn):
    '''
    returns list: [entry_type, main_class, sub_class]
    to characterize each input line from dns *.hosts file(s)
    derived from it's fqdn
    Uses 2step-cc entry

        possible entry_types:
            installable : use for DNS and as data set (hiera data) for puppet installation of a host
            interface   : use for DNS as data set for additional interface of an installable host
            dns         : use for DNS only (all additional DNS entrys for one domain (or site)

        main_class, sub_class: puppet/hiera parameters which control installation
    '''
    # get hostname from fqdn
    hn = fqdn.split('.')[0]
    pre_suf = hn.split('-')
    pre = pre_suf[0]
    pre = re.sub(r'[0-9]+$', "", pre)

    entry_type = 'dns'
    main_class = None
    sub_class = None

    if len(pre_suf) == 1 and pre == 'nss':
        entry_type = 'installable'
        main_class = 'nss'
        sub_class = None
    elif len(pre_suf) == 2:
        suf = pre_suf[1]
        if pre in installable_prefixes and suf in installable_suffixes:
            entry_type = 'installable'
            main_class = 'nsc'
            sub_class  = pre
        elif pre == "2step" and suf == 'cc':
            entry_type = 'defaults'
            main_class = None
            sub_class = None
    elif DV[fqdn] and DV[fqdn] != DV[getDefaultKey(fqdn)]:
        entry_type = 'interface'

    return entry_type, main_class, sub_class

# is mal so eine idee fuer ein objekt :-))

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

# READ input file

lines = [line.rstrip('\n') for line in open(infile) if not line.startswith('#')]
lines = list(line for line in lines if line) # only non blank lines
for line in lines:
    records = line.split('#')
    # GET ip, fqdn and hn
    ip_fqdn_hn = records[0]
    l = ip_fqdn_hn.split()
    if len(l) > 2:
        ip, fqdn, hn = l[:3]
        IP[fqdn] = ip
        HN[fqdn] = hn
        FQDNS.add(fqdn)
    else:
        continue

    # host_outfile = os.path.join(deploydir, hn + '.' + format)
    # Create a new entry and an host_entrys_update to update host_entrys dict
    # new_entry = {}
    # host_entrys_update = {}
    description = ""


    # Parse lines
    #
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
            elif key == 'dv':
                DV[fqdn] = val
            elif key == 'sn':
                SN[fqdn] = val
            elif key == 'gw':
                GW[fqdn] = val
            elif key == 'ns':
                NS[fqdn] = val
            elif key == 'mac':
                MAC[fqdn] = val
            elif key == 'sy':
                SY[fqdn] = val

# classify fqdn entrys and set defaults for missing values from 2step-cc entry

for fqdn in FQDNS:
    entry_type, main_class, sub_class = getEntryClassification(fqdn)
    ENTRY_TYPE[fqdn], MAIN_CLASS[fqdn], SUB_CLASS[fqdn] = entry_type, main_class, sub_class

    if entry_type == 'installable' or entry_type == 'interface':
        # set default for dv after classification
        dn_default = getDefaultKey(fqdn)
        if not DN[fqdn]:
            DN[fqdn] = DN[dn_default]
        if not SN[fqdn]:
            SN[fqdn] = SN[dn_default]
        if not NS[fqdn]:
            NS[fqdn] = NS[dn_default]
        if not GW[fqdn]:
            GW[fqdn] = GW[dn_default]
        if not DV[fqdn]:
           DV[fqdn] = DV[dn_default]

        #print("{}:\t {}\tclasses:{}.{}\t dv={}".format(fqdn, entry_type, main_class, sub_class, DV[fqdn]))
        # Use for configuration data for installable hosts
        if entry_type == 'installable':
            INSTALLABLE_FQDNS.add(fqdn)
            for hn_entry in HN_ENTRYS[fqdn]:
                if hn_entry == hn_entry.split('.')[0]:
                    fqdn_entry = "{}.{}".format(hn_entry, DN[fqdn])
                else:
                    fqdn_entry = hn_entry
                IF_ENTRYS[fqdn].append(fqdn_entry)
                #print ("\t{}\tdv={}".format(fqdn_entry,DV[fqdn_entry]))

    else:
        # Use as DNS entry only
        #print("{}:\t {}\t".format(entry_type, fqdn))
        DNS_ENTRYS.append(fqdn)

def generateHostDataStruct(main_fqdn):
    #data = {}
    dv = {
        'ipaddress':IP[main_fqdn],
        'netmask':SN[main_fqdn],
        'gateway':GW[main_fqdn],
        'DNS1':NS[main_fqdn],
        'peerdns': 'true',

    }
    data = {DV[main_fqdn]:dv}

    for fqdn in IF_ENTRYS[main_fqdn]:
        dv = {
            'ipaddress': IP[fqdn],
            'netmask': SN[fqdn],
            'gateway': GW[fqdn],
            'DNS1': NS[fqdn],
        }
        data.update({DV[fqdn]: dv})
    network_if_static = {'network::if_static': data}
    return network_if_static

def generateDnsLines(fqdn_list, txt_rec_list):
    dns_lines = []
    for fqdn in fqdn_list:
        hn = fqdn.split('.')[0]
        dns_lines.append("{}\t{}\t{}".format(hn, fqdn, IP[fqdn]))
    return dns_lines

# output hiera yaml files

for fqdn in INSTALLABLE_FQDNS:
    print("{}".format(fqdn))
    data = generateHostDataStruct(fqdn)
    outfile = os.path.join(deploydir, fqdn + '.' + format)

    with open(outfile, mode='w') as f:
        print("writing {} file {}".format(format,host_outfile))

        if format == "json":
                f.write(json.dumps(data, sort_keys=False, indent=2, separators=(',', ': ')))
        elif format == "yaml":
                yaml.dump(data, f, default_flow_style=False)
    print(data)



# yaml output
    #
    # network::if_static:
    #   'eth0':
    #     ensure: up
    #     ipaddress: 192.168.40.20
    #     netmask: 255.255.255.0
    #     gateway: 192.168.40.20
    #     peerdns: true
    #     dns1: 192.168.40.10




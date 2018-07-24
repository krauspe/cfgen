#!/usr/bin/env python

# Is now compatible for Python 2.x AND 3.x !!

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
import os, sys
import socket
from collections import defaultdict, Mapping
import argparse
import json
import yaml
import prettyprint as pp
import re
import netaddr
#from netaddr import *

##usage: pp(content) # where content is json

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir, "config")
domain_default = "am.muc.dfs.de"
#domain_default = "ka1.krl.dfs.de"
#domain_default = "atg2.lgn.dfs.de"
#domain_default = "atg2.lgn.dfs.de"
#domain_default = "te3.lgn.dfs.de"
#domain_default = "ak2.lgn.dfs.de"
#domain_default = "afs.lgn.dfs.de"
#domain_default = "lx3.lgn.dfs.de"
nss_default_subclass = 'light'
#domain_default = "mu1.muc.dfs.de"
deploydir_base_default = os.path.join(basedir, "deployment", "hieradata")

if os.path.exists('/mnt/puppet/hieradata'):
    puppet_dir = '/mnt/puppet'
elif os.path.exists('/opt/export/puppet-master/hieradata'):
    puppet_dir = '/opt/export/puppet-master'
else:
    puppet_dir = None

# /opt/export/puppet-master/modules/dns_server_config/files/data
# /mnt/puppet/modules/dns_server_config/files/data

tempfile = os.path.join(deploydir_base_default, "temp_out.txt")

# parse args
formats = ['json',]

parser = argparse.ArgumentParser(description="convert dns hosts entrys with txt records to json")
parser.add_argument("-d", "--domain", type=str, required=False, default=domain_default, help="DNS Domain")
parser.add_argument("-f", "--format" , type=str, required=False, default='yaml', choices=formats, help="output format")
parser.add_argument("-b", "--deploybase", type=str, required=False, default=deploydir_base_default, choices=formats, help="basedir for deployment")
parser.add_argument("-s", "--nss-subclass", type=str, required=False, default=nss_default_subclass, choices=formats, help="sub_class for nss")
args = parser.parse_args()

domain = args.domain
format = args.format
deploydir_base = args.deploybase

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)


dnsdir_default = os.path.join(confdir, "dns_hosts")
dnsdir_puppet = os.path.join(puppet_dir, "modules", "dns_server_config", "files", "data")
hosts_default = os.path.join(dnsdir_default,domain+'.'+'hosts' )
hosts_puppet = os.path.join(dnsdir_puppet,domain+'.'+'hosts' )

if os.path.exists(hosts_default):
    dnsdir = dnsdir_default
    infile = hosts_default
    print("Using test file {}".format(infile))
else:
    if puppet_dir:
        dnsdir = dnsdir_puppet
        infile = hosts_puppet
        print("Using PRODUCTION file {}".format(infile))
    else:
        print("NO default hosts file {} exists".format(hosts_default))
        print("No PRODIUCTION hosts file {} exists, exiting".format(hosts_puppet))

deploydir = os.path.join(deploydir_base, domain)
ensure_dir(deploydir)

#dns_hosts_outfile = os.path.join(deploydir, args.hosts.split('/')[-1].rstrip('.hosts') + '.' + format)
dns_hosts_outfile = os.path.join(deploydir, domain, domain+'.'+format)

#host_outfile = defaultdict(str)

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

installable_prefixes = ['psp', 'cwp', 'adc', 'sup', 'dap', 'siu', 'sim', 'iss', 'gen', 'hmi']
installable_suffixes = ['s1', 's2']
DNS_ENTRYS = []
DNS_ENTRY_LINES = []



print("\ninput  file: %s" % infile)
print("output format: %s\n" % format)

# functions

if not os.path.exists(infile):
    print ("ERROR: %s doesn't exist !!" % infile)
    exit()

def update_nested_dict(d, u):
    #for k, v in u.iteritems():A python 2.x
    if sys.version_info.major == 2:
        Items = u.iteritems()
    else:
        Items = u.items()

    for k, v in Items:
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
    elif len(pre_suf) == 1 and pre == 'ams':
        entry_type = 'installable'
        main_class = 'ams'
        sub_class = 'centos'
    elif len(pre_suf) == 1 and pre == 'hmi':
        entry_type = 'installable'
        main_class = 'amc'
        sub_class = 'hmi'
    elif len(pre_suf) == 1 and pre == 'gen':
        entry_type = 'installable'
        main_class = 'amc'
        sub_class = 'gen'
    elif len(pre_suf) == 2:
        suf = pre_suf[1]
        if pre in installable_prefixes and suf in installable_suffixes :
            entry_type = 'installable'
            main_class = 'nsc'
            sub_class  = pre
        elif pre == "2step" and suf == 'cc':
            entry_type = 'defaults'
            main_class = None
            sub_class = None
        else:
            entry_type = 'unknown1'
            main_class = None
            sub_class = None

    if DV[fqdn] and DV[fqdn] != DV[getDefaultKey(fqdn)]:
        entry_type = 'interface'

    #print("  getEntryClassification: {} : DV[fqdn]={} DV[getDefaultKey(fqdn)={}".format(fqdn, DV[fqdn], DV[getDefaultKey(fqdn)]))
    return entry_type, main_class, sub_class

def getSubnet(ip, netmask):
    ip_int = ip.split('.')
    netmask_int = netmask.split('.')
    subnet = '.'.join([str(int(ip_int[n]) & int(netmask_int[n])) for n in range(0,4)])
    return subnet


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
    #print("{}: ENTRY TYPE: {}".format(fqdn, entry_type))
    ENTRY_TYPE[fqdn], MAIN_CLASS[fqdn], SUB_CLASS[fqdn] = entry_type, main_class, sub_class

    if entry_type == 'installable' or entry_type == 'interface':
        # set default for dv after classification
        dn_default = getDefaultKey(fqdn)
        if not DN[fqdn]:
            DN[fqdn] = DN[dn_default]
        if not SN[fqdn]:
            if SN[dn_default]:
                SN[fqdn] = SN[dn_default]
                #print("  NETMASK for {} = {}".format(fqdn,SN[fqdn]))

            else:
                print("Warning: NO NETMASK (and NO default) found for {} !!".format(fqdn))
        if not NS[fqdn]:
            NS[fqdn] = NS[dn_default]
        if not GW[fqdn]:
            GW[fqdn] = GW[dn_default]
        if not DV[fqdn]:
           DV[fqdn] = DV[dn_default]

        #print("{}:\t {}\tclasses:{}.{}\t dv={} sn={}".format(fqdn, entry_type, main_class, sub_class, DV[fqdn], SN[fqdn]))
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
    #print("{}:\tentry_type={} dv={} dev_default={} sn={}".format(fqdn, entry_type, DV[fqdn], DV[getDefaultKey(fqdn)], SN[fqdn]))


def getHostClasses(fqdn):
    hn = fqdn.split('.')[0]
    main = ''; sub = ''

    # if hn == 'nss':
    #     main = 'nss'
    #     sub =  nss_default_subclass
    # else:
    #     prefix = hn[0:3]
    #     if prefix in installable_prefixes:
    #         main = 'nsc'
    #         sub  = prefix
    #
    # host_classes = {
    #     'host_classes::main': main,
    #     'host_classes::sub': sub,
    # }

    entry_type, main_class, sub_class = getEntryClassification(fqdn)

    if main_class in ['nss', 'ams'] and sub_class == None:
        sub_class = nss_default_subclass

    host_classes = {
        'host_classes::main': main_class,
        'host_classes::sub': sub_class,
    }

    return host_classes

def getDhcpConfig(fqdn):
    # TODO: generate subnet address
    # TODO: USE IT :-)
    #dn = '.'.join(fqdn.split('.'))
    subnet = getSubnet(IP[fqdn], SN[fqdn])
    data = {
      'netmask': SN[fqdn],
      'subnet':  "{}".format(subnet),
      'routers': GW[fqdn],
      'domain_name_servers': "{}".format(NS[fqdn]),
      'domain_name':         "{}".format(DN[fqdn]),
      'range_start':         '200',
      'range_end':           '239',
      'default_lease_time':  '3600',
      'max_lease_time':      '21600',
      'args':                'eth0',
      'ensure':              'running',
      'enable':              True,
    }
    dataout = {'dhcpd': data}
    return dataout

def generateHostDataStruct(main_fqdn):
    hn = main_fqdn.split('.')[0]

    # get host classes
    dataout = getHostClasses(main_fqdn)
    main = dataout['host_classes::main']
    #sub  = dataout['host_classes']['sub']

    if main in ['nss', 'cis', 'ams']:
        dhcpd   = getDhcpConfig(main_fqdn)
        dataout = update_nested_dict(dataout, dhcpd)
        ns      = 'localhost'
    else:
        ns = NS[main_fqdn]
    # get network interface config data


    peerdns = True

    dv_dhcp = {
        'ensure': 'up',
        'peerdns': 'false',
    }
    ifdata_dhcp = {}

    dv = {
        'ensure': 'up',
        'ipaddress': IP[main_fqdn],
        'netmask': SN[main_fqdn],
        'gateway': GW[main_fqdn],
        'dns1': ns,
        'peerdns': peerdns,
    }
    ifdata = {DV[main_fqdn]:dv}

    dhcp_if_count = 0

    for fqdn in IF_ENTRYS[main_fqdn]:
        if IP[fqdn] == '0.0.0.0':
            ifdata_dhcp.update({DV[fqdn]: dv_dhcp})
            dhcp_if_count += 1
        else:
            dv = {
                'ensure': 'up',
                'ipaddress': IP[fqdn],
                'netmask': SN[fqdn],
            }
            ifdata.update({DV[fqdn]: dv})

    network_if_static = {'network::if_static': ifdata}
    dataout = update_nested_dict(dataout, network_if_static)

    if dhcp_if_count > 0:
        network_if_dynamic = {'network::if_dynamic': ifdata_dhcp}
        dataout = update_nested_dict(dataout, network_if_dynamic)

    # get dhcpd config if hn==nss



    return dataout


def generateDnsLines(fqdn_list, txt_rec_list):
    '''NOT USED yet !!'''
    dns_lines = []
    for fqdn in fqdn_list:
        hn = fqdn.split('.')[0]
        dns_lines.append("{}\t{}\t{}".format(hn, fqdn, IP[fqdn]))
    return dns_lines

# output hiera yaml files

for fqdn in INSTALLABLE_FQDNS:
    #print("{}".format(fqdn))
    data = generateHostDataStruct(fqdn)
    outfile = os.path.join(deploydir, fqdn + '.' + format)

    with open(outfile, mode='w') as f:
        print("writing {} file {}".format(format,outfile))

        if format == "json":
                f.write(json.dumps(data, sort_keys=False, indent=2, separators=(',', ': ')))
        elif format == "yaml":
                yaml.dump(data, f, default_flow_style=False)
    #print(data)



# yaml output (only IFs)
    #
    # network::if_static:
    #   'eth0':
    #     ensure: up
    #     ipaddress: 192.168.40.20
    #     netmask: 255.255.255.0
    #     gateway: 192.168.40.20
    #     peerdns: true
    #     dns1: 192.168.40.10




#!/usr/bin/env python

from __future__ import print_function
import os
import socket
import collections
import argparse
import json
import hjson
from prettyprint import pp
import re
##usage: pp(content) # where content is json

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
#tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")
default_hosts_file = os.path.join(confdir,"mu1.muc.dfs.de.dns.hosts")
tempfile = os.path.join(deploydir,"temp_out.txt")

# parse args
formats = ['json,']

parser = argparse.ArgumentParser(description="convert dns hosts entrys with txt records to json")
parser.add_argument("--hosts", type=str, required=False,default=default_hosts_file ,help="hosts file")
parser.add_argument("-f", "--format" , type=str, required=False, default='json', choices=formats, help="output format")
args = parser.parse_args()

infile = args.hosts
format = args.format
outfile = os.path.join(deploydir,args.hosts.split('/')[-1].rstrip('.hosts') + '.' + format)

#print('hosts file: {} '.format(args.hosts))
print("\ninput  file: %s" % infile)
print("output file: %s" % outfile)
print("output format: %s\n" % format)


#TODO:

file = infile

#host_entrys = {}

# host_entrys dict with test data

# host_entrys = {
#         "nss.nsa.lgn.dfs.de" :{
#             "ip": "10.232.222.10",
#             "hname": "nss",
#             "dv"  : "eth0",
#             "gw"  : "10.232.222.253",
#             "sn"  : "255.255.255.0",
#             "hn_list": ["nss-mgt","nss-p1","nss-ph"],
#             "sy"  : "SIU AFS"
#         }
# }

host_entrys = {}

if not os.path.exists(file):
    print ("ERROR: %s doesn't exist !!" % file)
    exit()

# functions

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



# records = [line.rstrip('\n').split('#') for line in open(file) if not line.startswith('#')]
lines = [line.rstrip('\n') for line in open(file) if not line.startswith('#')]
lines = list(line for line in lines if line) # only non blank lines
for line in lines:
    records = line.split('#')

    # GET ip, fqdn and hn
    ip_fqdn_hn = records[0]
    # debug
    print("ip_fqdn_hn = " + ip_fqdn_hn)
    l = ip_fqdn_hn.split()
    if len(l) > 1:
        ip,fqdn = l[:2]
    else:
        continue

    # Add a new entry in host_entrys dict

    new_entry = {}
    host_entrys_update = {}
    # create empty hn list for each host entry which define additional interface configurations in 2step
    hn_list = []

    # is there a '#" after hn AND is there a non emtpy string
    if len(records) >1 and len(records[-1]) > 0:
        # get string after last '#'
        t_rec_string = records[-1]
        # remove leading whitespace
        t_rec_string = re.sub(r'^\s+', "", records[-1])

        # get 'key=val' strings
        key_value_pair_strings = t_rec_string.split()
        # get keys and their values

        # emtpy keys list
        keys = []
        key = ""
        val = ""

        for key_val in key_value_pair_strings:
            # do we have a non 'emtpy' value for the key
            l = key_val.split('=')
            if len(l) == 2:
                key,val = l
            else:
                continue

            if key == 'hn':
                hn_list.append(val)
            else:
                new_entry[key] = val
        if len(hn_list) > 0:
            new_entry['hn_list'] = hn_list

    host_entrys_update[fqdn] = new_entry
    #host_entrys[fqdn] = new_entry
    update_nested_dict(host_entrys,host_entrys_update)

    # else:
    #     t_rec_string = "NO-T-RECORDS"

    # get text records


    #outline = "ip=" + ip + " fqdn=" + fqdn + " hn=" + hn + " TREC=\"" + t_rec_string + '\"'
    #print(outline)

# Debug ouput file
with open(tempfile,mode='w') as f:
    for line in lines:
        f.write (line + '\n')

# write output file
with open(outfile,mode='w') as f:
    f.write(json.dumps(host_entrys, sort_keys=True, indent=2, separators=(',', ': ')))

pp(host_entrys)


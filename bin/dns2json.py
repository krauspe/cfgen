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
default_hosts_file = os.path.join(confdir,"test.dns.hosts")
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

host_entrys = {
        "nss.nsa.lgn.dfs.de" :{
            "ip": "10.232.222.10",
            "hname": "nss",
            "dv"  : "eth0",
            "gw"  : "10.232.222.253",
            "sn"  : "255.255.255.0",
            "hn_list": ["nss-mgt","nss-p1","nss-ph"],
            "sy"  : "SIU AFS"
        }
}



if os.path.exists(file):
    # records = [line.rstrip('\n').split('#') for line in open(file) if not line.startswith('#')]
    lines = [line.rstrip('\n') for line in open(file) if not line.startswith('#')]
    lines = list(line for line in lines if line) # only non blank lines
    for line in lines:
        records = line.split('#')
        ip_fqdn_hn = records[0]

        # GET ip, fqdn and hn and add to host_entrys hash


        ip,fqdn,hn = ip_fqdn_hn.split()[:3]



        hn_list = []

        if len(records) >1 and len(records[-1]) > 0:  # is there a '#" after hn AND is there a non emtpy string
            t_rec_string = records[-1] # get string after last '#'
            t_rec_string = re.sub(r'^\s+', "", records[-1]) # remove leading whitespace

            # get the text records from each line (t_rec_string)

            key_value_pair_strings = t_rec_string.split()
            for key_val in key_value_pair_strings:
                if len(key_val) == 2:
                    key,val = key_val.split('=')

        # else:
        #     t_rec_string = "NO-T-RECORDS"

        # get text records


        #outline = "ip=" + ip + " fqdn=" + fqdn + " hn=" + hn + " TREC=\"" + t_rec_string + '\"'
        #print(outline)

    # Debug ouput file
    with open(tempfile,mode='w') as f:
        for line in lines:
            f.write (' '.join(line) + '\n')

else:
    print ("WARNING: %s doesn't exist !!" % file)
    #return []



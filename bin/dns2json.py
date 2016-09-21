#!/usr/bin/env python

from __future__ import print_function
import os
import socket
import collections
import argparse
import json
import hjson
from prettyprint import pp
#import re
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



#TODO: read dns hosts file ....

def getDnsHostsFile(file):
    if os.path.exists(file):
        lines = [line.rstrip('\n').split() for line in open(file) if not line.startswith('#')]
        lines = list(line for line in lines if line) # only non blank lines
        if len(lines) < 0:
            print("WARNING: %s is empty or has no valid lines !!" % file)
        return lines
    else:
        print ("WARNING: %s doesn't exist !!" % file)
        return []

dnslines = getDnsHostsFile(infile)

# Debug ouput file

with open(tempfile,mode='w') as f:
    for line in dnslines:
        f.write (' '.join(line) + '\n')
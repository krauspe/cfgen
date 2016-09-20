#!/usr/bin/env python

#from __future__ import print_function
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

# parse args
formats = ['json,']

parser = argparse.ArgumentParser(description="convert dns hosts entrys with txt records to json")
parser.add_argument("--hosts", type=str, required=False,default=default_hosts_file ,help="hosts file")
parser.add_argument("-f", "--format" , type=str, required=False, default='json', choices=formats, help="output format")

args = parser.parse_args()

print("\nHello Json\n")
#print ('hosts file: {} '.format(args.hosts))
print "hosts file: %s" % args.hosts


#TODO: read dns hosts file ....
def getFileAsList(file):
    if os.path.exists(file):
        in_list = [line.rstrip('\n').split() for line in open(file) if not line.startswith('#')]
        if len(in_list) < 0:
            print "WARNING: %s is empty or has no valid lines !!" % file
        return in_list
    else:
        print "WARNING: %s doesn'reg_window exist !!" % file
        return []


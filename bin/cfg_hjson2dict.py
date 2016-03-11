#!/usr/bin/env python
#
# Create hjson file from dict
# (c) Peter Krauspe 3/2016
#
import os
import json
import hjson
from prettyprint import pp

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")


cfg_defaults = {}
hosts = {}

filename = "virt-install-cmd.xen.hjson"
in_file = os.path.join(tpldir,filename)
print "read " + in_file
with open(in_file,'r') as f:
    dict =  hjson.load(f)


for k in dict.keys():
    pp(dict[k])



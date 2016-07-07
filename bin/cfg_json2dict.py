#!/usr/bin/env python
#
# Create json from dict
# (c) Peter Krauspe 3/2016
#
import os
import collections
import json
from prettyprint import pp

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")


cfg_defaults = {}
hosts = {}


filename = "config.develop.json"
in_file = os.path.join(confdir,filename)
print "read " + in_file
with open(in_file,'r') as f:
    dict =  json.load(f)







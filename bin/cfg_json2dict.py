#!/usr/bin/env python
#
# Create json file from cfg dict
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



# config_dict = {
#     'cfg_defaults':cfg_defaults,
#     'hosts':hosts,
# }
# contens = json.dumps(config_dict,indent=2)

filename = "config.json"
in_file = os.path.join(confdir,filename)
print "read " + in_file
with open(in_file,'r') as f:
    config_dict =  json.load(f)


# ankucken :

#prettyprint.pp(config_dict['cfg_defaults'])
#prettyprint.pp(config_dict['hosts'])

# oder

pp(config_dict)



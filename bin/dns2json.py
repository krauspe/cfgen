#!/usr/bin/env python
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

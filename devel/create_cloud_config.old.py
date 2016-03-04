#!/usr/bin/env python

#
# Create cloud config yml files from template
# (c) Peter Krauspe 2/2016
#
from sys import argv,exit
import os 
import socket
import re

hn = ''
ip = ''

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
ymltpl_file = ''
tpl = ''

def get_ip(hn):
    ip = ''
    try:
        ip =  socket.gethostbyname(hn)
    except socket.gaierror:
        ip = '0.0.0.0'
    return ip

settings = {
	'disk':'/dev/xvda',
	'hn':'',
	'ip':'',
	'ip-etcd-01':get_ip('etcd-01'),
	'ip-etcd-02':get_ip('etcd-02'),
	'ip-etcd-03':get_ip('etcd-03'),
	'ns':'192.169.42.10',
	'gw':'192.169.42.1',
	'dv':'eth0',
	'cloud-config-server':'is01',
	'target-yml':''
}

if len(argv) < 3 :
    print "\nusage: " + os.path.basename(argv[0]) + " <hostname> <tpl-variant>\n"
else:
    hn = argv[1]
    settings['hn'] = hn
    settings['ip'] = get_ip(hn)
    settings['target-yml'] = hn+'.yml' 

    for seStr,repStr in settings.iteritems():
        print "%s = %s" % (seStr,repStr)

    try:
        tpl = argv[2]
    except IndexError:
        print "<hostname> or <tpl-variant> not given. exit."
        exit()

    ymltpl_file = os.path.join(tpldir,"cloud-config."+tpl + '.yml.tpl')

    is_tpl = False
    out_list = []

    ymltpl = open(ymltpl_file,"r")

    for line in ymltpl:
        for seStr,repStr in settings.iteritems():
            if repStr != '':
                l = line.replace('@@'+seStr+'@@',repStr)
                line = l
        if re.match('.*@@.*@@.*',line):
            is_tpl = True
        out_list.append(line)

    ymltpl.close()


    if is_tpl:
        out_file = hn + ".yml.tpl"
        print "creating another template since not all params could be set !"
    else:
	if tpl == 'auto-install': 
            out_file = tpl+'.'+hn + ".yml"
        else:
            out_file = hn + ".yml"


    print "create " + out_file

    ymlout = open(out_file,"w")
    for line in out_list:
        ymlout.write(line)
    ymlout.close()

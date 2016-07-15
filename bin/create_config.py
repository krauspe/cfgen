#!/usr/bin/env python
#
# Create various files from templates
# (c) Peter Krauspe 3/2016
#
import os
import socket
import collections
import argparse
import json
import hjson
from prettyprint import pp
#import re
#from sys import argv,exit


# data handling
# DONEse json.load config/config.develop.json instead of hard coded dict for config
# DONEse hjson for templates (supports multiline strings)
# DONE: create hjson files from tpl files and define short cuts to use in the template strings
# DONEead hjson tpl files and build flat cfg dict as database for replacements
# TODO: import network module, create funcs to calculate bc,subnet from ip,sn  or so, then change templates

# command line handling
# TODO: get possible choices for variants from files in tpl dir :-)
# TODO: add values for dhcpd.conf in hosts and/or host_default
# TODO: complete and activate when everything else works

types =     ['cloud-config','dhcpd','virt-install','kickstart-http','kickstart-nfs']
templates = ['auto-install','xen','entry','gitsrv','nsc']

parser = argparse.ArgumentParser(description="create various config files from host atributes")
parser.add_argument("--hn", type=str, required=True, help="hostname")
parser.add_argument("-p", "--tpl" , type=str, required=True, choices=templates, help="template to use")
parser.add_argument("-t", "--type", type=str, required=True, choices=types, help="config file to create")
args = parser.parse_args()

hn = args.hn
tpl_type = args.type
tpl = args.tpl

#hn = 'etcd-02'
#hn = 'gitsrv2'
#hn = 'adc3-s1'
#tpl_type = 'cloud-config'
#tpl_type = 'kickstart-nfs'
#tpl_type = 'kickstart-http'
#tpl_type = 'dhcpd'
#tpl_type = 'virt-install-cmd'
#tpl = 'auto-install'
#tpl = 'xen'
#tpl = 'entry'
#tpl = 'nsc'
#tpl = 'gitsrv'

site = "lx3.lgn.dfs.de"

# TODO: filname should be defined in template
out_filename = {
    'cloud-config':'@@hn@@.yml',
    'dhcpd':'dhcpd'+'.@@hn@@.conf.entry',
    'virt-install-cmd':'virt-install'+'.@@hn@@.sh',
    'kickstart-nfs':'@@hn@@.' + site + '.nfs.ks',
    'kickstart-http':'@@hn@@.' + site + '.http.ks'
}


# print "hn = %s" % (hn)
# print "tpl_type = %s" % (tpl_type)
# print "tpl = %s" % (tpl)

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")

#tpl_file = os.path.join(tpldir, tpl_type + '.' + tpl + '.tpl')


# vmhost settings

img_basedir = "/var/lib/libvirt/images"
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")

# hack: hard coded SITE
# TODO: generate SITE from current dns domain
#site = "develop"
# read config file config/config.develop.json

filename = "config." + site + ".json"
in_file = os.path.join(confdir,filename)
print "read " + in_file
with open(in_file,'r') as f:
    config_dict = json.load(f)

cfg_defaults = config_dict['cfg_defaults'].copy()
hosts = config_dict['hosts'].copy()


# TODO: not used yet !!
KnownFunctions = [
    'getCoreosInitialClusterString',
    'getAllDhcpHostEntrys',
    ]

# common functions

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

# hostlist functions

def getHostlistFromType(type):
    hostlist = []
    for hn in hosts.iterkeys():
        if hosts[hn]['type'] == type:
            hostlist.append()
    return hostlist



def getDhcpHostEntrys(): # TODO: awake to live :-)
    pass

# network functions

def get_ip(hn):
    ip = ''
    try:
        ip =  socket.gethostbyname(hn)
    except socket.gaierror:
        ip = '0.0.0.0'
    return ip

# application specific functions. The alternative to antlr :-)

# coreos.fleet

def getCoreosInitialClusterString():
    string = ''
    for hn in hosts.iterkeys():
        if hosts[hn]['classes'][0] == 'etcd':
            ip = hosts[hn]['net']['nics']['nic0']['ip']
            string += hn+"=http://"+str(ip)+":2380,"
    string = string.rstrip(',')
    return string

def getTargetYaml(hn):
    return hn+".yml"

# vm creation

# TODO: not yet used
def getInstallImgPath(vm_name,disk):
    dir = getInstallImgDir(vm_name)
    return os.path.join(dir,cfg['vm-name'],cfg['disks'][disk]['img-name'])

# TODO: not yet used
def getInstallImgDir(vm_name):
    return os.path.join(img_basedir,cfg[vm_name])

# TODO: not yet used
def getCreateVmImagesCmd(hn):
    pass


# "@@install-img-path@@": "os.path.join(img_basedir,cfg['vm']['vm-name'],cfg['vm']['disks']['disk0']['img-name'])",
# "@@install-img-format@@": "cfg['vm']['disks']['disk0']['img-format']",
# "@@img-size@@":"cfg['vm']['disks']['disk0']['img-size']"

# "tpl-text":
# '''
# qemu-img create -f @@install-img-format@@ @@install-img-path@@ 10G
# '''


# UTIL

def createObjectFromHostCfg(hn,tpl,tpl_type):
    cfg['hn'] = hn
    update_nested_dict(cfg,hosts[hn]) # join the dicts
    return createObjectFromTemplate(tpl,tpl_type)

def createObjectFromTemplate(tpl,tpl_type):
    tpl_file = os.path.join(tpldir, tpl_type + '.' + tpl + '.hjson')

    print "read tlp_file %s" % tpl_file
    with open(tpl_file,'r') as f:
        tpl_dict =  hjson.load(f)

    content = str(tpl_dict['tpl-text'])
    for k,v in tpl_dict['cfg'].iteritems():
        if v != '':
            seStr = k
            #repStr = eval(v)  # implicit use of cfg,the mad solution :-)
            repStr = getValFromCfg(v)  # implicit use of cfg,the mad solution :-)

            print "replace(%s = %s)" % (k,repStr)
            #conten = content.replace('@@'+seStr+'@@',repStr)
            content = content.replace(seStr, repStr)
    return content

    # pp(cfg)

# TODO: development in parse_tpl_cfg_value_strings.py
def getValFromCfg(v):
    return eval(v)  # TODO: to be exchanged with intelligent save function :-)


#TODO: filenem/(path ?) generation in eigene Struktur mit unterscheidung ob host-bezogen (yml Files) oder liste (dhcpd.con) etc
#TODO ggfs hn aus writeFile hearusnehmen und abghaengig vom tpl/tpl-type anderen parameter uebergeben ?!

def writeFile(hn,contens):
    if tpl == 'auto-install':
        out_filename['cloud-config'] = 'auto-install'+'.@@hn@@.yml'
    filename = out_filename[tpl_type].replace('@@hn@@', hn)
    out_file = os.path.join(deploydir,filename)

    print "create " + out_file
    with open(out_file,'w+') as f:
        f.write(contens)


# main

cfg = cfg_defaults.copy()

# for testing only one possibility: use given tpl and tpl_type
# TODO: handle values/options from cmdline args and create single host related outputs as well as hostlist based outputs
content = createObjectFromHostCfg(hn,tpl,tpl_type)


print "\nOUTPUT:\n"
pp(content)

writeFile(hn, content)


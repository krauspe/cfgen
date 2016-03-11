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
# DONEse json.load config/config.json instead of hard coded dict for config
# DONEse hjson for templates (supports multiline strings)
# TODO: create hjson files from tpl files and define short cuts to use in the template strings
# DONEead hjson tpl files and build flat cfg dict as database for replacements
# TODO: import network module, create funcs to calculate bc,subnet from ip,sn  or so, then change templates

# command line handling
# TODO: get possible choices for variants from files in tpl dir :-)
# TODO: add values for dhcpd.conf in hosts and/or host_default
# TODO: complete and activate when everything else works
# parser = argparse.ArgumentParser(description="create various config files from host atributes")
# parser.add_argument("--hn", type=str, required=True, help="hostname")
# parser.add_argument("-t", "--type", type=str, required=True, choices=['cloud-config','dhcpd','virt-install'], help="config file to create")
# parser.add_argument("-p", "--tpl", type=str, required=True, help="template to use")
# args = parser.parse_args()
#
# hn = args.hn
# tpl_class = args.type
# tpl = args.tpl

hn = 'etcd-02'
tpl_class = 'cloud-config'
#tpl_class = 'dhcpd'
#tpl_class = 'virt-install-cmd'
#tpl = 'auto-install'
#tpl = 'xen'
#tpl = 'entry'
tpl = 'etcd'


out_filename = {
    'cloud-config':'@@hn@@.yml',
    'dhcpd':'dhcpd'+'.@@hn@@.conf.entry',    
    'virt-install-cmd':'virt-install'+'.@@hn@@.sh',
}


# print "hn = %s" % (hn)
# print "tpl_class = %s" % (tpl_class)
# print "tpl = %s" % (tpl)

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")

#tpl_file = os.path.join(tpldir, tpl_class + '.' + tpl + '.tpl')
tpl_file = os.path.join(tpldir, tpl_class + '.' + tpl + '.hjson')


# vmhost settings

img_basedir = "/var/lib/libvirt/images"
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")

# vm settings

#------ hard coded dicts from developement -------
# cfg_defaults = {
#     'descr':'Host definitions',
#     'classes':[],
#     'hardware':'virtual',
#     'net':{
#         'dn':'nw1.lgn.dfs.de',
#         'ns':'192.169.42.10',
#         'gw':'192.169.42.1',
#         'is':'192.169.42.10',
#         'subnet':'192.169.42.0',
#         'dhcp-range-from':'192.169.42.100',
#         'dhcp-range-to':'192.169.42.200',
#         'netconf-type':'dhcp',
#         'nic':'nic0',
#         'nics':{
#             'nic0':{
#                 'dv':'eth0',
#                 'ip':'',
#                 'sn':'255.255.255.0',
#                 'mac':'',
#                 'bridge':'br0',
#                 'options':''
#                 }
#             }
#         },
#     'vm':{
#         'install-tpl':'xen',
#         'ram':'1024',
#         'vcpus':'1',
#         'disks':{
#             'disk0':{
#                 'device':'/dev/xvda',
#                 'img-name':'disk0.qcow2',
#                 'img-format':'qcow2',
#                 'disk-size':'4G',
#                 },
#             },
#         'disk':'disk0',
#     },
#     'app':{
#         'cloud-config-server':'is01',
#         },
#     }
#
# hosts = {
#     'etcd-01':{
#         'classes':['etcd'],
#         'vm':{
#             'vm-name':'etcd-01',
#         },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'ens3',
#                     'ip':'192.168.42.11',
#                     'mac':'00:00:00:00:00:01',
#                     'bridge':'virbr2',
#                     },
#                 },
#             }
#         },
#     'etcd-02':{
#         'classes':['etcd'],
#         'vm':{
#             'vm-name':'etcd-02',
#         },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'ens3',
#                     'ip':'192.168.42.12',
#                     'mac':'00:00:00:00:00:02',
#                     'bridge':'virbr2',
#                     },
#                 },
#             },
#         },
#     'etcd-03':{
#         'classes':['etcd'],
#         'vm':{
#             'vm-name':'etcd-03',
#         },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'ens3',
#                     'ip':'192.168.42.13',
#                     'mac':'00:00:00:00:00:03',
#                     'bridge':'virbr2',
#                     },
#                 },
#             },
#         },
#     'cwp1-s1':{
#         'classes':['nsc.cwp.s1'],
#         'hardware':'physical',
#         'vm':{
#             'vm-name':'cwp1-s1',
#         },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'eth0',
#                     'ip':'192.168.96.20',
#                     'mac':'01:e4:d3:ac:bd:03',
#                     },
#                 },
#             },
#         },
#     'nss':{
#         'classes':['nss','is'],
#         'hardware':'physical',
#         'vm':{
#             'vm-name':'nss-lx3',
#         },
#         'net':{
#             'subnet':'192.168.33.0',
#             'dn':'lx3.lgn.dfs.de',
#             'sn':'255.255.255.0',
#             'gw':'10.232.250.253',
#             'ns':'192.168.33.10',
#             'is':'10.232.250.190',
#             'netconf-type':'static',
#             'nic':'nic0',
#             'nics':{
#                 'nic0':{
#                     'dv':['eth0','is09'],
#                     'ip':['192.168.33.10','192.168.33.9'],
#                     'mac':'00:30:48:b8:f8:80',
#                     'options':'speed 100 duplex ful wol g',
#                     },
#                 'nic1':{
#                     'dv':'eth1',
#                     'ip':'10.232.250.232',
#                     'sn':'255.255.254.0',
#                     'mac':'00:30:48:b8:f8:81',
#                     },
#                 },
#             },
#         },
#
#     'sim1-s1':{
#         'classes':['nsc.sim.s1','failover-nss'],
#         'hardware':'physical',
#         'vm':{
#             'vm-name':'sim1-s1',
#         },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'eth0',
#                     'ip':'192.168.96.20',
#                     'mac':'01:e4:d3:ac:bd:03',
#                     },
#                 },
#             },
#         },
#
#     'is01':{
#         'classes':['is'],
#         'vm':{
#             'vm-name':'inw1',
#             },
#         'net':{
#             'nics':{
#                 'nic0':{
#                     'dv':'eth0',
#                     'ip':'192.168.42.10',
#                     'mac':'00:16:3e:02:3d:c3',
#                     'bridge':'virbr2',
#                     'netconf-type':'static',
#                     },
#                 'nic1':{
#                     'dv':'eth1',
#                     'dn':'se.dfs.de',
#                     'ip':'10.232.250.14',
#                     'sn':'255.255.254.0',
#                     'gw':'10.232.250.253',
#                     'mac':'00:16:3e:02:3d:c3',
#                     'bridge':'br0',
#                     'netconf-type':'static',
#                     },
#                 },
#             },
#         },
#     }
#
# # only for debugging
# # write hard coded dicts to config.json --------
#
# config_dict = {
#     'cfg_defaults':cfg_defaults,
#     'hosts':hosts,
# }
#
# filename = "config.json"
# out_file = os.path.join(confdir,filename)
# print "create " + out_file
# with open(out_file,'w') as f:
#     json.dump(config_dict,f,indent=2)
#----------------------------------------------------------


# read config file config/config.json

filename = "config.json"
in_file = os.path.join(confdir,filename)
print "read " + in_file
with open(in_file,'r') as f:
    config_dict = json.load(f)

cfg_defaults = config_dict['cfg_defaults'].copy()
hosts = config_dict['hosts'].copy()


getFunction = {
    'cloud-config':{
        'initial-cluster-string':'getCoreosInitialClusterString',
        },
    'dhcpd':{
        'dhcpd-host-entrys':'getAllDhcpHostEntrys',
        }
    }

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

# coreos functions

def getCoreosInitialClusterString():
    string = ''
    for hn in hosts.iterkeys():
        if hosts[hn]['classes'][0] == 'etcd':
            ip = hosts[hn]['net']['nics']['nic0']['ip']
            string += hn+"=http://"+str(ip)+":2380,"
    string = string.rstrip(',')
    return string


def getInstallImgPath():
    return os.path.join(img_basedir,cfg['vm-name'],cfg['disks']['disk0']['img-name'])

def getTargetYaml(hn):
    return hn+".yml"

def createObjectFromHostCfg(hn):

    cfg['hn'] = hn
    update_nested_dict(cfg,hosts[hn])  # rekursuv wg hierachie in der cfg ?


    # with open(tpl_file,'r+') as f:
    #     contens = f.read()
    #


    with open(tpl_file,'r') as f:
        tpl_dict =  hjson.load(f)

    #update_nested_dict(cfg,tpl_dict['cfg'])

    contens = str(tpl_dict['tpl-text'])

    for k,v in tpl_dict['cfg'].iteritems():
        if v != '':
            seStr = k
            repStr = eval(v)
            print "replace(%s = %s)" % (k,repStr)
            #ontens = contens.replace('@@'+seStr+'@@',repStr)
            contens = contens.replace(seStr,repStr)
    return contens

    # pp(cfg)

#TODO: filenem/(path ?) generation in eigene Struktur mit unterscheidung ob host-bezogen (yml Files) oder liste (dhcpd.con) etc
#TODO ggfs hn aus writeFile hearusnehmen und abghaengig vom tpl/tpl-type anderen parameter uebergeben ?!

def writeFile(hn,contens):
    if tpl == 'auto-install':
        out_filename['cloud-config'] = 'auto-install'+'.@@hn@@.yml'
    filename = out_filename[tpl_class].replace('@@hn@@', hn)
    out_file = os.path.join(deploydir,filename)

    print "create " + out_file
    with open(out_file,'w+') as f:
        f.write(contens)


# main

cfg = cfg_defaults.copy()
contens = createObjectFromHostCfg(hn)


print "\nOUTPUT:\n"
pp(contens)

writeFile(hn,contens)


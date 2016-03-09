#!/usr/bin/env python
#
# Create various files from templates
# (c) Peter Krauspe 3/2016
#
import os
import socket
import collections
import argparse
#import re
#from sys import argv,exit

# command line handling
#TODO: get possible choices for variants from files in tpl dir :-)
#TODO: add values for dhcpd.conf in hosts and/or host_default

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
    'cloud-config':'cloud-config'+'.@@hn@@.yml',
    'dhcpd':'dhcpd'+'.@@hn@@.conf.entry',    
    'virt-install':'virt-install'+'.@@hn@@.sh',    
}


# print "hn = %s" % (hn)
# print "tpl_class = %s" % (tpl_class)
# print "tpl = %s" % (tpl)

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")

tpl_file = os.path.join(tpldir, tpl_class + '.' + tpl + '.tpl')


# vmhost settings

img_basedir = "/var/lib/libvirt/images"
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")

# vm settings

host_defaults = {
    }

cfg_defaults = {
    'net':{
        'bridge':'virbr2',
        'dn':'nw1.lgn.dfs.de',
        'ns':'192.169.42.10',
        'is':'192.169.42.10',
        'gw':'192.169.42.1',
        'sn':'255.255.255.0',
        'bc':'192.168.24.255',
        'subnet':'192.169.42.0',
        'dhcp-range-from':'192.169.42.100',
        'dhcp-range-to':'192.169.42.200',
        'netconf-type':'dhcp',
        'nic':'nic0',
        },
    'vm'
        'install-tpl':'xen',
        'ram':'1024',
        'vcpus':'1',
        'disks':{
            'disk0':{
                'device':'/dev/xvda',
                'img-name':'disk0.qcow2',
                'img-format':'qcow2',
                'disk-size':'4G',
                },
            },
        'disk':'disk0',
    'app':{
        'cloud-config-server':'is01',
        }
    }

hosts = {
    'etcd-01':{
        'vm-name':'etcd-01',
        'type':'etcd',
        'nics':{
            'nic0':{
                'dv':'ens3',
                'ip':'192.168.42.11',
                'mac':'00:00:00:00:00:01',
                },
            },
        },
    'etcd-02':{
        'vm-name':'etcd-01',
        'type':'etcd',
        'nics':{
            'nic0':{
                'dv':'ens3',
                'ip':'192.168.42.12',
                'mac':'00:00:00:00:00:02',
                },
            },
        },
    'etcd-03':{
        'vm-name':'etcd-01',
        'type':'etcd',
        'nics':{
            'nic0':{
                'dv':'ens3',
                'ip':'192.168.42.13',
                'mac':'00:00:00:00:00:03',
                },
            },
        },
    'is01':{
        'vm-name':'inw1',
        'type':'is',
        'nics':{
            'nic0':{
                'dv':'eth0',
                'ip':'192.168.42.10',
                'mac':'00:16:3e:02:3d:c3',
                'netconf-type':'static',
                },
            'nic1':{
                'dv':'eth1',
                'ip':'10.232.250.14',
                'sn':'255.255.254.0',
                'gw':'10.232.250.253',
                'mac':'00:16:3e:02:3d:c3',
                'netconf-type':'static',
                },
            },
        },
    }

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
        if hosts[hn]['type'] == 'etcd':
            ip = hosts[hn]['ip']
            string += hn+"=http://"+ip+":2380,"
    string = string.rstrip(',')
    return string


def getInstallImgPath():
    return os.path.join(img_basedir,cfg['vm-name'],cfg['disks']['disk0']['img-name'])


def createObjectFromHostCfg(hn):

    cfg['hn'] = hn
    cfg.update(hosts[hn])  # rekursuv wg hierachie in der cfg ?
    #TODO: use update_nested_dict !!1

    cfg['target-yml'] = hn + '.yml'
    cfg['initial-cluster-string'] = getCoreosInitialClusterString()
    cfg['install-img-path'] = getInstallImgPath()
    cfg['install-img-format'] = cfg['disks']['disk0']['img-format']
    cfg['install-bridge'] = cfg['nics']['nic0']['bridge']
    cfg['install-mac'] = cfg['nics']['nic0']['mac']

    with open(tpl_file,'r+') as f:
        contens = f.read()

    for seStr,repStr in cfg.iteritems():
        if repStr != '':
            contens = contens.replace('@@'+seStr+'@@',repStr)
    return contens

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

cfg = host_defaults.copy()
contens = createObjectFromHostCfg(hn)

writeFile(hn,contens)


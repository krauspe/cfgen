#!/usr/bin/env python
#
# Create various files from templates
# (c) Peter Krauspe 3/2016
#
import os
import socket
import argparse
import re


pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")

img_basedir = "/var/lib/libvirt/images"
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")


#tpl_type = 'cloud-config'
#tpl_type = 'dhcpd'
tpl_type = 'virt-install'
#tpl = 'auto-install'
tpl = 'xen_new2'
#tpl = 'entry'
#tpl = 'etcd'

tpl_file = os.path.join(tpldir,tpl_type + '.' + tpl + '.tpl')

cfg = {
    'install-tpl':'xen',
    'cloud-config-server':'is01',
    'ram':'1024',
    'vcpus':'1',
    'disks':{
        'disk0':{
            'device':'/dev/xvda',
            'img-name':'disk0.qcow2',
            'img-format':'qcow2',
            'disk-size':'4G',
        }
    },
    'nics':{
        'nic0':{
            'dv':'eth0',
            'bridge':'virbr2',
            'dn':'nw1.lgn.dfs.de',
            'ns':'192.169.42.10',
            'is':'192.169.42.10',
            'gw':'192.169.42.1',
            'sn':'255.255.255.0',
            'netconf-type':'dhcp',

        }
    },
}

cfg['install-img-path'] = os.path.join(img_basedir,cfg['vm-name'],cfg['disks']['disk0']['img-name'])


with open(tpl_file,'r+') as f:
    tpl_text = f.read()

#print contens

for m in set(re.findall('@@([a-zA-Z0-9-_:()]+)@@',tpl_text)):
    print m

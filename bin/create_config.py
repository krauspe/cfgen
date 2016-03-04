#!/usr/bin/env python
#
# Create various files from templates
# (c) Peter Krauspe 3/2016
#
import os
import socket
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
# tpl_type = args.type
# tpl = args.tpl

hn = 'etcd-01'
#tpl_type = 'cloud-config'
#tpl_type = 'dhcpd'
tpl_type = 'virt-install'
#tpl = 'auto-install'
tpl = 'xen'



out_filename = {
    'cloud-config':'cloud-config'+'.@@hn@@.yml',
    'dhcpd':'dhcpd'+'.@@hn@@.conf.entry',    
    'virt-install':'virt-install'+'.@@hn@@.sh',    
}

if tpl == 'auto-install':
    out_filename['cloud-config'] = 'auto-install'+'.@@hn@@.yml'

# print "hn = %s" % (hn)
# print "tpl_type = %s" % (tpl_type)
# print "tpl = %s" % (tpl)

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")
deploydir = os.path.join(basedir,"deployment")
tpl_file = ''


# vmhost settings

img_basedir = "/var/lib/libvirt/images"
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")

# vm settings

host_defaults = {
    'disk':'/dev/xvda',
    'img-name':'disk0.qcow2',
    'img-format':'qcow2',
    'ram':'1024',
    'vcpus':'1',
    'disk-size':'4G',
    'dv':'eth0',
    'bridge':'virbr2',
    'dn':'nw1.lgn.dfs.de',
    'ns':'192.169.42.10',
    'gw':'192.169.42.1',
    'sn':'255.255.255.0',
    'cloud-config-server':'is01',
    'install-tpl':'xen'
}

hosts = {
    'etcd-01':{
        'vm-name':'etcd-01',
        'ip':'192.168.42.11',
        'mac':'00:00:00:00:00:01',
        'type':'etcd',
        },
    'etcd-02':{
        'vm-name':'etcd-01',
        'ip':'192.168.42.12',
        'mac':'00:00:00:00:00:02',
        'type':'etcd',
        },
    'etcd-03':{
        'vm-name':'etcd-01',
        'ip':'192.168.42.13',
        'mac':'00:00:00:00:00:03',
        'type':'etcd',
        },
    'is01':{
        'vm-name':'inw1',
        'ip':'192.168.42.10',
        'mac':'00:16:3e:02:3d:c3',
        'type':'is',
        }
}

def get_ip(hn):
    ip = ''
    try:
        ip =  socket.gethostbyname(hn)
    except socket.gaierror:
        ip = '0.0.0.0'
    return ip


def get_coreos_initial_cluster_string(*args):
    string = ''
    for hn in args:
        ip = hosts[hn]['ip']
        string += hn+"=http://"+ip+":2380,"
    string = string.rstrip(',')
    return string
    

settings = host_defaults.copy()
settings['hn'] = hn
settings.update(hosts[hn])

settings['target-yml'] = hn+'.yml'
settings['img-path'] = os.path.join(img_basedir,settings['vm-name'],settings['img-name'])
out_filename[tpl_type] = out_filename[tpl_type].replace('@@hn@@',hn)

tpl_file = os.path.join(tpldir,tpl_type + '.' + tpl + '.tpl')
out_file = os.path.join(deploydir,out_filename[tpl_type])

infile = open(tpl_file,"r")
out_list = []

for line in infile:
    for seStr,repStr in settings.iteritems():
        if repStr != '':
            l = line.replace('@@'+seStr+'@@',repStr)
            line = l
    print line
    out_list.append(line)

infile.close()



print "create " + out_file

outfile = open(out_file, "w")
for line in out_list:
    outfile.write(line)
outfile.close()

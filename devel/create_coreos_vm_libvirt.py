#!/usr/bin/env python

#from sys import *
import os
import errno    
cmd_list = []

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

#export http_proxy="http://bremen.se.dfs.de:80"
#export https_proxy=$http_proxy
#export HTTP_PROXY=$http_proxy
#export HTTPS_PROXY=$http_proxy
#export no_proxy=".se.dfs.de,is01"

##if len(argv) <= 1:
##  print "usage: %s <docker-vm-name>" % os.path.basename(__file__)
##  exit()
  
#vm = argv[1]

vm = "etcd-01"
mac = "00:00:00:00:00:01"
disk_size = "4G"

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")

libvirt_img_dir = "/var/lib/libvirt/images"
vm_dir = os.path.join(libvirt_img_dir,vm)
tftp_dir = "/srv/inst/tftpboot"
initrd = os.path.join(tftp_dir,"coreos_production_pxe_image.cpio.gz")
kernel = os.path.join(tftp_dir,"coreos_production_pxe.vmlinuz")
vm_disk = os.path.join(vm_dir,vm+".disk0.qcow2")

#mkdir_p(vm_dir)

cmd_line = "mkdir -p "+vm_dir 
print cmd_line
cmd_line = "qemu-img create -f qcow2 "+vm_disk+" "+disk_size
print cmd_line
cmd_list = []
cmd_list.append("virt-install")
cmd_list.append("--connect xen+ssh:///system")
cmd_list.append("--pxe")
cmd_list.append("--hvm")
cmd_list.append("--name="+vm)
cmd_list.append("--ram=1024")
cmd_list.append("--vcpus=1")
cmd_list.append("--os-type=linux")
cmd_list.append("--os-variant=sles12")
#cmd_list.append("--disk path="+vm_disk+",format=qcow2,bus=virtio")
cmd_list.append("--disk path="+vm_disk+",format=qcow2")
#cmd_list.append("--filesystem "+vm_dir+"/,config-2,type=mount,mode=squash")
cmd_list.append("--network bridge=virbr2,mac="+mac)
cmd_list.append("--vnc")
#cmd_list.append("--noautoconsole")

#cmd_line = " ".join(cmd_list)
#print cmd_line

for s in cmd_list:
    print " %s \\" % (s)
print ""


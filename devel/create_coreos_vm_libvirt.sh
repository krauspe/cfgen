#!/bin/bash

export http_proxy="http://bremen.se.dfs.de:80"
export https_proxy=$http_proxy
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$http_proxy
export no_proxy=".se.dfs.de,is01"

docker_vm=$1

if [[ -z $docker_vm ]]; then
  echo
  echo "usage: $(basename $0) <docker-vm-name>"
  echo
  exit 1
fi

libvirt_img_dir=/var/lib/libvirt/images
vm_dir=${libvirt_img_dir}/${docker_vm}
source_img_dir=${libvirt_img_dir}/INSTALL
coreos_img=${source_img_dir}/coreos_production_qemu_image.img
vm_disk0=${vm_dir}/${docker_vm}.disk0.qcow2

mkdir -p ${vm_dir}/openstack/latest

if [[ $2 == "-u" ]]; then
  echo
  echo "updating ${coreos_img}.."
  wget http://stable.release.core-os.net/amd64-usr/current/coreos_production_qemu_image.img.bz2 -O - | bzcat > ${coreos_img}
  echo "update done."
fi

if [[ -d $vm_dir && -f $coreos_img ]] ; then
  cd $vm_dir
  cmd="qemu-img create -f qcow2 -b $coreos_img $vm_disk0 "; echo $cmd
  $cmd
  cmd="wget http://is01/docker/${docker_vm}.yml"; echo $cmd
  $cmd
pwd
  cmd="mv ${docker_vm}.yml  openstack/latest/user_data"; echo $cmd
  $cmd
else
  echo "$vm_dir or $coreos_img doesn't exit or could'nt create it, exiting !"
  exit 1
fi

if [[ $2 == "-s" || $2 == "-us" ]]; then
  echo
  echo "running virt-install .."
  echo
  cmd="virt-install --connect qemu:///system \
	--import --name $docker_vm \
	--ram 1024 --vcpus 1 --os-type=linux \
	--os-variant=virtio26 \
	--disk path=$vm_disk0,format=qcow2,bus=virtio \
	--filesystem $vm_dir/,config-2,type=mount,mode=squash \
	--network bridge=virbr0,type=bridge \
	--vnc --noautoconsole"
	#--network bridge=virbr0,mac=52:54:00:fe:b3:c1,type=bridge \
  echo $cmd
  $cmd
  echo
fi


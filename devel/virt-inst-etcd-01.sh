img=/var/lib/libvirt/images/etcd-01/etcd-01.disk0.qcow2 

[[ -f $img ]] && rm $img
qemu-img create -f qcow2 $img 5g

 virt-install \
 --connect xen+ssh:///system \
 --pxe \
 --hvm \
 --name=etcd-01 \
 --ram=1024 \
 --vcpus=1 \
 --os-type=linux \
 --os-variant=sles12 \
 --disk path=/var/lib/libvirt/images/etcd-01/etcd-01.disk0.qcow2,format=qcow2 \
 --network bridge=virbr2,mac=00:00:00:00:00:01 \
 --vnc 

# --noautoconsole 


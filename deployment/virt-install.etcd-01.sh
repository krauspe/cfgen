virt-install \
    --connect xen+ssh:///system \
    --pxe \
    --hvm \
    --os-type=linux \
    --os-variant=sles12 \
    --disk path="/var/lib/libvirt/images/etcd-01/disk0.qcow2",format=qcow2 \
    --network bridge=virbr2,mac=00:00:00:00:00:01 \
    --vnc

virt-install \
    --connect xen+ssh:///system \
    --pxe \
    --hvm \
    --os-type=linux \
    --os-variant=sles12 \
    --disk path="@@img-path@@",format=@@img-format@@ \
    --network bridge=@@bridge@@,mac=@@mac@@ \
    --vnc

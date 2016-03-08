virt-install \
    --connect xen+ssh:///system \
    --pxe \
    --hvm \
    --os-type=linux \
    --os-variant=sles12 \
    --disk path="@@install-img-path@@",format=@@install-img-format@@ \
    --network bridge=@@install-bridge@@,mac=@@install-mac@@ \
    --vnc

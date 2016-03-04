for i in 01 02 03
do
  ./create_cloud_config.py etcd-$i auto-install
  ./create_cloud_config.py etcd-$i etcd
done

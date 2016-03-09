# /etc/dhcpd.conf 
#
# Peter Krauspe DFS, 03/2016
#
#default-lease-time 14400; # suse orig
default-lease-time 300;
#max-lease-time 172800; # suse orig
max-lease-time 600;
ddns-update_nested_dict2-style none; ddns-updates off;
#log-facility local7;
server-name newsimweb;

option domain-name "@@dn@@";
option domain-name-servers @@ns@@;

#allow bootp;

subnet @@subnet@@ netmask @@sn@@ {
  range dynamic-bootp @@range_from@@ @@range_to@@;
  option subnet-mask @@sn@@;
  option broadcast-address @@bc@@;
  next-server @@is@@;
  filename "pxelinux.0";
}

@@dhcpd-host-entrys@@
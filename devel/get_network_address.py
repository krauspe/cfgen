#!/usr/bin/env python



def getNetworkAddr(ip, netmask):
    ip_int = ip.split('.')
    netmask_int = netmask.split('.')
    network = '.'.join([str(int(ip_int[n]) & int(netmask_int[n])) for n in range(0,4)])
    print network


ip = '10.232.250.190'
netmask = '255.255.254.0'

getNetworkAddr(ip, netmask)
#!/usr/bin/env python
#
# Create json file from cfg dict
# (c) Peter Krauspe 3/2016
#
import os
import collections
import json
import prettyprint

pydir =  os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(pydir)
confdir = os.path.join(basedir,"config")
tpldir = os.path.join(basedir,"tpl")


cfg_defaults = {
    'descr':'Host definitions',
    'classes':[],
    'hardware':'virtual',
    'net':{
        'dn':'nw1.lgn.dfs.de',
        'ns':'192.169.42.10',
        'gw':'192.169.42.1',
        'is':'192.169.42.10',
        'subnet':'192.169.42.0',
        'dhcp-range-from':'192.169.42.100',
        'dhcp-range-to':'192.169.42.200',
        'netconf-type':'dhcp',
        'nic':'nic0',
        'nics':{
            'nic0':{
                'dv':'eth0',
                'ip':'',
                'sn':'255.255.255.0',
                'mac':'',
                'options':''
                }
            }
        },
    'vm':{
        'install-tpl':'xen',
        'ram':'1024',
        'vcpus':'1',
        'bridge':'virbr2',
        'disks':{
            'disk0':{
                'device':'/dev/xvda',
                'img-name':'disk0.qcow2',
                'img-format':'qcow2',
                'disk-size':'4G',
                },
            },
        'disk':'disk0',
    },
    'app':{
        'cloud-config-server':'is01',
        },
    }

hosts = {
    'etcd-01':{
        'classes':['etcd'],
        'vm':{
            'vm-name':'etcd-01',
        },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'ens3',
                    'ip':'192.168.42.11',
                    'mac':'00:00:00:00:00:01',
                    },
                },
            }
        },
    'etcd-02':{
        'classes':['etcd'],
        'vm':{
            'vm-name':'etcd-02',
        },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'ens3',
                    'ip':'192.168.42.12',
                    'mac':'00:00:00:00:00:02',
                    },
                },
            },
        },
    'etcd-03':{
        'classes':['etcd'],
        'vm':{
            'vm-name':'etcd-03',
        },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'ens3',
                    'ip':'192.168.42.13',
                    'mac':'00:00:00:00:00:03',
                    },
                },
            },
        },
    'cwp1-s1':{
        'classes':['nsc.cwp.s1'],
        'hardware':'physical',
        'vm':{
            'vm-name':'cwp1-s1',
        },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'eth0',
                    'ip':'192.168.96.20',
                    'mac':'01:e4:d3:ac:bd:03',
                    },
                },
            },
        },
    'nss':{
        'classes':['nss','is'],
        'hardware':'physical',
        'vm':{
            'vm-name':'nss-lx3',
        },
        'net':{
            'subnet':'192.168.33.0',
            'dn':'lx3.lgn.dfs.de',
            'sn':'255.255.255.0',
            'gw':'10.232.250.253',
            'ns':'192.168.33.10',
            'is':'10.232.250.190',
            'netconf-type':'static',
            'nic':'nic0',
            'nics':{
                'nic0':{
                    'dv':['eth0','is09'],
                    'ip':['192.168.33.10','192.168.33.9'],
                    'mac':'00:30:48:b8:f8:80',
                    'options':'speed 100 duplex ful wol g',
                    },
                'nic1':{
                    'dv':'eth1',
                    'ip':'10.232.250.232',
                    'sn':'255.255.254.0',
                    'mac':'00:30:48:b8:f8:81',
                    },
                },
            },
        },

    'sim1-s1':{
        'classes':['nsc.sim.s1','failover-nss'],
        'hardware':'physical',
        'vm':{
            'vm-name':'sim1-s1',
        },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'eth0',
                    'ip':'192.168.96.20',
                    'mac':'01:e4:d3:ac:bd:03',
                    },
                },
            },
        },

    'is01':{
        'classes':['is'],
        'vm':{
            'vm-name':'inw1',
            },
        'net':{
            'nics':{
                'nic0':{
                    'dv':'eth0',
                    'ip':'192.168.42.10',
                    'mac':'00:16:3e:02:3d:c3',
                    'netconf-type':'static',
                    },
                'nic1':{
                    'dv':'eth1',
                    'dn':'se.dfs.de',
                    'ip':'10.232.250.14',
                    'sn':'255.255.254.0',
                    'gw':'10.232.250.253',
                    'mac':'00:16:3e:02:3d:c3',
                    'netconf-type':'static',
                    },
                },
            },
        },
    }



config_dict = {
    'cfg_defaults':cfg_defaults,
    'hosts':hosts,
}

filename = "config.develop.json"
out_file = os.path.join(confdir,filename)
print "create " + out_file
with open(out_file,'w') as f:
    json.dump(config_dict,f,indent=2)



#cloud-config

hostname: @@hn@@

coreos:
  fleet:
    etcd_servers: "http://127.0.0.1:4001"
    metadata: "hw=metal,disk=hdd"
  update_nested_dict2:
    reboot-strategy: etcd-lock
  locksmith:
      endpoint: 127.0.0.1:4001

  units:
    - name: etcd_env.service
      command: start
      content: |
          [Unit]
          Description=etcd_env
          Requires=network.target network-online.target
          After=network.target network-online.target

          [Service]
          ExecStart=/etc/etcd_env.sh

    - name: etcd.service
      command: start
      content: |
        [Unit]
        Description=etcd
        Requires=etcd_env.service
        After=etcd_env.service
        Conflicts=etcd2.service

        [Service]
        User=etcd
        PermissionsStartOnly=true
        EnvironmentFile=/etc/etcd.env
        ExecStart=/usr/bin/etcd -name ${HOSTNAME} -addr ${IP}:4001 -peer-addr ${IP}:7001 -data-dir=/var/lib/etcd -discovery ${DISCOVERY_URL}
        Restart=always
        RestartSec=10s
        LimitNOFILE=40000

    - name: fleet.service
      command: start
    - name: docker.service
      command: restart
    - name: update_nested_dict2-engine.service
      command: restart


users:
   - name: core
     passwd: $1$17tYvTBd$RrkLVIogkO6D.C7HEhSAV.
     groups:
       - sudo
       - docker
     ssh-authorized-keys:
       - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDJm894+prTMekU1aSpvxBIC0/9fQbWzsi4PioHFHON7SLbNs4yzhRPVsQckix8i9Xz1egIFyKs4HU87tE1M8KhDt23KjRTcpWvdn1FRbqGKxumUeGlsnCGcWMq7ijsIq95P/7W3McSvaqCyHQeLomIk/oEEnbq8576kUAMU3GKihuBWHYFkrnsBV9NcLXkbzN/1tfrysWGNNtowkD52tc2aInCIMHEdTp1c7Uod/MrCM6gOefhsTYKkwXkBM+Jw1eVk2Zg28FsHAuB7GuxdFysCjEk0FWR7ZT7g0ZbkbOUgXXOnoZyxJeyOF3uyXLfAjvsrbOZzGFPvKFeSiyq1/w5

write_files:
    - path: /etc/systemd/system/docker.service.d/http-proxy.conf
      owner: core:core
      permissions: 0644
      content: |
        [Service]
        Environment="HTTP_PROXY=http://bremen.se.dfs.de:80" "NO_PROXY=localhost,127.0.0.0/8,10.232.0.0/23,se.dfs.de"
    - path: /etc/systemd/system/update_nested_dict2-engine.service.d/proxy.conf
      permissions: 0644
      content: |
        [Service]
        Environment="ALL_PROXY=http://bremen:80" "HTTP_PROXY=http://bremen.se.dfs.de:80"
    - path: /etc/systemd/system/docker.service.d/insecure-registry.conf
      permissions: 0644
      content: |
        [Service]
        Environment=DOCKER_OPTS='--insecure-registry="dreg01.se.dfs.de:5000"'
    - path: /etc/etcd_env.sh
      permissions: 0755
      content: |
         #!/bin/sh
         echo "IP=`ip route get 8.8.8.8 | awk 'NR==1 {print $NF}'`" > /etc/etcd.env
         #echo "DISCOVERY_URL=http://10.232.250.164:4001/v2/keys/64a804bb-b3da-4e8b-884e-1a78239181ab" >> /etc/etcd.env
         echo "DISCOVERY_URL=@@discovery_url@@" >> /etc/etcd.env
         echo "HOSTNAME=`hostname`" >> /etc/etcd.env




#cloud-config

hostname: @@hn@@


coreos:
  etcd2:
    advertise-client-urls: "http://127.0.0.1:2379"
    initial-advertise-peer-urls: "http://localhost:2380,http://localhost:7001"
    listen-client-urls: "http://0.0.0.0:2379"
    listen-peer-urls: "http://localhost:2380"
  fleet:
    etcd_servers: "http://127.0.0.1:2379"
    metadata: "hw=virtual,disk=virtual,role=worker,frontend=true"
  units:
    - name: etcd2.service
      command: start
    - name: fleet.service
      command: start
    - name: docker.service
      command: restart
    - name: update-engine.service
      command: restart
    - name: systemd-timesyncd.service
      command: start
    - name: settimezone.service
      command: start
      content: |
        [Unit]
        Description=Set the timezone

        [Service]
        ExecStart=/usr/bin/timedatectl set-timezone Europe/Berlin
        RemainAfterExit=yes
        Type=oneshot

  update:
    reboot-strategy: off

users:
   - name: core
     passwd: $1$17tYvTBd$RrkLVIogkO6D.C7HEhSAV.
     groups:
       - sudo
       - docker
     ssh-authorized-keys:
       - ssh-dss AAAAB3NzaC1kc3MAAACBANJK832kLar/WqWvQIwYlbx5xqbKPjV62NoLhzue1krJ1q37DO0X35sZiTtWt8Mj+rrkJhn4Y0tiKvQ+7qnkP4w9MjNrV8wciudjFRJjO5hHI7KUAGTzbXEjvlgh/koKTobRSMH8bBQcbOhgUG9F9BLQh9YhKtANvHxsF68VZ639AAAAFQCbaLxQko8Rl7DfVoUrLpq84qenUQAAAIEAiC06PTDxtYQcnRRIpzgJwxFdvT5ARiwHxcntVZgQ2LaEJBo3WRDm7fmmTdj9TPt8H8Nufv94MFwBToboEvq8N9QLaDOUngALI8hfzwXLbDBigo+0cLxZX4nUi5iHXKyNzlGfKfA1GTnf+fItZRKeabV9Ddqbajkw07NW5XnkVM0AAACAPIv9BkDtdGd2PavtlawHQ1O1S7ViNFdjijQBTxDncm1VfiDwzGMjFeR90Jse3Lyj6tbfW3BC8XMdVJYnV1pbfqTTVEs2Elq/Ww9Y4Oo9ttAga9em18X+wCQA89BGlj9DNobQmUR0cqeX8IwGnrEWUk9gqJ3geyjyrnCgKtKULN8= 
   - name: root
     passwd: $1$17tYvTBd$RrkLVIogkO6D.C7HEhSAV.
     groups:
       - root
       - wheel
     ssh-authorized-keys:
       - ssh-dss AAAAB3NzaC1kc3MAAACBANJK832kLar/WqWvQIwYlbx5xqbKPjV62NoLhzue1krJ1q37DO0X35sZiTtWt8Mj+rrkJhn4Y0tiKvQ+7qnkP4w9MjNrV8wciudjFRJjO5hHI7KUAGTzbXEjvlgh/koKTobRSMH8bBQcbOhgUG9F9BLQh9YhKtANvHxsF68VZ639AAAAFQCbaLxQko8Rl7DfVoUrLpq84qenUQAAAIEAiC06PTDxtYQcnRRIpzgJwxFdvT5ARiwHxcntVZgQ2LaEJBo3WRDm7fmmTdj9TPt8H8Nufv94MFwBToboEvq8N9QLaDOUngALI8hfzwXLbDBigo+0cLxZX4nUi5iHXKyNzlGfKfA1GTnf+fItZRKeabV9Ddqbajkw07NW5XnkVM0AAACAPIv9BkDtdGd2PavtlawHQ1O1S7ViNFdjijQBTxDncm1VfiDwzGMjFeR90Jse3Lyj6tbfW3BC8XMdVJYnV1pbfqTTVEs2Elq/Ww9Y4Oo9ttAga9em18X+wCQA89BGlj9DNobQmUR0cqeX8IwGnrEWUk9gqJ3geyjyrnCgKtKULN8= 

write_files:
    - path: /etc/systemd/system/docker.service.d/http-proxy.conf
      owner: core:core
      permissions: 0644
      content: |
        [Service]
        Environment="HTTP_PROXY=http://bremen.se.dfs.de:80" "NO_PROXY=localhost,127.0.0.0/8,10.232.0.0/23,se.dfs.de"
    - path: /etc/systemd/system/update-engine.service.d/proxy.conf
      permissions: 0644
      content: |
        [Service]
        Environment="ALL_PROXY=http://bremen.se.dfs.de:80" "HTTP_PROXY=http://bremen.se.dfs.de:80"
    - path: /etc/systemd/system/docker.service.d/insecure-registry.conf
      permissions: 0644
      content: |
        [Service]
        Environment=DOCKER_OPTS='--insecure-registry="dreg01.se.dfs.de:5000"'
    - path: /etc/systemd/timesyncd.conf
      content: |
         [Time]
         NTP=timesrv.se.dfs.de
    - path: /etc/profile.d/etcdctl.sh
      content: |
         export ETCDCTL_PEERS=http://127.0.0.1:2379



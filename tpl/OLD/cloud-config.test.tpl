#cloud-config

hostname: @@hn@@

write_files:
    - path: /etc/systemd/network/static.network
      owner: core:core
      permissions: 0644
      content: |
        [Match]
        Name=@@dv@@

        [Network]
        Address=@@ip@@
        Gateway=@@gw@@
        DNS=@@ns@@

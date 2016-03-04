#cloud-config

coreos:
  units:
    - name: auto-worker-install.service
      command: start
      content: |
        [Unit]
        Description=Autoinstall core os
        [Service]
        Type=oneshot
        Environment=SYSTEMD_LOG_LEVEL=debug
        ExecStartPre=/bin/wget http://@@cloud-config-server@@/cloud-config/@@target-yml@@
        ExecStart=/bin/sh -c "/usr/bin/coreos-install -b http://@@cloud-config-server@@/coreos -c @@target-yml@@ -o xen -d @@disk@@ "
        ExecStartPost=/bin/sh -c "reboot"

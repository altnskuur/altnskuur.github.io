---
technical: true
personal: false
date: 2026-10-18
edited: 2026-10-18T15:54:00.000Z
notion: 3fd945c9dc4380e8aef9c84098f856f8
---
# Configuring Kernel Console Output

1. Edit the GRUB Configuration:
```bash
sudo nano /etc/default/grub
```

2. Configure the Kernel Command Line: 
  Locate the `GRUB_CMDLINE_LINUX_DEFAULT` or `GRUB_CMDLINE_LINUX` line and add multiple `console=` parameters. For example:

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash console=tty0 console=ttyS0,115200n8"
```

3. Update GRUB:
```bash
sudo update-grub
```

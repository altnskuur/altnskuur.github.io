---
technical: true
personal: false
date: 2026-10-18
edited: 2026-10-18T15:54:00.000Z
notion: 3fd945c9dc4380929e61f32c8e0a336f
---
# Creating a Script

`/usr/local/bin` path is on `sudo` ’s path by default. So if you want to create a script working with `sudo`, create it on this path. 

These example belongs to a fan speed/pwm controller for ADLINK products. 

### Create the Script

```bash
sudo nano /usr/local/bin/fan_set
```

### Fill the Script

```bash
#!/bin/bash
# Usage: fan_set <percent 0-100>

if [ -z "$1" ]; then
    echo "Usage: fan_set <0-100>"
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -gt 100 ]; then
    echo "Error: value must be an integer between 0 and 100"
    exit 1
fi

semautil /f set_pwm_points 1 20 20 20 "$1"
```

Save with `Ctrl+O`, then `Enter`, then exit with `Ctrl+X`.

### Make It Exacutable

```bash
sudo chmod +x /usr/local/bin/fan_set
```

### Use It

```bash
sudo fan_set 60
```

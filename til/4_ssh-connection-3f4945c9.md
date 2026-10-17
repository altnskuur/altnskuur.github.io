---
technical: true
personal: false
date: 2026-10-09
edited: 2026-10-17T19:21:00.000Z
notion: 3f4945c9dc4380d79ad7c780c1b79c03
---
# SSH Connection

---

# Pre-Descriptions

Two device defined. 

1. **Host Device:** The device that we want to control.
2. **Client Device:**  The device used to control the host device.

# SSH Connection Commands

## Host Commands

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo ufw allow OpenSSH
```

## Client Commands

```bash
ssh-keygen -t ed25519
ssh-copy-id <host_username>@<host_ip>
ssh <host_username>@<host_ip>
```

## Details About Commands

| Command | Where | What it does | Why |
|---|---|---|---|
| `ssh-keygen -t ed25519` | Client | Creates your key pair in `~/.ssh/` | `-t ed25519` selects a modern, fast, secure algorithm (shorter keys than RSA with equal or better security) |
| `sudo apt install -y openssh-server` | Host | Installs the SSH server | Ubuntu Desktop images don’t include it by default, which caused “Connection refused” |
| `sudo systemctl enable --now ssh` | Host | Starts the SSH server now and on every boot | `enable` = start at boot, `--now` = start immediately |
| `sudo ufw allow OpenSSH` | Host | Opens port 22 in the firewall | Keeps the firewall from blocking SSH once it’s enabled |
| `ssh-copy-id <host_username>@<host_ip>` | Client | Logs in once with the password, then appends your **public key** to `/home/mnas/.ssh/authorized_keys` on the MNAS with the correct permissions | One-time setup, so future logins use the key instead of the password |
| `ssh <host_username>@<host_ip>` | Client | Opens a remote terminal on the MNAS | Verifies that key login works with no password prompt |

## Additional Points About Commands

### `ssh-keygen -t ed15519`  

- `ssh-keygen`: Command of generating a key.
- `-t`: it means “What type of key that we want to generate”.
- `ed25519`: Edwards Curva Digital Signature Algorithm. a method for creating and checking digital signatures. 25519 means, curve 25119 elliptic curve. Curve defined over the prime number. ($2^{255}-19$)
  - What can we write instead of `ed25519`.
|  |  |  |
|---|---|---|
| ed25519  | `ed25519` | best. modern, fast, secure |
| rsa | `rsa -b 4096` | for old servers. default number is 3072 |
| edcsa | `edcsa -b 521` | rarely. can be 256, 384, 521 |

### `sudo apt instal -y openssh-server`  

SSH is one of the “conversation” that travel on those roads, just like web browsing “HTTP” is another. The original SSH was written by Tatu Ylönen in 1995 in Finland. it started free, but later versions became commercial and closed source. In 1999, developers of the OpenBSD operating system took the last freely licansed version, cleaned it up and continued it as OpenSSH.

- OpenSSH: the standard on most systems.
- Dropbear: very small version used on router and embedded systems.
- PuTTY: popular SSH client for windows.
- Tectia: commercial descendant of the original SSH.
- libssh and Paramiko: libraries that let programs use SSH

### `ssh-copy-id <host_username>@<host_ip>`  

- `ssh-copy-id`: shares with device to the public key.

**NAS Example:**

- <host_username>: `nas`
- <host_ip>: `192.168.10.1`  
- Complete command: `ssh-copy-id nas@192.168.10.1`  
# Additional Commands

## Removing Remembered Host

```bash
ssh-keygen -f "<path_to_ssh>/.ssh/knownhosts" -R "<host_username>@<host_ip>"
```

If reader try to connect different device with the same ip, reader needs to remove latest host’s informations.

**NAS Example:**

- <path_to_ssh>: `~`
- <host_username>: `nas`  
- <host_ip>: `192.168.10.1`  
- Complete command: `ssh-keygen -f "~/.ssh/knownhosts" -R "nas@192.168.10.1"`  
## Shorter SSH Connection Command with an SSH Config Alias

```bash
nano <path_to_ssh>/.ssh/config
# ------------------------------
# config file opens
Host <custom_name>
	HostName <host_ip>
	User <host_username>
	IdentityFile <path_to_ssh>/.ssh/id_ed25519 # if take ssh key with ed25519
```

After this config file, reader can connect ssh with this command:

```bash
ssh <custom_name>
```

**NAS Example:**

- <custom_name>: `ssh_nas`
- <host_ip>: `192.168.10.1`  
- <host_username>: `nas`  
- <path_to_ssh>: ~
- Complete config:
```bash
nano ~/.ssh/config
# ------------------------------
# config file opens
Host ssh_nas
	HostName 192.168.10.1
	User nas
	IdentityFile ~/.ssh/id_ed25519 # if take ssh key with ed25519
```

- Complete command:
```bash
ssh ssh_nas
```

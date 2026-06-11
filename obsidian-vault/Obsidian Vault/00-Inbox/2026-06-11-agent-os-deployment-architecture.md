---
date: 2026-06-11
tags: [agent-os, deployment, cloudflare-tunnel, vps, caddy, hosting, security]
project: "AI-Automation"
source: "Deployment Architecture Session"
---

# Agent OS Deployment Architecture & Implementation Guide

## Key Idea
Exposing the local Agent OS instance via a secure Cloudflare Tunnel, or deploying to a dedicated Linux VPS Droplet backed by Caddy reverse proxy, while maintaining the hybrid link to the local Obsidian Vault.

## Details

### 1. Architectural Strategy: Local Tunnel vs. Remote VPS

Depending on computing requirements, you can choose between two main deployment styles:

| Feature | Option A: Local Cloudflare Tunnel (Recommended) | Option B: Remote Linux VPS |
| :--- | :--- | :--- |
| **Where it runs** | Your local desktop machine (Windows) | A cloud provider (DigitalOcean, GCP, Hetzner) |
| **Obsidian Access**| Direct, real-time filesystem access | Delegated via Local Bridge URL tunnel |
| **Security** | Cloudflare Access + Local Authentication | Firewall, SSH, systemd sandbox, reverse proxy |
| **Setup Cost** | Free, runs on existing hardware | ~$5-$10/month Droplet cost |

---

### 2. Option A: Local Cloudflare Tunnel (Windows Host)

A Cloudflare Tunnel connects your local machine to Cloudflare's network without opening inbound firewall ports on your router.

#### A. Installation
Install the Cloudflare Tunnel daemon (`cloudflared`) on Windows using Winget:
```powershell
winget install --id Cloudflare.cloudflared
```

#### B. Authentication & Login
Log in to your Cloudflare account to associate the daemon with your domain:
```powershell
cloudflared tunnel login
```
*This opens a browser window. Select your domain to generate the certificate file (`cert.pem`).*

#### C. Create the Tunnel
Create a named tunnel named `agent-os`:
```powershell
cloudflared tunnel create agent-os
```
*This command outputs a Tunnel UUID and generates a credential JSON file in `C:\Users\navka\.cloudflared\`.*

#### D. Configuration File
Create a configuration file at `C:\Users\navka\.cloudflared\config.yml`:
```yaml
tunnel: <TUNNEL_UUID>
credentials-file: C:\Users\navka\.cloudflared\<TUNNEL_UUID>.json

ingress:
  - hostname: agentos.yourdomain.com
    service: http://localhost:8765
  - service: http_status:404
```

#### E. Route Domain & Run
Create the DNS record routing your subdomain to the tunnel:
```powershell
cloudflared tunnel route dns agent-os agentos.yourdomain.com
```

Test running the tunnel from the command line:
```powershell
cloudflared tunnel run agent-os
```

#### F. Run as a Windows Service
To ensure the tunnel runs 24/7 in the background without terminal windows:
```powershell
cloudflared service install
Start-Service-WithName "cloudflared"
```

---

### 3. Option B: Linux VPS Droplet + Caddy Reverse Proxy

If you want a dedicated cloud instance running Ubuntu 22.04 LTS:

#### A. Initial Server Configuration
Log into the server and ensure core tools are installed:
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git python3 python3-pip python3-venv curl ufw
```

#### B. Execute Deployment Script
Run the automated `deploy.sh` script to set up a dedicated system user, configure a python virtual environment, and install the systemd service:
```bash
sudo bash deploy.sh
```

#### C. Configure Caddy for SSL
Caddy automatically provisions and renews SSL certificates (Let's Encrypt). Install Caddy:
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y
```

Configure `/etc/caddy/Caddyfile`:
```caddy
agentos.yourdomain.com {
    reverse_proxy localhost:8765
}
```
Reload Caddy to apply settings:
```bash
sudo systemctl reload caddy
```

---

### 4. Hybrid Local Bridge Integration
When Agent OS is running on a cloud VPS, it cannot directly access your local Obsidian Vault. It relies on the **Local Bridge** model to forward file actions back to your local machine.

```
[Cloud VPS] ──(Forward POST/GET)──> [Cloudflare/Ngrok Tunnel] ──> [Local Windows Bridge] ──> [Local Obsidian Vault]
```

To configure this:
1. Keep the local server running on your Windows machine, exposed via Ngrok/Cloudflare (e.g. `https://crying-chili-almost.ngrok-free.dev`).
2. On the Cloud VPS, update `/opt/agent_os/.env` to point to the local instance:
   ```env
   AGENT_OS_HOST=0.0.0.0
   AGENT_OS_PORT=8765
   AGENT_OS_API_KEY=e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b

   # Forwarding configuration
   LOCAL_BRIDGE_URL=https://crying-chili-almost.ngrok-free.dev
   LOCAL_BRIDGE_KEY=e84c2337a06d5d5f46406911060bdae59f41ce2c6e276ce87de502ff34526f8b
   ```

---

## Action / Next Steps
- [ ] Determine if Option A (Local Tunnel) or Option B (VPS Droplet) fits your current workflow goals.
- [ ] Purchase/Map domain in Cloudflare (if configuring Option A).
- [ ] Spin up a $5 Ubuntu droplet (if configuring Option B).

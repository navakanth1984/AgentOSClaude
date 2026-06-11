#!/bin/bash
# deploy.sh - Automation script to deploy Agent OS onto a Linux VPS (Ubuntu/Debian)
# Run as root or with sudo.

set -e

# Colors for logs
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}  Agent OS - Automated VPS Deployment Script        ${NC}"
echo -e "${CYAN}====================================================${NC}"

# 1. Update OS and Install Core Packages
echo -e "\n${GREEN}[1/5] Updating packages and installing dependencies...${NC}"
apt-get update
apt-get install -y git python3 python3-pip python3-venv curl ufw

# 2. Setup Dedicated Application User
if ! id "agentos" &>/dev/null; then
    echo -e "\n${GREEN}[2/5] Creating dedicated system user 'agentos'...${NC}"
    useradd -m -s /bin/bash agentos
fi

# 3. Setup Project Directory and Virtual Environment
echo -e "\n${GREEN}[3/5] Setting up virtual environment...${NC}"
INSTALL_DIR="/opt/agent_os"
mkdir -p "$INSTALL_DIR"
chown -R agentos:agentos "$INSTALL_DIR"

# Copy files or pull from repository (assuming script runs in copy context)
cp -r . "$INSTALL_DIR/"
chown -R agentos:agentos "$INSTALL_DIR"

# Initialize virtualenv as agentos user
sudo -u agentos python3 -m venv "$INSTALL_DIR/venv"
sudo -u agentos "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
sudo -u agentos "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# 4. Handle Configuration files
echo -e "\n${GREEN}[4/5] Setting up environment variables...${NC}"
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        chown agentos:agentos "$INSTALL_DIR/.env"
        chmod 600 "$INSTALL_DIR/.env"
        echo -e "${RED}[!] WARNING: Created default .env from template.${NC}"
        echo -e "${RED}    Please edit $INSTALL_DIR/.env and set your keys/secrets before starting the service.${NC}"
    else
        touch "$INSTALL_DIR/.env"
        chown agentos:agentos "$INSTALL_DIR/.env"
        chmod 600 "$INSTALL_DIR/.env"
    fi
fi

# Setup systemd service file
cat <<EOF > /etc/systemd/system/agentos.service
[Unit]
Description=Agent OS HTTP API Server
After=network.target

[Service]
Type=simple
User=agentos
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python -u server.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=$INSTALL_DIR/.env

# Security Sandbox
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable systemd service
systemctl daemon-reload
systemctl enable agentos.service

# 5. Setup Firewall (UFW)
echo -e "\n${GREEN}[5/5] Configuring firewall...${NC}"
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP (Caddy/Nginx)
ufw allow 443/tcp    # HTTPS (Caddy/Nginx)
# ufw allow 8765/tcp # Uncomment if direct access to API is required without Nginx proxy
ufw --force enable

echo -e "\n${CYAN}====================================================${NC}"
echo -e "${GREEN}  ✓ Deployment foundations completed successfully!   ${NC}"
echo -e "${CYAN}  Next Steps:                                       ${NC}"
echo -e "${NC}   1. Run 'nano $INSTALL_DIR/.env' to add your API keys.${NC}"
echo -e "${NC}   2. Start the service: 'systemctl start agentos'   ${NC}"
echo -e "${NC}   3. Check status: 'systemctl status agentos'        ${NC}"
echo -e "${CYAN}====================================================${NC}"

# deploy_to_vps.ps1
# PowerShell script to deploy Agent OS from Windows to a Linux VPS (Ubuntu/Debian).
# Uses native Windows ssh/scp and zip/unzip to transfer files efficiently.

$ErrorActionPreference = "Stop"

# === 1. Configuration & Input ===
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Agent OS - Windows to VPS Deployer           " -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$vpsIp = Read-Host "Enter your VPS IP Address"
$vpsUser = Read-Host "Enter SSH User [default: root]"
if (-not $vpsUser) { $vpsUser = "root" }

$targetHost = "$vpsUser@$vpsIp"
$vpsPath = "/opt/agent_os"
$zipName = "agent_os_deploy.zip"
$localZipPath = Join-Path $PSScriptRoot $zipName

# === 2. Create ZIP Archive of Files ===
Write-Host "[1/4] Packaging deployment archive..." -ForegroundColor Green

# Remove any old zip if exists
if (Test-Path $localZipPath) { Remove-Item $localZipPath }

# Define files/directories to exclude
$excludePatterns = @(
    "*.zip",
    "*.log",
    "*.png",
    "*.jpg",
    "*.mp4",
    "dashboard_screenshot.png",
    "neural_3d_screenshot.png",
    ".git*",
    "__pycache__*",
    "node_modules*",
    "browser_session*",
    "pqc_keys*",
    "generated_skills*",
    "*.log*",
    "lead_behind_out.txt",
    "lead_behind_err.txt",
    "live_output.txt",
    "live_err.txt",
    "stress_out*",
    "stress_err*"
)

# Zip files in current directory recursively, applying exclusions
$files = Get-ChildItem -Path $PSScriptRoot -Recurse -File | Where-Object {
    $filePath = $_.FullName
    $matchExclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($_.Name -like $pattern -or $filePath -like "*\$pattern*" -or $filePath -like "*/$pattern*") {
            $matchExclude = $true
            break
        }
    }
    -not $matchExclude
}

# Create a temporary directory to build zip structure
$tempDir = Join-Path $env:TEMP "agent_os_build_temp"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
New-Item -ItemType Directory -Path $tempDir > $null

# Copy files keeping directory structure
foreach ($f in $files) {
    $relative = Resolve-Path -Path $f.FullName -Relative
    # Remove leading .\ or ./
    $relative = $relative -replace "^\.\\", "" -replace "^\./", ""
    
    $destFile = Join-Path $tempDir $relative
    $destDir = Split-Path $destFile -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir > $null }
    Copy-Item $f.FullName $destFile
}

# Compress the temporary folder
Compress-Archive -Path "$tempDir\*" -DestinationPath $localZipPath -Force
Remove-Item $tempDir -Recurse -Force

Write-Host "  [+] Archive created successfully: $zipName ($([int]((Get-Item $localZipPath).Length / 1KB)) KB)" -ForegroundColor Green

# === 3. Transfer Archive via SCP ===
Write-Host "`n[2/4] Uploading archive to VPS ($vpsIp)..." -ForegroundColor Green
try {
    scp.exe -o ConnectTimeout=10 $localZipPath "$($targetHost):/tmp/$zipName"
    Write-Host "  ✓ Upload completed successfully." -ForegroundColor Green
} catch {
    Write-Host "[!] Error uploading via SCP. Check your IP, username, and SSH keys." -ForegroundColor Red
    if (Test-Path $localZipPath) { Remove-Item $localZipPath }
    Exit
}

# Clean up local zip
Remove-Item $localZipPath

# === 4. Unpack and Run deploy.sh on VPS ===
Write-Host "`n[3/4] Running remote deployment script..." -ForegroundColor Green

$remoteScript = @'
set -e
echo "Checking and installing unzip if missing..."
if ! command -v unzip &> /dev/null; then
    apt-get update && apt-get install -y unzip
fi

echo "Creating deploy target /opt/agent_os..."
mkdir -p /opt/agent_os
unzip -o /tmp/agent_os_deploy.zip -d /opt/agent_os
rm /tmp/agent_os_deploy.zip

cd /opt/agent_os
chmod +x deploy.sh
echo "Launching deploy.sh..."
bash deploy.sh
'@

# Execute the remote command block over SSH
try {
    ssh.exe -o ConnectTimeout=10 $targetHost "bash -s" <<EOF
$remoteScript
EOF
    Write-Host "  ✓ Remote script completed." -ForegroundColor Green
} catch {
    Write-Host "[!] Error executing commands over SSH." -ForegroundColor Red
    Exit
}

# === 5. Setup Configuration Reminder ===
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Deployment successfully finished!            " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Next Steps on the VPS:" -ForegroundColor Yellow
Write-Host "  1. SSH into the server: 'ssh $vpsUser@$vpsIp'"
Write-Host "  2. Edit '.env' file: 'nano /opt/agent_os/.env'"
Write-Host "  3. Configure your API keys (OpenRouter, IBM Quantum, Local Bridge URL)."
Write-Host "  4. Start the service: 'systemctl start agentos'"
Write-Host "  5. Verify status: 'systemctl status agentos'"
Write-Host "================================================" -ForegroundColor Cyan

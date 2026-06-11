# start_agent_os.ps1
# Auto-starts Agent OS server + ngrok tunnel at Windows login.
# Placed in Startup folder -- no admin rights needed.

$PYTHON  = "C:\Users\navka\AppData\Local\Programs\Python\Python312\python.exe"
$SERVER  = "C:\Users\navka\navakanth001\agent_os\server.py"
$WORKDIR = "C:\Users\navka\navakanth001\agent_os"
$NGROK   = "C:\Users\navka\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
$LOGFILE = "$WORKDIR\startup.log"
$ENVFILE = "C:\Users\navka\navakanth001\.env"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts  $msg" | Out-File -FilePath $LOGFILE -Append -Encoding utf8
}

# Read API key from .env
$apiKey = ""
if (Test-Path $ENVFILE) {
    $line = Get-Content $ENVFILE | Where-Object { $_ -match "^AGENT_OS_API_KEY=" }
    if ($line) { $apiKey = $line -replace "^AGENT_OS_API_KEY=", "" }
}

Log "=== Agent OS startup ==="

# Kill any stale server on port 8765
Log "Clearing port 8765..."
try {
    $oldpids = (Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue).OwningProcess | Sort-Object -Unique
    foreach ($p in $oldpids) {
        if ($p -gt 0) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    }
} catch {}
Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Log "Cleared."

# Start Agent OS server (hidden window)
Log "Starting server.py..."
Start-Process -FilePath $PYTHON `
    -ArgumentList $SERVER `
    -WorkingDirectory $WORKDIR `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$WORKDIR\server_stdout.log" `
    -RedirectStandardError  "$WORKDIR\server_stderr.log"

Start-Sleep -Seconds 5

# Check server is up (include API key header)
try {
    $headers = @{ "X-API-Key" = $apiKey }
    $r = Invoke-WebRequest -Uri "http://localhost:8765/health" -Headers $headers -UseBasicParsing -TimeoutSec 5
    Log "Server OK (HTTP $($r.StatusCode))"
    Start-Process "http://localhost:8765/neural"
} catch {
    Log "Server health check failed"
}

# Start ngrok tunnel (hidden window)
Log "Starting ngrok..."
Start-Process -FilePath $NGROK `
    -ArgumentList "http 8765" `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$WORKDIR\ngrok_stdout.log" `
    -RedirectStandardError  "$WORKDIR\ngrok_stderr.log"

# Retry loop: wait up to 20 seconds for ngrok to come up
$publicUrl = ""
for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 2
    try {
        $tunnels   = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 3
        $publicUrl = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" }).public_url
        if ($publicUrl) { break }
    } catch {}
    Log "Waiting for ngrok... ($i/10)"
}

if ($publicUrl) {
    Log "ngrok tunnel: $publicUrl"
    $publicUrl | Out-File -FilePath "$WORKDIR\ngrok_url.txt" -Encoding utf8 -NoNewline
    Log "URL saved to ngrok_url.txt"
} else {
    Log "ngrok did not respond in time"
}

Log "=== Startup complete ==="

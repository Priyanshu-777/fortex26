# Start ZAP in Daemon Mode
# Usage: ./start_zap_daemon.ps1

# 1. Try to read API KEY from .env
$envFile = ".env"
$apiKey = "changeme"

if (Test-Path $envFile) {
    $lines = Get-Content $envFile
    foreach ($line in $lines) {
        if ($line -match "^ZAP_API_KEY=(.*)$") {
            $apiKey = $matches[1].Trim()
            break
        }
    }
}

Write-Host "[+] Found ZAP API Key: $apiKey"

# 2. Define ZAP Path (Modify this if installed elsewhere)
$zapPath = "C:\Program Files\OWASP\Zed Attack Proxy\zap.bat"

if (-not (Test-Path $zapPath)) {
    Write-Host "[-] ZAP not found at default location: $zapPath"
    Write-Host "    Trying to run 'zap.bat' from PATH..."
    $zapPath = "zap.bat"
}

# 3. Launch ZAP
Write-Host "[+] Launching ZAP Daemon on port 8080..."
Write-Host "    Command: $zapPath -daemon -port 8080 -config api.key=$apiKey"

try {
    Start-Process -FilePath $zapPath -ArgumentList "-daemon", "-port", "8080", "-config", "api.key=$apiKey"
    Write-Host "[+] ZAP started in background."
} catch {
    Write-Host "[-] Failed to start ZAP. Please check installation."
    Write-Error $_
}

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

# 2. Define ZAP Path (Search in common locations)
$commonPaths = @(
    "C:\Program Files\OWASP\Zed Attack Proxy\zap.bat",
    "C:\Program Files\ZAP\Zed Attack Proxy\zap.bat",
    "$env:LOCALAPPDATA\Programs\ZAP\Zed Attack Proxy\zap.bat"
)

$zapPath = ""
foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        $zapPath = $path
        break
    }
}

if ($zapPath -eq "") {
    Write-Host "[-] ZAP not found in common locations."
    Write-Host "    Trying to find 'zap.bat' in PATH..."
    $zapPath = Get-Command zap.bat -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    
    if (-not $zapPath) {
        Write-Host "[-] ZAP not found. Please install it or set ZAP_PROXY in .env to a remote instance."
        exit 1
    }
}

# 3. Launch ZAP
Write-Host "[+] Found ZAP at: $zapPath"
Write-Host "[+] Launching ZAP Daemon on port 8080..."

try {
    Start-Process -FilePath $zapPath -ArgumentList "-daemon", "-port", "8080", "-config", "api.key=$apiKey"
    Write-Host "[+] ZAP started in background."
} catch {
    Write-Host "[-] Failed to start ZAP."
    Write-Error $_
}

function Get-GiftMonitors {
    param (
        [string]$ApiUrl = "http://127.0.0.1:8000/list_monitors"
    )
    $response = Invoke-RestMethod -Uri $ApiUrl -Method Get
    Write-Host "Available VLC Monitors:`n"
    foreach ($monitor in $response) {
        Write-Host ("- {0}: {1}" -f $monitor.monitor_key, $monitor.device_name)
    }
}

# Usage:
Get-GiftMonitors
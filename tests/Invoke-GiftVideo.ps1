function Invoke-GiftVideo {
    param (
        [Parameter(Mandatory=$true)]
        [string]$VideoKey,

        [Parameter(Mandatory=$true)]
        [string]$TargetMonitor
    )

    $headers = @{ "Content-Type" = "application/json" }
    $uri = "http://127.0.0.1:8000/play_video?video_key=$VideoKey&target_monitor=$TargetMonitor"

    Invoke-RestMethod -Uri $uri -Method Post -Headers $headers
}

# Example usage:
Invoke-GiftVideo -VideoKey "test_video" -TargetMonitor "1"
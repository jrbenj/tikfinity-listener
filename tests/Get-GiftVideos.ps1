function Get-GiftVideo {
    param (
        [string]$ApiUrl = "http://127.0.0.1:8000/list_videos"
    )
    $response = Invoke-RestMethod -Uri $ApiUrl -Method Get
    Write-Host "Available Videos:`n"
    foreach ($video in $response) {
        Write-Host ("- {0}: {1}" -f $video.video_key, $video.file_path)
    }
}

# Usage:
Get-GiftVideo
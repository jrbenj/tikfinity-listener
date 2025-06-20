# TikFinity Video Player API

This service allows you to play video clips on a specific monitor using VLC, triggered by HTTP requests. It is designed for use with TikFinity or similar automation tools.

---

## 1. Running the Flask App

1. Open a terminal in the `src` directory.
2. Run the Flask app:
   ```powershell
   python app.py
   ```
3. The server will start on `http://127.0.0.1:8000` by default.

---

## 2. Testing with PowerShell Functions

### List Available Videos
Use the provided PowerShell function to list all available video keys and their file paths:

```powershell
# In PowerShell:
. ./tests/Get-GiftVideos.ps1
Get-GiftVideo
```

### List Available Monitors
Use the provided PowerShell function to list all available monitor IDs and their device names:

```powershell
# In PowerShell:
. ./tests/Get-GiftMonitors.ps1
Get-GiftMonitors
```

### Play a Video on a Monitor
Use the provided PowerShell function to trigger video playback:

```powershell
# In PowerShell:
. ./tests/Invoke-GiftVideo.ps1
Invoke-GiftVideo -VideoKey "lion_gift" -TargetMonitor "1"
```
- Replace `lion_gift` with any available video key.
- Replace `1` with the monitor number you want to use (see `MONITOR_DEVICE_NAMES` in `app.py` or use `Get-GiftMonitors`).

---

## 3. Updating `config.json` with Video File Paths and Monitor Devices

1. Open `config.json` in the `src` directory.
2. Add or update entries in the `VIDEO_LIBRARY` dictionary:

```json
{
    "VIDEO_LIBRARY": {
        "lion_gift": "C:\\Videos\\tikfinity_videos\\lion_gift.mp4",
        "follow_alert": "https://yourvideoserver.com/follow_alert.mp4",
        "rose_gift": "C:\\Videos\\tikfinity_videos\\rose_reveal.mp4",
        "default_alert": "C:\\Videos\\tikfinity_videos\\default_alert.mp4",
        "test_video": "C:\\Videos\\tikfinity_videos\\test_video.mp4"
    },
    "MONITOR_DEVICE_NAMES": {
        "1": "\\\\.\\DISPLAY1",
        "2": "\\\\.\\DISPLAY2",
        "3": "\\\\.\\DISPLAY3",
        "4": "\\\\.\\DISPLAY4"
    }
}
```
- The key (e.g., `lion_gift`) is what you use as `video_key` in the API or PowerShell function.
- The value is the full file path or a direct video URL.
- The `MONITOR_DEVICE_NAMES` dictionary maps monitor numbers to device names as recognized by VLC.

### How to Find Your Monitor Device Names

1. Open a terminal or PowerShell and run:
   ```powershell
   "C:\Program Files\VideoLAN\VLC\vlc.exe" --directx-device=help
   ```
2. In VLC, go to **Tools > Messages** (Ctrl+M), set verbosity to 2, and look for lines listing available DirectX display devices (e.g., `\\.\\DISPLAY1`).
3. Update the `MONITOR_DEVICE_NAMES` values in `config.json` to match the device names VLC reports for your monitors.

---

## 4. Playing a Video via HTTP Request

You can trigger video playback by sending a GET or POST request to:

```
http://127.0.0.1:8000/play_video?video_key=lion_gift&target_monitor=1
```
- Replace `lion_gift` with your desired video key.
- Replace `1` with your desired monitor number.

You can also use the `video_url` parameter to play a direct video URL:

```
http://127.0.0.1:8000/play_video?video_url=https://yourvideoserver.com/clip.mp4&target_monitor=1
```

---

## 5. Notes
- Ensure VLC is installed and the path in `app.py` is correct.
- The monitor numbers must match those in the `MONITOR_DEVICE_NAMES` dictionary in `app.py` or use the `/list_monitors` endpoint.
- Only one VLC instance will play per request, on the specified monitor.
- For best results, set VLC's video output to DirectX (DirectDraw) in VLC preferences.

---

For further customization, edit `app.py` as needed.

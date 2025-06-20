from flask import Flask, request, jsonify
import subprocess
import platform
import os
import json
import threading
import time # For potential future use, e.g., brief pause after playing

app = Flask(__name__)

# --- CONFIGURATION SECTION ---
# 1. VLC Executable Path: IMPORTANT - Adjust this path to your VLC installation
#    Typical paths:
#    Windows (64-bit): r"C:\Program Files\VideoLAN\VLC\vlc.exe"
#    Windows (32-bit): r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
#    macOS: "/Applications/VLC.app/Contents/MacOS/VLC"
#    Linux: "vlc" (if in your PATH)
VLC_EXE_PATH = "C:/Program Files/VideoLAN/VLC/vlc.exe"

# Load video library and monitor device names from a JSON configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("VIDEO_LIBRARY", {}), config.get("MONITOR_DEVICE_NAMES", {})
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return {}, {}

VIDEO_LIBRARY, MONITOR_DEVICE_NAMES = load_config(CONFIG_PATH)
# --- END CONFIGURATION SECTION ---


def play_video_vlc(video_source, monitor_id):
    if not os.path.exists(VLC_EXE_PATH):
        print(f"Error: VLC executable not found at {VLC_EXE_PATH}")
        return False
    if monitor_id not in MONITOR_DEVICE_NAMES:
        print(f"Error: Invalid monitor ID '{monitor_id}'. Valid IDs are: {', '.join(MONITOR_DEVICE_NAMES.keys())}")
        return False
    if not (video_source.startswith("http://") or video_source.startswith("https://") or video_source.startswith("file://") or os.path.exists(video_source)):
        print(f"Error: Invalid or non-existent video source '{video_source}'.")
        return False
    # Prepare the command to run VLC
    command = [
                VLC_EXE_PATH,
                video_source,
                "--fullscreen",
                "--play-and-exit",
                f"--directx-device={MONITOR_DEVICE_NAMES[monitor_id]}",
                "--no-video-title-show",
                "--no-embedded-video",
                "--video-on-top"
            ]
    try:
        # Use subprocess.Popen to run VLC without blocking the Flask app
        # detaching the process so it runs in the background.
        # On Windows, creationflags=subprocess.DETACHED_PROCESS and close_fds=True
        # helps ensure the VLC process doesn't stay tied to the Python script.
        if platform.system() == "Windows":
            subprocess.Popen(command, creationflags=subprocess.DETACHED_PROCESS, close_fds=True)
        else: # Linux/macOS
            subprocess.Popen(command)
        print(f"Initiated video playback: {video_source} on monitor {monitor_id}")
        return True
    except Exception as e:
        print(f"Error initiating video playback: {e}")
        return False

@app.route('/play_video', methods=['POST'])
def handle_play_video():
    try:
        # Get video_key from URL query parameter
        requested_video_key = request.args.get('video_key')  # e.g., /play_video?video_key=lion_gift
        direct_video_url = request.args.get('video_url')
        target_monitor = request.args.get('target_monitor', '1')  # Default to monitor 1 if not specified

        print(f"Received TikFinity webhook: video_key={requested_video_key}, video_url={direct_video_url}, target_monitor={target_monitor}")

        final_video_source = None

        if direct_video_url:
            # Validate the direct video URL
            if not (direct_video_url.startswith("http://") or direct_video_url.startswith("https://") or direct_video_url.startswith("file://")):
                return jsonify({"status": "error", "message": "Invalid video URL scheme. Only http, https, and file schemes are allowed."}), 400
            if not any(direct_video_url.lower().endswith(ext) for ext in [".mp4", ".avi", ".mkv", ".mov"]):
                return jsonify({"status": "error", "message": "Invalid video file format. Supported formats are: .mp4, .avi, .mkv, .mov."}), 400
            if ";" in direct_video_url or "&" in direct_video_url or "|" in direct_video_url:
                return jsonify({"status": "error", "message": "Invalid characters in video URL."}), 400
            
            # Normalize and validate the path
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
            normalized_path = os.path.normpath(os.path.abspath(direct_video_url.replace("file://", "")))
            if not normalized_path.startswith(base_path):
                return jsonify({"status": "error", "message": "Access to the specified path is not allowed."}), 400
            
            final_video_source = "file://" + normalized_path
            print(f"Using direct video URL from webhook: {direct_video_url}")
        elif requested_video_key:
            if requested_video_key in VIDEO_LIBRARY:
                final_video_source = VIDEO_LIBRARY[requested_video_key]
                print(f"Mapping '{requested_video_key}' to video: {final_video_source}")
            else:
                return jsonify({"status": "error", "message": f"Invalid video key: {requested_video_key}"}), 400

        if not final_video_source:
            return jsonify({"status": "error", "message": "No video source defined or default video not found"}), 400

        # Play video on the specified monitor (default is 1)
        success = play_video_vlc(final_video_source, target_monitor)

        if success:
            return jsonify({"status": "success", "message": f"Video playback initiated for {final_video_source} on monitor {target_monitor}"}), 200
        else:
            return jsonify({"status": "error", "message": f"Failed to initiate video playback on monitor {target_monitor}"}), 500

    except Exception as e:
        print(f"Error handling webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/list_videos', methods=['GET'])
def list_videos():
    """
    Returns a JSON list of available video_key and their file paths.
    """
    return jsonify([
        {"video_key": key, "file_path": path}
        for key, path in VIDEO_LIBRARY.items()
    ])

@app.route('/list_monitors', methods=['GET'])
def list_monitors():
    """
    Returns a JSON list of available monitor IDs and their device names.
    """
    return jsonify([
        {"monitor_id": monitor_id, "device_name": device_name}
        for monitor_id, device_name in MONITOR_DEVICE_NAMES.items()
    ])

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Listening on http://127.0.0.1:8000")
    print("Make sure this port is accessible or use ngrok for public access.")
    # host='0.0.0.0' makes the server accessible from other devices on your local network.
    # If you only need it accessible from your own machine, use '127.0.0.1'.
    app.run(host='127.0.0.1', port=8000)

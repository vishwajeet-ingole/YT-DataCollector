import pandas as pd
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

QUEUE = Path("output/approved_download_queue.xlsx")
TRACKER = Path("output/permission_tracker.xlsx")
VIDEO_DIR = Path("downloads/video")
STATUS_FILE = Path("output/approved_download_status.json")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

print("\nAPPROVED VIDEO DOWNLOAD PIPELINE")
print("--------------------------------")

if not QUEUE.exists() or not TRACKER.exists():
    raise SystemExit("ERROR: Permission files missing.")

if not shutil.which("yt-dlp"):
    raise SystemExit("ERROR: yt-dlp not installed.")

if not shutil.which("ffmpeg"):
    raise SystemExit("ERROR: FFmpeg not installed.")

queue = pd.read_excel(QUEUE)
tracker = pd.read_excel(TRACKER)

history = (
    json.loads(STATUS_FILE.read_text())
    if STATUS_FILE.exists() else {}
)

if queue.empty:
    print("No approved videos available.")
    print("Download blocked for safety.")
else:
    for _, row in queue.iterrows():
        video_id = str(row["Video ID"]).strip()
        url = str(row.get("Video URL", "")).strip()

        matches = tracker[
            tracker["Video ID"].astype(str).str.strip() == video_id
        ]

        approved = (
            len(matches) == 1
            and str(matches.iloc[0]["Permission Status"]).strip() == "Verified"
            and str(matches.iloc[0]["Download Allowed"]).strip() == "Yes"
            and str(matches.iloc[0]["AI Training Allowed"]).strip() == "Yes"
            and str(row["Approval Status"]).strip() == "APPROVED"
            and str(row["Owner Confirmed"]).lower() == "true"
            and str(row["Evidence Link"]).startswith("http")
            and url == f"https://www.youtube.com/watch?v={video_id}"
        )

        if not approved:
            print("BLOCKED:", video_id)
            continue

        if history.get(video_id, {}).get("status") == "SUCCESS":
            print("ALREADY DOWNLOADED:", video_id)
            continue

        print("\nDownloading:", video_id)

        command = [
            "yt-dlp",
            "--no-playlist",
            "--no-overwrites",
            "--merge-output-format", "mp4",
            "--write-info-json",
            "-f", "bestvideo+bestaudio/best",
            "-o", str(VIDEO_DIR / "%(id)s.%(ext)s"),
            url
        ]

        result = subprocess.run(command)

        files = list(VIDEO_DIR.glob(f"{video_id}.*"))
        video_files = [
            f for f in files
            if f.suffix.lower() in {
                ".mp4", ".mkv", ".webm", ".mov", ".avi"
            }
        ]

        if result.returncode == 0 and video_files:
            history[video_id] = {
                "status": "SUCCESS",
                "file": str(video_files[0]),
                "downloaded_at": datetime.now().isoformat()
            }
            print("SUCCESS:", video_files[0].name)
        else:
            history[video_id] = {
                "status": "FAILED",
                "downloaded_at": datetime.now().isoformat()
            }
            print("FAILED:", video_id)

        STATUS_FILE.write_text(json.dumps(history, indent=4))

print("\nDOWNLOAD PIPELINE COMPLETED")
print("Status file:", STATUS_FILE)
print("Video directory:", VIDEO_DIR)

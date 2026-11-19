import pandas as pd
import os
import json

INPUT = "output/approved_downloads.xlsx"
STATUS_FILE = "output/download_status.json"

os.makedirs("downloads/video", exist_ok=True)
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if os.path.exists(INPUT):
    df = pd.read_excel(INPUT)
else:
    df = pd.DataFrame()

if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE, "r") as f:
        status = json.load(f)
else:
    status = {}

print("DOWNLOAD MANAGER")
print("----------------")

if df.empty:
    print("No permission-approved videos available.")
else:
    for _, row in df.iterrows():
        video_id = row["Video ID"]

        status.setdefault(video_id, {
            "status": "pending",
            "video_file": None,
            "audio_file": None
        })

    print("Approved videos:", len(df))
    print("Tasks registered:", len(status))

with open(STATUS_FILE, "w") as f:
    json.dump(status, f, indent=4)

print("Status saved:", STATUS_FILE)

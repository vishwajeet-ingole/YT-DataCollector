import subprocess
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

VIDEO_DIR = Path("downloads/video")
AUDIO_DIR = Path("downloads/audio")
OUTPUT = Path("output/audio_extraction_report.xlsx")
STATUS_FILE = Path("output/audio_extraction_status.json")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

extensions = {".mp4", ".mkv", ".webm", ".mov", ".avi"}

videos = [
    f for f in VIDEO_DIR.iterdir()
    if f.is_file() and f.suffix.lower() in extensions
]

history = (
    json.loads(STATUS_FILE.read_text())
    if STATUS_FILE.exists() else {}
)

results = []

print("\nAUDIO EXTRACTION PIPELINE")
print("-------------------------")
print("Videos found:", len(videos))

for video in videos:

    audio = AUDIO_DIR / f"{video.stem}.wav"

    if audio.exists() and audio.stat().st_size > 44:
        print("SKIPPED:", video.name)

        results.append({
            "Video": video.name,
            "Audio": audio.name,
            "Status": "Already Exists"
        })
        continue

    command = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-i", str(video),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio)
    ]

    process = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    success = (
        process.returncode == 0
        and audio.exists()
        and audio.stat().st_size > 44
    )

    if success:
        print("SUCCESS:", audio.name)
        status = "SUCCESS"
        error = ""
    else:
        print("FAILED:", video.name)
        status = "FAILED"
        error = process.stderr[-500:]

        if audio.exists():
            audio.unlink()

    history[video.name] = {
        "status": status,
        "audio_file": str(audio) if success else None,
        "processed_at": datetime.now().isoformat(),
        "error": error
    }

    results.append({
        "Video": video.name,
        "Audio": audio.name,
        "Status": status,
        "Error": error
    })

STATUS_FILE.write_text(json.dumps(history, indent=4))

pd.DataFrame(results).to_excel(OUTPUT, index=False)

print("\nEXTRACTION SUMMARY")
print("------------------")
print("Total videos:", len(videos))
print("Successful:", sum(r["Status"] == "SUCCESS" for r in results))
print("Skipped:", sum(r["Status"] == "Already Exists" for r in results))
print("Failed:", sum(r["Status"] == "FAILED" for r in results))

print("\nReport:", OUTPUT)
print("Status:", STATUS_FILE)
print("\nSTEP 28 COMPLETED")

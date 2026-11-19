import subprocess
import json
import pandas as pd
from pathlib import Path

VIDEO_DIR = Path("downloads/video")
OUTPUT = Path("output/video_metadata_report.xlsx")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)

extensions = {".mp4", ".mkv", ".webm", ".mov", ".avi"}

videos = [
    f for f in VIDEO_DIR.iterdir()
    if f.is_file() and f.suffix.lower() in extensions
]

print("\nVIDEO METADATA EXTRACTION")
print("-------------------------")
print("Videos found:", len(videos))

results = []

for video in videos:

    command = [
        "ffprobe",
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        str(video)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        results.append({
            "File": video.name,
            "Status": "Corrupted",
            "Error": result.stderr[-300:]
        })
        continue

    try:
        data = json.loads(result.stdout)

        streams = data.get("streams", [])

        video_stream = next(
            (s for s in streams if s.get("codec_type") == "video"),
            {}
        )

        audio_stream = next(
            (s for s in streams if s.get("codec_type") == "audio"),
            {}
        )

        duration = float(
            data.get("format", {}).get("duration", 0)
        )

        fps = video_stream.get("avg_frame_rate", "0/1")

        try:
            numerator, denominator = map(int, fps.split("/"))
            fps_value = round(numerator / denominator, 2) if denominator else 0
        except (ValueError, ZeroDivisionError):
            fps_value = 0

        valid = bool(video_stream) and duration > 0

        results.append({
            "File": video.name,
            "Duration Seconds": round(duration, 2),
            "Duration Minutes": round(duration / 60, 2),
            "Width": video_stream.get("width"),
            "Height": video_stream.get("height"),
            "FPS": fps_value,
            "Video Codec": video_stream.get("codec_name"),
            "Audio Codec": audio_stream.get("codec_name"),
            "Audio Available": bool(audio_stream),
            "Size MB": round(video.stat().st_size / 1048576, 2),
            "Status": "Valid" if valid else "Invalid"
        })

    except (ValueError, KeyError, TypeError) as error:
        results.append({
            "File": video.name,
            "Status": "Metadata Error",
            "Error": str(error)
        })

df = pd.DataFrame(results)

df.to_excel(OUTPUT, index=False)

print("\nRESULTS")

if not df.empty:
    print(df.to_string(index=False))
    print("\nValid videos:",
          (df["Status"] == "Valid").sum())
    print("Invalid videos:",
          (df["Status"] != "Valid").sum())
else:
    print("No downloaded videos available.")

print("\nReport saved:", OUTPUT)
print("\nSTEP 27 COMPLETED")

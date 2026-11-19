import subprocess
import json
import pandas as pd
from pathlib import Path

AUDIO_DIR = Path("downloads/audio")
OUTPUT = Path("output/audio_quality_report.xlsx")

results = []

print("\nAUDIO QUALITY VALIDATION")
print("------------------------")

for audio in AUDIO_DIR.glob("*.wav"):

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "stream=sample_rate,channels,codec_name,bits_per_sample",
        "-show_entries",
        "format=duration",
        "-of", "json",
        str(audio)
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        results.append({
            "File": audio.name,
            "Status": "Corrupted"
        })
        continue

    data = json.loads(process.stdout)

    stream = next(
        (s for s in data.get("streams", [])
         if s.get("codec_type") == "audio"),
        {}
    )

    duration = float(data.get("format", {}).get("duration", 0))
    sample_rate = int(stream.get("sample_rate", 0))
    channels = stream.get("channels", 0)
    codec = stream.get("codec_name", "")
    bits = stream.get("bits_per_sample", 0)

    valid = (
        duration > 0
        and sample_rate == 16000
        and channels == 1
        and codec == "pcm_s16le"
        and audio.stat().st_size > 44
    )

    results.append({
        "File": audio.name,
        "Duration": round(duration, 2),
        "Sample Rate": sample_rate,
        "Channels": channels,
        "Codec": codec,
        "Bits Per Sample": bits,
        "Size MB": round(audio.stat().st_size / 1048576, 2),
        "Status": "Valid" if valid else "Invalid"
    })

df = pd.DataFrame(results)
df.to_excel(OUTPUT, index=False)

print(df.to_string(index=False) if not df.empty else "No WAV files found.")

print("\nValid:", (df["Status"] == "Valid").sum() if not df.empty else 0)
print("Invalid:", (df["Status"] == "Invalid").sum() if not df.empty else 0)

print("\nReport saved:", OUTPUT)
print("\nSTEP 28 COMPLETED")

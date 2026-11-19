from pathlib import Path
import pandas as pd
import json

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
VIDEO_DIR = ROOT / "downloads" / "video"
AUDIO_DIR = ROOT / "downloads" / "audio"

OUTPUT.mkdir(exist_ok=True)

def read_excel_safe(path):
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(path).fillna("")
    except Exception:
        return pd.DataFrame()

def clean(value):
    return str(value).strip() if value is not None else ""

def yes(value):
    return clean(value).lower() in ("yes", "true", "approved", "verified")

def find_video(video_id):
    for path in VIDEO_DIR.glob("*"):
        if path.is_file() and path.stem == video_id:
            return str(path.relative_to(ROOT))
    return ""

def find_audio(video_id):
    path = AUDIO_DIR / f"{video_id}.wav"
    return str(path.relative_to(ROOT)) if path.exists() else ""

tracker = read_excel_safe(OUTPUT / "permission_tracker.xlsx")
requests = read_excel_safe(OUTPUT / "permission_requests.xlsx")
metadata = read_excel_safe(OUTPUT / "video_metadata_report.xlsx")
audio_report = read_excel_safe(OUTPUT / "audio_quality_report.xlsx")

if tracker.empty:
    print("ERROR: permission_tracker.xlsx missing ya empty hai.")
    raise SystemExit(1)

# Permission request records ko Video ID se map karo
request_map = {}
if "Video ID" in requests.columns:
    for _, row in requests.iterrows():
        vid = clean(row.get("Video ID"))
        if vid:
            request_map[vid] = row.to_dict()

# Metadata/audio reports ko Video ID se map karo
def make_report_map(df):
    result = {}
    if df.empty:
        return result

    for _, row in df.iterrows():
        data = row.to_dict()
        vid = clean(data.get("Video ID"))

        if not vid:
            for key in ("File Name", "Filename", "File", "Video File"):
                filename = clean(data.get(key))
                if filename:
                    vid = Path(filename).stem
                    break

        if vid:
            result[vid] = data

    return result

metadata_map = make_report_map(metadata)
audio_map = make_report_map(audio_report)

records = []

for _, row in tracker.iterrows():
    item = row.to_dict()
    video_id = clean(item.get("Video ID"))

    request = request_map.get(video_id, {})
    video_path = find_video(video_id) if video_id else ""
    audio_path = find_audio(video_id) if video_id else ""

    permission_status = clean(item.get("Permission Status"))
    download_allowed = clean(item.get("Download Allowed"))
    ai_allowed = clean(item.get("AI Training Allowed"))

    owner_confirmed = clean(
        request.get("Rights Ownership Confirmed", "")
    )
    evidence_link = clean(request.get("Evidence Link", ""))

    permission_ready = (
        permission_status.lower() == "verified"
        and yes(download_allowed)
        and yes(ai_allowed)
        and yes(owner_confirmed)
        and evidence_link.startswith(("https://", "http://"))
    )

    item["Owner Confirmation"] = owner_confirmed or "Pending"
    item["Evidence Link"] = evidence_link
    item["Video File"] = video_path or "Not downloaded"
    item["Video Download Status"] = "Downloaded" if video_path else "Not downloaded"
    item["Audio File"] = audio_path or "Not extracted"
    item["Audio Extraction Status"] = "Extracted" if audio_path else "Not extracted"
    item["Dataset Readiness"] = (
        "READY - FILES AVAILABLE"
        if permission_ready and video_path and audio_path
        else "BLOCKED - PERMISSION PENDING"
        if not permission_ready
        else "WAITING - FILES NOT AVAILABLE"
    )

    # Video metadata fields
    for key, value in metadata_map.get(video_id, {}).items():
        if key not in ("Video ID",):
            item[f"Video Metadata - {key}"] = value

    # Audio quality fields
    for key, value in audio_map.get(video_id, {}).items():
        if key not in ("Video ID",):
            item[f"Audio Quality - {key}"] = value

    records.append(item)

master = pd.DataFrame(records)

# Summary
total = len(master)
summary = pd.DataFrame([
    ["Total video records", total],
    ["Permission verified", sum(
        clean(x).lower() == "verified"
        for x in master.get("Permission Status", [])
    )],
    ["Download approved", sum(
        yes(x) for x in master.get("Download Allowed", [])
    )],
    ["AI training approved", sum(
        yes(x) for x in master.get("AI Training Allowed", [])
    )],
    ["Videos downloaded", sum(
        x == "Downloaded" for x in master["Video Download Status"]
    )],
    ["Audio files extracted", sum(
        x == "Extracted" for x in master["Audio Extraction Status"]
    )],
    ["Dataset ready", sum(
        x == "READY - FILES AVAILABLE" for x in master["Dataset Readiness"]
    )],
], columns=["Metric", "Count"])

master.to_excel(OUTPUT / "master_dataset.xlsx", index=False)
master.to_csv(OUTPUT / "master_dataset.csv", index=False)

with pd.ExcelWriter(OUTPUT / "dataset_summary.xlsx") as writer:
    summary.to_excel(writer, sheet_name="Summary", index=False)
    master["Dataset Readiness"].value_counts().rename_axis(
        "Readiness Status"
    ).reset_index(name="Count").to_excel(
        writer, sheet_name="Readiness Breakdown", index=False
    )

print("\nMASTER DATASET CREATED")
print("----------------------")
print(f"Total records: {total}")
print(f"Videos downloaded: {sum(master['Video Download Status'] == 'Downloaded')}")
print(f"Audio extracted: {sum(master['Audio Extraction Status'] == 'Extracted')}")
print(f"Dataset ready: {sum(master['Dataset Readiness'] == 'READY - FILES AVAILABLE')}")

print("\nFiles created:")
print("output/master_dataset.xlsx")
print("output/master_dataset.csv")
print("output/dataset_summary.xlsx")

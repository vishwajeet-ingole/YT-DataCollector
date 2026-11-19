from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
MASTER_FILE = OUTPUT / "master_dataset.xlsx"

if not MASTER_FILE.exists():
    print("ERROR: master_dataset.xlsx nahi mila. Pehle Step 29 run karo.")
    raise SystemExit(1)

df = pd.read_excel(MASTER_FILE).fillna("")
issues = []

def add_issue(level, video_id, message):
    issues.append({
        "Level": level,
        "Video ID": video_id,
        "Issue": message
    })

required = [
    "Video ID",
    "Permission Status",
    "Download Allowed",
    "AI Training Allowed",
    "Video File",
    "Audio File",
    "Dataset Readiness"
]

for column in required:
    if column not in df.columns:
        add_issue("ERROR", "", f"Missing required column: {column}")

if "Video ID" in df.columns:
    ids = df["Video ID"].astype(str).str.strip()
    for vid in ids[ids.duplicated(keep=False)].unique():
        add_issue("ERROR", vid, "Duplicate Video ID")

    for index, vid in enumerate(ids):
        if not vid or vid.lower() == "nan":
            add_issue("ERROR", "", f"Row {index + 2}: Missing Video ID")

def is_yes(value):
    return str(value).strip().lower() in ("yes", "true", "approved", "verified")

for _, row in df.iterrows():
    vid = str(row.get("Video ID", "")).strip()

    for column in ("Video File", "Audio File"):
        value = str(row.get(column, "")).strip()

        if value and value not in ("Not downloaded", "Not extracted"):
            file_path = ROOT / value
            if not file_path.exists():
                add_issue("ERROR", vid, f"{column} path does not exist: {value}")

    if row.get("Dataset Readiness") == "READY - FILES AVAILABLE":
        permissions_ok = (
            str(row.get("Permission Status", "")).strip().lower() == "verified"
            and is_yes(row.get("Download Allowed", ""))
            and is_yes(row.get("AI Training Allowed", ""))
            and str(row.get("Owner Confirmation", "")).strip().lower()
                in ("yes", "true")
            and str(row.get("Evidence Link", "")).strip().startswith(
                ("https://", "http://")
            )
        )

        files_ok = (
            str(row.get("Video File", "")).strip() != "Not downloaded"
            and str(row.get("Audio File", "")).strip() != "Not extracted"
            and (ROOT / str(row.get("Video File", ""))).exists()
            and (ROOT / str(row.get("Audio File", ""))).exists()
        )

        if not permissions_ok:
            add_issue("ERROR", vid, "Marked READY but permission checks are incomplete")

        if not files_ok:
            add_issue("ERROR", vid, "Marked READY but video/audio file is missing")

issues_df = pd.DataFrame(
    issues,
    columns=["Level", "Video ID", "Issue"]
)

errors = len(issues_df[issues_df["Level"] == "ERROR"])
warnings = len(issues_df[issues_df["Level"] == "WARNING"])

summary = pd.DataFrame([
    ["Total records", len(df)],
    ["Duplicate IDs", int(df["Video ID"].astype(str).duplicated().sum())
     if "Video ID" in df.columns else 0],
    ["Downloaded videos", int((df["Video File"] != "Not downloaded").sum())
     if "Video File" in df.columns else 0],
    ["Extracted audio files", int((df["Audio File"] != "Not extracted").sum())
     if "Audio File" in df.columns else 0],
    ["Dataset ready records", int((df["Dataset Readiness"] == "READY - FILES AVAILABLE").sum())
     if "Dataset Readiness" in df.columns else 0],
    ["Errors", errors],
    ["Warnings", warnings],
    ["Final result", "PASS" if errors == 0 else "FAIL"]
], columns=["Check", "Result"])

with pd.ExcelWriter(OUTPUT / "final_quality_report.xlsx") as writer:
    summary.to_excel(writer, sheet_name="Summary", index=False)
    issues_df.to_excel(writer, sheet_name="Issues", index=False)

print("\nFINAL QUALITY CHECK")
print("-------------------")
print(summary.to_string(index=False))
print("\nReport saved: output/final_quality_report.xlsx")

if errors:
    print("\nPlease fix the ERROR entries before using the dataset.")
else:
    print("\nQuality checks passed. Permission approval is still required before data use.")

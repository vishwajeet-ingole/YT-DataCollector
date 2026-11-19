import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil

REQUEST_FILE = Path("output/permission_requests.xlsx")
TRACKER_FILE = Path("output/permission_tracker.xlsx")
QUEUE_FILE = Path("output/approved_download_queue.xlsx")
REPORT_FILE = Path("output/permission_verification_report.xlsx")

print("\nPERMISSION APPROVAL ENGINE")
print("--------------------------")

requests = pd.read_excel(REQUEST_FILE)
tracker = pd.read_excel(TRACKER_FILE)

def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()

def valid_evidence(value):
    value = clean(value)
    return value.startswith(("https://", "http://"))

# Identify duplicate IDs
duplicate_ids = set(
    requests.loc[
        requests["Video ID"].duplicated(keep=False), "Video ID"
    ].astype(str)
)

results = []

for _, row in requests.iterrows():
    video_id = str(row["Video ID"]).strip()

    checks = {
        "Owner Confirmed": clean(row["Rights Ownership Confirmed"]) == "yes",
        "Download Allowed": clean(row["Download Permission"]) == "yes",
        "AI Training Allowed": clean(row["AI Training Permission"]) == "yes",
        "Verification Complete": clean(row["Verification Status"]) == "verified",
        "Evidence Available": valid_evidence(row["Evidence Link"]),
        "Unique Video ID": video_id not in duplicate_ids
    }

    approved = all(checks.values())

    results.append({
        "Video ID": video_id,
        "Video Title": row["Video Title"],
        "Channel Name": row["Channel Name"],
        "License Type": row["License Type"],
        "Owner Confirmed": checks["Owner Confirmed"],
        "Download Allowed": checks["Download Allowed"],
        "AI Training Allowed": checks["AI Training Allowed"],
        "Verification Complete": checks["Verification Complete"],
        "Evidence Available": checks["Evidence Available"],
        "Unique Video ID": checks["Unique Video ID"],
        "Evidence Link": row["Evidence Link"],
        "Attribution Requirements": row["Attribution Requirements"],
        "Approval Status": "APPROVED" if approved else "PENDING"
    })

report = pd.DataFrame(results)

# Approved queue
queue = report[report["Approval Status"] == "APPROVED"].copy()

# Backup tracker before updating
if not report.empty:
    backup = TRACKER_FILE.with_name(
        f"permission_tracker_backup_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    )
    shutil.copy2(TRACKER_FILE, backup)

    approved_ids = set(queue["Video ID"])

    # Update only matching approved records
    tracker["Video ID"] = tracker["Video ID"].astype(str).str.strip()

    for _, approved_row in queue.iterrows():
        mask = tracker["Video ID"] == approved_row["Video ID"]

        tracker.loc[mask, "Permission Status"] = "Verified"
        tracker.loc[mask, "Download Allowed"] = "Yes"
        tracker.loc[mask, "AI Training Allowed"] = "Yes"
        tracker.loc[mask, "Notes"] = (
            "Owner confirmation and permission evidence verified. "
            "See permission_requests.xlsx"
        )

    tracker.to_excel(TRACKER_FILE, index=False)
else:
    backup = "No backup needed"

# Save reports
report.to_excel(REPORT_FILE, index=False)
queue.to_excel(QUEUE_FILE, index=False)

print("\nTOTAL VIDEOS:", len(report))
print("APPROVED:", len(queue))
print("PENDING:", len(report) - len(queue))

print("\nAPPROVED DOWNLOAD QUEUE:")
if queue.empty:
    print("No approved videos. Downloads remain blocked.")
else:
    print(queue[["Video ID", "Video Title"]].to_string(index=False))

print("\nBackup:", backup)
print("Report:", REPORT_FILE)
print("Queue:", QUEUE_FILE)
print("Tracker updated:", TRACKER_FILE)

print("\nSTEP 23 COMPLETED")

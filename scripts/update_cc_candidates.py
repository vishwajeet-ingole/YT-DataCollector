import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

AUDIT_FILE = Path("output/license_audit.xlsx")
TRACKER_FILE = Path("output/permission_tracker.xlsx")
OUTPUT_FILE = Path("output/creative_commons_candidates.xlsx")

print("\nCREATIVE COMMONS UPDATE")
print("-----------------------")

audit = pd.read_excel(AUDIT_FILE)
tracker = pd.read_excel(TRACKER_FILE)

# Fix pandas data types
for col in tracker.columns:
    if col in ["Notes", "License Type", "Permission Status",
               "AI Training Allowed", "Download Allowed"]:
        tracker[col] = tracker[col].astype("object")

# Detect license column
license_col = next(
    c for c in audit.columns
    if c.replace(" ", "").lower() == "youtubelicense"
)

audit["Video ID"] = audit["Video ID"].astype(str).str.strip()
tracker["Video ID"] = tracker["Video ID"].astype(str).str.strip()

# Find Creative Commons videos
cc = audit[
    audit[license_col].astype(str).str.strip().str.lower()
    == "creativecommon"
].copy()

cc_ids = set(cc["Video ID"])

# Backup
backup = TRACKER_FILE.with_name(
    f"permission_tracker_backup_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
)

shutil.copy2(TRACKER_FILE, backup)

# Match records
matches = tracker["Video ID"].isin(cc_ids)

# Update only matching records
tracker.loc[matches, "License Type"] = "Creative Commons"
tracker.loc[matches, "Permission Status"] = "Not Verified"
tracker.loc[matches, "AI Training Allowed"] = "Unknown"
tracker.loc[matches, "Download Allowed"] = "Unknown"

tracker.loc[matches, "Notes"] = (
    "YouTube API reports Creative Commons. "
    "Owner rights and AI training permission require verification."
)

# Save
tracker.to_excel(TRACKER_FILE, index=False)
cc.to_excel(OUTPUT_FILE, index=False)

print("Creative Commons found:", len(cc))
print("Tracker matches:", matches.sum())
print("Backup:", backup)
print("Updated:", TRACKER_FILE)
print("Candidates:", OUTPUT_FILE)

print("\nUPDATED RECORDS")

print(tracker.loc[matches, [
    "Video ID",
    "License Type",
    "Permission Status",
    "AI Training Allowed",
    "Download Allowed",
    "Notes"
]].to_string(index=False))

print("\nSTEP 17 COMPLETED")

import pandas as pd
from pathlib import Path

QUEUE = Path("output/approved_download_queue.xlsx")
TRACKER = Path("output/permission_tracker.xlsx")

queue = pd.read_excel(QUEUE)
tracker = pd.read_excel(TRACKER)

print("\nDOWNLOAD QUEUE SAFETY CHECK")
print("---------------------------")

approved = 0
blocked = 0

for _, row in queue.iterrows():
    video_id = str(row["Video ID"]).strip()

    match = tracker[
        tracker["Video ID"].astype(str).str.strip() == video_id
    ]

    safe = (
        len(match) == 1
        and str(match.iloc[0]["Permission Status"]).strip() == "Verified"
        and str(match.iloc[0]["Download Allowed"]).strip() == "Yes"
        and str(match.iloc[0]["AI Training Allowed"]).strip() == "Yes"
    )

    if safe:
        approved += 1
        print("READY:", video_id)
    else:
        blocked += 1
        print("BLOCKED:", video_id)

print("\nREADY:", approved)
print("BLOCKED:", blocked)

print("\nQueue safety check completed.")

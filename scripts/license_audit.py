
import os
import pandas as pd

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

INPUT = "output/selected_metadata.xlsx"
OUTPUT = "output/license_audit.xlsx"

df = pd.read_excel(INPUT)

video_ids = df["Video ID"].dropna().astype(str).unique().tolist()

results = []

print("Total videos to audit:", len(video_ids))

# YouTube API supports up to 50 IDs per request
for start in range(0, len(video_ids), 50):

    batch = video_ids[start:start + 50]

    response = youtube.videos().list(
        part="status",
        id=",".join(batch)
    ).execute()

    for video in response.get("items", []):

        status = video.get("status", {})

        results.append({
            "Video ID": video["id"],
            "YouTube License": status.get(
                "license", "Unknown"
            ),
            "Privacy Status": status.get(
                "privacyStatus", "Unknown"
            ),
            "Embeddable": status.get(
                "embeddable", False
            )
        })

audit_df = pd.DataFrame(results)

final_df = df.merge(
    audit_df,
    on="Video ID",
    how="left"
)

final_df.to_excel(OUTPUT, index=False)

print("\n====== LICENSE AUDIT ======")
print("Audited videos:", len(audit_df))
print("\nLicense distribution:")
print(audit_df["YouTube License"].value_counts())

print("\nSaved:", OUTPUT)
print("License audit completed!")

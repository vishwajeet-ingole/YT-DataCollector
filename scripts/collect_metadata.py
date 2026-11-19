
import os
import re
import time
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load API key
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YouTube API key missing!")

youtube = build("youtube", "v3", developerKey=API_KEY)

INPUT_FILE = Path("input/channels.xlsx")
OUTPUT_FILE = Path("output/video_metadata.xlsx")

# Safe test limits
MAX_CHANNELS = 3
MAX_VIDEOS_PER_CHANNEL = 10


def duration_to_seconds(duration):
    """Convert ISO 8601 duration into seconds."""
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duration
    )

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def get_channel_info(channel_id):

    response = youtube.channels().list(
        part="snippet,contentDetails",
        id=channel_id
    ).execute()

    items = response.get("items", [])

    if not items:
        return None

    channel = items[0]

    return {
        "channel_name": channel["snippet"]["title"],
        "uploads_playlist": channel["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]
    }


def get_video_ids(playlist_id):

    video_ids = []
    page_token = None

    while len(video_ids) < MAX_VIDEOS_PER_CHANNEL:

        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(
                50,
                MAX_VIDEOS_PER_CHANNEL - len(video_ids)
            ),
            pageToken=page_token
        ).execute()

        for item in response.get("items", []):
            video_ids.append(
                item["contentDetails"]["videoId"]
            )

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return video_ids


def main():

    df = pd.read_excel(INPUT_FILE)

    required = [
        "Category",
        "Channel URL",
        "Channel Name",
        "Channel ID"
    ]

    if not all(col in df.columns for col in required):
        raise ValueError("Excel columns are incorrect!")

    df = df.dropna(subset=["Channel ID"])

    channels = df.head(MAX_CHANNELS)

    results = []

    for _, row in channels.iterrows():

        channel_id = str(row["Channel ID"]).strip()

        print("\nProcessing:", row["Channel Name"])

        try:
            info = get_channel_info(channel_id)

            if not info:
                print("Channel not found:", channel_id)
                continue

            video_ids = get_video_ids(
                info["uploads_playlist"]
            )

            print("Videos found:", len(video_ids))

            # Fetch video details in batches of 50
            for start in range(0, len(video_ids), 50):

                batch = video_ids[start:start + 50]

                response = youtube.videos().list(
                    part="snippet,contentDetails",
                    id=",".join(batch)
                ).execute()

                for video in response.get("items", []):

                    snippet = video["snippet"]
                    details = video["contentDetails"]

                    results.append({
                        "Category": row["Category"],
                        "Channel Name": info["channel_name"],
                        "Channel ID": channel_id,
                        "Video Title": snippet["title"],
                        "Video ID": video["id"],
                        "Video URL": (
                            "https://www.youtube.com/watch?v="
                            + video["id"]
                        ),
                        "Duration": details["duration"],
                        "Duration Seconds": duration_to_seconds(
                            details["duration"]
                        ),
                        "Upload Date": snippet["publishedAt"]
                    })

            time.sleep(0.2)

        except Exception as error:
            print("Error:", error)

    output = pd.DataFrame(results)

    if not output.empty:
        output.to_excel(OUTPUT_FILE, index=False)
        total_seconds = output["Duration Seconds"].sum()

        print("\n========== COMPLETE ==========")
        print("Total Videos:", len(output))
        print("Total Hours:", round(total_seconds / 3600, 2))
        print("Saved:", OUTPUT_FILE)

    else:
        print("No video metadata collected.")


if __name__ == "__main__":
    main()

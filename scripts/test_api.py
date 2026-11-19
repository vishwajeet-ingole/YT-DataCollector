
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found in .env")

youtube = build("youtube", "v3", developerKey=API_KEY)

request = youtube.channels().list(
    part="snippet,statistics",
    id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
)

response = request.execute()

for channel in response.get("items", []):
    print("API CONNECTED SUCCESSFULLY!")
    print("Channel:", channel["snippet"]["title"])
    print("Subscribers:", channel["statistics"].get("subscriberCount"))

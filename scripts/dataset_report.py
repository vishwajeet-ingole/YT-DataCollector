
import pandas as pd

FILE = "output/video_metadata.xlsx"

df = pd.read_excel(FILE)

# Total statistics
total_videos = len(df)
total_seconds = df["Duration Seconds"].sum()
total_hours = total_seconds / 3600

print("\n====== DATASET REPORT ======")

print("Total Videos:", total_videos)
print("Total Duration (Seconds):", total_seconds)
print("Total Hours:", round(total_hours, 2))

print(
    "Average Video Duration (Minutes):",
    round(df["Duration Seconds"].mean() / 60, 2)
)

# Channel-wise report
print("\n====== CHANNEL-WISE REPORT ======")

channel_report = df.groupby("Channel Name").agg(
    Total_Videos=("Video ID", "count"),
    Total_Seconds=("Duration Seconds", "sum")
)

channel_report["Total_Hours"] = (
    channel_report["Total_Seconds"] / 3600
)

print(channel_report)

# Category-wise report
print("\n====== CATEGORY-WISE REPORT ======")

category_report = df.groupby("Category").agg(
    Total_Videos=("Video ID", "count"),
    Total_Seconds=("Duration Seconds", "sum")
)

category_report["Total_Hours"] = (
    category_report["Total_Seconds"] / 3600
)

print(category_report)

# Save reports
channel_report.to_excel(
    "output/channel_report.xlsx"
)

category_report.to_excel(
    "output/category_report.xlsx"
)

print("\nReports generated successfully!")

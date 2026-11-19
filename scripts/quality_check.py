
import pandas as pd
from pathlib import Path

input_file = Path("output/video_metadata.xlsx")
output_file = Path("output/clean_metadata.xlsx")

df = pd.read_excel(input_file)

print("\n====== DATA QUALITY CHECK ======")

original_count = len(df)

# 1. Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# 2. Check duplicate video IDs
duplicates = df.duplicated(subset=["Video ID"])

print("\nDuplicate videos:", duplicates.sum())

# 3. Remove duplicates
df = df.drop_duplicates(
    subset=["Video ID"],
    keep="first"
)

# 4. Remove rows with missing important data
df = df.dropna(
    subset=[
        "Video ID",
        "Video Title",
        "Video URL",
        "Duration Seconds"
    ]
)

# 5. Validate video duration
df = df[df["Duration Seconds"] > 0]

# 6. Validate YouTube video URL
df = df[
    df["Video URL"].astype(str).str.startswith(
        "https://www.youtube.com/watch?v="
    )
]

# Save cleaned dataset
df.to_excel(output_file, index=False)

print("\n====== QUALITY SUMMARY ======")
print("Original videos:", original_count)
print("Clean videos:", len(df))
print("Removed videos:", original_count - len(df))

print(
    "Total clean hours:",
    round(df["Duration Seconds"].sum() / 3600, 2)
)

print("\nSaved:", output_file)
print("Quality check completed!")


import pandas as pd

INPUT = "output/clean_metadata.xlsx"
OUTPUT = "output/selected_metadata.xlsx"

# Load dataset
df = pd.read_excel(INPUT)

print("Original videos:", len(df))

# Rule 1: Minimum duration 60 seconds
df = df[df["Duration Seconds"] >= 60]

# Rule 2: Valid video ID and URL
df = df.dropna(subset=["Video ID", "Video URL"])

# Rule 3: Remove duplicate IDs
df = df.drop_duplicates(subset=["Video ID"])

# Calculate selected hours
total_seconds = df["Duration Seconds"].sum()
total_hours = total_seconds / 3600

# Save selected dataset
df.to_excel(OUTPUT, index=False)

print("\n====== FILTERING REPORT ======")
print("Selected videos:", len(df))
print("Selected hours:", round(total_hours, 2))
print("Saved file:", OUTPUT)

print("\nFiltering completed!")

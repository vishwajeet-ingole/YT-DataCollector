
import pandas as pd
from pathlib import Path

# Excel file location
file_path = Path("input/channels.xlsx")

# Check whether file exists
if not file_path.exists():
    print("Excel file not found!")
    exit()

# Read Excel
df = pd.read_excel(file_path)

# Required columns
required_columns = [
    "Category",
    "Channel URL",
    "Channel Name",
    "Channel ID"
]

# Validate columns
missing = [col for col in required_columns if col not in df.columns]

if missing:
    print("Missing columns:", missing)
    exit()

# Clean data
df = df.dropna(subset=["Channel URL"])
df["Channel URL"] = df["Channel URL"].astype(str).str.strip()

# Display results
print("\n===== YOUTUBE CHANNEL DATA =====")
print("Total Channels:", len(df))

for index, row in df.iterrows():
    print(f"\nChannel {index + 1}")
    print("Category:", row["Category"])
    print("Name:", row["Channel Name"])
    print("URL:", row["Channel URL"])
    print("ID:", row["Channel ID"])

# Save cleaned dataset
output_path = Path("output/clean_channels.xlsx")
df.to_excel(output_path, index=False)

print("\nSuccessfully saved:", output_path)


import pandas as pd

# Load selected metadata
df = pd.read_excel(
    "output/selected_metadata.xlsx"
)

# Create permission tracker
tracker = df[
    ["Category", "Channel Name", "Channel ID",
     "Video Title", "Video ID", "Video URL"]
].copy()

# Add permission columns
tracker["Owner Contact"] = ""
tracker["Permission Status"] = "Not Verified"
tracker["License Type"] = "Unknown"
tracker["AI Training Allowed"] = "Unknown"
tracker["Download Allowed"] = "Unknown"
tracker["Attribution Required"] = "Unknown"
tracker["Evidence Link"] = ""
tracker["Notes"] = ""

# Save tracker
tracker.to_excel(
    "output/permission_tracker.xlsx",
    index=False
)

print("Permission tracker created!")
print("Total videos:", len(tracker))
print("File: output/permission_tracker.xlsx")

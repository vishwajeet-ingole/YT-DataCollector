import pandas as pd

license_file = "output/license_audit.xlsx"
permission_file = "output/permission_tracker.xlsx"

license_df = pd.read_excel(license_file)
permission_df = pd.read_excel(permission_file)

# Match using Video ID
df = license_df.merge(
    permission_df[["Video ID", "Permission Status",
                   "Download Allowed", "AI Training Allowed"]],
    on="Video ID",
    how="left"
)

# Strict permission filter
approved = df[
    (df["Permission Status"].astype(str).str.lower() == "verified") &
    (df["Download Allowed"].astype(str).str.lower() == "yes") &
    (df["AI Training Allowed"].astype(str).str.lower() == "yes")
].copy()

approved.to_excel(
    "output/approved_downloads.xlsx",
    index=False
)

print("Total videos:", len(df))
print("Approved videos:", len(approved))
print("Pending permission:", len(df) - len(approved))
print("Saved: output/approved_downloads.xlsx")

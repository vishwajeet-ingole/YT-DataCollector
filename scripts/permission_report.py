import pandas as pd
from pathlib import Path

FILE = Path("output/permission_tracker.xlsx")
OUTPUT = Path("output/permission_summary.xlsx")

df = pd.read_excel(FILE)

print("\nPERMISSION VERIFICATION REPORT")
print("-------------------------------")

print("Total videos:", len(df))

for col in [
    "Permission Status",
    "AI Training Allowed",
    "Download Allowed",
    "License Type"
]:
    print(f"\n{col} distribution:")
    print(df[col].value_counts(dropna=False).to_string())

pending = df[
    (df["Permission Status"].astype(str).str.lower() != "verified")
    | (df["AI Training Allowed"].astype(str).str.lower() != "yes")
    | (df["Download Allowed"].astype(str).str.lower() != "yes")
].copy()

pending.to_excel(OUTPUT, index=False)

print("\nPending verification:", len(pending))
print("Report saved:", OUTPUT)

print("\nPermission verification report completed.")

import pandas as pd
from pathlib import Path

SOURCE = Path("output/permission_tracker.xlsx")
OUTPUT = Path("output/permission_requests.xlsx")
CSV_OUTPUT = Path("output/permission_requests.csv")

df = pd.read_excel(SOURCE)

requests = pd.DataFrame({
    "Category": df["Category"],
    "Channel Name": df["Channel Name"],
    "Video Title": df["Video Title"],
    "Video ID": df["Video ID"],
    "Video URL": df["Video URL"],
    "License Type": df["License Type"],
    "Owner Contact": df["Owner Contact"],
    "Request Status": "Not Sent",
    "Rights Ownership Confirmed": "Pending",
    "Download Permission": "Pending",
    "AI Training Permission": "Pending",
    "Commercial Use Permission": "Pending",
    "Attribution Requirements": "Pending",
    "Evidence Link": "",
    "Verification Date": "",
    "Verification Status": "Not Verified"
})

requests.to_excel(OUTPUT, index=False)
requests.to_csv(CSV_OUTPUT, index=False)

print("\nPERMISSION REQUEST SYSTEM")
print("-------------------------")
print("Total requests prepared:", len(requests))
print("Creative Commons candidates:",
      (requests["License Type"] == "Creative Commons").sum())
print("Other license candidates:",
      (requests["License Type"] != "Creative Commons").sum())

print("\nFiles created:")
print(OUTPUT)
print(CSV_OUTPUT)

print("\nAll permission fields initialized as Pending.")
print("No permissions have been granted automatically.")

print("\nSTEP 20 COMPLETED")


import pandas as pd

# Read cleaned dataset
df = pd.read_excel("output/clean_metadata.xlsx")

print("\n====== CATEGORY ANALYSIS ======")

# Group data by category
report = df.groupby("Category").agg(
    Total_Videos=("Video ID", "count"),
    Total_Seconds=("Duration Seconds", "sum"),
    Average_Duration=("Duration Seconds", "mean")
).reset_index()

# Convert seconds into hours
report["Total_Hours"] = (
    report["Total_Seconds"] / 3600
).round(2)

report["Average_Duration"] = (
    report["Average_Duration"] / 60
).round(2)

# Sort by total hours
report = report.sort_values(
    by="Total_Hours",
    ascending=False
)

print(report.to_string(index=False))

# Save report
report.to_excel(
    "output/category_analysis.xlsx",
    index=False
)

print("\nTotal videos:", len(df))
print(
    "Total hours:",
    round(df["Duration Seconds"].sum() / 3600, 2)
)

print("\nCategory report saved successfully!")

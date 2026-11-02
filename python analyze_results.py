
import pandas as pd
import matplotlib.pyplot as plt
import os

# Dataset location
file_path = r"C:\dataset\Experimental_Dataset.csv"

# Result folder
result_folder = r"C:\dataset\results"
os.makedirs(result_folder, exist_ok=True)

# Load dataset
df = pd.read_csv(file_path)

print("Dataset Loaded Successfully")
print("Total Records:", len(df))

# Metrics
metrics = [
    "CPU_Usage",
    "RAM_Usage",
    "Disk_Read_MBps",
    "Disk_Write_MBps"
]

# Statistical Analysis
summary = df.groupby(
    ["Workload_Type", "Intensity"]
)[metrics].agg(
    ["mean", "min", "max", "std"]
)

# Save Excel file
summary.to_excel(
    os.path.join(
        result_folder,
        "Performance_Summary.xlsx"
    )
)

# Generate Graphs
for metric in metrics:

    pivot = df.pivot_table(
        index="Workload_Type",
        columns="Intensity",
        values=metric,
        aggfunc="mean"
    )

    pivot = pivot.reindex(
        ["Idle", "CPU", "Memory", "Disk", "Combined"]
    )

    pivot = pivot.reindex(
        columns=["Low", "Medium", "High"]
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6)
    )

    ax.set_title(
        metric + " Comparison Across Workloads"
    )

    ax.set_xlabel("Workload Type")
    ax.set_ylabel(metric)
    ax.legend(title="Intensity")

    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            result_folder,
            metric + "_Comparison.png"
        ),
        dpi=300
    )

    plt.close()

print("\nAnalysis Completed Successfully!")
print("Results saved at:", result_folder)

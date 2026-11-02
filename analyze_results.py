
import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET = os.path.join(
    BASE_DIR, "dataset", "Experimental_Dataset.csv"
)

RESULTS = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS, exist_ok=True)

# Load dataset
df = pd.read_csv(DATASET)

print("Dataset Loaded Successfully")
print("Total Records:", len(df))

# Statistical summary
metrics = [
    "CPU_Usage",
    "RAM_Usage",
    "Disk_Read_MBps",
    "Disk_Write_MBps"
]

summary = df.groupby(
    ["Workload_Type", "Intensity"]
)[metrics].agg(["mean", "min", "max", "std"])

summary.to_excel(
    os.path.join(RESULTS, "Performance_Summary.xlsx")
)

# Create comparison graphs
for metric in metrics:

    pivot = df.pivot_table(
        index="Workload_Type",
        columns="Intensity",
        values=metric,
        aggfunc="mean"
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6),
        width=0.8
    )

    ax.set_title(
        metric + " Comparison Across Workloads"
    )

    ax.set_xlabel("Workload Type")
    ax.set_ylabel(metric)
    ax.legend(title="Intensity")
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=0)
    plt.tight_layout()

    filename = metric + "_Comparison.png"

    plt.savefig(
        os.path.join(RESULTS, filename),
        dpi=300
    )

    plt.close()

print("\nAnalysis Completed!")
print("Graphs and Excel Summary saved in results folder.")

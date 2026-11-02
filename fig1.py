
import pandas as pd
import matplotlib.pyplot as plt
import os

folder = r"C:\dataset"

files = {
    "CPU": "CPU_Workload_Pilot.csv",
    "Memory": "Memory_Workload_Pilot.csv",
    "Disk": "Disk_Workload_Pilot.csv",
    "Combined": "Combined_Workload_Pilot.csv"
}

data = []

for workload, filename in files.items():
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        df = pd.read_csv(path)

        data.append({
            "Workload": workload,
            "Average_CPU": df["CPU_Usage"].mean(),
            "Average_RAM": df["RAM_Usage"].mean()
        })

summary = pd.DataFrame(data)
print(summary.round(2))

# CPU Comparison Graph
plt.figure(figsize=(8, 5))
plt.bar(summary["Workload"], summary["Average_CPU"])
plt.title("Average CPU Usage by Workload")
plt.xlabel("Workload")
plt.ylabel("CPU Usage (%)")
plt.tight_layout()
plt.savefig(os.path.join(folder, "CPU_Comparison.png"))
plt.show()

# RAM Comparison Graph
plt.figure(figsize=(8, 5))
plt.bar(summary["Workload"], summary["Average_RAM"])
plt.title("Average RAM Usage by Workload")
plt.xlabel("Workload")
plt.ylabel("RAM Usage (%)")
plt.tight_layout()
plt.savefig(os.path.join(folder, "RAM_Comparison.png"))
plt.show()

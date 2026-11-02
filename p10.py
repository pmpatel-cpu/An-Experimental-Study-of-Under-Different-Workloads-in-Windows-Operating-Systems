
import psutil
import pandas as pd
import time
from datetime import datetime

records = []

# Initialize CPU counter
psutil.cpu_percent(interval=None)

previous_disk = psutil.disk_io_counters()
previous_time = time.perf_counter()

print("Windows Performance Monitoring Started")

for i in range(60):

    time.sleep(1)

    current_disk = psutil.disk_io_counters()
    current_time = time.perf_counter()

    elapsed = current_time - previous_time

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()

    read_speed = (
        current_disk.read_bytes - previous_disk.read_bytes
    ) / elapsed / (1024 * 1024)

    write_speed = (
        current_disk.write_bytes - previous_disk.write_bytes
    ) / elapsed / (1024 * 1024)

    records.append({
        "Timestamp": datetime.now(),
        "CPU_Usage": cpu,
        "RAM_Usage": memory.percent,
        "RAM_Available_MB": memory.available / (1024 * 1024),
        "Disk_Read_MBps": read_speed,
        "Disk_Write_MBps": write_speed,
        "Process_Count": len(psutil.pids())
    })

    previous_disk = current_disk
    previous_time = current_time

df = pd.DataFrame(records)

df.to_csv(
    "Windows_Performance_Dataset.csv",
    index=False
)

print("Dataset Created Successfully!")
print(df.head())

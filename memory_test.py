
import psutil
import pandas as pd
import time
import os
from datetime import datetime

records = []
duration = 30

print("Memory Workload Experiment Started")

# Allocate 256 MB memory
memory_block = bytearray(256 * 1024 * 1024)

# Touch memory pages
for i in range(0, len(memory_block), 4096):
    memory_block[i] = 1

previous_disk = psutil.disk_io_counters()
previous_time = time.perf_counter()

try:
    for i in range(duration):

        time.sleep(1)

        current_disk = psutil.disk_io_counters()
        current_time = time.perf_counter()

        elapsed = current_time - previous_time

        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()

        read_speed = (
            current_disk.read_bytes -
            previous_disk.read_bytes
        ) / elapsed / (1024 * 1024)

        write_speed = (
            current_disk.write_bytes -
            previous_disk.write_bytes
        ) / elapsed / (1024 * 1024)

        records.append({
            "Timestamp": datetime.now(),
            "Workload_Type": "Memory",
            "Intensity": "Pilot",
            "Run_Number": 1,
            "CPU_Usage": cpu,
            "RAM_Usage": memory.percent,
            "RAM_Available_MB": memory.available / (1024 * 1024),
            "Disk_Read_MBps": read_speed,
            "Disk_Write_MBps": write_speed,
            "Process_Count": len(psutil.pids())
        })

        previous_disk = current_disk
        previous_time = current_time

finally:
    del memory_block

df = pd.DataFrame(records)

os.makedirs(r"C:\dataset", exist_ok=True)

df.to_csv( r"C:\dataset\Memory_Workload_Pilot.csv",index=False
)

print("Memory Workload Experiment Completed!")
print("Total Records:", len(df))
print(df.head())
print("Saved: C:\\dataset\\Memory_Workload_Pilot.csv")

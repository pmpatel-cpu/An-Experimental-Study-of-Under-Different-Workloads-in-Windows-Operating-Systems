
import psutil
import pandas as pd
import time
import os
import tempfile
from datetime import datetime

records = []
duration = 30
file_path = r"C:\dataset\disk_test_temp.bin"

os.makedirs(r"C:\dataset", exist_ok=True)

print("Disk I/O Workload Experiment Started")

# Create 8 MB test data
data = b"0123456789ABCDEF" * (512 * 1024)

previous_disk = psutil.disk_io_counters()
previous_time = time.perf_counter()

try:
    with open(file_path, "wb") as f:

        for i in range(duration):

            # Write test data
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

            # Read test data
            with open(file_path, "rb") as read_file:
                read_file.read()

            time.sleep(1)

            current_disk = psutil.disk_io_counters()
            current_time = time.perf_counter()

            elapsed = current_time - previous_time

            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=None)

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
                "Workload_Type": "Disk",
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
    if os.path.exists(file_path):
        os.remove(file_path)

df = pd.DataFrame(records)

df.to_csv(
    r"C:\dataset\Disk_Workload_Pilot.csv",
    index=False
)

print("Disk I/O Experiment Completed!")
print("Total Records:", len(df))
print(df.head())
print("Saved: C:\\dataset\\Disk_Workload_Pilot.csv")

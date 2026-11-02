
import psutil
import pandas as pd
import time
import multiprocessing
import os
from datetime import datetime

def cpu_workload(stop_event):
    number = 0
    while not stop_event.is_set():
        number = (number + 1) % 1000000

if __name__ == "__main__":

    records = []
    duration = 30

    stop_event = multiprocessing.Event()

    worker = multiprocessing.Process(
        target=cpu_workload,
        args=(stop_event,)
    )

    print("CPU Workload Experiment Started")

    previous_disk = psutil.disk_io_counters()
    previous_time = time.perf_counter()

    worker.start()

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
                "Workload_Type": "CPU",
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
        stop_event.set()
        worker.join(timeout=5)

        if worker.is_alive():
            worker.terminate()
            worker.join()

    df = pd.DataFrame(records)

    os.makedirs(r"C:\dataset", exist_ok=True)

    df.to_csv(
        r"C:\dataset\CPU_Workload_Pilot.csv",
        index=False
    )

    print("\nCPU Workload Experiment Completed!")
    print("Total Records:", len(df))
    print(df.head())
    print("Saved: C:\\dataset\\CPU_Workload_Pilot.csv")

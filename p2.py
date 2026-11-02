
import os
import time
import psutil
import pandas as pd
import multiprocessing as mp
from datetime import datetime

# ---------------------------------
# RESEARCH CONFIGURATION
# ---------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    DATASET_DIR, "Experimental_Dataset.csv"
)

DURATION = 20
REPETITIONS = 1
INTERVAL = 1

# Safe initial settings for 4 GB RAM
INTENSITY = {
    "Low": {
        "memory": 64,
        "disk": 8,
        "cpu_workers": 1
    },
    "Medium": {
        "memory": 128,
        "disk": 16,
        "cpu_workers": 1
    },
    "High": {
        "memory": 192,
        "disk": 24,
        "cpu_workers": 2
    }
}

records = []


# ---------------------------------
# CPU WORKLOAD
# ---------------------------------

def cpu_workload(duration):

    end_time = time.monotonic() + duration

    while time.monotonic() < end_time:
        x = 12345 * 67890
        x = x % 99991


# ---------------------------------
# MEMORY WORKLOAD
# ---------------------------------

def memory_workload(duration, memory_mb):

    memory = bytearray(memory_mb * 1024 * 1024)

    # Touch allocated memory pages
    for i in range(0, len(memory), 4096):
        memory[i] = 1

    time.sleep(duration)


# ---------------------------------
# DISK WORKLOAD
# ---------------------------------

def disk_workload(duration, disk_mb):

    temp_dir = os.path.join(BASE_DIR, "results")
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(
        temp_dir, f"disk_test_{os.getpid()}.bin"
    )

    data = b"0" * (1024 * 1024)
    end_time = time.monotonic() + duration

    try:
        while time.monotonic() < end_time:

            # Write test file
            with open(file_path, "wb") as f:
                for _ in range(disk_mb):
                    f.write(data)

                f.flush()
                os.fsync(f.fileno())

            # Read test file
            with open(file_path, "rb") as f:
                while f.read(1024 * 1024):
                    pass

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# ---------------------------------
# RUN ONE EXPERIMENT
# ---------------------------------

def run_experiment(workload, intensity, run_number):

    config = INTENSITY.get(intensity, {})

    processes = []

    cpu_workers = config.get("cpu_workers", 1)
    memory_mb = config.get("memory", 0)
    disk_mb = config.get("disk", 0)

    if workload in ["CPU", "Combined"]:

        if workload == "CPU":
            for _ in range(cpu_workers):
                p = mp.Process(
                    target=cpu_workload,
                    args=(DURATION,)
                )
                processes.append(p)

        else:
            p = mp.Process(
                target=cpu_workload,
                args=(DURATION,)
            )
            processes.append(p)

    if workload in ["Memory", "Combined"]:

        p = mp.Process(
            target=memory_workload,
            args=(DURATION, memory_mb)
        )
        processes.append(p)

    if workload in ["Disk", "Combined"]:

        p = mp.Process(
            target=disk_workload,
            args=(DURATION, disk_mb)
        )
        processes.append(p)

    # Start workloads
    for p in processes:
        p.start()

    worker_processes = [
        psutil.Process(p.pid) for p in processes
    ]

    # Initialize process CPU counters
    for p in worker_processes:
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    previous_disk = psutil.disk_io_counters()
    previous_time = time.perf_counter()

    print(
        f"\nRunning: {workload} | "
        f"{intensity} | Run {run_number}"
    )

    # Monitor for fixed duration
    for sample in range(DURATION):

        time.sleep(INTERVAL)

        now = time.perf_counter()
        elapsed = now - previous_time

        current_disk = psutil.disk_io_counters()
        memory = psutil.virtual_memory()

        disk_read = (
            current_disk.read_bytes - previous_disk.read_bytes
        ) / elapsed / (1024 * 1024)

        disk_write = (
            current_disk.write_bytes - previous_disk.write_bytes
        ) / elapsed / (1024 * 1024)

        worker_cpu = 0
        worker_read = 0
        worker_write = 0

        for proc in worker_processes:
            try:
                worker_cpu += proc.cpu_percent(interval=None)

                io = proc.io_counters()
                worker_read += io.read_bytes
                worker_write += io.write_bytes

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

        records.append({

            "Experiment_ID": workload + "_" + intensity,
            "Timestamp": datetime.now(),
            "Workload_Type": workload,
            "Intensity": intensity,
            "Run_Number": run_number,
            "Sample": sample + 1,

            "CPU_Usage": psutil.cpu_percent(interval=None),
            "Workload_CPU_Usage": worker_cpu,

            "RAM_Usage": memory.percent,
            "RAM_Used_MB": memory.used / (1024 * 1024),
            "RAM_Available_MB": memory.available / (1024 * 1024),

            "Disk_Read_MBps": disk_read,
            "Disk_Write_MBps": disk_write,

            "Process_Count": len(psutil.pids()),

            "Workload_Disk_Read_Bytes": worker_read,
            "Workload_Disk_Write_Bytes": worker_write

        })

        previous_disk = current_disk
        previous_time = now

    # Wait for all workload processes
    for p in processes:
        p.join(timeout=10)

        if p.is_alive():
            p.terminate()
            p.join()

    print("Experiment Completed!")


# ---------------------------------
# MAIN EXPERIMENT
# ---------------------------------

if __name__ == "__main__":

    mp.freeze_support()

    # Baseline
    for run in range(1, REPETITIONS + 1):
        run_experiment("Idle", "Low", run)

    workloads = ["CPU", "Memory", "Disk", "Combined"]

    for workload in workloads:

        for intensity in ["Low", "Medium", "High"]:

            for run in range(1, REPETITIONS + 1):

                run_experiment(
                    workload,
                    intensity,
                    run
                )

                # Allow system to cool down
                time.sleep(5)

    # Save dataset
    df = pd.DataFrame(records)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n================================")
    print("ALL EXPERIMENTS COMPLETED")
    print("================================")

    print("Total Records:", len(df))
    print("Dataset Location:", OUTPUT_FILE)

    print(df.head())


import os
import time
import gc
import psutil
import multiprocessing
import pandas as pd
from datetime import datetime

# --------------------------------
# Configuration
# --------------------------------
DURATION = 30
MEMORY_MB = 128
SAMPLE_INTERVAL = 1

OUTPUT_FILE = r"C:\dataset\Combined_Workload_Pilot.csv"
TEMP_FILE = r"C:\dataset\combined_temp.bin"

# --------------------------------
# CPU Workload
# --------------------------------
def cpu_workload(stop_event):
    while not stop_event.is_set():
        value = 0
        for i in range(100000):
            value += i * i

# --------------------------------
# Main Test
# --------------------------------
def main():

    print("Combined Workload Test Started")
    print("CPU + Memory + Disk I/O")
    print("Duration:", DURATION, "seconds")

    stop_event = multiprocessing.Event()
    cpu_process = multiprocessing.Process(
        target=cpu_workload,
        args=(stop_event,)
    )

    records = []
    memory_block = None

    try:
        # Allocate 128 MB RAM
        memory_block = bytearray(MEMORY_MB * 1024 * 1024)

        # Touch memory pages
        for i in range(0, len(memory_block), 4096):
            memory_block[i] = 1

        # Start CPU process
        cpu_process.start()

        # Disk test data: 1 MB
        disk_data = b"0123456789ABCDEF" * (64 * 1024)

        # Start monitoring
        psutil.cpu_percent(interval=None)

        start_time = time.time()

        while time.time() - start_time < DURATION:

            if psutil.virtual_memory().available < 1024 * 1024 * 1024:
                print("WARNING: Available RAM below 1 GB.")
                print("Stopping test for safety.")
                break

            # Disk write and read
            with open(TEMP_FILE, "wb") as f:
                f.write(disk_data)
                f.flush()
                os.fsync(f.fileno())

            with open(TEMP_FILE, "rb") as f:
                content = f.read()

            # System-wide disk I/O counters
            disk_before = psutil.disk_io_counters()

            time.sleep(SAMPLE_INTERVAL)

            disk_after = psutil.disk_io_counters()

            read_mbps = (
                (disk_after.read_bytes - disk_before.read_bytes)
                / (1024 * 1024)
            )

            write_mbps = (
                (disk_after.write_bytes - disk_before.write_bytes)
                / (1024 * 1024)
            )

            # Resource measurements
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()

            record = {
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Workload_Type": "Combined",
                "Intensity": "Pilot",
                "Run_Number": 1,
                "CPU_Usage": cpu,
                "RAM_Usage": ram.percent,
                "RAM_Available_MB": ram.available / (1024 * 1024),
                "Disk_Read_MBps": read_mbps,
                "Disk_Write_MBps": write_mbps,
                "Process_Count": len(psutil.pids())
            }

            records.append(record)

            print(
                f"Record {len(records)} | "
                f"CPU: {cpu}% | "
                f"RAM: {ram.percent}% | "
                f"Available RAM: {record['RAM_Available_MB']:.0f} MB"
            )

        # Save results
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_FILE, index=False)

        print("\nDataset saved:", OUTPUT_FILE)
        print("Total records:", len(df))

    finally:
        # Stop CPU process
        stop_event.set()

        if cpu_process.is_alive():
            cpu_process.join(timeout=3)

        if cpu_process.is_alive():
            cpu_process.terminate()
            cpu_process.join()

        # Release memory
        del memory_block
        gc.collect()

        # Delete temporary file safely
        try:
            if os.path.exists(TEMP_FILE):
                os.remove(TEMP_FILE)
        except PermissionError:
            print("Temporary file could not be deleted.")
            print("Delete it manually after closing the program.")

        print("Combined Workload Test Finished.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

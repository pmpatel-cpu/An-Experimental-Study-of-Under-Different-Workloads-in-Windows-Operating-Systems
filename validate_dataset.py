
import pandas as pd
import os

file_path = r"C:\dataset\Experimental_Dataset.csv"

df = pd.read_csv(file_path)

print("\n===== DATASET VALIDATION =====")

print("\n1. Dataset Shape:")
print(df.shape)

print("\n2. Column Names:")
print(df.columns.tolist())

print("\n3. Missing Values:")
print(df.isnull().sum())

print("\n4. Duplicate Records:")
print(df.duplicated().sum())

print("\n5. Workload Distribution:")
print(df["Workload_Type"].value_counts())

print("\n6. Experiment Distribution:")
print(
    df.groupby(
        ["Workload_Type", "Intensity"]
    ).size()
)

print("\n7. Statistical Summary:")
print(
    df[
        ["CPU_Usage", "RAM_Usage",
         "Disk_Read_MBps", "Disk_Write_MBps"]
    ].describe()
)

print("\n8. Dataset Validation Completed!")

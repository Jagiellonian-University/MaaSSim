import csv
import os

folders = []

# Find all directories that contain the specified files
for root, dirs, files in os.walk("."):
    if all(file in files for file in ['veh1.csv', 'veh2.csv', 'veh3.csv']):
        folders.append(root)

print(folders)
# Initialize a dictionary to hold the column sums
sums = {"veh1": 0, "veh2": 0, "veh3": 0}
# Read the data from each file and compute the column sums using the "sum" row
for folder in folders:
    with open(os.path.join(folder, "veh1.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        # print(data)
        sums["veh1"] += data["PAX_KM"]
    with open(os.path.join(folder, "veh2.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        sums["veh2"] += data["PAX_KM"]
    with open(os.path.join(folder, "veh3.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        sums["veh3"] += data["PAX_KM"]


# Create a new CSV file with the column sums and "REVENUE" as the row name
with open("PAX_KM.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["","veh1", "veh2", "veh3"])
    writer.writerow(["PAX_KM",sums["veh1"], sums["veh2"], sums["veh3"]])

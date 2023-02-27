import csv
import os

folders = []

# Find all directories that contain the specified files
for root, dirs, files in os.walk("."):
    if all(file in files for file in ['pax1.csv', 'pax2.csv', 'pax3.csv']):
        folders.append(root)

print(folders)
# Initialize a dictionary to hold the column sums
sums = {"pax1": 0, "pax2": 0, "pax3": 0}
# Read the data from each file and compute the column sums using the "sum" row
for folder in folders:
    with open(os.path.join(folder, "pax1.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        # print(data)
        sums["pax1"] += data["REQUESTS_RIDE"]
    with open(os.path.join(folder, "pax2.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        sums["pax2"] += data["REQUESTS_RIDE"]
    with open(os.path.join(folder, "pax3.csv")) as f:
        reader = csv.reader(f)
        header = next(reader)  # read header
        data = {col: 0.0 for col in header}  # initialize data dict
        for row in reader:
            if row[0] == "sum":
                for i in range(1, len(row)):
                    data[header[i]] += float(row[i])
        sums["pax3"] += data["REQUESTS_RIDE"]


# Create a new CSV file with the column sums and "REVENUE" as the row name
with open("REQUESTS_RIDE.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["","Profit Maximization", "Pooled Ride", "Private Ride"])
    writer.writerow(["REQUESTS_RIDE",sums["pax1"], sums["pax2"], sums["pax3"]])

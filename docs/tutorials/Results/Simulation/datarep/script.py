import re
import pandas as pd
import os
import glob

column = "PROFIT"
CSV_Startwith = "veh"
NumberOfCSV = 3
columnValues = [0] * NumberOfCSV

subfolders = glob.glob("nP=500; nV=50; Rep=*")

# Loop through each subfolder
for subfolder in subfolders:
    # Read each CSV file into a DataFrame and append it to the list
    for i in range(NumberOfCSV):
        csv_file = subfolder + "/" + CSV_Startwith + str(i + 1) + ".csv"
        df = pd.read_csv(csv_file)
        columnValues[i] += df[column]

# Calculate the average for each column value
newDf = {}
for i in range(len(columnValues)):
    col = CSV_Startwith + str(i + 1)
    newDf[col] = columnValues[i] / len(subfolders)

# Create a DataFrame with the calculated column values
df = pd.DataFrame(newDf)
df.index = ["sum", "mean", "std"]
df.to_csv(column+".csv")
print(df)

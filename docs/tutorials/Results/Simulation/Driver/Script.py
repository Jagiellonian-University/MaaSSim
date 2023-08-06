# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 20:00:01 2023

@author: KAMRAN KHAN
"""

import pandas as pd

def calculate_average_profit(csv_files):
    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    

    average_profit = combined_df['PROFIT'].mean()
    
    return average_profit

def main():

    csv_files = [
        r'D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/nP=100; nV=10; Rep=1/veh2.csv',
        r'D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/nP=100; nV=10; Rep= 2/veh2.csv',
        r'D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/nP=100; nV=10; Rep= 3/veh2.csv',
        r'D:/Development/GitHub-ProjectV2.0/MaaSSim/docs/tutorials/Results/Simulation/Driver/nP=100; nV=10; Rep= 4/veh2.csv'
    ]

    avg_profit = calculate_average_profit(csv_files)
    
    try:

        existing_data = pd.read_csv('average_profit.csv')
        num_existing_columns = len(existing_data.columns)
        avg_profit_df = pd.DataFrame({f'Average Profit {num_existing_columns}': [avg_profit]})
        combined_data = pd.concat([existing_data, avg_profit_df], axis=1)
        combined_data.to_csv('average_profit.csv', index=False)
    except FileNotFoundError:
        avg_profit_df = pd.DataFrame({'Average Profit 0': [avg_profit]})
        avg_profit_df.to_csv('average_profit.csv', index=False)
    
    print("Average profit calculated and stored in 'average_profit.csv'.")

if __name__ == "__main__":
    main()

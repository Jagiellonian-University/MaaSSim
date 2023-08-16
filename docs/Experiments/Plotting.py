# -*- coding: utf-8 -*-
"""
Created on Wed Aug 9 12:54:58 2023
@author: Usman Akhtar
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('D:\Development\GitHub-ProjectV2.0\MaaSSim\docs\Experiments\data.csv')

data.fillna(0, inplace=True)

time_values = data['Time']
service_rate1_values = data['service rate1']
service_rate2_values = data['service rate2']
service_rate3_values = data['service rate3']

# Combine data for Seaborn
seaborn_data = pd.melt(data, id_vars='Time', value_vars=['service rate1', 'service rate2', 'service rate3'],
                       value_name='Service Rate %', var_name='Service')

sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))

# Define a custom palette with colors for the bars
custom_palette = ['b', 'g', 'r']
sns.set_palette(custom_palette)

# Create a bar plot using Seaborn with hatching patterns
ax = sns.barplot(data=seaborn_data, x='Time', y='Service Rate %', hue='Service', alpha=0.8)

# Apply hatching patterns to each bar
hatches = ['//', '\\\\', 'x']
for i, patch in enumerate(ax.patches):
    hatch = hatches[i % len(hatches)]
    patch.set_hatch(hatch)

# Adjust other formatting
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Service Rate %', fontsize=12)
ax.set_title('Service Rates of Different KPIs', fontsize=14)
ax.tick_params(axis='both', which='major', labelsize=10)
ax.legend(title='Service', title_fontsize=10, fontsize=10)

plt.xticks(rotation=0)
plt.tight_layout()

plt.show()

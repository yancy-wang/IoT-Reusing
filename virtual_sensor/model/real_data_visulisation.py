import pandas as pd
import matplotlib.pyplot as plt

# File path
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/Normal_2024-11-18_19-44-12.csv'

# Load the dataset
data = pd.read_csv(file_path)

# Exclude specific columns including 'time', 'co_ppm', 'no2_ppb', and 'ozone_ppm'
excluded_columns = ['time', 'co_ppm', 'no2_ppb', 'ozone_ppm']
filtered_data = data.drop(columns=[col for col in excluded_columns if col in data.columns])

# Keep only rows where all y-values are between 0 and 500
filtered_data = filtered_data[(filtered_data >= 0).all(axis=1) & (filtered_data <= 500).all(axis=1)]

# Plot the filtered variables
plt.figure(figsize=(12, 8))
for column in filtered_data.columns:
    plt.plot(filtered_data.index, filtered_data[column], label=column)

# Add title, labels, and legend
plt.title('Filtered Sensor Data (Values between 0 and 500)', fontsize=16)
plt.xlabel('Index', fontsize=12)
plt.ylabel('Values', fontsize=12)
plt.legend(title='Variables', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()

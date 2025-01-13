import pandas as pd

# Load the CSV file
csv_file_path = '/Users/wangyangyang/Desktop/transmission_times_1000.csv'  # Change this to the path of your file
df = pd.read_csv(csv_file_path)

# Calculate statistics for Bluetooth Transmission Time
bluetooth_max = df['Bluetooth Transmission Time (seconds)'].max()
bluetooth_min = df['Bluetooth Transmission Time (seconds)'].min()
bluetooth_avg = df['Bluetooth Transmission Time (seconds)'].mean()

# Calculate statistics for SSH Transmission Time
ssh_max = df['SSH Transmission Time (seconds)'].max()
ssh_min = df['SSH Transmission Time (seconds)'].min()
ssh_avg = df['SSH Transmission Time (seconds)'].mean()

# Create a summary row with the calculated statistics
summary_row = {
    'Attempt': 'Summary',
    'Bluetooth Transmission Time (seconds)': f'Max: {bluetooth_max}, Min: {bluetooth_min}, Avg: {bluetooth_avg}',
    'SSH Transmission Time (seconds)': f'Max: {ssh_max}, Min: {ssh_min}, Avg: {ssh_avg}'
}

# Append the summary row to the DataFrame
df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)

# Save the updated CSV file
updated_csv_path = '/Users/wangyangyang/Desktop/transmission_times_1000_updated.csv'  # The updated file path
df.to_csv(updated_csv_path, index=False)

print(f"Updated CSV file saved as {updated_csv_path}")

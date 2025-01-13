import pandas as pd

# Load the data
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/tbs2_merged.csv'
data = pd.read_csv(file_path)

# Extract eCO2 and TVOC
input_data = data[['eCO2', 'TVOC']].dropna()

# Save input values for Xiao
input_data.to_csv('/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/eCO2_TVOC_input.txt', index=False, header=False)

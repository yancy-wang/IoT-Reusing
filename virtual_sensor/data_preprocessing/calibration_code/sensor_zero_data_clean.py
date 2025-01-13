import os
import pandas as pd

def remove_initial_zeros(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    
    non_zero_index = max(
        df[df['Temperature(°C)'] != 0].index[0],
        df[df['Ambient light(x)'] != 0].index[0],
        df[df['Pressure(mbar)'] != 0].index[0],
        df[df['humidity(%)'] != 0].index[0],
        df[df['sound level(dB)'] != 0].index[0],
        df[df['CO2(ppm)'] != 0].index[0]
    )
    
    df_cleaned = df[non_zero_index:]
    
    df_cleaned.to_csv(output_csv, index=False)

def process_all_csv_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            input_csv = os.path.join(input_folder, filename)
            output_csv = os.path.join(output_folder, filename)
            
            try:
                remove_initial_zeros(input_csv, output_csv)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")


input_folder = '/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_12_v4'
output_folder = '/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_12_v4_without0'


process_all_csv_files(input_folder, output_folder)

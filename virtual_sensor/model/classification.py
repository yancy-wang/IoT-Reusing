import os
import pandas as pd

# Load the datasets
mega_merged_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/mega_merged.csv'
tbs2_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/tbs2_merged.csv'

mega_merged = pd.read_csv(mega_merged_path, parse_dates=['time'])
tbs2 = pd.read_csv(tbs2_path, parse_dates=['time'])

# Target columns to split into levels
target_columns = ["co_ppm", "no2_ppb", "nc_0p5_npcm3", "nc_1p0_npcm3",
                  "nc_2p5_npcm3", "nc_4p0_npcm3", "nc_10p0_npcm3", "Mc_1p0_ugpm3",
                  "Mc_2p5_ugpm3", "Mc_4p0_ugpm3", "Mc_10p0_ugpm3"]

output_dir = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3'  # Directory to save files

# Generate files for each target column
for target in target_columns:
    # Ensure target-specific directory exists
    target_dir = f"{output_dir}/{target}"
    os.makedirs(target_dir, exist_ok=True)

    # Create 10 levels based on quantiles
    levels = pd.qcut(mega_merged[target], q=3, labels=False, duplicates='drop')
    mega_merged[f"{target}_level"] = levels

    # Generate a separate file for each level
    for level in range(3):
        level_data = mega_merged[mega_merged[f"{target}_level"] == level]

        # Skip levels with no data
        if level_data.empty:
            continue

        # Save the mega_merged data for this level
        level_file_path = f"{target_dir}/{target}_level_{level}.csv"
        level_data.to_csv(level_file_path, index=False)

        # Match with tbs2 data based on time
        matched_tbs2 = pd.merge_asof(
            level_data.sort_values('time'),
            tbs2.sort_values('time'),
            on='time',
            direction='nearest'
        )
        matched_tbs2 = matched_tbs2[['time', 'eCO2', 'TVOC']]

        # Save the tbs2 data for this level
        tbs2_file_path = f"{target_dir}/{target}_tbs2_level_{level}.csv"
        matched_tbs2.to_csv(tbs2_file_path, index=False)

print("Files have been generated and saved.")
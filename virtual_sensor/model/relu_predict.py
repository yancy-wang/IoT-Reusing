import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load datasets
mega_merged_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/mega_merged.csv'
tbs2_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/tbs2_merged.csv'
h5_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/model_esp32c3.h5'

mega_merged = pd.read_csv(mega_merged_path, parse_dates=['time'])
tbs2 = pd.read_csv(tbs2_path, parse_dates=['time'])

# Merge datasets on time
merged_data = pd.merge_asof(
    mega_merged.sort_values('time'),
    tbs2.sort_values('time'),
    on='time',
    direction='nearest'
)

# 保存按照 mega_sensor 对应挑选出来的 Thunderboard Sense 2 数据
selected_tbs2_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/selected_tbs2_points.csv'
selected_tbs2_data = merged_data[['time', 'eCO2', 'TVOC']]
selected_tbs2_data.to_csv(selected_tbs2_path, index=False)
print(f"Selected Thunderboard Sense 2 data points have been saved to {selected_tbs2_path}")

# Extract features and target columns
features = merged_data[['eCO2', 'TVOC']].fillna(0)  # Use Thunderboard Sense2 data as features
targets = merged_data[["co_ppm", "no2_ppb", "nc_0p5_npcm3", "nc_1p0_npcm3",
                        "nc_2p5_npcm3", "nc_4p0_npcm3", "nc_10p0_npcm3", "Mc_1p0_ugpm3",
                        "Mc_2p5_ugpm3", "Mc_4p0_ugpm3", "Mc_10p0_ugpm3"]].fillna(0)

# Scale data
scaler_features = StandardScaler()
scaler_targets = StandardScaler()
features_scaled = scaler_features.fit_transform(features)
targets_scaled = scaler_targets.fit_transform(targets)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(features_scaled, targets_scaled, test_size=0.2, random_state=42)

# Build a lightweight Dense model
model = Sequential([
    Dense(64, input_dim=X_train.shape[1], activation='relu'),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(targets.shape[1])  # Output layer for all target variables
])

# Compile the model
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train the model
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    verbose=1
)

# Save the trained model as .h5
model.save(h5_model_path)
print(f"Model has been saved to {h5_model_path}")

# Predict using the test data
y_pred_scaled = model.predict(X_test)

# Reverse the scaling for both targets and predictions to plot in the original scale
y_pred = scaler_targets.inverse_transform(y_pred_scaled)
y_actual = scaler_targets.inverse_transform(y_test)

# Get the target variable names
target_columns = targets.columns

# Plot each target variable's predicted vs actual data
pdf_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/predicted_vs_actual.pdf'

with PdfPages(pdf_path) as pdf:
    for i, target in enumerate(target_columns):
        plt.figure(figsize=(10, 6))
        plt.plot(y_actual[:, i], label='Actual', color='orange', alpha=0.6)
        plt.plot(y_pred[:, i], label='Predicted', color='blue', alpha=0.6)
        plt.title(f'Predicted vs Actual: {target}')
        plt.xlabel('Sample Index')
        plt.ylabel(target)
        plt.legend()
        pdf.savefig()  # Save the current figure into the PDF
        plt.close()  # Close the figure to free memory

print(f"All plots have been saved to {pdf_path}")
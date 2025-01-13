import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

# Load datasets
mega_merged_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/mega_merged.csv'
tbs2_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/tbs2_merged.csv'
h5_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/model.h5'

mega_merged = pd.read_csv(mega_merged_path, parse_dates=['time'])
tbs2 = pd.read_csv(tbs2_path, parse_dates=['time'])

# Merge datasets on time
merged_data = pd.merge_asof(
    mega_merged.sort_values('time'),
    tbs2.sort_values('time'),
    on='time',
    direction='nearest'
)

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

# Build the LSTM model
model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], 1), return_sequences=True, activation='relu'),
    Dropout(0.2),
    LSTM(32, return_sequences=False, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(targets.shape[1])  # Output layer for all target variables
])

# Compile the model
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Reshape input data to 3D for LSTM
X_train_lstm = np.expand_dims(X_train, axis=2)
X_test_lstm = np.expand_dims(X_test, axis=2)

# Train the model
history = model.fit(
    X_train_lstm, y_train,
    validation_data=(X_test_lstm, y_test),
    epochs=50,
    batch_size=32,
    verbose=1
)

# Save the trained model as .h5
model.save(h5_model_path)
print(f"Model has been saved to {h5_model_path}")

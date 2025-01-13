import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Define paths
base_dir = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level'
output_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/xiao_esp32c3_model.pkl'

# Load all files
target_columns = ["co_ppm", "nc_0p5_npcm3", "nc_1p0_npcm3",
                  "nc_2p5_npcm3", "nc_4p0_npcm3", "nc_10p0_npcm3", "Mc_1p0_ugpm3",
                  "Mc_2p5_ugpm3", "Mc_4p0_ugpm3", "Mc_10p0_ugpm3"]

X, y = [], []

for target in target_columns:
    target_dir = os.path.join(base_dir, target)
    for level in range(10):
        level_file_path = os.path.join(target_dir, f"{target}_level_{level}.csv")
        tbs2_file_path = os.path.join(target_dir, f"{target}_tbs2_level_{level}.csv")
        
        if os.path.exists(level_file_path) and os.path.exists(tbs2_file_path):
            tbs2_data = pd.read_csv(tbs2_file_path)
            tbs2_data['label'] = level
            X.append(tbs2_data[['eCO2', 'TVOC']].values)
            y.append(tbs2_data['label'].values)

# Combine data
X = np.vstack(X)
y = np.hstack(y)

# Preprocess data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Train a classification model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=[str(i) for i in label_encoder.classes_]))

# Save the model and scaler for deployment
joblib.dump({'model': model, 'scaler': scaler, 'label_encoder': label_encoder}, output_model_path)
print(f"Model and preprocessing artifacts saved to {output_model_path}")
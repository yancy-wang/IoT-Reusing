import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import subprocess
import os
import time

# File paths
tflite_model_path = "/home/pi/mu_code/tf_model/new_model.tflite"
scaler_params_path = "/home/pi/mu_code/tf_model/scaler_params.csv"
test_data_path = "/home/pi/mu_code/tf_model/test.csv"
metrics_output_path = "/home/pi/mu_code/tf_model/metrics_per_label.csv"
predictions_output_path = "/home/pi/mu_code/tf_model/predictions.csv"

# Load scaling parameters
scaler_params = pd.read_csv(scaler_params_path)
scaler = StandardScaler()
scaler.mean_ = scaler_params['mean'].values
scaler.scale_ = scaler_params['scale'].values

# Load test data
test_data = pd.read_csv(test_data_path)

# Ensure the test data contains the 'label' column
if 'label' not in test_data.columns:
    raise ValueError("Test data must contain 'label' column for accuracy calculation.")

X_test = test_data[['eCO2']].values
y_true = test_data['label'].values  # True labels

# Standardize the data
X_test_scaled = scaler.transform(X_test)

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Function to run perf and capture CPU metrics
def run_perf_command():
    perf_command = (
        "perf stat -e task-clock,cycles,instructions,cache-misses,cache-references "
        "-- sleep 0.01 2>&1 | grep -E '(task-clock|cycles|instructions|cache-misses|cache-references)'"
    )
    try:
        result = subprocess.check_output(perf_command, shell=True).decode()
        metrics = {}
        for line in result.strip().split("\n"):
            parts = line.split()
            metrics[parts[1]] = float(parts[0].replace(',', ''))
        return metrics
    except Exception as e:
        print(f"Error collecting perf metrics: {e}")
        return {}

# Function to get temperature
def get_temperature():
    try:
        with open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000.0  # Convert millidegree to Celsius
        return temp
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return -1

# Function to get voltage and current using vcgencmd
def get_voltage_and_current():
    try:
        voltage = float(
            subprocess.check_output("vcgencmd measure_volts", shell=True).decode().split('=')[1][:-1]
        )
        return voltage
    except Exception as e:
        print(f"Error collecting voltage metrics: {e}")
        return -1

# Get current process ID
current_pid = os.getpid()

# Begin inference and metrics recording
metrics_data = []
start_time = time.time()

predicted_labels = []
inference_times = []  # To store individual inference times
for idx, input_value in enumerate(X_test_scaled):
    input_data = np.array([input_value], dtype=np.float32)

    # Collect pre-inference metrics
    perf_metrics_before = run_perf_command()
    temp_before = get_temperature()
    voltage_before = get_voltage_and_current()

    # Perform inference and record time
    inference_start = time.time()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    inference_end = time.time()
    
    predicted_label = np.argmax(output_data)
    predicted_labels.append(predicted_label)

    # Collect post-inference metrics
    perf_metrics_after = run_perf_command()
    temp_after = get_temperature()
    voltage_after = get_voltage_and_current()

    # Calculate inference time in microseconds
    inference_time_us = (inference_end - inference_start) * 1_000_000
    inference_times.append(inference_time_us)

    # Append metrics data
    metrics_data.append({
        "Label_Index": idx,
        "Predicted_Label": predicted_label,
        "Task_Clock_Before": perf_metrics_before.get("task-clock", -1),
        "Cycles_Before": perf_metrics_before.get("cycles", -1),
        "Instructions_Before": perf_metrics_before.get("instructions", -1),
        "Cache_Misses_Before": perf_metrics_before.get("cache-misses", -1),
        "Temperature_Before": temp_before,
        "Voltage_Before": voltage_before,
        "Task_Clock_After": perf_metrics_after.get("task-clock", -1),
        "Cycles_After": perf_metrics_after.get("cycles", -1),
        "Instructions_After": perf_metrics_after.get("instructions", -1),
        "Cache_Misses_After": perf_metrics_after.get("cache-misses", -1),
        "Temperature_After": temp_after,
        "Voltage_After": voltage_after,
        "Inference_Time_us": round(inference_time_us, 3)
    })

end_time = time.time()

# Save metrics data to CSV
metrics_df = pd.DataFrame(metrics_data)
metrics_df.to_csv(metrics_output_path, index=False)
print(f"Metrics per label saved to {metrics_output_path}")

# Save predictions to CSV
test_data['Predicted_Label'] = predicted_labels
test_data.to_csv(predictions_output_path, index=False)
print(f"Predictions saved to {predictions_output_path}")

# Calculate accuracy
accuracy = accuracy_score(y_true, predicted_labels)
print(f"Accuracy: {accuracy:.4f}")

# Generate classification report
report = classification_report(y_true, predicted_labels)
print("Classification Report:\n", report)

# Calculate averages
average_inference_time_us = np.mean(inference_times)

# Print averages
print(f"Average Inference Time: {average_inference_time_us:.3f} µs")
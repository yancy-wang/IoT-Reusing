import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import subprocess
import os
import time

# 文件路径
tflite_model_path = "/home/pi/mu_code/tf_model/co_ppm_merged_eco2_model.tflite"
scaler_params_path = "/home/pi/mu_code/tf_model/co_ppm_merged_scaler_params.csv"
test_data_path = "/home/pi/mu_code/tf_model/test.csv"
metrics_output_path = "/home/pi/mu_code/tf_model/metrics_per_label.csv"
predictions_output_path = "/home/pi/mu_code/tf_model/test_predictions_original.csv"

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

# Function to get CPU and memory usage
def get_process_metrics(pid):
    command = f"ps -p {pid} -o %cpu,rss | tail -n 1"
    try:
        result = subprocess.check_output(command, shell=True).decode().strip()
        cpu, memory = result.split()
        return float(cpu), int(memory)
    except Exception as e:
        print(f"Error collecting metrics: {e}")
        return -1.0, -1

# Get current process ID
current_pid = os.getpid()

# Begin inference and metrics recording
metrics_data = []
start_time = time.time()

predicted_labels = []
inference_times = []  # To store individual inference times
for idx, input_value in enumerate(X_test_scaled):
    input_data = np.array([input_value], dtype=np.float32)

    # Record CPU and memory usage before inference
    cpu_before, memory_before = get_process_metrics(current_pid)

    # Perform inference and record time
    inference_start = time.time()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    inference_end = time.time()
    
    predicted_label = np.argmax(output_data)
    predicted_labels.append(predicted_label)

    # Record CPU and memory usage after inference
    cpu_after, memory_after = get_process_metrics(current_pid)

    # Calculate inference time in microseconds
    inference_time_us = (inference_end - inference_start) * 1_000_000
    inference_times.append(inference_time_us)

    # Append metrics data
    metrics_data.append({
        "Label_Index": idx,
        "Predicted_Label": predicted_label,
        "CPU_Usage_Before": cpu_before,
        "Memory_Usage_Before": memory_before,
        "CPU_Usage_After": cpu_after,
        "Memory_Usage_After": memory_after,
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
average_cpu_before = np.mean([x["CPU_Usage_Before"] for x in metrics_data])
average_memory_before = np.mean([x["Memory_Usage_Before"] for x in metrics_data])
average_cpu_after = np.mean([x["CPU_Usage_After"] for x in metrics_data])
average_memory_after = np.mean([x["Memory_Usage_After"] for x in metrics_data])
average_inference_time_us = np.mean(inference_times)

# Print averages
print(f"Average CPU Usage Before: {average_cpu_before:.2f}%")
print(f"Average Memory Usage Before: {average_memory_before:.2f} KB")
print(f"Average CPU Usage After: {average_cpu_after:.2f}%")
print(f"Average Memory Usage After: {average_memory_after:.2f} KB")
print(f"Average Inference Time: {average_inference_time_us:.3f} µs")
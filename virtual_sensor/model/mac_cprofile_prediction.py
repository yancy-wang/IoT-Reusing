import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import cProfile
import pstats
import io

# File paths
tflite_model_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/co_ppm_merged_eco2_model.tflite"
scaler_params_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/co_ppm_merged_scaler_params.csv"
test_data_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"
profiling_output_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/profiling_results.txt"

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


# Function to perform inference with printing results
def inference_with_metrics():
    predicted_labels = []
    for idx, input_value in enumerate(X_test_scaled):
        input_data = np.array([input_value], dtype=np.float32)

        # Perform inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predicted_label = np.argmax(output_data)
        predicted_labels.append(predicted_label)

        # Print inference results
        print(f"Index: {idx}, Input Value: {input_value[0]:.3f}, Predicted Label: {predicted_label}, True Label: {y_true[idx]}")

    return predicted_labels


# Profile the inference process
pr = cProfile.Profile()
pr.enable()  # Start profiling
predicted_labels = inference_with_metrics()
pr.disable()  # Stop profiling

# Print profiling results
s = io.StringIO()
ps = pstats.Stats(pr, stream=s)
ps.strip_dirs().sort_stats("cumulative").print_stats()

# Save profiling results to a file
with open(profiling_output_path, "w") as f:
    f.write(s.getvalue())

print(f"Profiling results saved to {profiling_output_path}")

# Calculate accuracy
accuracy = accuracy_score(y_true, predicted_labels)
print(f"Accuracy: {accuracy:.4f}")

# Generate classification report
report = classification_report(y_true, predicted_labels)
print("Classification Report:\n", report)
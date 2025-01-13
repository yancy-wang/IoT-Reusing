import tensorflow as tf
import numpy as np
from tensorflow.keras.losses import MeanSquaredError

# Paths
h5_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/model_esp32c3.h5'
tflite_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/model_esp32c3.tflite'
model_h_path = '/Users/wangyangyang/Desktop/Finland/summer_job/virtual_sensor/xiao_board/model.h'

# Load the trained model with explicit custom_objects
model = tf.keras.models.load_model(h5_model_path, custom_objects={'mse': MeanSquaredError()})

# Convert to TensorFlow Lite format with full integer quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Specify input and output types as INT8
def representative_dataset_gen():
    for _ in range(100):
        # Replace with a sample of your training data
        data = np.random.rand(1, 2).astype(np.float32)
        yield [data]

converter.representative_dataset = representative_dataset_gen
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8  # Xiao ESP32C3 supports INT8
converter.inference_output_type = tf.int8

# Disable per-channel quantization for fully connected layers
converter._experimental_disable_per_channel_quantization_for_dense_layers = True

# Convert the model
tflite_model = converter.convert()

# Save the .tflite model
with open(tflite_model_path, 'wb') as f:
    f.write(tflite_model)
print(f"TFLite model has been saved to {tflite_model_path}")

# Convert .tflite model to a C array for Arduino
def convert_to_c_array(tflite_model):
    c_array = ', '.join(f'0x{byte:02x}' for byte in tflite_model)
    return c_array

c_model_content = convert_to_c_array(tflite_model)
model_h_content = f"""
#ifndef MODEL_H
#define MODEL_H

const unsigned char g_model[] = {{
{c_model_content}
}};
const int g_model_len = {len(tflite_model)};

#endif  // MODEL_H
"""

# Save the model.h file
with open(model_h_path, 'w') as f:
    f.write(model_h_content)
print(f"model.h has been saved to {model_h_path}")

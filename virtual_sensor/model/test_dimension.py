import tensorflow as tf

# Load TFLite model
tflite_model_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/model_esp32c3.tflite'
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Get output details
output_details = interpreter.get_output_details()
print("Output details:", output_details)

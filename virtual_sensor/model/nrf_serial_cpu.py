import serial
import pandas as pd
import time

# Configuration for the serial connection
port = "/dev/cu.usbmodem1101"  # Replace with your Xiao nRF52840 port
baudrate = 115200
ser = serial.Serial(port, baudrate, timeout=1)

# File paths
input_csv_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"
output_csv_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/xiao_board/predicted_results_all.csv"

# Read the CSV file
df = pd.read_csv(input_csv_path)
if "eCO2" not in df.columns:
    raise ValueError("CSV file must contain an 'eCO2' column.")

# Extract eCO2 data
eCO2_data = df["eCO2"]
predicted_labels = []
inference_times = []
cpu_usages = []
used_memories = []
free_memories = []

# Send data and receive predictions
print("Starting to send eCO2 data and receive predictions...")
for index, eCO2_value in enumerate(eCO2_data):
    try:
        # Send eCO2 data
        ser.write(f"{eCO2_value}\n".encode())
        print(f"Sent eCO2 value ({index + 1}): {eCO2_value}")

        # Wait for and process response
        predicted_label = None
        inference_time = None
        cpu_usage = None
        used_memory = None
        free_memory = None

        while True:
            line = ser.readline().decode().strip()
            if line.startswith("Predicted Label:"):
                # Parse predicted label
                predicted_label = int(line.split(" (")[0].split(":")[1].strip())
                print(f"Received Prediction: {predicted_label}")
            elif line.startswith("Inference Time:"):
                # Parse inference time
                inference_time = int(line.split(":")[1].strip().split()[0])
                print(f"Inference Time: {inference_time} us")
            elif line.startswith("CPU Usage:"):
                # Parse CPU usage
                cpu_usage = float(line.split(":")[1].strip().split()[0])
                print(f"CPU Usage: {cpu_usage} %")
            elif line.startswith("Used Memory:"):
                # Parse used memory
                used_memory = int(line.split(":")[1].strip().split()[0])
                print(f"Used Memory: {used_memory} bytes")
            elif line.startswith("Free Memory:"):
                # Parse free memory
                free_memory = int(line.split(":")[1].strip().split()[0])
                print(f"Free Memory: {free_memory} bytes")
                break  # End of metrics

            elif "ERROR" in line:
                print("Error received from device.")
                break

        # Append results
        predicted_labels.append(predicted_label)
        inference_times.append(inference_time)
        cpu_usages.append(cpu_usage)
        used_memories.append(used_memory)
        free_memories.append(free_memory)

    except Exception as e:
        print(f"An error occurred: {e}")
        predicted_labels.append(None)
        inference_times.append(None)
        cpu_usages.append(None)
        used_memories.append(None)
        free_memories.append(None)

    time.sleep(0.1)  # Avoid overloading the serial connection

# Save results to CSV
df["Predicted_Label"] = predicted_labels
df["Inference_Time_us"] = inference_times
df["CPU_Usage_Percent"] = cpu_usages
df["Used_Memory_Bytes"] = used_memories
df["Free_Memory_Bytes"] = free_memories
df.to_csv(output_csv_path, index=False)
print(f"Results saved to {output_csv_path}")

ser.close()
print("Serial connection closed.")
import serial
import pandas as pd
import time

# Serial port configuration
port = "/dev/cu.usbmodem1101"  # Replace with your nRF52840 port
baudrate = 115200
ser = serial.Serial(port, baudrate, timeout=1)

# File paths
input_csv_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"
output_csv_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/xiao_board/predicted_labels_pio.csv"

# Read CSV file
df = pd.read_csv(input_csv_path)
if "eCO2" not in df.columns:
    raise ValueError("Input CSV must contain an 'eCO2' column.")

eCO2_data = df["eCO2"]
results = []

# Interact with the device
print("Sending eCO2 data to the device...")
for index, eCO2_value in enumerate(eCO2_data):
    try:
        ser.write(f"{eCO2_value}\n".encode())
        print(f"Sent eCO2 value ({index + 1}/{len(eCO2_data)}): {eCO2_value}")

        response = []
        while True:
            line = ser.readline().decode().strip()
            if line:
                print(f"DEBUG: Received line: {line}")
                response.append(line)
                if line.startswith("CPU Usage:"):  # End of response
                    break

        # Parse response
        result = {
            "eCO2": eCO2_value,
            "Predicted_Label": None,
            "Inference_Time_us": None,
            "Memory_Used_Before": None,
            "Memory_Used_After": None,
            "CPU_Usage_%": None,
        }

        for line in response:
            if line.startswith("Predicted Label:"):
                result["Predicted_Label"] = line.split(":")[1].split("(")[0].strip()
            elif line.startswith("Inference Time:"):
                result["Inference_Time_us"] = int(line.split(":")[1].strip().split()[0])
            elif line.startswith("Memory Used Before:"):
                result["Memory_Used_Before"] = int(line.split(":")[1].strip().split()[0])
            elif line.startswith("Memory Used After:"):
                result["Memory_Used_After"] = int(line.split(":")[1].strip().split()[0])
            elif line.startswith("CPU Usage:"):
                result["CPU_Usage_%"] = float(line.split(":")[1].strip().split()[0])

        results.append(result)
    except Exception as e:
        print(f"Error: {e}")
        results.append({
            "eCO2": eCO2_value,
            "Predicted_Label": None,
            "Inference_Time_us": None,
            "Memory_Used_Before": None,
            "Memory_Used_After": None,
            "CPU_Usage_%": None,
        })

    time.sleep(0.1)

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(output_csv_path, index=False)
print(f"Results saved to {output_csv_path}")

ser.close()
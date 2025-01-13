import serial
import time
import pandas as pd
import os

def read_from_serial(port, baudrate=115200, timeout=1):
    ser = serial.Serial(port, baudrate, timeout=timeout)
    return ser

def save_to_csv(data, filename):
    try:
        df = pd.DataFrame(data, columns=[
            "Timestamp", "Temperature", "Humidity", "VOC_Index", "SRAW_VOC", "SRAW_NOx", "Lux", "Sound_dB", "PIR", "LowPulseOccupancy", "Ratio", "DustConcentration", "MassConcentration"
        ])
        df.to_csv(filename, index=False)
    except AttributeError as e:
        print(f"Error creating DataFrame or saving to CSV: {e}")
        print("Check your pandas installation and ensure DataFrame is available.")

def main():
    port = '/dev/cu.usbmodem101'
    output_dir = '/Users/wangyangyang/Desktop/wio/code/sensor_data/'  # 存储CSV文件的目录

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        ser = read_from_serial(port)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    start_time = time.time()
    hour = 0
    data = []

    while hour < 3:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                data.append(line.split(','))

            if time.time() - start_time >= 60:
                filename = os.path.join(output_dir, f"sensor_data_hour_{hour}.csv")
                save_to_csv(data, filename)
                data = []
                start_time = time.time()
                hour += 1

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during data read or write: {e}")

    ser.close()

if __name__ == "__main__":
    main()

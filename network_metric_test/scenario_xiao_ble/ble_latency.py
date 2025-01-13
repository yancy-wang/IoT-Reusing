import serial
import csv
import time

# Replace with your actual serial port and baud rate
SERIAL_PORT = '/dev/cu.usbmodem2101'  # Adjust this as needed
BAUD_RATE = 115200
OUTPUT_FILE = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/ble_latency_data.csv'  # Save path

# Number of readings to collect
MAX_READINGS = 314

def main():
    try:
        # Open the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow time for connection

        # Open the CSV file to save data
        with open(OUTPUT_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'BLE Latency (ms)'])  # CSV header

            print("Starting to read from Arduino...")

            count = 0  # Initialize count of latency readings

            while count < MAX_READINGS:
                line = ser.readline().decode().strip()
                
                # Filter for latency data based on Arduino output
                if "Temperature" in line:
                    print(line)  # Optional: print each line to the console

                elif "Latency" in line:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    # Extract latency value from Arduino output
                    latency_value = float(line.split(":")[1].strip().replace(" ms", ""))
                    
                    # Save to CSV
                    writer.writerow([timestamp, latency_value])
                    count += 1
                    print(f"Recorded Latency {count}: {latency_value} ms at {timestamp}")

    except serial.SerialException as e:
        print(f"Error reading serial port: {e}")
    except KeyboardInterrupt:
        print("Stopping data recording.")
    finally:
        ser.close()
        print("Serial connection closed.")
        print(f"Recorded a total of {count} latency values.")

if __name__ == "__main__":
    main()
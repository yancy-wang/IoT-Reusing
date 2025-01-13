import serial
import csv
import re

# 配置串口参数
SERIAL_PORT = "/dev/cu.usbmodem1101"  # 替换为实际的串口设备名
BAUD_RATE = 115200
OUTPUT_FILE = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/wifi_latency_data.csv"

# 正则表达式来匹配延时数据的格式
pattern = re.compile(r"Request (\d+), Latency: (\d+) ms")

def main():
    # 打开串口
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected to serial port:", SERIAL_PORT)

    # 打开CSV文件，写入标题行
    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Request Number", "Latency (ms)"])

        try:
            while True:
                # 读取串口的一行数据
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print("Received:", line)
                    
                    # 匹配延时数据
                    match = pattern.search(line)
                    if match:
                        request_number = match.group(1)
                        latency = match.group(2)
                        
                        # 将数据写入CSV文件
                        writer.writerow([request_number, latency])
                        print(f"Saved Request {request_number} with Latency: {latency} ms")

        except KeyboardInterrupt:
            print("\nScript terminated by user.")
        finally:
            # 关闭串口和文件
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
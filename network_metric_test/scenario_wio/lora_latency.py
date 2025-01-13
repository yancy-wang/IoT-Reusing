import serial
import re

# 配置串口
SERIAL_PORT = "/dev/cu.usbmodem101"
BAUD_RATE = 9600      # 根据你的设备配置调整波特率
OUTPUT_FILE = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_wio/timestamps.csv"

# 定义正则表达式以匹配时间戳
TIMESTAMP_REGEX = r"Timestamp: (\d+) ms"

def main():
    # 打开串口
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud rate...")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # 初始化变量
    timestamps = []
    count = 0

    try:
        while count < 1000:
            # 读取一行数据
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                # 查找时间戳
                match = re.search(TIMESTAMP_REGEX, line)
                if match:
                    timestamp = int(match.group(1))
                    timestamps.append(timestamp)
                    count += 1
                    print(f"[{count}] Timestamp: {timestamp} ms")
            
            # 结束条件
            if count >= 1000:
                print("Collected 1000 timestamps. Exiting...")
                break
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting...")
    finally:
        ser.close()

    # 保存时间戳到文件
    with open(OUTPUT_FILE, "w") as f:
        f.write("Timestamp (ms)\n")
        for ts in timestamps:
            f.write(f"{ts}\n")
    print(f"Timestamps saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
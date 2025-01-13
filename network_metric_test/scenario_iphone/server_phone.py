from flask import Flask, request, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__)

# 定义 CSV 文件路径
csv_file = 'temperature_data.csv'

# 如果 CSV 文件不存在，则创建并写入标题行
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Temperature"])  # 写入标题行

# 定义路由，用于接收温度数据
@app.route('/temperature', methods=['POST'])
def receive_temperature():
    data = request.get_json()  # 获取JSON数据
    temperature = data.get("temperature")

    if temperature is not None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间戳
        print(f"Received temperature data: {temperature} °C at {timestamp}")  # 打印温度数据和时间戳
        
        # 将数据追加写入 CSV 文件
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, temperature])
        
        return jsonify({"status": "success", "temperature": temperature}), 200
    else:
        return jsonify({"status": "error", "message": "No temperature provided"}), 400

# 启动服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 监听所有接口，端口为5000
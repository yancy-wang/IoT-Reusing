import pyshark
import csv

def calculate_http_latency_and_packets(pcap_file):
    # 读取 pcap 文件
    capture = pyshark.FileCapture(pcap_file, display_filter="ip.addr == 37.33.248.249 && tcp.port == 5000")
    
    # 分组 HTTP 消息，按流 (TCP Stream) 区分
    http_messages = {}
    packet_details = {}  # 用于记录每个流中的包序号
    
    for packet in capture:
        if "tcp" in packet:  # 确保是 TCP 包
            stream_id = packet.tcp.stream  # TCP 流 ID
            timestamp = float(packet.sniff_timestamp)  # 抓包时间
            packet_no = packet.number  # 包序号
            if stream_id not in http_messages:
                http_messages[stream_id] = []
                packet_details[stream_id] = []
            http_messages[stream_id].append(timestamp)
            packet_details[stream_id].append(packet_no)
    
    # 计算每个流的延迟
    latencies = {}
    for stream_id, timestamps in http_messages.items():
        if len(timestamps) > 1:  # 至少有开始和结束
            latency = (max(timestamps) - min(timestamps)) * 1000  # 转换为毫秒
            latencies[stream_id] = latency
    
    return latencies, packet_details

def save_to_csv(latencies, packet_details, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # 写入表头
        writer.writerow(["TCP Stream", "Latency (milliseconds)", "Packets"])
        # 写入每个流的信息
        for stream_id, latency in latencies.items():
            packets = ', '.join(packet_details[stream_id])
            writer.writerow([stream_id, latency, packets])

def analyze_csv(csv_file):
    latencies = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            latencies.append(float(row["Latency (milliseconds)"]))
    
    max_latency = max(latencies)
    min_latency = min(latencies)
    avg_latency = sum(latencies) / len(latencies)

    print(f"Maximum Latency: {max_latency:.3f} ms")
    print(f"Minimum Latency: {min_latency:.3f} ms")
    print(f"Average Latency: {avg_latency:.3f} ms")

# 使用示例
pcap_file = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_iphone/iphone_csc.pcap"  # 替换为你的 PCAP 文件路径
output_csv = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_iphone/iphone_csc.csv"  # 替换为你希望保存的 CSV 路径

# 计算延迟并保存到 CSV
latencies, packet_details = calculate_http_latency_and_packets(pcap_file)
save_to_csv(latencies, packet_details, output_csv)

# 分析生成的 CSV 文件
analyze_csv(output_csv)

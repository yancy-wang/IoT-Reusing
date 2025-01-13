import pandas as pd
import matplotlib.pyplot as plt

# 文件路径
rpi_metrics_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/metrics_per_label_rpi.csv"
mac_metrics_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/metrics_per_label_mac.csv"

# 加载数据
rpi_data = pd.read_csv(rpi_metrics_path)
mac_data = pd.read_csv(mac_metrics_path)

# 绘制 CPU 使用情况
def plot_cpu_usage(rpi_data, mac_data):
    plt.figure(figsize=(10, 6))

    # Raspberry Pi 数据
    plt.plot(rpi_data.index, rpi_data['CPU_Usage_Before'], label='Raspberry Pi - CPU Usage Before', linestyle='-', marker='o')
    plt.plot(rpi_data.index, rpi_data['CPU_Usage_After'], label='Raspberry Pi - CPU Usage After', linestyle='--', marker='o')

    # Mac 数据
    plt.plot(mac_data.index, mac_data['CPU_Usage_Before'], label='Mac - CPU Usage Before', linestyle='-', marker='x')
    plt.plot(mac_data.index, mac_data['CPU_Usage_After'], label='Mac - CPU Usage After', linestyle='--', marker='x')

    plt.xlabel("Sample Index")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage Before and After Inference (Raspberry Pi vs Mac)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("cpu_usage_comparison.png")  # 保存图像
    plt.show()

# 绘制内存使用情况
def plot_memory_usage(rpi_data, mac_data):
    plt.figure(figsize=(10, 6))

    # Raspberry Pi 数据
    plt.plot(rpi_data.index, rpi_data['Memory_Usage_Before'], label='Raspberry Pi - Memory Usage Before', linestyle='-', marker='o')
    plt.plot(rpi_data.index, rpi_data['Memory_Usage_After'], label='Raspberry Pi - Memory Usage After', linestyle='--', marker='o')

    # Mac 数据
    plt.plot(mac_data.index, mac_data['Memory_Usage_Before'], label='Mac - Memory Usage Before', linestyle='-', marker='x')
    plt.plot(mac_data.index, mac_data['Memory_Usage_After'], label='Mac - Memory Usage After', linestyle='--', marker='x')

    plt.xlabel("Sample Index")
    plt.ylabel("Memory Usage (KB)")
    plt.title("Memory Usage Before and After Inference (Raspberry Pi vs Mac)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("memory_usage_comparison.png")  # 保存图像
    plt.show()

# 调用绘图函数
plot_cpu_usage(rpi_data, mac_data)
plot_memory_usage(rpi_data, mac_data)
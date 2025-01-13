import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

# 1. 定义目标变量列表和文件路径
target_variables = [
    "co_ppm", "no2_ppb", "nc_0p5_npcm3", "nc_1p0_npcm3", "nc_2p5_npcm3",
    "nc_4p0_npcm3", "nc_10p0_npcm3", "Mc_1p0_ugpm3", "Mc_2p5_ugpm3",
    "Mc_4p0_ugpm3", "Mc_10p0_ugpm3"
]
folder_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files'
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 2. PDF 文件初始化
pdf_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files/pollution_text_report_with_plots.pdf'
pdf = PdfPages(pdf_path)

# 3. 定义处理和预测函数
def process_file(file_path, target_variable):
    # 加载数据
    df = pd.read_csv(file_path).dropna()
    
    # 数据标准化与 K-means 聚类 (k=3)
    features = ['eCO2', target_variable]  # 仅使用 eCO2 和目标变量
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['label'] = kmeans.fit_predict(scaled_data)
    
    # 聚类结果可视化
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(df['eCO2'], df[target_variable], c=df['label'], cmap='viridis', s=20)
    plt.colorbar(scatter, label="Cluster Label")
    ax.set_title(f"K-means Clustering: eCO2 vs {target_variable}")
    ax.set_xlabel('eCO2')
    ax.set_ylabel(target_variable)
    pdf.savefig(fig)  # 保存聚类图到 PDF
    plt.close()
    
    # 使用 eCO2 预测 target_variable 的 label
    X = df[['eCO2']]
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # 生成分类报告
    report = classification_report(y_test, y_pred)
    
    # 将报告内容写入 PDF
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('off')
    report_text = f"Processed File: {os.path.basename(file_path)}\nTarget Variable: {target_variable}\n\n{report}"
    plt.text(0, 1, report_text, fontsize=10, ha='left', va='top', family='monospace')
    pdf.savefig(fig)  # 保存报告文本到 PDF
    plt.close()
    
    print(f"Processed {target_variable}")
    return report_text

# 4. 批量处理文件和生成报告
for file in files:
    file_path = os.path.join(folder_path, file)
    for target in target_variables:
        if target in file:  # 文件名与目标变量匹配
            process_file(file_path, target)

# 5. 添加封面
fig, ax = plt.subplots(figsize=(8, 6))
ax.axis('off')
plt.text(0.5, 0.5, 'Pollution Level Clustering and Prediction Report\n\nGenerated Results with Visualizations', 
         fontsize=16, ha='center', va='center')
pdf.savefig()
plt.close()

# 关闭 PDF 文件
pdf.close()

print(f"文本报告已保存为: {pdf_path}")
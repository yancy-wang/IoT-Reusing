import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 1. 加载数据
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files/co_ppm_merged.csv'  # 确保文件路径正确
df = pd.read_csv(file_path)  # 读取 CSV 文件

# 2. 数据预处理
# 选择 eCO2、TVOC 和 co_ppm 特征
data = df[['eCO2', 'TVOC', 'co_ppm']]

# 删除缺失值
data = data.dropna()

# 3. 数据标准化
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data)

# 4. 使用肘部法确定最优的 K 值
inertia = []
k_range = range(1, 7)  # 尝试 1 到 6 个簇
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

# 绘制肘部法曲线
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.grid()
plt.show()

# 5. 使用 K-means 进行聚类
optimal_k = 3  # 根据肘部法选择最佳的 k 值
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df['Cluster'] = kmeans.fit_predict(scaled_data)

# 6. 3D 聚类结果可视化
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 绘制散点图
ax.scatter(df['eCO2'], df['TVOC'], df['co_ppm'], c=df['Cluster'], cmap='viridis', s=50)
ax.set_xlabel('eCO2')
ax.set_ylabel('TVOC')
ax.set_zlabel('co_ppm')
ax.set_title(f'3D K-means Clustering with k={optimal_k}')
plt.show()

# 7. 输出聚类结果
print("聚类结果：")
print(df.head())
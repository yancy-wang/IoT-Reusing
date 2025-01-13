from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd

# 数据加载
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files/co_ppm_merged.csv'
data = pd.read_csv(file_path)

# 特征工程
X = data[['eCO2', 'TVOC']]
X['eCO2_TVOC_ratio'] = X['eCO2'] / (X['TVOC'] + 1)
X['eCO2_log'] = np.log1p(X['eCO2'])
X['TVOC_log'] = np.log1p(X['TVOC'])

# 目标变量
y = data['label']

# 数据分割和标准化
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# KNN模型
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
print("Classification Report for KNN:\n", classification_report(y_test, y_pred_knn))

# 决策树模型
dt = DecisionTreeClassifier(random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)
print("Classification Report for Decision Tree:\n", classification_report(y_test, y_pred_dt))

# 朴素贝叶斯模型
nb = GaussianNB()
nb.fit(X_train, y_train)
y_pred_nb = nb.predict(X_test)
print("Classification Report for Gaussian Naive Bayes:\n", classification_report(y_test, y_pred_nb))
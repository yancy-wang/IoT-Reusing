from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 数据路径
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files/co_ppm_merged.csv'
data = pd.read_csv(file_path)

# 特征工程：加入co_ppm特征
X = data[['eCO2', 'TVOC']]
y = data['label']

# 数据分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练LightGBM
model = LGBMClassifier(class_weight='balanced', learning_rate=0.05, max_depth=6, n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 交叉验证
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print("Cross-Validation Accuracy:", np.mean(scores))

# 测试集评估
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# 可视化特征重要性
importances = model.feature_importances_
plt.bar(X.columns, importances)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('Feature Importance')
plt.show()
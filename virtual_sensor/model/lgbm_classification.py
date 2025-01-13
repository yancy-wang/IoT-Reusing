from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# 数据路径
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/merged_files/co_ppm_merged.csv'
data = pd.read_csv(file_path)

# 数据分割
X = data[['eCO2', 'TVOC']]
y = data['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练 LightGBM 模型
lgbm_model = LGBMClassifier(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=6, 
    class_weight='balanced',
    random_state=42
)
lgbm_model.fit(X_train, y_train)

# 预测
y_pred = lgbm_model.predict(X_test)

# 输出结果
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report of LightGBM:\n", classification_report(y_test, y_pred))
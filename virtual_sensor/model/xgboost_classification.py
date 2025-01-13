from xgboost import XGBClassifier
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

# 训练XGBoost模型
xgb_model = XGBClassifier(
    use_label_encoder=False, 
    eval_metric='mlogloss', 
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=6, 
    random_state=42,
    scale_pos_weight=1
)
xgb_model.fit(X_train, y_train)

# 预测
y_pred = xgb_model.predict(X_test)

# 输出结果
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report of XGBoost:\n", classification_report(y_test, y_pred))
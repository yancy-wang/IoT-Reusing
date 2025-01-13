from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from fpdf import FPDF
import pandas as pd
import os

# 文件夹路径
folder_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files'
output_pdf_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/classification_results.pdf'

# 初始化 PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Classification Results Report", ln=True, align='C')

# 遍历文件夹中的所有 CSV 文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)

        # 加载数据
        data = pd.read_csv(file_path)
        
        # 确保 'label' 和特征存在
        if 'label' in data.columns and 'eCO2' in data.columns and 'TVOC' in data.columns:
            X = data[['eCO2', 'TVOC']]
            y = data['label']

            # 数据标准化
            scaler = StandardScaler()
            X = scaler.fit_transform(X)

            # 数据分割
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 训练随机森林模型
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
            rf_model.fit(X_train, y_train)

            # 预测
            y_pred = rf_model.predict(X_test)

            # 评估结果
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)

            # 将结果写入 PDF
            pdf.cell(200, 10, txt=f"File: {file_name}", ln=True)
            pdf.cell(200, 10, txt=f"Accuracy: {accuracy:.4f}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Classification Report:\n{report}")
            pdf.ln(5)  # 添加间隔

        else:
            pdf.cell(200, 10, txt=f"File: {file_name} - Skipped (missing 'label', 'eCO2' or 'TVOC')", ln=True)

# 保存 PDF
pdf.output(output_pdf_path)
print(f"Classification results saved to {output_pdf_path}")
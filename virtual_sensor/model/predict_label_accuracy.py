import pandas as pd
from sklearn.metrics import accuracy_score

# File paths
predicted_labels_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/xiao_board/predicted_labels_pio.csv"
true_labels_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"

# Load the CSV files
predicted_df = pd.read_csv(predicted_labels_path)
true_labels_df = pd.read_csv(true_labels_path)

# Ensure the necessary columns are present
if 'Predicted_Label' not in predicted_df.columns:
    raise ValueError("The predicted labels file must contain a 'Predicted_Label' column.")
if 'label' not in true_labels_df.columns:
    raise ValueError("The true labels file must contain a 'label' column.")

# Ensure the lengths of the data match
if len(predicted_df) != len(true_labels_df):
    raise ValueError("The number of predicted labels and true labels must match.")

# Extract the necessary columns
predicted_labels = predicted_df['Predicted_Label']
true_labels = true_labels_df['label']

# Calculate accuracy
accuracy = accuracy_score(true_labels, predicted_labels)
print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.3f}%)")
import matplotlib.pyplot as plt
import pandas as pd
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/predictions.csv'
data = pd.read_csv(file_path)

# Plot all columns with a detailed legend
plt.figure(figsize=(15, 10))

for column in data.columns:
    plt.plot(data.index, data[column], label=f'Mega - {column}')

# Add labels, title, and legend
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Visualization of All Sensor Predictions')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')  # Adjusting legend position
plt.grid()
plt.tight_layout()
plt.show()

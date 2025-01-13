import serial
import pandas as pd
from datetime import datetime, timedelta

# win
#ser = serial.Serial('COM3', 115200)
# Mac
ser = serial.Serial('/dev/cu.usbmodem2101', 115200)


data_list = []
pm25_data_list = []

start_time = datetime.now()

def save_to_excel():
    # win
    #file_name = 'C:\\Users\\wangy\\Desktop\\wio\\THS_data' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
    #Mac
    file_name = '/Users/wangyangyang/Desktop/Finland/summer_job/wio/comparision_THS/Normal'+ datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'


    df = pd.DataFrame(data_list, columns=['Timestamp', 'Temperature', 'Humidity', 'Sound', 'Light', "VOCs", "PIR"])
    df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")


def save_pm25_to_excel():
    # Mac
    pm25_file_name = '/Users/wangyangyang/Desktop/Finland/summer_job/wio/comparision_THS/PM25' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'

    pm25_df = pd.DataFrame(pm25_data_list, columns=['Timestamp', 'PM2.5'])
    pm25_df.to_excel(pm25_file_name, index=False)
    print(f"PM2.5 data saved to {pm25_file_name}")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        
        if line.startswith("PM2.5="):
            pm25_value = float(line.split('=')[1])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pm25_data_list.append([timestamp, pm25_value])
            print(f"PM2.5: {pm25_value} at {timestamp}")
        else:
            data = line.split(',')
            if len(data) == 6:
                temperature = float(data[0])
                humidity = float(data[1])
                sound = int(data[2])
                light = int(data[3])
                vocs = int(data[4])
                pir = int(data[5])
            
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_list.append([temperature, humidity, sound, light, vocs, pir])
                print(f"Temp: {temperature}, Humidity: {humidity}, Sound: {sound}, Light:{light}, VOCs:{vocs}, PIR:{pir}")
    
    if datetime.now() - start_time >= timedelta(hours=0.05):
        save_to_excel()
        save_pm25_to_excel()
        data_list.clear()
        pm25_data_list.clear()
        start_time = datetime.now()
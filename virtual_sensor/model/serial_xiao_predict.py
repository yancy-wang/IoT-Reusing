import serial
import time
import pandas as pd

# Serial port configuration
SERIAL_PORT = '/dev/cu.usbmodem101'  # Replace with your Xiao's serial port
BAUD_RATE = 9600  # Match the baud rate in the Arduino code
INPUT_CSV = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/thunderboard_2024-11-18_19-43-49.csv'
OUTPUT_CSV = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/predictions.csv'

# Load eCO2 and TVOC data
data = pd.read_csv(INPUT_CSV)[['eCO2', 'TVOC']].dropna()

# Open serial connection
with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
    time.sleep(2)  # Wait for the Serial connection to initialize

    predictions = []

    for _, row in data.iterrows():
        eCO2, TVOC = row['eCO2'], row['TVOC']
        input_line = f"{eCO2},{TVOC}\n"  # Match the Arduino input format

        # Send data to Xiao
        ser.write(input_line.encode())
        time.sleep(0.1)

        # Read predictions
        result = []
        while True:
            line = ser.readline().decode().strip()
            if not line:  # Break if no more data
                break
            if "Predicted Values:" in line:  # Start reading results
                result = []
            elif ":" in line:  # Parse each sensor's output
                try:
                    result.append(float(line.split(": ")[1]))
                except (ValueError, IndexError):
                    continue  # Skip lines that cannot be parsed
        
        if result:  # Append results only if valid data is found
            predictions.append(result)
            print(result)

    # Save predictions to CSV
    predictions_df = pd.DataFrame(predictions, columns=[
        "co_ppm", "no2_ppb", "nc_0p5_npcm3", "nc_1p0_npcm3",
        "nc_2p5_npcm3", "nc_4p0_npcm3", "nc_10p0_npcm3",
        "Mc_1p0_ugpm3", "Mc_2p5_ugpm3", "Mc_4p0_ugpm3", "Mc_10p0_ugpm3"
    ])
    predictions_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Predictions saved to {OUTPUT_CSV}")

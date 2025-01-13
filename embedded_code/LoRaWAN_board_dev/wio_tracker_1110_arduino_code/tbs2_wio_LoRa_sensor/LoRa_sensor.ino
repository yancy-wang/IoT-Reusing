/*
 * Default_Firmware.ino
 * Copyright (C) 2023 Seeed K.K.
 * MIT License
 */

////////////////////////////////////////////////////////////////////////////////
// Includes

#include <Arduino.h>

#include <LbmWm1110.hpp>
#include <Lbmx.hpp>

#include <Lbm_Modem_Common.hpp>
#include <WM1110_Geolocation.hpp>
#include <WM1110_BLE.hpp>
#include <WM1110_Storage.hpp>
#include <WM1110_At_Config.hpp>
#include <Tracker_Peripheral.hpp>

#include <Wire.h>
#include <Digital_Light_TSL2561.h>
#include <SoftwareSerial.h>
#include <map>
#include <string>


// Thunderboard sense2 settings
SoftwareSerial tbs2Serial(24, 25); // RX, TX
const unsigned long interval = 10;
unsigned long previousMillis = 0;
char buffer[10000];
int bufferIndex = 0;
//Thunderboard sense2 data
std::map<std::string, std::string> sensorData;

//Thunderboard sense2 state
bool tbs2Ready = false;


//PIR pin
#define PIR_MOTION_SENSOR 15

//PM2.5 PIN
#define DUST_SENSOR 13

// Set a execution period
static constexpr uint32_t EXECUTION_PERIOD = 1000;    // [msec.]

// Instance
static WM1110_Geolocation& wm1110_geolocation = WM1110_Geolocation::getInstance();

// Track 
uint32_t track_timeout = 2*60*1000;
uint32_t consume_time = 0;
uint32_t track_period_time = 0;  

// Sensor measurement
uint32_t start_sensor_read_time = 0; 
uint32_t sensor_read_period = 0; 

// Button interrupt
bool button_press_flag = false;
bool button_trig_track = false;
bool button_trig_collect = false;

// 3-axis interrupt
bool shock_flag = false;
bool shock_trig_track = false;
bool shock_trig_collect = false;

// Packed buf & size
uint8_t sensor_data_buf[128] = {0};
uint8_t sensor_data_size = 0;

// Packed custom data buffer & size
uint8_t buf[128];
uint8_t size = 0;

// Custom data buffer & size 
uint8_t custom_data_buf[40];
uint8_t custom_data_len = 0;

// Combined data buffer & size
uint8_t combined_sensor_data_buf[256];
uint8_t combined_sensor_data_size = 0;

//tbs2 buffer
String tbs2_buffer ="";

// Sensor data
float x; 
float y; 
float z;
float temperature; 
float humidity;
int32_t vocs_index;
uint16_t sound;
long light_lux;

//tbs2 data
float tbs2_humidity;
float tbs2_temperature;
float tbs2_light;
float tbs2_uv;
float tbs2_pressure;
uint32_t tbs2_eCO2;
uint32_t tbs2_TVOC;
float tbs2_sound;



// The dust sensor configuration
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;
float mass_concentration = 0;

// Receice cmd buf & size
uint8_t cmd_data_buf[244] = {0};
uint8_t cmd_data_size = 0;

// Convert the float to the UINT_32
uint32_t float_to_uint32(float f) {
    if (f < 0) {
        return 0;
    } else if (f > (float)UINT32_MAX) {
        return UINT32_MAX;
    } else {
        return (uint32_t)roundf(f * 100);
    }
}

// For dust sensor calculation
float calculateMassConcentration(float concentration_pcs) {
    const float density = 1.65; // g/cm³
    const float diameter = 2.5e-6; 
    const float volume = (4.0/3.0) * 3.14159 * pow(diameter / 2, 3);
    const float mass = density * volume;
    const float pcs_to_micrograms = mass * 1e12;

    // pcs/0.01CF => pcs/m³
    const float pcs_per_cubic_meter = concentration_pcs * 28316.8;
    return pcs_per_cubic_meter * pcs_to_micrograms;
}

// Get button and vibration actions to trigger positioning
void trigger_track_action(void)
{
    //button action detect
    tracker_peripheral.getUserButtonIrqStatus(&button_press_flag);
    if(button_press_flag)
    {
        printf("Button press down\r\n");
        if((button_trig_track == false) && (button_trig_collect == false))
        {
            button_trig_track = true;
            button_trig_collect = true;
            wm1110_geolocation.setEventStateAll(TRACKER_STATE_BIT0_SOS);    // Set event state
            tracker_peripheral.setSensorEventStatus(TRACKER_STATE_BIT0_SOS); 

        }
        tracker_peripheral.clearUserButtonFlag();
    }

    // Vibration action detect
    tracker_peripheral.getLIS3DHTRIrqStatus(&shock_flag);
    if(shock_flag)
    {
        printf("Shock trigger\r\n");
        if((shock_trig_track == false) && (shock_trig_track == false))
        {
            shock_trig_track = true;
            shock_trig_collect = true;
            wm1110_geolocation.setEventStateAll(TRACKER_STATE_BIT5_DEV_SHOCK);   // Set event state
            tracker_peripheral.setSensorEventStatus(TRACKER_STATE_BIT5_DEV_SHOCK);
        }
        tracker_peripheral.clearShockFlag();
    }
}

// Thunderboars Sense 2 communication
void parseAndSendLoRaData(std::map<std::string, std::string>& data) {
    tbs2_humidity = data.count("Humidity") ? String(data["Humidity"].c_str()).toFloat() : 0;
    tbs2_temperature = data.count("Temperature") ? String(data["Temperature"].c_str()).toFloat() : 0;
    tbs2_light = data.count("AmbientLight") ? String(data["AmbientLight"].c_str()).toFloat() : 0;
    tbs2_uv = data.count("UVIndex") ? String(data["UVIndex"].c_str()).toFloat() : 0;
    tbs2_pressure = data.count("Pressure") ? String(data["Pressure"].c_str()).toFloat() : 0;
    tbs2_eCO2 = data.count("eCO2") ? String(data["eCO2"].c_str()).toInt() : 0;
    tbs2_TVOC = data.count("TVOC") ? String(data["TVOC"].c_str()).toInt() : 0;
    tbs2_sound = data.count("SoundLevel") ? String(data["SoundLevel"].c_str()).toFloat() : 0;
    Serial.print("tbs2_Humidity: "); Serial.println(tbs2_humidity);
    Serial.print("tbs2_Temperature: "); Serial.println(tbs2_temperature);
    Serial.print("tbs2_Light: "); Serial.println(tbs2_light);
    Serial.print("tbs2_UV: "); Serial.println(tbs2_uv);
    Serial.print("tbs2_Pressure: "); Serial.println(tbs2_pressure);
    Serial.print("tbs2_eCO2: "); Serial.println(tbs2_eCO2);
    Serial.print("tbs2_TVOC: "); Serial.println(tbs2_TVOC);
    Serial.print("tbs2_Sound: "); Serial.println(tbs2_sound);
    tbs2Ready = true;
}

void processIncomingData(String input) {
    input.trim();

    if (input.startsWith("[I] ExpSend")) {
        sensorData.clear();
    } else if (input.startsWith("[I] Humidity =")) {
        String value = input.substring(14, input.indexOf(" %RH"));
        value.trim();
        sensorData["Humidity"] = value.c_str();
    } else if (input.startsWith("[I] Temperature =")) {
        String value = input.substring(17, input.indexOf(" C"));
        value.trim();
        sensorData["Temperature"] = value.c_str();
    } else if (input.startsWith("[I] Ambient light =")) {
        String value = input.substring(19, input.indexOf(" lux"));
        value.trim();
        sensorData["AmbientLight"] = value.c_str();
    } else if (input.startsWith("[I] UV Index =")) {
        String value = input.substring(13);
        value.trim();
        sensorData["UVIndex"] = value.c_str();
    } else if (input.startsWith("[I] Pressure =")) {
        String value = input.substring(14, input.indexOf(" mbar"));
        value.trim();
        sensorData["Pressure"] = value.c_str();
    } else if (input.startsWith("[I] eCO2 =")) {
        String value = input.substring(9, input.indexOf(" ppm"));
        value.trim();
        sensorData["eCO2"] = value.c_str();
    } else if (input.startsWith("[I] TVOC =")) {
        String value = input.substring(9, input.indexOf(" ppd"));
        value.trim();
        sensorData["TVOC"] = value.c_str();
    } else if (input.startsWith("[I] Sound level =")) {
        String value = input.substring(17, input.indexOf(" dBA"));
        value.trim();
        sensorData["SoundLevel"] = value.c_str();
    }

    if (sensorData.size() == 8) {
        parseAndSendLoRaData(sensorData);
        sensorData.clear();
    }
}

void tbs2_logic()
{
  // First read the UART data from Thunderboard sense2
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        while (tbs2Serial.available()) {
            char c = tbs2Serial.read();    
            if (c == '\n') {
                buffer[bufferIndex] = '\0';
                processIncomingData(String(buffer));
                bufferIndex = 0;
            } else {
                buffer[bufferIndex++] = c;
                if (bufferIndex >= sizeof(buffer) - 1) {
                    bufferIndex = sizeof(buffer) - 2;
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// setup and loop
void setup()
{
    Serial.begin(115200);
    Wire.begin();
    TSL2561.init();
    pinMode(DUST_SENSOR, INPUT);
    pinMode(PIR_MOTION_SENSOR, INPUT);
    starttime = millis();//get the current time;

    while (!Serial) delay(100);     // Wait for ready
    // set the data rate for the SoftwareSerial port
    tbs2Serial.begin(9600);

    // Initializes the storage area
    wm1110_storage.begin();
    wm1110_storage.loadBootConfigParameters(); // Load all parameters (WM1110_Param_Var.h)

    delay(1000);

    wm1110_ble.begin(); // Init BLE
    wm1110_ble.setName(); // Set the  Bluetooth broadcast name

    // Set broadcast parameters
    // true: central,  false:peripheral   empty:both
    wm1110_ble.setStartParameters();

    // Start broadcast
    wm1110_ble.startAdv();

    // Initializes the detected IIC peripheral sensors(include LIS3DHTR,SHT4x,Si1151,SGP40,DPS310)    
    tracker_peripheral.begin();
    tracker_peripheral.setUserButton(); // Set user button detection

    // Set the location mode to GNSS and uplink the data to SenseCAP platform
    wm1110_geolocation.begin(Track_Scan_Gps,true);

    // Initialize command parsing
    wm1110_at_config.begin();

    sensor_read_period = wm1110_geolocation.getSensorMeasurementPeriod();    // Get period for reading sensor data
    sensor_read_period =1;
    sensor_read_period = sensor_read_period*60*1000;  // Convert to ms
    Serial.print("=============================");
    Serial.print("Time we need:\n");
    Serial.print(sensor_read_period);

    track_period_time = wm1110_geolocation.getTrackPeriod();    // Get period for positioning
    track_period_time = track_period_time*60*1000;  // Convert to ms  

    track_timeout = wm1110_geolocation.getTrackTimeout();
    track_timeout = track_timeout *1000;  // Convert to ms

    // Start running    
    wm1110_geolocation.run();

}


void loop()
{            
    static uint32_t now_time = 0;
    static uint32_t start_scan_time = 0;   

    bool result = false;    

    // Run process 
    // sleepTime is the desired sleep time for LoRaWAN's next task (Periodic positioning is not included)    
    uint32_t sleepTime = wm1110_geolocation.lbmxProcess(); 

    // Light action for Join 
    wm1110_geolocation.modemLedActionProcess();

    if(wm1110_geolocation.time_sync_flag== true) // The device has been synchronized time from the LNS
    {
        trigger_track_action();

        // track
        if(sleepTime > 300) // Free time
        {  
            now_time = smtc_modem_hal_get_time_in_ms( );
            switch(wm1110_geolocation.tracker_scan_status) // Tracker scan status
            {
                case Track_None:
                case Track_Start:
                    if(now_time - start_scan_time > track_period_time ||(start_scan_time == 0)||button_trig_track ||shock_trig_track)
                    {
                        if(wm1110_geolocation.startTrackerScan()) // Start positioning
                        {
                            printf("Start tracker scan\r\n");
                            start_scan_time = smtc_modem_hal_get_time_in_ms( );
                            consume_time = start_scan_time - now_time;
                        }
                        else
                        {
                            consume_time = smtc_modem_hal_get_time_in_ms() - now_time;                    
                        } 
                    }
                    break;
                case Track_Scaning:
                    if(smtc_modem_hal_get_time_in_ms( ) - start_scan_time > track_timeout)
                    {
                        wm1110_geolocation.stopTrackerScan(); // Timeout,stop positioning    
                        result = wm1110_geolocation.getTrackResults( ); // Get results
                        if(result)
                        {
                            wm1110_geolocation.displayTrackRawDatas(); // Dispaly raw datas
                        } 
                    }
                    break;
                case Track_End:
                    result = wm1110_geolocation.getTrackResults( ); // End of position,get results
                    if(result)
                    {
                        wm1110_geolocation.displayTrackRawDatas();
                    }
                    wm1110_geolocation.stopTrackerScan(); // Stop positioning 
                    break;
                case Track_Stop:
                    printf("Stop tracker scan\r\n");
                    //Insert  position data to lora tx buffer 
                    wm1110_geolocation.insertTrackResultsIntoQueue();
                    consume_time = smtc_modem_hal_get_time_in_ms( ) - now_time; 
                    wm1110_geolocation.tracker_scan_status = Track_None;
                    button_trig_track = false;
                    shock_trig_track = false;
                    break;
                default :
                    break;
            }
            sleepTime = sleepTime - consume_time; 
        }
        // sensor 
        if(sleepTime > 500) // Free time : [correct this for test]
        { 

            now_time = smtc_modem_hal_get_time_in_ms();
            if(now_time - start_sensor_read_time > sensor_read_period ||(start_sensor_read_time == 0) ||button_trig_collect ||shock_trig_collect)
            {
                printf("Reading sensor data...\r\n");

                // wio board sensors
                tracker_peripheral.measureLIS3DHTRDatas(&x,&y,&z); // Get the 3-axis data
                tracker_peripheral.measureSHT4xDatas(&temperature,&humidity); // Get the Temperture & humidity data
                tracker_peripheral.measureSGP41Datas(temperature,humidity, &vocs_index); // Get the vocs_index
                tracker_peripheral.measureSoundAdc(&sound);// Get the sound data

                // customized sensors
                // dust
                duration = pulseIn(DUST_SENSOR, LOW);
                lowpulseoccupancy = lowpulseoccupancy+duration;
                ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
                concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
                // （µg/m³）
                float mass_concentration = calculateMassConcentration(concentration);
                Serial.print(lowpulseoccupancy);
                Serial.print(",");
                Serial.print(ratio);
                Serial.print(",");
                Serial.println(concentration);
                Serial.print(",");
                Serial.print(mass_concentration);
                Serial.println(" µg/m³");
                lowpulseoccupancy = 0;


                uint32_t light_value = static_cast<uint32_t>(TSL2561.readVisibleLux()); // Get the light sensor value
                uint32_t dust_value = float_to_uint32(mass_concentration); // Get the dust value
                uint32_t pir_value = digitalRead(PIR_MOTION_SENSOR); // Get the pir status

                Serial.print("light_value:");
                Serial.print(light_value);
                Serial.print("dust_value:");
                Serial.print(dust_value);
                Serial.print("pir_value:");
                Serial.print(pir_value);

                while(tbs2Ready != true)
                {
                  tbs2_logic();
                }

                
                tbs2Ready = false;
                //Transfer tbs2 data
                uint32_t tbs2_humidity_value = float_to_uint32(tbs2_humidity);
                uint32_t tbs2_temperature_value = float_to_uint32(tbs2_temperature);
                uint32_t tbs2_light_value = float_to_uint32(tbs2_light); 
                uint32_t tbs2_uv_value = float_to_uint32(tbs2_uv);
                uint32_t tbs2_pressure_value = float_to_uint32(tbs2_pressure);
                uint32_t tbs2_sound_value = float_to_uint32(tbs2_sound);

                

                // Put in custom_data_buf(4 bytes of data in a group)
                memcpyr(custom_data_buf,(uint8_t*)&tbs2_sound_value,4);
                memcpyr(&custom_data_buf[4],(uint8_t*)&dust_value,4);
                memcpyr(&custom_data_buf[8],(uint8_t*)&pir_value,4);
                memcpyr(&custom_data_buf[12], (uint8_t*)&tbs2_humidity_value,4);
                memcpyr(&custom_data_buf[16], (uint8_t*)&tbs2_temperature_value,4);
                memcpyr(&custom_data_buf[20], (uint8_t*)&tbs2_light_value,4);
                memcpyr(&custom_data_buf[24], (uint8_t*)&tbs2_uv_value,4);
                memcpyr(&custom_data_buf[28], (uint8_t*)&tbs2_pressure_value,4);
                memcpyr(&custom_data_buf[32], (uint8_t*)&tbs2_TVOC,4);
                memcpyr(&custom_data_buf[36], (uint8_t*)&tbs2_eCO2,4);

                // Set custom_data_len
                custom_data_len = 40;

                // Pack datas      
                tracker_peripheral.packUplinkSensorDatas();
                // Pack custom datas      
                tracker_peripheral.packUplinkCustomDatas(custom_data_buf,custom_data_len);

                // Display sensor raw datas 
                tracker_peripheral.displaySensorDatas();
                // Dispaly packed datas
                tracker_peripheral.displayUplinkCustomDatas();
                Serial.print("============================");
                Serial.print("custome size:");
                Serial.print(custom_data_len);

                // Get packed datas
                tracker_peripheral.getUplinkSensorDatas(sensor_data_buf, &sensor_data_size);
                // Get packed datas
                tracker_peripheral.getUplinkCustomDatas(buf, &size);
                Serial.print("============================");
                Serial.print("size:");
                Serial.print(size);

                // Combine sensor and custom data
                memcpy(combined_sensor_data_buf, sensor_data_buf, sensor_data_size);
                memcpy(combined_sensor_data_buf + sensor_data_size, buf, size);
                combined_sensor_data_size = sensor_data_size + size;
                // Insert all combined sensor data to lora tx buffer
                wm1110_geolocation.insertIntoTxQueue(combined_sensor_data_buf, combined_sensor_data_size);
                start_sensor_read_time = smtc_modem_hal_get_time_in_ms( );
                consume_time = start_sensor_read_time - now_time; 
                sleepTime = sleepTime - consume_time;
                button_trig_collect = false;
                shock_trig_collect = false;
            }
        }
    }

    if(wm1110_ble.getBleRecData(cmd_data_buf,&cmd_data_size))    // Communicate commands with APP
    {
        cmd_parse_type = 1;
        wm1110_at_config.parseCmd((char *)cmd_data_buf,cmd_data_size);
        memset(cmd_data_buf,0,cmd_data_size);
        cmd_data_size = 0;
        cmd_parse_type = 0;
    }
    //The Bluetooth connection is disconnected. Restart the device to make the configuration take effect 
    if(wm1110_ble.getBleStatus() == BleRunState::StateDisconnect)
    {
        smtc_modem_hal_reset_mcu();
    }

    delay(min(sleepTime, EXECUTION_PERIOD));

}
////////////////////////////////////////////////////////////////////////////////


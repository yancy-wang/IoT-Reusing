#include <Arduino.h>
#include <Adafruit_TinyUSB.h>

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

//PIR pin
#define PIR_MOTION_SENSOR 15
//PM2.5 PIN
#define DUST_SENSOR 13

float temperature; 
float humidity;
uint16_t sound;
uint16_t light;
int32_t vocs_index;
float temperature_2;
float humidity_2;
uint32_t pir_value;

// The dust sensor configuration

unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;
float mass_concentration = 0;

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

void setup() {
  // put your setup code here, to run once:
    pinMode(DUST_SENSOR, INPUT);
    pinMode(PIR_MOTION_SENSOR, INPUT);
    Serial.begin(115200);
    Wire.begin();
    tracker_peripheral.begin();
    TSL2561.init();
    starttime = millis();//get the current time;
}

void loop() {
  // put your main code here, to run repeatedly: 
  tracker_peripheral.measureSHT4xDatas(&temperature,&humidity); // Get the Temperture & humidity data
  tracker_peripheral.measureSoundAdc(&sound);// Get the sound data
  light = TSL2561.readVisibleLux();
  tracker_peripheral.measureSGP41Datas(temperature_2,humidity_2, &vocs_index); // Get the vocs_index
  pir_value = digitalRead(PIR_MOTION_SENSOR);
  // dust
  duration = pulseIn(DUST_SENSOR, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;
  
  if ((millis()-starttime) > sampletime_ms)//if the sampel time == 30s
    {
      ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
      concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
      // （µg/m³）
      float mass_concentration = calculateMassConcentration(concentration);

      Serial.print("PM2.5=");
      Serial.print(mass_concentration);
      Serial.print("\n");
      
      lowpulseoccupancy = 0;
      starttime = millis();
    }

  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.print(sound);
  Serial.print(","); 
  Serial.print(light);
  Serial.print(",");
  Serial.print(vocs_index);
  Serial.print(",");
  Serial.print(pir_value);
  Serial.print("\n");
}

/**
 * BasicHTTPClient.ino
 *
 * Created on: 24.05.2015
 *
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>

#define USE_SERIAL Serial

WiFiMulti wifiMulti;

void setup() {
  USE_SERIAL.begin(115200);
  USE_SERIAL.println();

  for (uint8_t t = 4; t > 0; t--) {
    USE_SERIAL.printf("[SETUP] WAIT %d...\n", t);
    USE_SERIAL.flush();
    delay(1000);
  }

  wifiMulti.addAP("tpppt", "123456789"); // Replace with your SSID and password
}

void loop() {
  for (int i = 1; i <= 1000; i++) {
    // wait for WiFi connection
    if ((wifiMulti.run() == WL_CONNECTED)) {

      HTTPClient http;
      USE_SERIAL.print("[HTTP] begin...\n");
      http.begin("http://195.148.30.41:5000/sensor");  // HTTP URL for POST

      // Set request headers
      http.addHeader("Content-Type", "application/json");

      // Prepare JSON payload
      String timestamp = String(millis());
      float temperature = 23.5;
      String payload = "{\"timestamp\":\"" + timestamp + "\",\"temperature\":" + String(temperature) + "}";

      uint32_t startTime = millis();
      int httpCode = http.POST(payload);
      uint32_t endTime = millis();

      uint32_t latency = endTime - startTime;

      USE_SERIAL.printf("Request %d, Latency: %d ms\n", i, latency);

      if (httpCode > 0) {
        USE_SERIAL.printf("[HTTP] POST... code: %d\n", httpCode);
        if (httpCode == HTTP_CODE_OK) {
          String response = http.getString();
          USE_SERIAL.println(response);
        }
      } else {
        USE_SERIAL.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    }

    delay(1000);
  }
  while(1);
}
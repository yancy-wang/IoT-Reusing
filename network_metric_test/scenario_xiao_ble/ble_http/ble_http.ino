#include <Arduino.h>
#include <BLEDevice.h>

// Thunderboard MAC address, service UUID, and characteristic UUID
#define THUNDERBOARD_MAC "00:0D:6F:20:D4:96"
static BLEUUID serviceUUID("0000181a-0000-1000-8000-00805f9b34fb");  // Service UUID
static BLEUUID charUUID("00002a6e-0000-1000-8000-00805f9b34fb");     // Temperature characteristic UUID

BLEClient* pClient;
BLERemoteCharacteristic* pRemoteCharacteristic;
bool connected = false;

// Function to read temperature and calculate latency
float readTemperature() {
  if (connected && pRemoteCharacteristic) {
    uint32_t startMicros = micros();  // Start time in microseconds

    // Read value
    String value = pRemoteCharacteristic->readValue();
    uint32_t endMicros = micros();    // End time in microseconds

    // Calculate and print latency
    uint32_t latency = endMicros - startMicros;
    Serial.printf("BLE Read Latency: %d us\n", latency);

    // Parse temperature data
    int16_t tempRaw = (int16_t)((value[1] << 8) | value[0]);
    float temperature = tempRaw / 100.0;
    return temperature;
  }
  return NAN;
}

// Connect to Thunderboard device
bool connectToThunderboard() {
  Serial.print("Connecting to Thunderboard at ");
  Serial.println(THUNDERBOARD_MAC);

  BLEDevice::init("");
  pClient = BLEDevice::createClient();

  if (pClient->connect(BLEAddress(THUNDERBOARD_MAC))) {
    Serial.println("Connected to Thunderboard.");
    connected = true;

    // Retrieve service and characteristic
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      Serial.println("Failed to find our service UUID.");
      pClient->disconnect();
      connected = false;
      return false;
    }
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
      Serial.println("Failed to find our characteristic UUID.");
      pClient->disconnect();
      connected = false;
      return false;
    }
    return true;
  } else {
    Serial.println("Failed to connect to Thunderboard.");
    return false;
  }
}

void setup() {
  Serial.begin(115200);

  // Connect to Thunderboard
  if (!connectToThunderboard()) {
    Serial.println("Failed to connect to Thunderboard, restarting...");
    ESP.restart();
  }
}

void loop() {
  if (connected) {
    float temperature = readTemperature();
    if (!isnan(temperature)) {
      Serial.printf("Temperature: %.2f°C\n", temperature);
    } else {
      Serial.println("Failed to read temperature.");
    }

    // Delay between readings to avoid rapid consecutive reads
    delay(5000);  // Adjust delay as needed
  } else {
    Serial.println("Attempting to reconnect to Thunderboard...");
    connectToThunderboard();
    delay(1000);  // Short delay before trying to reconnect
  }
}
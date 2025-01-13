/*
  Software serial multiple serial test

 Receives from the hardware serial, sends to software serial.
 Receives from software serial, sends to hardware serial.

 The circuit:
 * RX is digital pin A0 (connect to TX of other device)
 * TX is digital pin A1 (connect to RX of other device)
 
 This example code is in the public domain.
 
 Software Serial will not work when Bluetooth Radio is active because the softdevice
 interrupts the library.

 */

#include <Arduino.h>
#include <Adafruit_TinyUSB.h> // for Serial
#include <SoftwareSerial.h>

SoftwareSerial mySerial(24, 25); // RX, TX
const unsigned long interval = 10;  // 5秒间隔
unsigned long previousMillis = 0;     // 上一次时间戳

char buffer[1000]; // 用于存储每行的数据
int bufferIndex = 0;


void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while ( !Serial ) delay(10);   // for nrf52840 with native usb

 
  // set the data rate for the SoftwareSerial port
  mySerial.begin(9600);
}

void loop() // run over and over//
{
  unsigned long currentMillis = millis();

  // 每5秒执行一次读取
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    while (mySerial.available()) {
      char c = mySerial.read();  // 读取一个字符

      // 如果是换行符，表示一行结束
      if (c == '\n') {
        buffer[bufferIndex] = '\0';  // 添加字符串结束符
        Serial.println(buffer);      // 输出接收到的数据

        bufferIndex = 0;  // 重置索引，准备下一行数据
      } else {
        // 如果不是换行符，继续存储字符
        buffer[bufferIndex++] = c;

        // 确保不越界
        if (bufferIndex >= sizeof(buffer) - 1) {
          bufferIndex = sizeof(buffer) - 2;  // 防止越界
        }
      }
    }
  }
}

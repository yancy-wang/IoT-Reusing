#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// WiFi information
const char* ssid = "iPhone";
const char* password = "123456789";

// AWS IoT endpoint
const char* mqttServer = "a3bmzijldaiej2-ats.iot.us-west-2.amazonaws.com";  
const int mqttPort = 8883;

// 设备证书和私钥
const char* certificatePemCrt = 
"-----BEGIN CERTIFICATE-----\n"
"MIIDWTCCAkGgAwIBAgIUdYpmLEITXk6OM6dIFCGH8uN3DugwDQYJKoZIhvcNAQEL\n"
"BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\n"
"SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI0MTExMjA5MzMy\n"
"NVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\n"
"ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALzPh22HVY2uHK28l1iB\n"
"kCYK74LLVQCG54ypqcYNb6jQVBBa1FrhKFmYGeffJGRGAbetdjGQ8U7De3kMUqsH\n"
"X1Xljy5uM8MYkVCNM2XF08XLVwiarW9HFhGkFpo3DFWJz0O/9bFbi6KpdZVo+cEL\n"
"y6rfdXqdaubQce45y3qwxsZVupOg/rPqMx9hxgDb68MKNy9xXmg2V9+fzOm5N6Xw\n"
"/CX7Gn0xLQod+bQ0dTqSY22B1p1psfBhyQLSkD1sxznX+VgZBEcwqOW2+7EtHGJJ\n"
"/0pgzvyP6mIfzPmvtV3axgBnF8sSD7f+Tk4U5GAxYEM0WXak4e2GPp1J6EHSYUO3\n"
"Tt8CAwEAAaNgMF4wHwYDVR0jBBgwFoAUvVQ3GsDLY1Jv3gmVq2oau6HwGh0wHQYD\n"
"VR0OBBYEFGFvu78r6V/XvNHr306Jm+i9U5/OMAwGA1UdEwEB/wQCMAAwDgYDVR0P\n"
"AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQB5Xvhonq2gUzM3K+l3Xv5d8fvB\n"
"z4raKti5qm+Yvt7aiymxYyRzjGQvRRaQYflozE3ZwbzyOvfoDGpNEOm3aRoHeQEU\n"
"pUN/fTPUdWtZmmFXJHRLmI8rIdsddugWhBg85K2h6sCbVahp0/qYrTCo5F8vG0m0\n"
"5ztohz34XI65StJTec8oVFXIyjHiVbMRyHTPxfxXfgXlqNSDtEDnHvPywWDkObR6\n"
"H09DIZWfZWmaYpnffrvIeexRVicB1enl5hZ9+wMCvhsHqMhEBBX7pTnSDVqX1x5E\n"
"tlQ/Nyf4lm9xW01W3lyLRs/5rCNvEpdQXEIuBMat/K55/MxU2EylK/H5VK0b\n"
"-----END CERTIFICATE-----\n";

const char* privatePemKey = 
"-----BEGIN RSA PRIVATE KEY-----\n"
"MIIEpQIBAAKCAQEAvM+HbYdVja4crbyXWIGQJgrvgstVAIbnjKmpxg1vqNBUEFrU\n"
"WuEoWZgZ598kZEYBt612MZDxTsN7eQxSqwdfVeWPLm4zwxiRUI0zZcXTxctXCJqt\n"
"b0cWEaQWmjcMVYnPQ7/1sVuLoql1lWj5wQvLqt91ep1q5tBx7jnLerDGxlW6k6D+\n"
"s+ozH2HGANvrwwo3L3FeaDZX35/M6bk3pfD8JfsafTEtCh35tDR1OpJjbYHWnWmx\n"
"8GHJAtKQPWzHOdf5WBkERzCo5bb7sS0cYkn/SmDO/I/qYh/M+a+1XdrGAGcXyxIP\n"
"t/5OThTkYDFgQzRZdqTh7YY+nUnoQdJhQ7dO3wIDAQABAoIBAQCwlXM2d8UG7dj6\n"
"kBAIAZy8R6v7aomEJad3QdJ7XWOZwcVtSlWi7UOcj4li96oEcgj3LS8GamWU4XSg\n"
"IGtMc2exYTIJHZ4hj9+QM47nVx6ZtXQfovIjyZsVQp60+lj5wxpqZaS2jETLC6vh\n"
"4bz71DlWBQnNdF5fooF7aOgqRhyRrk6elpaGE9ELiP2omDKvRygBAb3Eor2Vih9b\n"
"2CCJdJuIo+apjeHnHdjvNbv8y4dmrxq/NkfR2ihucLjbAUm16dHpHRe5cCN2sgL1\n"
"NQGXykSKi76rcR/z+Tg+CbfXM9A9hQJMkHxuO2kI/MZ38K06urunSwiF+67EhXEb\n"
"2b5Me44ZAoGBAOHbg7edzg7fbMHZ8ijbf0MtOgJvQGMsT4GB390RuJxDhEJqvQ2i\n"
"2dLwiPuN/zTbYwGa5DyyezMskbUjbmE9TWHGu3KbfKUGHlbCjd4Qs/prmtI5V5+y\n"
"NLaEViE1Igt8cZ/JgzHQjgwPT9yKVivbfTU8I7M4wH/Q6bkOA4YaIH37AoGBANYC\n"
"TKDE3TctTuOGkl82xlGraNyqlWhDZaiZf8eTKKMOivp7T3/zeCiyqOBnu6pblFpm\n"
"BIDj07SjJaf+LkbQs3DGedQ4KjGyPWxczoDP3Rzcma9DjYPMZODTKGlfqsBqauRj\n"
"VJTgV9DbBxMAMtnoYsrSpiv1NHUCKXAyxdivTBFtAoGBAJYYTKucypCluGAHV+AB\n"
"Jszc5H0zs+V0UA3v4nbGzRnD4MRGrQa/3+RIB7CtCBn3Zg9uARm5PxieGOL4/eTP\n"
"WXqOGIosfKQqscTUnHUkQoc8NXJZuzqcsl1NCvQcnFhnxhb7Ux2qzIuFLXyRznxs\n"
"7AORyOPU5lDK5Fgf0QWwnUE7AoGBAKqXYJ/S7Ye7PSRPNERjtEiLu2YTME/RUarI\n"
"2TusSXtY713lh6S13jWK3OUsq0KMB8Dbi4F2ml5monC8RAU8/ZzLCXgqYTAGJcJI\n"
"ZG/3wgjsrDEyRw8lkdBJYfBFSyZgbd6qc1TNVBLvVT9HLEHZZU7KBZ4KswsGcyO1\n"
"xVIJwjgtAoGAOY5DxM6r6t5y57NcPh14PLS/uRfydddHAsw/dCfWcQi78fmV+FHF\n"
"CW4nsDLrbqNCv3fKKj7FX6Xo3Sc3l1dNP4B2RYvNlVY8HOZ6M21Hhkm8sntRa4Hm\n"
"Q6ypQbFJaFE82kfAOa77/28W80X5xgg60eGzLpl8SKdiVdZHWBgqYiY=\n"
"-----END RSA PRIVATE KEY-----\n";

const char* rootCa = 
"-----BEGIN CERTIFICATE-----\n"
"MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\n"
"ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\n"
"b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\n"
"MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\n"
"b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\n"
"ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\n"
"9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\n"
"IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\n"
"VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\n"
"93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\n"
"jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\n"
"AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\n"
"A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\n"
"U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\n"
"N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\n"
"o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\n"
"5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\n"
"rqXRfboQnoZsG4q5WTP468SQvvG5\n"
"-----END CERTIFICATE-----\n";

WiFiClientSecure net;
PubSubClient client(net);

void setup() {
  Serial.begin(115200);
  
  // 连接到WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("正在连接到WiFi...");
  }
  Serial.println("已连接到WiFi");

  // 设置WiFiClientSecure以使用证书
  net.setCACert(rootCa);
  net.setCertificate(certificatePemCrt);
  net.setPrivateKey(privatePemKey);

  // 设置MQTT服务器
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  connectToAWS();
}

void connectToAWS() {
  while (!client.connected()) {
    Serial.println("正在连接到AWS IoT...");
    if (client.connect("ESP32_Client")) {
      Serial.println("已连接到AWS IoT");
      client.subscribe("esp32/test");  // 订阅主题
    } else {
      Serial.print("连接失败，状态: ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("收到消息，主题: ");
  Serial.println(topic);
  Serial.print("消息内容: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void loop() {
  if (!client.connected()) {
    connectToAWS();
  }
  client.loop();

  // 示例：发布消息
  String message = "{\"message\": \"Hello from ESP32\"}";
  client.publish("esp32/test", message.c_str());
  delay(5000);  // 每5秒发送一次消息
}
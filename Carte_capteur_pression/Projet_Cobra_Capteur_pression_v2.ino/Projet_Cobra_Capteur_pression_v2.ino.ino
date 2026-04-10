/*
Simple Deep Sleep with Timer Wake Up
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories

This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots

This code is under Public Domain License.

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
*/


#define uS_TO_S_FACTOR 1000000ULL /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  10          /* Time ESP32 will go to sleep (in seconds) */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>
#include <Arduino_LPS22HB.h>


#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-5678-1234-5678-abcdef123456"

RTC_DATA_ATTR int bootCount = 0;

BLECharacteristic *pCharacteristic;

/*
Method to print the reason by which ESP32
has been awaken from sleep
*/
void print_wakeup_reason() {
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch (wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:     Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1:     Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER:    Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD: Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP:      Serial.println("Wakeup caused by ULP program"); break;
    default:                        Serial.printf("Wakeup was not caused by deep sleep: %d\n", wakeup_reason); break;
  }
}

//void read_pressure(){

  //float pressure = BARO.readPressure();
  //Serial.print("Pressure = ");
  //Serial.println(pressure);
  //Serial.println(" kPa");
  //Serial.println();
//}


void setupBLE(float pressure) {
  BLEDevice::init("ESP32_Pressure");

  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  pCharacteristic->addDescriptor(new BLE2902());

  // Convertir la valeur en string
  String value = String(pressure, 2);
  pCharacteristic->setValue(value.c_str());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();

  Serial.println("BLE advertising...");
  Serial.print("Pressure = ");
  Serial.println(pressure);
}

float read_pressure(){
  float pressure = BARO.readPressure();
  //Serial.print("Pressure = ");
  //Serial.println(pressure);
  return pressure;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(21, 22);

  if (!BARO.begin()) {
    Serial.println("Sensor error");
    return;
  }

  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));
  
  //Print the wakeup reason for ESP32
  print_wakeup_reason();

  //Appeler la fonction pour lire la pression

  float pressure = read_pressure();

  //read_pressure();

  // Lancer BLE
  setupBLE(pressure);

  // Laisser le temps à la Raspberry de se connecter
  delay(10000);  // 10 secondes (à ajuster)

  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) + " Seconds");

  Serial.println("Going to sleep now");
  Serial.flush();
  esp_deep_sleep_start();
}

void loop() {
  // vide
}

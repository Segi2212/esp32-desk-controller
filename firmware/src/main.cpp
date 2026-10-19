#include <Arduino.h>
#include <BluetoothSerial.h>
#include <BleKeyboard.h>

BluetoothSerial SerialBT;

#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32 Desk Controller");
  pinMode(LED_PIN, OUTPUT);
  delay(1000);
  Serial.println("Hello from the ESP32!");
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
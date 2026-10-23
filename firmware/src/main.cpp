#include <Arduino.h>
#include <NimBLEDevice.h>

#define LED_PIN 2
#define LED_DISCONNECT_PIN 25 // Red LED: "unplug the charger"
#define LED_CONNECT_PIN 26    // Green LED: "plug in the charger"

class ConnectionEvents : public NimBLEServerCallbacks
{
  void onConnect(NimBLEServer *server, NimBLEConnInfo &info) override
  {
    digitalWrite(LED_PIN, HIGH);
    Serial.printf("Connected: %s\n", info.getAddress().toString().c_str());
  }

  void onDisconnect(NimBLEServer *server, NimBLEConnInfo &info, int reason) override
  {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(LED_CONNECT_PIN, LOW);
    digitalWrite(LED_DISCONNECT_PIN, LOW);

    Serial.println("Disconnected");
  }

  void onAuthenticationComplete(NimBLEConnInfo &info) override
  {
    if (info.isEncrypted())
      Serial.println("Paired: the connection is encrypted");
    else
      Serial.println("Pairing failed (wrong PIN?)");
  }
};

class BatteryEvents : public NimBLECharacteristicCallbacks
{
  void onWrite(NimBLECharacteristic *characteristic, NimBLEConnInfo &info) override
  {
    NimBLEAttValue value = characteristic->getValue();
    std::string line(value.c_str(), value.length());

    int battery, charging;
    if (sscanf(line.c_str(), "BAT:%d,CHG:%d", &battery, &charging) == 2)
    {
      if (battery < 0)
        Serial.println("The laptop has no battery");
      else
      {
        Serial.printf("Battery: %d%% %s\n", battery, charging ? "(charging)" : "");
      }
    }
    else
    {
      Serial.printf("Unknown message: %s\n", line.c_str());
    }
  }
};

class ChargerEvents : public NimBLECharacteristicCallbacks
{
  void onWrite(NimBLECharacteristic *characteristic, NimBLEConnInfo &info) override
  {
    NimBLEAttValue value = characteristic->getValue();
    std::string command(value.c_str(), value.length());

    bool connect = (command == "connect");
    bool disconnect = (command == "disconnect");

    if (!connect && !disconnect && command != "none")
    {
      Serial.printf("Unknown LED command: %s\n", command.c_str());
      return;
    }

    digitalWrite(LED_CONNECT_PIN, connect ? HIGH : LOW);
    digitalWrite(LED_DISCONNECT_PIN, disconnect ? HIGH : LOW);
    Serial.printf("LED: %s\n", command.c_str());
  }
};

void setup()
{
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_CONNECT_PIN, OUTPUT);
  pinMode(LED_DISCONNECT_PIN, OUTPUT);
  digitalWrite(LED_CONNECT_PIN, LOW);
  digitalWrite(LED_DISCONNECT_PIN, LOW);

  delay(1000);
  Serial.println("Hello from the ESP32!");

  // 1. Start Bluetooth with security
  NimBLEDevice::init(DEVICE_NAME);
  NimBLEDevice::setSecurityAuth(true, true, true);
  NimBLEDevice::setSecurityIOCap(BLE_HS_IO_DISPLAY_ONLY);
  NimBLEDevice::setSecurityPasskey(BLE_PIN);

  // 2. Create the server and connect its events
  NimBLEServer *server = NimBLEDevice::createServer();
  server->setCallbacks(new ConnectionEvents());

  server->advertiseOnDisconnect(true);
  // 3. Create the service and the battery characteristic
  NimBLEService *service = server->createService(SERVICE_UUID);
  NimBLECharacteristic *battery = service->createCharacteristic(
      BATTERY_UUID,
      NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_ENC | NIMBLE_PROPERTY::WRITE_AUTHEN);
  battery->setCallbacks(new BatteryEvents());

  // 3.1 Create the characteristics
  NimBLECharacteristic *charger = service->createCharacteristic(
      CHARGER_UUID,
      NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_ENC | NIMBLE_PROPERTY::WRITE_AUTHEN);
  charger->setCallbacks(new ChargerEvents());

  service->start();

  // 4. Start advertising so the laptop can find it
  NimBLEAdvertising *advertising = NimBLEDevice::getAdvertising();
  advertising->setName(DEVICE_NAME);
  advertising->start();

  Serial.printf("Advertising as \"%s\". Pair it from the laptop.\n", DEVICE_NAME);
}

void loop()
{
}
import os
import psutil
import asyncio
import json

from pathlib import Path
from dotenv import load_dotenv
from bleak.exc import BleakError
from bleak import BleakClient, BleakScanner

ROOT = Path(__file__).resolve().parent.parent
ROOT_HOST = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")
PROTOCOL = json.loads((ROOT / "protocol.json").read_text(encoding="utf-8"))

BATTERY_UUID = PROTOCOL["characteristics"]["battery"]
CHARGER_UUID = PROTOCOL["characteristics"]["charger"]
SETTINGS = json.loads((ROOT_HOST / "settings.json").read_text(encoding="utf-8"))

DEVICE_NAME = os.getenv("DESK_DEVICE_NAME")
INTERVAL = 2  # seconds between messages

BATTERY_LOW = SETTINGS["battery_low"]
BATTERY_HIGH = SETTINGS["battery_high"]

if not DEVICE_NAME:
    raise SystemExit("Missing DESK_DEVICE_NAME. Copy .env.example to .env and fill it in.")

if not (0 <= BATTERY_LOW < BATTERY_HIGH <= 100):
    raise SystemExit("Battery_low must be lower than battery_high, both between 0 and 100.")

def read_battery():
    battery = psutil.sensors_battery()
    return battery

def build_message(data):
    if data is None:
        return "No Battery"

    battery_percent = round(data.percent)
    battery_charge = "Charging" if data.power_plugged else "Not Charging"
    
    return f"The battery is {battery_charge}. Percent battery at {battery_percent}%"

def build_esp_message(data):
    """Compact message for the ESP32, e.g. "BAT:87,CHG:1"."""
    if data is None:
        return "BAT:-1,CHG:0"
    return f"BAT:{round(data.percent)},CHG:{int(bool(data.power_plugged))}"

def decide_led(data):
    """Which LED should be on: "connect" (plug in the charger), "disconnect" (unplug it) or "none"."""
    if data is None:
        return "none"

    percent = round(data.percent)

    if percent <= BATTERY_LOW and not data.power_plugged:
        return "connect"
    if percent >= BATTERY_HIGH and data.power_plugged:
        return "disconnect"
    return "none"

async def send_battery(client, battery_data):
    await client.write_gatt_char(BATTERY_UUID, build_esp_message(battery_data).encode(), response=True)
    
async def send_led(client, led):
    await client.write_gatt_char(CHARGER_UUID, led.encode(), response=True)
    
async def main():
    print(f"LOOKING for {DEVICE_NAME}")
    try:
        device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10)
    except (BleakError, OSError) as error:
        print(f"Bluetooth is not available: {error}")
        print("Check that this computer has Bluetooth and that it's turned on.")
        return
    
    if not device:
        print("Device not found. Is it on and paired?")
        return
    async with BleakClient(device) as client:
        print("Connected")
        while True:
            battery_data = read_battery()
            led = decide_led(battery_data)
            await send_battery(client, battery_data)
            await send_led(client, led)
            await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
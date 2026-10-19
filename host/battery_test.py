import os
import psutil
import asyncio

from pathlib import Path
from dotenv import load_dotenv
from bleak.exc import BleakError
from bleak import BleakClient, BleakScanner

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DEVICE_NAME = os.getenv("DESK_DEVICE_NAME")
BATTERY_UUID = "4c2f0001-8e3d-4b7a-9c61-2f5d8a1b3e70"
INTERVAL = 2  # seconds between messages


if not DEVICE_NAME:
    raise SystemExit("Missing DESK_DEVICE_NAME. Copy .env.example to .env and fill it in.")

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

async def send_battery(client):
    battery_data = read_battery()
    await client.write_gatt_char(BATTERY_UUID, build_esp_message(battery_data).encode(), response=True)
    
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
            await send_battery(client)
            await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
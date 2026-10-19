"""Loads settings from the .env file (or environment variables) into the firmware build."""

import os
from pathlib import Path

Import("env")  # noqa: F821 - provided by PlatformIO

def read_dotenv(path):
    values = {}
    
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
            
    return values

dotenv = read_dotenv(Path(env["PROJECT_DIR"]).parent / ".env")

def setting(name, default=None):
    """Returns a setting. A real environment variable wins over the .env file."""
    value = os.environ.get(name, dotenv.get(name, default))
    if value is None:
        print(f"Missing setting {name}. Copy .env.example to .env and fill it in.")
        env.Exit(1)
    return value

device_name = setting("DESK_DEVICE_NAME", "ESP32 Desk Controller")
pin = setting("DESK_BLE_PIN")

if not (pin.isdigit() and len(pin) == 6):
    print("DESK_BLE_PIN must be exactly 6 digits, e.g. 123456.")
    env.Exit(1)
    
env.Append(CPPDEFINES=[
    ("DEVICE_NAME", env.StringifyMacro(device_name)),
    ("BLE_PIN", str(int(pin))),  # int() removes leading zeros: in C, 012345 would be read as octal
])

print(f"Building for device: {device_name}")
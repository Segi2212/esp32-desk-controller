"""Loads settings (.env) and protocol constants (protocol.json) into the firmware build."""

import os
import json

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
protocol_path = Path(env["PROJECT_DIR"]).parent / "protocol.json"
if not protocol_path.exists():
    print(f"Missing {protocol_path}.")
    env.Exit(1)
protocol = json.loads(protocol_path.read_text(encoding="utf-8"))

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
    
defines = [
    ("DEVICE_NAME", env.StringifyMacro(device_name)),
    ("BLE_PIN", str(int(pin))),  # int() removes leading zeros: in C, 012345 would be read as octal
    ("SERVICE_UUID", env.StringifyMacro(protocol["service_uuid"])),
]

# One define per characteristic: "battery" becomes BATTERY_UUID
for name, uuid in protocol["characteristics"].items():
    defines.append((f"{name.upper()}_UUID", env.StringifyMacro(uuid)))

env.Append(CPPDEFINES=defines)

print(f"Building for device: {device_name}")
import time
import psutil


INTERVAL = 2  # seconds between messages

def read_battery():
    battery = psutil.sensors_battery()
    return battery

def build_message(data):
    if data is None:
            return "No Battery"

    battery_percent = round(data.percent)
    battery_charge = "Charging" if data.power_plugged else "Not Charging"
    
    return f"The battery is {battery_charge}. Percent battery at {battery_percent}%"

def main():
    battery_data = read_battery()
    print(build_message(battery_data))

if __name__ == "__main__":
    try:
        while True:
            main()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
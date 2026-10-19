# esp32-desk-controller

ESP32 desk controller for your PC: volume knob, mic mute, notifications and battery status.

> 🚧 Work in progress. I'm building this project step by step while learning.

## Project structure

- `firmware/`: ESP32 code (PlatformIO)
- `host/`: Python program that runs on the PC

## Host setup

From the `host` folder:

1. Create a virtual environment:

   ```bash
   py -3.12 -m venv .venv
   ```

2. Activate it:

   ```bash
   # Windows
   .venv\Scripts\activate

   # Linux
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python battery_test.py
```
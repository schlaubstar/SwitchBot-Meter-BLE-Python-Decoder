# SwitchBotMeter2MQTT-Python
A lightweight Python-based Bluetooth Low Energy (BLE) scanner that reads temperature, humidity, battery level, and RSSI from SwitchBot Meter devices and publishes the values to MQTT.
This project is ideal for:
- Home automation systems (ioBroker, Home Assistant, Node-RED, OpenHAB)
- Raspberry Pi or Linux-based gateways
- Users who want a simple, dependency-light alternative to ESP32-based solutions

## ✨ Features
- Scans for SwitchBot Meter BLE advertisements using bluepy
- Correctly decodes negative temperatures (including sub-zero values)
- Extracts:
- Temperature (°C)
- Humidity (%)
- Battery level (%)
- RSSI (dBm)
- Publishes all values to MQTT in the format:
SwitchBot2MQTT/<MAC>/<attribute>
Example: SwitchBot2MQTT/ce:2a:81:86:4d:2c/temp SwitchBot2MQTT/ce:2a:81:86:4d:2c/hum SwitchBot2MQTT/ce:2a:81:86:4d:2c/bat SwitchBot2MQTT/ce:2a:81:86:4d:2c/rssi
- Filters out corrupted BLE frames
- Optional debug output
- Optional WhatsApp alert on BLE scan failure (via user-provided function)

## 🧠 SWITCHBOT BLE PAYLOAD FORMAT
SwitchBot Meter broadcasts a 16‑byte BLE Service Data frame:
Byte 0–3: Header
Byte 4: Battery level (0–100%)
Byte 5: Temperature low byte
Byte 6: Temperature high byte (bit 7 = sign, bits 0–6 = integer part)
Byte 7: Humidity (0–100%)

### ✔Correct Temperature Decoding (including negative values):
SwitchBot uses a sign bit in the high byte:
bit 7 = 1 → positive temperature
bit 7 = 0 → negative temperature
Remaining 7 bits = integer part
Low byte = decimal part (0–9)
Formula:
```python
int_part = temp_high & 0x7F
dec_part = temp_low / 10.0
if temp_high & 0x80:
temp = int_part + dec_part     # positive
else:
temp = -(int_part + dec_part)  # negative
```

### Example:
Raw bytes: 01 04
integer = 4
decimal = 0.1
sign bit = 0 (negative)
temperature = -4.1°C
This decoding method fixes the common “-127°C bug” seen in many scripts online.

## 🚀 INSTALLATION
- Install dependencies:
sudo apt install python3-pip bluetooth bluez
pip3 install bluepy paho-mqtt
- Clone the repository:
git clone https://github.com/<yourname>/SwitchBotMeter2MQTT-Python
cd SwitchBotMeter2MQTT-Python
- Run the script:
python3 switchbot2mqtt.py

## 🔧 CONFIGURATION
Inside the script:
- Add your MQTT server credentials
- Add your known SwitchBot MAC addresses (optional)
- Enable debug output if needed

## 📡 MQTT OUTPUT EXAMPLE
SwitchBot2MQTT/ce:23:45:67:89:0e/temp  -4.1  
SwitchBot2MQTT/ce:23:45:67:89:0e/hum   57  
SwitchBot2MQTT/ce:23:45:67:89:0e/bat   89  
SwitchBot2MQTT/ce:23:45:67:89:0e/rssi  -91

## 🛠 SYSTEMD SERVICE (optional)
Create:
/etc/systemd/system/switchbot2mqtt.service
Content:
[Unit]
Description=SwitchBot Meter BLE to MQTT
After=bluetooth.target
[Service]
ExecStart=/usr/bin/python3 /path/to/switchbot2mqtt.py
Restart=always
[Install]
WantedBy=multi-user.target
Enable:
sudo systemctl enable --now switchbot2mqtt

This project was developed to provide a clean, reliable, and fully documented Python alternative to ESP32-based SwitchBot Meter integrations.

LICENSE
MIT License

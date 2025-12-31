#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, datetime, binascii
from dataclasses import dataclass

from bluepy.btle import DefaultDelegate, Scanner
import paho.mqtt.client as mqtt

showUnknownDevices = False

@dataclass
class Switchbotdata:
    addr: str
    temp: float
    hum: float
    rssi: int
    bat: int

SwitchBotDataList = []

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        known_devices = {
            "fb:ec:12:34:56:78": "Room1",
            "f1:13:45:67:89:0c": "Room2",
            "dd:42:19:87:65:2e": "Reference_Meter",
            "ce:23:45:67:89:0e": "Room3"
        }

        if dev.addr not in known_devices:
            return

        room = known_devices.get(dev.addr)
        print("-------------------------------------------")
        print(f"Discovered Switchbot: {dev.addr} ({room})")
        print("RSSI:", dev.rssi)

        for adtype, desc, value in dev.getScanData():
            if desc != '16b Service Data':
                continue

            hexv = binascii.unhexlify(value)
            print("ServiceData:", " ".join(f"{b:02X}" for b in hexv))

            bat = hexv[4] & 0x7F
            hum = hexv[7] & 0x7F

            temp_low  = hexv[5]
            temp_high = hexv[6]

            # Correct temperature decoding
            int_part = temp_high & 0x7F
            dec_part = temp_low / 10.0

            if temp_high & 0x80:
                temp = int_part + dec_part
            else:
                temp = -(int_part + dec_part)

            print(f"Temp: {temp}°C")
            print(f"Humidity: {hum}%")
            print(f"Battery: {bat}%")

            if not any(d.addr == dev.addr for d in SwitchBotDataList):
                SwitchBotDataList.append(Switchbotdata(dev.addr, temp, hum, dev.rssi, bat))
                print(f"Added {dev.addr}")

def doManual():
    scanner = Scanner().withDelegate(ScanDelegate())

    try:
        scanner.scan(20.0)
    except Exception as e:
        print(f"⚠️ BLE scan interrupted: {e}")

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.username_pw_set(username="YOUR_MQTT_USER", password="YOUR_MQTT_PASSWORD")
    mqttc.connect("YOUR_MQTT_SERVER", 1883, 60)
    mqttc.loop_start()

    for entry in SwitchBotDataList:
        for attr in ['temp', 'hum', 'rssi', 'bat']:
            value = getattr(entry, attr)
            topic = f"SwitchBot2MQTT/{entry.addr}/{attr}"
            mqttc.publish(topic, value, qos=0)

    mqttc.loop_stop()

if __name__ == '__main__':
    doManual()

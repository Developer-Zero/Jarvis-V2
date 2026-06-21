import json
import datetime

import main

_main = main.Main()

while True:
    packet = input("Enter packet: ")
    _main.recivePacket({"protocol_version": 1, "user_id": "...", "device_id": "...", "type": "input", "payload": packet, "encoding": "utf-8", "request_id": "...", "timestamp": int(datetime.datetime.now().timestamp())})
import json
from core.types import Message

class Main:
    def __init__(self):
        return

    def recivePacket(self, message: dict):
        _packet = Message.from_dict(message)
        print(_packet.to_dict())
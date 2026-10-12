import asyncio
from csv import reader, writer
import json
from pathlib import Path
import sys
from typing import Any

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from models import ConnectionManager, Message, Session

from router.packet_handler import packet_handler


class Server:
    def __init__(self):
        self.connection_manager = ConnectionManager(connections={})
        print("connection manager initialized")

        self.session = Session()
        print("session initialized")

    async def run(self) -> None:
        while True:
            type = input("Enter message type: ")

            payload = input("Enter payload: ")
            encoding = input("Enter encoding (text/json): ")
            if encoding == "json":
                payload = json.loads(payload)

            message = Message(device_id="debug", type=type, payload=payload, encoding=encoding, request_id="debug", timestamp=0)

            asyncio.create_task(packet_handler(message, self.session, self.connection_manager))

from dataclasses import dataclass
import json
from typing import Dict
import asyncio

from models.message import Message

@dataclass
class Connection:
    device_id: str
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

@dataclass
class ConnectionManager:
    connections: Dict[str, Connection]

    def get_connection(self, device_id: str) -> Connection | None: # Easier search
        return self.connections.get(device_id)
    
    def get_connections(self) -> list[Connection] | None:
        return [conn for conn in self.connections.values()]
    
    def remove_connection(self, writer: asyncio.StreamWriter) -> None: # Removes from only the writer
        for device_id, connection in self.connections.items():
            if connection.writer == writer:
                del self.connections[device_id]
                break
    
    async def send_packet(self, message: Message) -> None:
        try:
            connection = self.get_connection(message.device_id)
            if connection is not None:
                connection.writer.write((json.dumps(message.to_dict(), ensure_ascii=False) + "\n").encode("utf-8"))
                await connection.writer.drain()
        except Exception as exc:
            print(f"Failed to send packet to {message.device_id}: {exc}")

import asyncio
import json
from typing import Any

from models import Connection, ConnectionManager, Message, SessionManager
from router.packet_handler import packet_handler


HOST = "0.0.0.0"
PORT = 8765
READ_LIMIT_BYTES = 12 * 1024 * 1024


class Server:
    def __init__(self, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.connection_manager = ConnectionManager(connections={})
        self.session_manager = SessionManager(sessions={})

    async def run(self) -> None:
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            limit=READ_LIMIT_BYTES,
        )
        addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
        print(f"Jarvis TCP packet receiver listening on {addresses}")

        async with server:
            await server.serve_forever()

    async def send_packet(self, writer: asyncio.StreamWriter, packet: dict[str, Any]) -> None:
        writer.write((json.dumps(packet, ensure_ascii=False) + "\n").encode("utf-8"))
        await writer.drain()


    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        print(f"client connected: {peer}")

        try:
            while line := await reader.readline():
                try:
                    data = json.loads(line.decode("utf-8"))
                    message = Message.from_dict(data)
                except Exception as exc:
                    print(f"bad packet from {peer}: {exc}")
                    continue

                if self.connection_manager.get_connection(message.device_id) is None:
                    self.connection_manager.connections[message.device_id] = Connection(
                        user_id=message.user_id,
                        device_id=message.device_id,
                        reader=reader,
                        writer=writer,
                    )

                print(message.to_dict())

                asyncio.create_task(packet_handler(message, self.connection_manager, self.session_manager))
        finally:
            print(f"client disconnected: {peer}")
            writer.close()
            self.connection_manager.remove_connection(writer)
            await writer.wait_closed()

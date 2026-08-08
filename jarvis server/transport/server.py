import asyncio
import json
from typing import Any

from models import Connection, ConnectionManager, Message, Session
from router.packet_handler import packet_handler


HOST = "0.0.0.0"
PORT = 8765
READ_LIMIT_BYTES = 12 * 1024 * 1024 # Max size. 12 MB


class Server:
    def __init__(self, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        print("jarvis server initialized")

        self.connection_manager = ConnectionManager(connections={})
        print("connection manager initialized")

        self.session = Session()
        print("session initialized")

    async def run(self) -> None:
        try:
            server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port,
                limit=READ_LIMIT_BYTES,
            )
            addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
            print(f"jarvis TCP packet receiver listening on {addresses}")

            async with server:
                await server.serve_forever()
        except Exception as exc:
            print(f"failed to start server: {exc}")
            return

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        print(f"client connected: {peer}")

        try:
            while line := await reader.readline():
                print(f"received line from {peer}: {line}")

                try:
                    data = json.loads(line.decode("utf-8"))
                    message = Message.from_dict(data)
                except Exception as exc:
                    print(f"bad packet from {peer}: {exc}")
                    continue
                print(f"Successfully decoded message from {peer}: {data}")

                if self.connection_manager.get_connection(message.device_id) is None:
                    self.connection_manager.connections[message.device_id] = Connection(
                        device_id=message.device_id,
                        reader=reader,
                        writer=writer,
                    )
                    print(f"new connection registered: {message.device_id}")

                asyncio.create_task(packet_handler(message, self.session, self.connection_manager))
        finally:
            print(f"client disconnected: {peer}")
            writer.close()
            self.connection_manager.remove_connection(writer)
            await writer.wait_closed()

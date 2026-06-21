import asyncio
import base64
import json
import time
import uuid
from typing import Any

from core.types import Message


HOST = "0.0.0.0"
PORT = 8765
READ_LIMIT_BYTES = 64 * 1024 * 1024


def summarize_payload(message: Message) -> str:
    if message.encoding == "wav" and isinstance(message.payload, str):
        try:
            wav = base64.b64decode(message.payload)
            return f"<wav {len(wav)} bytes>"
        except Exception:
            return "<invalid wav base64>"

    if message.encoding == "json":
        return json.dumps(message.payload, ensure_ascii=False)

    return str(message.payload)


async def send_packet(writer: asyncio.StreamWriter, packet: dict[str, Any]) -> None:
    writer.write((json.dumps(packet, ensure_ascii=False) + "\n").encode("utf-8"))
    await writer.drain()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
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

            print(
                f"[{message.type}] user={message.user_id} device={message.device_id} "
                f"encoding={message.encoding} payload={summarize_payload(message)}"
            )

            if message.type == "input":
                await send_packet(
                    writer,
                    {
                        "user_id": message.user_id,
                        "device_id": "jarvis-server",
                        "type": "event",
                        "payload": {
                            "name": "input_received",
                            "request_id": message.request_id,
                        },
                        "encoding": "json",
                        "request_id": uuid.uuid4().hex,
                        "timestamp": int(time.time()),
                    },
                )
    finally:
        print(f"client disconnected: {peer}")
        writer.close()
        await writer.wait_closed()


async def main() -> None:
    server = await asyncio.start_server(handle_client, HOST, PORT, limit=READ_LIMIT_BYTES)
    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"Jarvis TCP packet receiver listening on {addresses}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

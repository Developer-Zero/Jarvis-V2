import time
import uuid

from models import ConnectionManager, Message, Session

from router.input import handle_input
from router.tool_call import handle_tool_call

async def packet_handler(message: Message, session: Session, connection_manager: ConnectionManager) -> None:
    output = await handle_message(message, session, connection_manager)
    if output is not None:
        response = Message(
            device_id=output.get("device_id") or message.device_id,
            type=output.get("type") or message.type,
            payload=output.get("payload"),
            encoding=output.get("encoding"),
            request_id=message.request_id,
            timestamp=int(time.time()),
            metadata=output.get("metadata"),
        )
        print(f"created response for message: {response.to_dict()}")
        await connection_manager.send_packet(response)
    else:
        print(f"no instant response generated for message: {message.request_id}")

async def handle_message(message: Message, session: Session, connection_manager: ConnectionManager) -> dict | None:
    if message.type == "input":
        await handle_input(message, session, connection_manager)
        return None
    elif message.type == "tool_call":
        await handle_tool_call(message, session, connection_manager)
        return None
    elif message.type == "heartbeat":
        print(f"received heartbeat from device {message.device_id}")
        return {"type": "heartbeat"}
    else:
        print(f"unknown message type: {message.type}")
        return {
            "type": "error", 
            "payload": f"Unknown message type: {message.type}", 
            "encoding": "text",
        }

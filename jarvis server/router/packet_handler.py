import time

from models import ConnectionManager, Message, Session, ChatMessage

from input import handle_input

async def packet_handler(message: Message, session: Session, connection_manager: ConnectionManager) -> None:
    output = await handle_message(message, session, connection_manager)
    if output is not None:
        response = Message(
            device_id=output["device_id"] or message.device_id,
            type=output["type"] or message.type,
            payload=output["payload"] or None,
            encoding=output["encoding"] or None,
            request_id=message.request_id,
            timestamp=int(time.time()),
            metadata=output["metadata"] or None,
        )
        print(f"created responsefor message: {response.to_dict()}")
        await connection_manager.send_packet(response)
    else:
        print(f"no response generated for message: {message.request_id}")

async def handle_message(message: Message, session: Session, connection_manager: ConnectionManager) -> dict | None:
    if message.type == "input":
        return await handle_input(message)
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

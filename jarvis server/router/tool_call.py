import asyncio
import time
import uuid

from models import ConnectionManager, Message, Session, ChatMessage, ToolResult

import agent.agent_manager

async def handle_tool_call(message: Message, session: Session, connection_manager: ConnectionManager):
    # append tool result
    try:
        session.messages.append(ChatMessage(role="tool", tool_result=ToolResult.from_dict(message.payload), timestamp=int(time.time())))
    except Exception as exc:
        print(f"error while adding message and parsing tool result: {exc}")

    session.current_tool_call += 1

    if session.current_tool_call < len(session.current_tool_calls):
        print(f"recived tool result, sending next tool call: {session.current_tool_calls[session.current_tool_call].to_dict()}")
        await connection_manager.send_message(Message(
            device_id=message.device_id,
            type="tool_call",
            request_id=uuid.uuid4(),
            timestamp=int(time.time()),
            payload=session.current_tool_calls[session.current_tool_call].to_dict(),
            encoding="json",
        ))
    else:
        print(f"recived tool result, no more tool calls")
        asyncio.create_task(agent.agent_manager.run(session, connection_manager, message.device_id))
            
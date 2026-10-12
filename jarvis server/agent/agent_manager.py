import time, uuid

from models import ConnectionManager, Session, Message, ChatMessage, AgentContext
from agent import agents

agent = agents.OpenAIJarvisDefault()

async def run(session: Session, connection_manager: ConnectionManager, device_id: str):
    # get memory context
    connections = connection_manager.get_connections() or []
    context = AgentContext(
        messages=session.messages,
        semantic_memories=[],
        episodic_memories=[],
        devices={connection.device_id: {} for connection in connections},
        capabilities={connection.device_id: [] for connection in connections},
        final_answer=True,
    )
    print(f"built agent context: {context}")

    response = await agent.run(context)
    print(f"agent response: {response.to_dict()}")
    session.messages.append(response)

    if response.text:
        await connection_manager.send_packet(Message(
            device_id=device_id,
            type="final_answer",
            request_id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            payload=response.text,
            encoding="text",
        ))
    if response.tool_calls:
        session.current_tool_calls = response.tool_calls
        session.current_tool_call = 0
        await connection_manager.send_packet(Message(
            device_id=device_id,
            type="tool_call",
            request_id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            payload=response.tool_calls[0].to_dict(),
            encoding="json",
        ))

    # return tool calls or final answer

    pass

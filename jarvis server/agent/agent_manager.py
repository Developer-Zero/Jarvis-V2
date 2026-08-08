import time

from models import ConnectionManager, Session, Message, ChatMessage, AgentContext
import agents

agent = agents.OpenAIJarvisDefault()

async def run(session: Session, connection_manager: ConnectionManager, input: str, device_id: str) -> Message:
    # Add input
    session.messages.append(ChatMessage(role="user", content=input, timestamp=int(time.time())))
    session.last_activity = int(time.time())
    print(f"updated session")


    # get memory context
    context = AgentContext(
        messages=session.messages,
        current_steps=session.current_steps,
        connections=connection_manager.get_connections(),
        tool_calls=[],
        capabilities=[],
    )
    print(f"built agent context: {context}")

    agent.run(context)

    # return tool calls or final answer

    pass

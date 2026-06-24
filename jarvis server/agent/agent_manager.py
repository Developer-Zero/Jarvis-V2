import time

from models import ConnectionManager, Session, Message, ChatMessage
import agents

agent = agents.OpenAIJarvisDefault()

def run(session: Session, connection_manager: ConnectionManager, input: str) -> Message:
    # Add input
    session.messages.append(ChatMessage(role="user", content=input, timestamp=int(time.time())))
    session.last_activity = int(time.time())


    # get memory context

    agent.run(session, connection_manager, memories={})

    # return tool calls or final answer

    pass

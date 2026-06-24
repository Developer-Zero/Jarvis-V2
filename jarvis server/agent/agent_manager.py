
from models import ConnectionManager, Session
import agents

agent = agents.OpenAIJarvisDefault()

def run(session: Session, connection_manager: ConnectionManager) -> str:
    # get memory context

    agent.run(session, connection_manager)

    # return tool calls or final answer

    pass

from models import Session, ConnectionManager, AgentContext




def agent_context_builder(session: Session, connection_manager: ConnectionManager) -> AgentContext:

    return AgentContext(
        messages=session.messages,
        current_steps=session.current_steps,
        connections=connection_manager.get_connections(session.user_id),
        tool_calls=None,
        capabilities=None
    )
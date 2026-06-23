from abc import ABC, abstractmethod

from agent.agents.agent import Agent
from models import Session, ConnectionManager

class OpenAISummaryAgent(Agent):
    async def run(self, session: Session, connection_manager: ConnectionManager, memories: dict):
        pass

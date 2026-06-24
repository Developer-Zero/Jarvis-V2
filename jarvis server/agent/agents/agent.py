from abc import ABC, abstractmethod

from models import Session, ConnectionManager, ChatMessage, AgentContext

class Agent(ABC):
    @abstractmethod
    async def run(self, context: AgentContext) -> ChatMessage:
        pass

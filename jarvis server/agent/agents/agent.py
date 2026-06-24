from abc import ABC, abstractmethod

from models import Session, ConnectionManager

class Agent(ABC):
    @abstractmethod
    async def run(self, session: Session, connection_manager: ConnectionManager, memories: dict) -> str:
        pass

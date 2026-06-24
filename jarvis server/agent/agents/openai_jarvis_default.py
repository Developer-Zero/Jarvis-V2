from abc import ABC, abstractmethod

from agent.agents.agent import Agent
from models import Session, ConnectionManager, ChatMessage, AgentContext

class OpenAIJarvisDefault(Agent):
    async def run(self, context: AgentContext) -> ChatMessage:
        pass

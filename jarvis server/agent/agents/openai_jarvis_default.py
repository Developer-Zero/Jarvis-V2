from abc import ABC, abstractmethod
import time

from agent.agents.agent import Agent
from models import ChatMessage, AgentContext

class OpenAIJarvisDefault(Agent):
    async def run(self, context: AgentContext) -> ChatMessage:
        return ChatMessage(role="assistant", text="Hello World", timestamp=time.time())

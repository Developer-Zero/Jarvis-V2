from abc import ABC, abstractmethod

from agent.agents.agent import Agent
from models import ChatMessage, AgentContext

class OpenAISummaryAgent(Agent):
    async def run(self, context: AgentContext) -> ChatMessage:
        pass

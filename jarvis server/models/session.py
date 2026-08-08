from dataclasses import dataclass
import time
import asyncio

from models import ChatMessage, ToolCall



@dataclass
class Session:
    messages: list[ChatMessage]

    last_activity: int
    active: bool
    
    current_steps: int
    current_tool_calls: list[ToolCall] | None = None

    async def session_canceller(self):
        while self.active:
            await asyncio.sleep(60)

            if int(time.time()) - self.last_activity > 5 * 60 * 60:
                self.active = False
                self.reset()

    def reset(self):
        self.messages = []
        self.last_activity = 0
        self.current_steps = 0
        self.current_tool_calls = []



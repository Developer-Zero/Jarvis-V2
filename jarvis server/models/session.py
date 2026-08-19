from dataclasses import dataclass
import time
import asyncio

from models import ChatMessage, ToolCall, ToolResult



@dataclass
class Session:
    messages: list[ChatMessage] = []

    last_activity: int = 0
    active: bool = False
    
    current_steps: int = 0

    current_tool_call: int = 0
    tool_call_requests: list[ToolCall] | None = None

    def __post_init__(self):
        self.last_activity = int(time.time())
        asyncio.create_task(self.session_canceller())

    async def session_canceller(self):
        while True:
            await asyncio.sleep(60)

            if self.active:
                if int(time.time()) - self.last_activity > 5 * 60 * 60:
                    self.active = False
                    self.reset()
            else:
                if int(time.time()) - self.last_activity < 5 * 60 * 60:
                    self.active = True

    def reset(self):
        self.messages = []
        self.last_activity = 0
        self.current_steps = 0
        self.current_tool_call = 0
        self.tool_call_requests = None
        self.tool_call_responses = None



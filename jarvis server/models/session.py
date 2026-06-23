from dataclasses import dataclass
import time



@dataclass
class Session:
    user_id: str
    messages: list[str]
    last_activity: int
    
    current_steps: int
    current_tool_calls: list[dict] | None = None


@dataclass
class SessionManager:
    sessions: dict[str, Session]

    def get_session(self, user_id: str) -> Session | None:
        if user_id in self.sessions:
            return self.sessions.get(user_id)
        else:
            session = Session(user_id=user_id, messages=[], current_steps=0, last_activity=int(time.time()))
            self.sessions[user_id] = session
            return session

    def remove_session(self, user_id: str) -> None:
        if user_id in self.sessions:
            del self.sessions[user_id]





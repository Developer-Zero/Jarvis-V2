from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Message:
    user_id: str
    device_id: str
    type: str # input, transcription, tool_call, final_answer, event, heartbeat, error
    request_id: str
    timestamp: int
    payload: Any = None
    encoding: str = "text" # text, wav, json

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "device_id": self.device_id,
            "type": self.type,
            "payload": self.payload,
            "encoding": self.encoding,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            user_id=data["user_id"],
            device_id=data["device_id"],
            type=data["type"],
            request_id=data["request_id"],
            timestamp=data["timestamp"],
            payload=data.get("payload"),
            encoding=data.get("encoding", "text"),
        )

    

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

    def __post_init__(self) -> None:
        if not isinstance(self.user_id, str):
            raise TypeError("user_id must be a string")
        if not isinstance(self.device_id, str):
            raise TypeError("device_id must be a string")
        if not isinstance(self.type, str):
            raise TypeError("type must be a string")
        if not isinstance(self.encoding, str):
            raise TypeError("encoding must be a string")
        if not isinstance(self.request_id, str):
            raise TypeError("request_id must be a string")
        if not isinstance(self.timestamp, int):
            raise TypeError("timestamp must be an integer")

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

    

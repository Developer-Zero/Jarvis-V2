from dataclasses import dataclass
from typing import Any, Dict, Literal


@dataclass
class Message:
    user_id: str
    device_id: str
    type: Literal["input", "transcription", "tool_call", "tool_result", "final_answer", "event", "heartbeat"]
    payload: Any
    encoding: str
    request_id: str
    timestamp: int

    def __post_init__(self) -> None:
        if not isinstance(self.user_id, str):
            raise TypeError("user_id must be a string")
        if not isinstance(self.device_id, str):
            raise TypeError("device_id must be a string")
        if not isinstance(self.type, str):
            raise TypeError("type must be a type")
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
            payload=data.get("payload"),
            encoding=data["encoding"],
            request_id=data["request_id"],
            timestamp=data["timestamp"],
        )

    
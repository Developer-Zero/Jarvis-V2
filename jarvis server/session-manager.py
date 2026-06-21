from dataclasses import dataclass
from typing import Any, Dict, Literal

from core.types import Message
import core.decoder

@dataclass
class Session:
    user_id: str
    messages: list


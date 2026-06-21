# Decodes payload and handles STT

from core.types import Message
from speech.stt import transcribe_wav


async def decode(message: Message) -> str:
    encoding = message.encoding.lower()

    if encoding == "utf-8":
        if isinstance(message.payload, str):
            return message.payload
        return message.payload.decode("utf-8")

    if encoding == "wav":
        return await transcribe_wav(message.payload)

    raise ValueError(f"Unsupported message encoding: {message.encoding}")

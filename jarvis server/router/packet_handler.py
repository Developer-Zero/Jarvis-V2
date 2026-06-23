import base64
import time

from models import ConnectionManager, Message, SessionManager
from speech.stt.openai_stt_agent import OpenAISTTAgent

stt_agent: OpenAISTTAgent | None = None # What agent to use for transcription


def get_stt_agent() -> OpenAISTTAgent:
    global stt_agent
    if stt_agent is None:
        stt_agent = OpenAISTTAgent()
    return stt_agent

async def packet_handler(message: Message, connection_manager: ConnectionManager, session_manager: SessionManager) -> None:
    output = await handle_message(message, connection_manager, session_manager)
    if output is not None:
        await connection_manager.send_packet(message.device_id, output)

async def handle_message(message: Message, connection_manager: ConnectionManager, session_manager: SessionManager) -> Message | None:
    if message.type == "input":
        if message.encoding in ("text", "utf-8"):
            input_text = message.payload
        elif message.encoding == "wav":
            try:
                wav = base64.b64decode(message.payload)
            except Exception as exc:
                return Message(
                    user_id=message.user_id,
                    device_id=message.device_id,
                    type="error",
                    payload=f"Failed to decode base64 WAV: {exc}",
                    encoding="text",
                    request_id=message.request_id,
                    timestamp=int(time.time())
                )
            input_text = await get_stt_agent().transcribe_wav(wav)
        else:
            return Message(
                user_id=message.user_id,
                device_id=message.device_id,
                type="error",
                payload=f"Unsupported input encoding: {message.encoding}",
                encoding="text",
                request_id=message.request_id,
                timestamp=int(time.time())
            )

        session = session_manager.get_session(message.user_id)
        session.messages.append(input_text)
        session.last_activity = int(time.time())
        # call agent with return tool calls
    elif message.type == "heartbeat":
        return Message(
            user_id=message.user_id,
            device_id=message.device_id,
            type="heartbeat",
            encoding="text",
            request_id=message.request_id,
            timestamp=int(time.time())
        )
    else:
        return Message(
            user_id=message.user_id,
            device_id=message.device_id,
            type="error",
            payload=f"Unknown message type: {message.type}",
            encoding="text",
            request_id=message.request_id,
            timestamp=int(time.time())
        )

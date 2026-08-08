import base64
import time
import asyncio

from models import Session, ConnectionManager, Message
from speech.stt.openai_stt_agent import OpenAISTTAgent
import agent.agent_manager

stt_agent: OpenAISTTAgent

async def handle_input(message: Message, session: Session, connection_manager: ConnectionManager) -> dict:
    if message.encoding in ("text", "utf-8"):
        input_text = message.payload
        print(f"decoded text input: {input_text}")
    elif message.encoding == "wav":
        try:
            wav = base64.b64decode(message.payload)
            print(f"decoded WAV input: {len(wav)} bytes")
        except Exception as exc:
            print(f"failed to decode base64 WAV: {exc}")
            return {
                "type": "error", 
                "payload": f"Failed to decode base64 WAV: {exc}", 
                "encoding": "text",
            }
        input_text = await stt_agent.transcribe_wav(wav)
        print(f"transcribed WAV input to text: {input_text}")
    else:
        print(f"unsupported input encoding: {message.encoding}")
        return {
            "type": "error", 
            "payload": f"Unsupported input encoding: {message.encoding}", 
            "encoding": "text",
        }
    asyncio.create_task(agent.agent_manager.run(session, connection_manager, input_text, message.device_id))
    return {"type": "input"}
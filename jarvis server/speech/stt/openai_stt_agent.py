from io import BytesIO
from openai import AsyncOpenAI

from speech.stt.stt import STTAgent


class OpenAISTTAgent(STTAgent):
    def __init__(self):
        self.model = "gpt-4o-mini-transcribe"
        self.client = AsyncOpenAI()

    async def transcribe_wav(self, wav: bytes) -> str:

        audio_file = BytesIO(wav)
        audio_file.name = "audio.wav"

        try:
            transcript = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
            )
            return transcript.text
        finally:
            audio_file.close()

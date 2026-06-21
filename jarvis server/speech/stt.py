from io import BytesIO

DEFAULT_STT_MODEL = "gpt-4o-mini-transcribe"


async def transcribe_wav(wav: bytes) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI()

    audio_file = BytesIO(bytes(wav))
    audio_file.name = "audio.wav"

    try:
        transcript = await client.audio.transcriptions.create(
            model=DEFAULT_STT_MODEL,
            file=audio_file,
        )
        return transcript.text
    finally:
        audio_file.close()

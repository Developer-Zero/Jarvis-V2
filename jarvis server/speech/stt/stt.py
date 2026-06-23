from abc import ABC, abstractmethod

class STTAgent(ABC):
    @abstractmethod
    async def transcribe_wav(self, wav: bytes) -> str:
        pass
    async def transcribe_mp3(self, mp3: bytes) -> str: # Optional: Not used by default
        pass
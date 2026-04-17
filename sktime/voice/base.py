"""Base classes for voice integration module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class VoiceService(ABC):
    """Abstract base class for voice services."""

    def __init__(self, api_key: Optional[str] = None, language: str = "hi"):
        """Initialize voice service.

        Parameters
        ----------
        api_key : str, optional
            API key for the voice service
        language : str, default="hi"
            Language code (hi, kn, pa, te, en)
        """
        self.api_key = api_key
        self.language = language

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Process voice input.

        Returns
        -------
        dict
            Processing result
        """
        pass


class ASRServiceBase(VoiceService):
    """Base class for Automatic Speech Recognition services."""

    @abstractmethod
    async def transcribe(
        self, audio_base64: str, language: Optional[str] = None
    ) -> str:
        """Transcribe audio to text.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio data
        language : str, optional
            Language code for transcription

        Returns
        -------
        str
            Transcribed text
        """
        pass


class TTSServiceBase(VoiceService):
    """Base class for Text-to-Speech services."""

    @abstractmethod
    async def synthesize(self, text: str, language: Optional[str] = None) -> bytes:
        """Synthesize text to audio.

        Parameters
        ----------
        text : str
            Text to synthesize
        language : str, optional
            Language code for synthesis

        Returns
        -------
        bytes
            Audio bytes (MP3 or WAV)
        """
        pass


class EntityExtractorBase(ABC):
    """Base class for entity extractors."""

    def __init__(self, language: str = "hi"):
        """Initialize entity extractor.

        Parameters
        ----------
        language : str, default="hi"
            Language for entity extraction
        """
        self.language = language

    @abstractmethod
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities from text.

        Parameters
        ----------
        text : str
            Input text

        Returns
        -------
        dict
            Extracted entities with confidence scores
        """
        pass


class IntentMapperBase(ABC):
    """Base class for intent mapping."""

    @abstractmethod
    def map_intent(self, text: str) -> Dict[str, Any]:
        """Map text to intent and operation.

        Parameters
        ----------
        text : str
            Input text

        Returns
        -------
        dict
            Intent mapping with operation details
        """
        pass


class ResponseFormatterBase(ABC):
    """Base class for response formatting."""

    def __init__(self, language: str = "hi"):
        """Initialize response formatter.

        Parameters
        ----------
        language : str, default="hi"
            Language for response formatting
        """
        self.language = language

    @abstractmethod
    def format_response(self, result: Dict[str, Any]) -> str:
        """Format result for voice response.

        Parameters
        ----------
        result : dict
            Sktime result or analysis output

        Returns
        -------
        str
            Formatted response text in target language
        """
        pass

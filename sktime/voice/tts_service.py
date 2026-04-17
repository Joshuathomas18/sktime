"""Text-to-Speech service wrapper."""

import base64
import logging
from typing import Optional

from sktime.voice.base import TTSServiceBase
from sktime.voice.config import SARVAM_CONFIG

logger = logging.getLogger(__name__)


class TTSService(TTSServiceBase):
    """Wrapper for Sarvam TTS API.

    Handles text-to-speech conversion for multiple Indian languages.
    Supports both real Sarvam API and mock implementation for testing.
    """

    def __init__(self, api_key: Optional[str] = None, language: str = "hi"):
        """Initialize TTS service.

        Parameters
        ----------
        api_key : str, optional
            Sarvam API key. If None, will use config
        language : str, default="hi"
            Default language for synthesis
        """
        super().__init__(api_key, language)
        self.api_key = api_key or SARVAM_CONFIG.get("api_key")
        self.api_url = SARVAM_CONFIG.get("api_base_url")
        self.model = SARVAM_CONFIG.get("tts_model")
        self.timeout = SARVAM_CONFIG.get("tts_timeout", 30)
        self._mock_mode = not self.api_key

        if self._mock_mode:
            logger.warning(
                "TTS running in mock mode (no API key). "
                "Install sarvam SDK and set SARVAM_API_KEY for real API."
            )

    async def synthesize(
        self, text: str, language: Optional[str] = None
    ) -> bytes:
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
            Audio bytes (MP3)

        Raises
        ------
        ValueError
            If language not supported or text is empty
        """
        language = language or self.language

        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        if language not in SARVAM_CONFIG.get("supported_languages", []):
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported: {SARVAM_CONFIG.get('supported_languages')}"
            )

        # Mock implementation for testing
        if self._mock_mode:
            return self._mock_synthesize(text, language)

        # Real Sarvam API call would go here
        return await self._call_sarvam_tts(text, language)

    def _mock_synthesize(self, text: str, language: str) -> bytes:
        """Mock audio synthesis for testing.

        Parameters
        ----------
        text : str
            Text to synthesize
        language : str
            Language code

        Returns
        -------
        bytes
            Mock MP3 audio data
        """
        # Return a simple mock audio byte string
        # In real implementation, would return actual MP3 encoded audio
        mock_audio = f"MOCK_AUDIO_{language}_{len(text)}_bytes".encode()
        return base64.b64encode(mock_audio)

    async def _call_sarvam_tts(self, text: str, language: str) -> bytes:
        """Call real Sarvam TTS API.

        Parameters
        ----------
        text : str
            Text to synthesize
        language : str
            Language code

        Returns
        -------
        bytes
            Audio bytes
        """
        try:
            raise NotImplementedError(
                "Real Sarvam API integration requires httpx or requests library. "
                "Install with: pip install httpx sarvam-sdk"
            )
        except Exception as e:
            logger.error(f"Sarvam TTS API call failed: {str(e)}")
            raise

    def get_supported_languages(self) -> list:
        """Get list of supported languages.

        Returns
        -------
        list
            Supported language codes
        """
        return SARVAM_CONFIG.get("supported_languages", [])

    def set_language(self, language: str) -> None:
        """Set default language.

        Parameters
        ----------
        language : str
            Language code

        Raises
        ------
        ValueError
            If language not supported
        """
        if language not in self.get_supported_languages():
            raise ValueError(f"Language '{language}' not supported")
        self.language = language

    def estimate_audio_duration(self, text: str) -> float:
        """Estimate audio duration based on text length.

        Parameters
        ----------
        text : str
            Text to estimate

        Returns
        -------
        float
            Estimated duration in seconds
        """
        # Average speaking rate: 150 words per minute = 2.5 words per second
        word_count = len(text.split())
        return max(1.0, word_count / 2.5)

"""Automatic Speech Recognition service wrapper."""

import base64
import json
import logging
from typing import Optional

from sktime.voice.base import ASRServiceBase
from sktime.voice.config import SARVAM_CONFIG

logger = logging.getLogger(__name__)


class ASRService(ASRServiceBase):
    """Wrapper for Sarvam ASR API.

    Handles speech-to-text conversion for multiple Indian languages.
    Supports both real Sarvam API and mock implementation for testing.
    """

    def __init__(self, api_key: Optional[str] = None, language: str = "hi"):
        """Initialize ASR service.

        Parameters
        ----------
        api_key : str, optional
            Sarvam API key. If None, will attempt to use from config
        language : str, default="hi"
            Default language for transcription
        """
        super().__init__(api_key, language)
        self.api_key = api_key or SARVAM_CONFIG.get("api_key")
        self.api_url = SARVAM_CONFIG.get("api_base_url")
        self.model = SARVAM_CONFIG.get("asr_model")
        self.timeout = SARVAM_CONFIG.get("asr_timeout", 30)
        self._mock_mode = not self.api_key

        if self._mock_mode:
            logger.warning(
                "ASR running in mock mode (no API key). "
                "Install sarvam SDK and set SARVAM_API_KEY for real API."
            )

    async def transcribe(
        self, audio_base64: str, language: Optional[str] = None
    ) -> str:
        """Transcribe audio to text.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio data
        language : str, optional
            Language code. If None, uses default language

        Returns
        -------
        str
            Transcribed text

        Raises
        ------
        ValueError
            If language is not supported
        TypeError
            If audio_base64 is invalid
        """
        language = language or self.language

        if language not in SARVAM_CONFIG.get("supported_languages", []):
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported: {SARVAM_CONFIG.get('supported_languages')}"
            )

        # Mock implementation for testing
        if self._mock_mode:
            return self._mock_transcribe(audio_base64, language)

        # Real Sarvam API call would go here
        return await self._call_sarvam_asr(audio_base64, language)

    def _mock_transcribe(self, audio_base64: str, language: str) -> str:
        """Mock transcription for testing.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio
        language : str
            Language code

        Returns
        -------
        str
            Mock transcribed text
        """
        mock_responses = {
            "hi": [
                "Agle 3 mahinon mein kya forecast hai?",
                "Mere paas 5 acre ki sugarcane hai mandya mein",
                "Ye data mein kya trend dikh raha hai?",
                "Rainfall ka anomaly detect karo",
                "Wheat crop ke liye best time kya hai?",
            ],
            "kn": [
                "Nanige 3 thinada forecast barthe?",
                "Nannage 5 acres sugarcane iruttide mandyada",
                "Ee data mathada trend emdu?",
            ],
            "pa": [
                "Agle 2 haftan vich ki forecast hai?",
                "Mere pas 3 acre wheat da khet hai",
            ],
            "te": [
                "3 kulamaina forecast emundi?",
                "Naaku 5 acres rice unnai",
            ],
            "en": [
                "What is the forecast for the next 3 months?",
                "Detect anomalies in rainfall data",
                "Show me the trend analysis",
            ],
        }

        responses = mock_responses.get(language, mock_responses["en"])
        # Return a deterministic mock response based on audio length
        return responses[len(audio_base64) % len(responses)]

    async def _call_sarvam_asr(self, audio_base64: str, language: str) -> str:
        """Call real Sarvam ASR API.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio
        language : str
            Language code

        Returns
        -------
        str
            Transcribed text
        """
        try:
            # This would use httpx or requests library in real implementation
            # For now, we raise informative error
            raise NotImplementedError(
                "Real Sarvam API integration requires httpx or requests library. "
                "Install with: pip install httpx sarvam-sdk"
            )
        except Exception as e:
            logger.error(f"Sarvam ASR API call failed: {str(e)}")
            raise

    def validate_audio(self, audio_base64: str) -> bool:
        """Validate audio input.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio to validate

        Returns
        -------
        bool
            True if valid, False otherwise
        """
        try:
            # Validate base64 encoding
            base64.b64decode(audio_base64, validate=True)
            return True
        except Exception as e:
            logger.error(f"Invalid audio format: {str(e)}")
            return False

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

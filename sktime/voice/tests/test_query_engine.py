"""Tests for voice query engine."""

import pytest
import asyncio
from sktime.voice import VoiceQueryEngine


class TestVoiceQueryEngine:
    """Test voice query engine."""

    def setup_method(self):
        """Setup test fixtures."""
        self.engine = VoiceQueryEngine(language="hi", enable_tts=False)

    @pytest.mark.asyncio
    async def test_process_voice_query_hindi(self):
        """Test processing Hindi voice query."""
        audio_base64 = "bW9ja19hdWRpb19kYXRh"  # base64 of "mock_audio_data"

        result = await self.engine.process_voice_query(audio_base64)

        assert result["success"] is True
        assert result["transcribed_text"] is not None
        assert result["entities"] is not None
        assert result["intent"] is not None
        assert result["response_text"] is not None

    def test_set_language(self):
        """Test setting language."""
        engine = VoiceQueryEngine(language="en")
        assert engine.language == "en"

        engine.set_language("hi")
        assert engine.language == "hi"

    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.engine.get_supported_languages()

        assert "hi" in languages
        assert "en" in languages
        assert "kn" in languages

    def test_get_supported_intents(self):
        """Test getting supported intents."""
        intents = self.engine.get_supported_intents()

        assert "forecast" in intents
        assert "classify" in intents
        assert "anomaly_detect" in intents

    def test_validate_audio(self):
        """Test audio validation."""
        valid_audio = "bW9ja19hdWRpb19kYXRh"  # valid base64
        invalid_audio = "!!!invalid!!!"

        assert self.engine.validate_audio(valid_audio) is True
        assert self.engine.validate_audio(invalid_audio) is False

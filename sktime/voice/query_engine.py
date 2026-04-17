"""Main voice query orchestration engine."""

import logging
from typing import Any, Dict, Optional

from sktime.voice.asr_service import ASRService
from sktime.voice.entity_extractor import EntityExtractor
from sktime.voice.intent_mapper import IntentMapper
from sktime.voice.response_formatter import ResponseFormatter
from sktime.voice.tts_service import TTSService

logger = logging.getLogger(__name__)


class VoiceQueryEngine:
    """Main orchestrator for voice-based time series queries.

    Coordinates:
    1. Speech-to-text (ASRService)
    2. Entity extraction (EntityExtractor)
    3. Intent mapping (IntentMapper)
    4. Operation execution (sktime estimators)
    5. Response formatting (ResponseFormatter)
    6. Text-to-speech (TTSService)
    """

    def __init__(
        self,
        language: str = "hi",
        api_key: Optional[str] = None,
        enable_tts: bool = True,
    ):
        """Initialize voice query engine.

        Parameters
        ----------
        language : str, default="hi"
            Default language for all components
        api_key : str, optional
            Sarvam API key for real Sarvam integration
        enable_tts : bool, default=True
            Whether to enable text-to-speech responses
        """
        self.language = language
        self.api_key = api_key
        self.enable_tts = enable_tts

        # Initialize components
        self.asr = ASRService(api_key=api_key, language=language)
        self.extractor = EntityExtractor(language=language)
        self.intent_mapper = IntentMapper()
        self.formatter = ResponseFormatter(language=language)
        self.tts = TTSService(api_key=api_key, language=language) if enable_tts else None

        logger.info(
            f"VoiceQueryEngine initialized (language={language}, tts={'enabled' if enable_tts else 'disabled'})"
        )

    async def process_voice_query(
        self, audio_base64: str, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process complete voice query pipeline.

        Pipeline:
        1. Transcribe audio → text (ASR)
        2. Extract entities from text
        3. Map intent to sktime operation
        4. Execute operation (delegated to caller)
        5. Format result for voice response
        6. Synthesize response → audio (TTS)

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio data
        language : str, optional
            Language for this query (overrides default)

        Returns
        -------
        dict
            Complete query result:
            {
                "transcribed_text": str,
                "entities": dict,
                "intent": dict,
                "response_text": str,
                "response_audio_base64": str or None,
                "confidence": float,
                "success": bool,
                "error": str or None
            }
        """
        language = language or self.language
        result = {
            "transcribed_text": None,
            "entities": None,
            "intent": None,
            "response_text": None,
            "response_audio_base64": None,
            "confidence": 0.0,
            "success": False,
            "error": None,
        }

        try:
            # Step 1: Transcribe audio
            logger.info("Step 1: Transcribing audio...")
            transcribed_text = await self.asr.transcribe(audio_base64, language)
            result["transcribed_text"] = transcribed_text
            logger.info(f"Transcribed: {transcribed_text}")

            # Step 2: Extract entities
            logger.info("Step 2: Extracting entities...")
            entities = self.extractor.extract(transcribed_text)
            result["entities"] = entities
            logger.info(f"Entities extracted: {entities}")

            # Step 3: Map intent
            logger.info("Step 3: Mapping intent...")
            intent = self.intent_mapper.map_intent(entities)
            result["intent"] = intent
            logger.info(f"Intent mapped: {intent}")

            # Step 4: Execute operation
            # NOTE: Actual execution delegated to caller or higher-level orchestrator
            logger.info("Step 4: Ready for operation execution...")

            # Step 5: Format response
            logger.info("Step 5: Formatting response...")
            response_text = self._generate_response_text(
                transcribed_text, entities, intent, language
            )
            result["response_text"] = response_text
            logger.info(f"Response: {response_text}")

            # Step 6: Synthesize audio response (optional)
            if self.enable_tts and self.tts:
                logger.info("Step 6: Synthesizing audio response...")
                try:
                    response_audio = await self.tts.synthesize(response_text, language)
                    result["response_audio_base64"] = response_audio.decode()
                except Exception as e:
                    logger.warning(f"TTS synthesis failed: {str(e)}")
                    result["response_audio_base64"] = None

            result["confidence"] = entities.get("confidence", 0.0)
            result["success"] = True

        except Exception as e:
            logger.error(f"Error processing voice query: {str(e)}")
            result["error"] = str(e)
            result["response_text"] = self.formatter.format_error(str(e), language)
            result["success"] = False

        return result

    def _generate_response_text(
        self,
        transcribed_text: str,
        entities: Dict[str, Any],
        intent: Dict[str, Any],
        language: str,
    ) -> str:
        """Generate response text based on entities and intent.

        Parameters
        ----------
        transcribed_text : str
            Original transcribed text
        entities : dict
            Extracted entities
        intent : dict
            Mapped intent
        language : str
            Response language

        Returns
        -------
        str
            Response text
        """
        analysis_type = intent.get("intent", "forecast")
        ts_name = entities.get("time_series_name", "data")
        confidence = entities.get("confidence", 0.0)

        if language == "hi":
            if analysis_type == "forecast":
                response = f"Aapke {ts_name} ka forecast {intent.get('estimator')} "
                response += f"model se calculate karenge. "
                if confidence > 0.8:
                    response += "Humko kaafi sure lagta hai."
                elif confidence > 0.5:
                    response += "Yeh estimate thoda unsure hai."
                else:
                    response += "Zyada jankari ke liye aur data do."
            elif analysis_type == "anomaly_detect":
                response = f"{ts_name} mein anomalies detect kar rahe hain..."
            elif analysis_type == "classify":
                response = f"{ts_name} ko classify kar rahe hain..."
            else:
                response = f"Aapke {ts_name} ka analysis kar rahe hain..."

        else:
            if analysis_type == "forecast":
                response = f"Forecasting {ts_name} using {intent.get('estimator')}. "
                if confidence > 0.8:
                    response += "Confidence is high."
                elif confidence > 0.5:
                    response += "Confidence is moderate."
                else:
                    response += "More data would help improve accuracy."
            elif analysis_type == "anomaly_detect":
                response = f"Detecting anomalies in {ts_name}..."
            elif analysis_type == "classify":
                response = f"Classifying {ts_name}..."
            else:
                response = f"Analyzing {ts_name}..."

        return response

    def set_language(self, language: str) -> None:
        """Set default language for all components.

        Parameters
        ----------
        language : str
            Language code (hi, kn, pa, te, en)
        """
        self.language = language
        self.asr.set_language(language)
        self.extractor.language = language
        self.formatter.language = language
        if self.tts:
            self.tts.set_language(language)
        logger.info(f"Language set to {language}")

    def get_supported_languages(self) -> list:
        """Get list of supported languages.

        Returns
        -------
        list
            Supported language codes
        """
        return self.asr.get_supported_languages()

    def get_supported_intents(self) -> list:
        """Get list of supported analysis intents.

        Returns
        -------
        list
            Supported intent types
        """
        return self.intent_mapper.get_supported_intents()

    def validate_audio(self, audio_base64: str) -> bool:
        """Validate audio input.

        Parameters
        ----------
        audio_base64 : str
            Base64-encoded audio

        Returns
        -------
        bool
            True if valid
        """
        return self.asr.validate_audio(audio_base64)

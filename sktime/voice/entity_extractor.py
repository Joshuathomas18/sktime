"""Entity extraction from voice queries."""

import logging
import re
from typing import Any, Dict, Optional, Tuple

from sktime.voice.base import EntityExtractorBase
from sktime.voice.config import ENTITY_CONFIG, LANGUAGE_SETTINGS

logger = logging.getLogger(__name__)


class EntityExtractor(EntityExtractorBase):
    """Extract structured entities from voice queries.

    Parses natural language text to extract:
    - Time series name (temperature, rainfall, price, etc.)
    - Analysis operation (forecast, classify, anomaly_detect)
    - Time horizon (next_week, next_month, etc.)
    - Confidence level
    - Additional parameters (crop type, location, etc.)
    """

    def __init__(self, language: str = "hi"):
        """Initialize entity extractor.

        Parameters
        ----------
        language : str, default="hi"
            Language for extraction
        """
        super().__init__(language)
        self.language_config = LANGUAGE_SETTINGS.get(language, LANGUAGE_SETTINGS["en"])

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities from text.

        Parameters
        ----------
        text : str
            Input text from voice transcription

        Returns
        -------
        dict
            Extracted entities with structure:
            {
                "time_series_name": str,
                "analysis_type": str,
                "time_horizon": int,  # days
                "confidence": float,
                "crop_type": str (optional),
                "location": str (optional),
                "practices": list (optional),
            }
        """
        if not text:
            return self._empty_result()

        # Language-specific extraction
        if self.language == "hi":
            return self._extract_hindi(text)
        elif self.language == "kn":
            return self._extract_kannada(text)
        elif self.language in ["pa", "te"]:
            return self._extract_generic(text)
        else:
            return self._extract_english(text)

    def _extract_hindi(self, text: str) -> Dict[str, Any]:
        """Extract entities from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        dict
            Extracted entities
        """
        text_lower = text.lower()
        result = self._empty_result()

        # Extract time horizon
        result["time_horizon"] = self._extract_time_horizon_hindi(text_lower)

        # Extract time series name
        ts_name, ts_confidence = self._extract_time_series_hindi(text_lower)
        result["time_series_name"] = ts_name
        result["confidence"] = ts_confidence

        # Extract analysis type
        analysis_type, analysis_confidence = self._extract_analysis_type_hindi(
            text_lower
        )
        result["analysis_type"] = analysis_type
        result["confidence"] = min(result["confidence"], analysis_confidence)

        # Extract crop type if mentioned
        crop, crop_conf = self._extract_crop_hindi(text_lower)
        if crop:
            result["crop_type"] = crop

        # Extract location if mentioned
        location = self._extract_location_hindi(text_lower)
        if location:
            result["location"] = location

        return result

    def _extract_english(self, text: str) -> Dict[str, Any]:
        """Extract entities from English text.

        Parameters
        ----------
        text : str
            English text

        Returns
        -------
        dict
            Extracted entities
        """
        text_lower = text.lower()
        result = self._empty_result()

        # Extract time series name
        for ts_name in ENTITY_CONFIG["supported_time_series"]:
            if ts_name in text_lower:
                result["time_series_name"] = ts_name
                result["confidence"] = 0.8
                break

        # Extract analysis type
        for op in ENTITY_CONFIG["supported_operations"]:
            if op in text_lower or op.replace("_", " ") in text_lower:
                result["analysis_type"] = op
                result["confidence"] = min(result["confidence"], 0.75)
                break

        # Extract time horizon
        if "next week" in text_lower or "next 7 days" in text_lower:
            result["time_horizon"] = 7
        elif "next month" in text_lower or "next 30 days" in text_lower:
            result["time_horizon"] = 30
        elif "next 3 months" in text_lower or "next quarter" in text_lower:
            result["time_horizon"] = 90
        elif "next year" in text_lower or "next 12 months" in text_lower:
            result["time_horizon"] = 365

        return result

    def _extract_kannada(self, text: str) -> Dict[str, Any]:
        """Extract entities from Kannada text.

        Parameters
        ----------
        text : str
            Kannada text

        Returns
        -------
        dict
            Extracted entities
        """
        # Fallback to generic extraction for now
        # Full Kannada NLP would require additional dependencies
        return self._extract_generic(text)

    def _extract_generic(self, text: str) -> Dict[str, Any]:
        """Generic entity extraction fallback.

        Parameters
        ----------
        text : str
            Input text

        Returns
        -------
        dict
            Extracted entities
        """
        result = self._empty_result()
        text_lower = text.lower()

        # Try to find time series name
        for ts in ENTITY_CONFIG["supported_time_series"]:
            if ts in text_lower:
                result["time_series_name"] = ts
                break

        # Try to find analysis type
        for op in ENTITY_CONFIG["supported_operations"]:
            if op in text_lower:
                result["analysis_type"] = op
                break

        return result

    def _extract_time_horizon_hindi(self, text: str) -> int:
        """Extract time horizon from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        int
            Number of days in forecast horizon
        """
        # Pattern: number + time unit
        number_words = self.language_config.get("number_words", {})
        time_units = self.language_config.get("time_units", {})

        # Try regex patterns first
        if re.search(r"(\d+)\s*(din|hafta|mahina|saal)", text):
            match = re.search(r"(\d+)\s*(din|hafta|mahina|saal)", text)
            if match:
                num = int(match.group(1))
                unit = match.group(2)
                if unit == "din":
                    return num
                elif unit == "hafta":
                    return num * 7
                elif unit == "mahina":
                    return num * 30
                elif unit == "saal":
                    return num * 365

        # Default 30 days if not specified
        return 30

    def _extract_time_series_hindi(
        self, text: str
    ) -> Tuple[Optional[str], float]:
        """Extract time series name from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        tuple
            (time_series_name, confidence)
        """
        hindi_ts_map = {
            "temperature": ["temperature", "taapman", "garam"],
            "rainfall": ["rainfall", "varsa", "barish", "pani"],
            "price": ["price", "dam", "kimat"],
            "crop": ["crop", "fasal"],
            "humidity": ["humidity", "nammi"],
        }

        for ts_name, keywords in hindi_ts_map.items():
            for keyword in keywords:
                if keyword in text:
                    return ts_name, 0.85

        return None, 0.0

    def _extract_analysis_type_hindi(
        self, text: str
    ) -> Tuple[Optional[str], float]:
        """Extract analysis type from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        tuple
            (analysis_type, confidence)
        """
        hindi_op_map = {
            "forecast": [
                "forecast",
                "prediction",
                "anumar",
                "ayenge",
                "hoga",
                "predict",
            ],
            "anomaly_detect": ["anomaly", "unusual", "anormal", "unusual"],
            "trend_analysis": ["trend", "pravarti", "pattern"],
            "classify": ["classify", "type", "category"],
        }

        for op_name, keywords in hindi_op_map.items():
            for keyword in keywords:
                if keyword in text:
                    return op_name, 0.8

        # Default to forecast
        return "forecast", 0.5

    def _extract_crop_hindi(self, text: str) -> Tuple[Optional[str], float]:
        """Extract crop type from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        tuple
            (crop_name, confidence)
        """
        hindi_crop_map = {
            "wheat": ["wheat", "gehu"],
            "rice": ["rice", "chawal", "dhan"],
            "sugarcane": ["sugarcane", "ganna"],
            "cotton": ["cotton", "kapas"],
            "paddy": ["paddy", "dhan"],
            "maize": ["maize", "makka"],
            "chickpea": ["chickpea", "chana"],
        }

        for crop, keywords in hindi_crop_map.items():
            for keyword in keywords:
                if keyword in text:
                    return crop, 0.85

        return None, 0.0

    def _extract_location_hindi(self, text: str) -> Optional[str]:
        """Extract location/region from Hindi text.

        Parameters
        ----------
        text : str
            Hindi text

        Returns
        -------
        str or None
            Location name
        """
        hindi_locations = {
            "haryana": ["haryana", "hari"],
            "punjab": ["punjab", "punj"],
            "karnataka": ["karnataka", "mandya"],
            "maharashtra": ["maharashtra"],
            "madhya_pradesh": ["madhya_pradesh", "mp"],
        }

        for location, keywords in hindi_locations.items():
            for keyword in keywords:
                if keyword in text:
                    return location

        return None

    def _empty_result(self) -> Dict[str, Any]:
        """Get empty result template.

        Returns
        -------
        dict
            Empty result with default values
        """
        return {
            "time_series_name": None,
            "analysis_type": "forecast",  # default
            "time_horizon": 30,  # default 30 days
            "confidence": 0.5,
            "crop_type": None,
            "location": None,
            "practices": [],
        }

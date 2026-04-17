"""Configuration for Sarvam voice integration module."""

import os
from typing import Dict, List

# Sarvam API Configuration
SARVAM_CONFIG = {
    "api_base_url": os.getenv("SARVAM_API_BASE", "https://api.sarvam.ai/v1"),
    "api_key": os.getenv("SARVAM_API_KEY", None),
    "asr_model": "Shaktiman",  # Multi-lingual ASR model
    "tts_model": "Bulbul",  # TTS model for Indian languages
    "supported_languages": ["hi", "kn", "pa", "te", "en"],
    "default_language": os.getenv("SARVAM_LANGUAGE", "hi"),
    "asr_timeout": 30,  # seconds
    "tts_timeout": 30,  # seconds
}

# Entity Extraction Configuration
ENTITY_CONFIG = {
    "confidence_threshold": 0.7,
    "supported_time_series": [
        "temperature",
        "rainfall",
        "price",
        "demand",
        "stock_index",
        "sales",
        "passengers",
        "power",
        "wind_speed",
        "humidity",
        "custom",
    ],
    "supported_operations": [
        "forecast",
        "classify",
        "anomaly_detect",
        "trend_analysis",
        "decompose",
    ],
    "supported_crops": [
        "wheat",
        "rice",
        "sugarcane",
        "cotton",
        "paddy",
        "maize",
        "chickpea",
    ],
}

# Intent Mapping Configuration
INTENT_CONFIG = {
    "auto_select_estimator": True,
    "prefer_interpretable": True,
    "timeout_seconds": 60,
    "forecast_horizons": {
        "next_week": 7,
        "next_2_weeks": 14,
        "next_month": 30,
        "next_quarter": 90,
        "next_year": 365,
    },
}

# Response Formatting Configuration
RESPONSE_CONFIG = {
    "max_decimal_places": 2,
    "include_confidence": True,
    "include_units": True,
    "verbose_explanations": True,
}

# Language-specific settings
LANGUAGE_SETTINGS: Dict[str, Dict] = {
    "hi": {
        "name": "Hindi",
        "code": "hi",
        "script": "Devanagari",
        "number_words": {
            "ek": 1,
            "do": 2,
            "tin": 3,
            "char": 4,
            "paanch": 5,
            "chhah": 6,
            "saat": 7,
            "aath": 8,
            "nau": 9,
            "das": 10,
            "bees": 20,
            "tees": 30,
            "chalis": 40,
            "pachas": 50,
            "saath": 60,
            "sattar": 70,
            "assi": 80,
            "nabbe": 90,
            "sau": 100,
            "hazaar": 1000,
            "lakh": 100000,
        },
        "time_units": {
            "din": "day",
            "hafta": "week",
            "mahina": "month",
            "saal": "year",
            "ghanta": "hour",
            "minute": "minute",
        },
    },
    "kn": {
        "name": "Kannada",
        "code": "kn",
        "script": "Kannada",
        "number_words": {
            "ondu": 1,
            "eradu": 2,
            "muru": 3,
            "nalku": 4,
            "aidu": 5,
            "aru": 6,
            "eelu": 7,
            "enimba": 8,
            "ombattu": 9,
            "hatthu": 10,
        },
    },
    "pa": {
        "name": "Punjabi",
        "code": "pa",
        "script": "Gurmukhi",
        "number_words": {
            "ek": 1,
            "do": 2,
            "teen": 3,
            "char": 4,
            "panj": 5,
        },
    },
    "te": {
        "name": "Telugu",
        "code": "te",
        "script": "Telugu",
        "number_words": {
            "okati": 1,
            "rendu": 2,
            "moodu": 3,
            "naalugu": 4,
            "aidu": 5,
        },
    },
    "en": {
        "name": "English",
        "code": "en",
        "script": "Latin",
    },
}

# Default configuration for voice module
DEFAULT_CONFIG = {
    "enabled": os.getenv("SKTIME_VOICE_ENABLED", "true").lower() == "true",
    "log_level": os.getenv("SKTIME_VOICE_LOG_LEVEL", "INFO"),
    "cache_responses": True,
    "cache_ttl": 3600,  # seconds
}

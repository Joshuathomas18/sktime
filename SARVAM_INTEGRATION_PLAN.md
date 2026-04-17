# Sarvam Voice Integration Plan for sktime

**Version:** 1.0  
**Date:** April 17, 2026  
**Branch:** `claude/sarvam-integration-plan-UnYHE`  
**Status:** Planning Phase

---

## Executive Summary

This document outlines the integration of **Sarvam AI** voice capabilities into sktime, enabling users to interact with the time series analysis library using natural language voice commands in Indian languages (Hindi, Kannada, Punjabi, Telugu, English).

The integration will add a new optional module `sktime.voice` that provides:
- **Speech-to-Text (STT)**: Convert voice queries to text using Sarvam ASR
- **Natural Language Understanding**: Parse voice commands to extract time series analysis intent
- **Query Execution**: Execute sktime operations (forecast, classify, detect) based on voice input
- **Text-to-Speech (TTS)**: Respond to users in their preferred language using Sarvam TTS

---

## Problem Statement

### Current Limitations
1. **Accessibility Gap**: Technical users dominate sktime usage; non-technical farmers, analysts need voice interface
2. **Language Barrier**: English-only interface excludes Indian language speakers
3. **Mobile-First Need**: Farmers and field agents lack keyboards; voice is natural input method
4. **Low-Bandwidth Scenarios**: Voice queries work in areas with poor connectivity (more efficient than data-heavy ML workflows)

### Use Case: Agricultural Time Series
```
Farmer (Hindi): "Mere 5 saal ke gaon ke temperature data mein monsoon kab start hoga?"
         (Translation: "When will monsoon start based on 5 years of village temperature data?")

Sarvam ASR → sktime.voice.VoiceQueryEngine → parse intent (forecast + monsoon detection)
         ↓
      sktime.forecasting.ExponentialSmoothing.fit_predict()
         ↓
Sarvam TTS → "Aapke data ke anusar, monsoon 15 June se shuru hoga"
         (Response: "Based on your data, monsoon will start from June 15")
```

---

## Architecture: Voice Integration Module

### New Module Structure
```
sktime/voice/
├── __init__.py                    # Public API exports
├── base.py                        # Base classes for voice modules
├── query_engine.py                # Main orchestrator (Voice → Intent → Action → Voice)
├── asr_service.py                 # Speech-to-text wrapper (Sarvam)
├── tts_service.py                 # Text-to-speech wrapper (Sarvam)
├── entity_extractor.py            # NLP: Parse voice to extract fields
├── intent_mapper.py               # Map intent strings to sktime operations
├── response_formatter.py           # Format results for voice response
└── tests/
    ├── test_asr_service.py
    ├── test_query_engine.py
    └── test_entity_extractor.py
```

### Core Classes

#### 1. `VoiceQueryEngine` (query_engine.py)
```python
class VoiceQueryEngine:
    """Main orchestrator for voice-based time series queries."""
    
    def __init__(self, language: str = "hi", sarvam_api_key: str = None):
        """Initialize with Sarvam credentials and language preference."""
        self.asr = ASRService(sarvam_api_key)
        self.tts = TTSService(sarvam_api_key)
        self.entity_extractor = EntityExtractor(language)
        self.intent_mapper = IntentMapper()
    
    async def process_voice_query(self, audio_base64: str) -> dict:
        """
        Main flow:
        1. Transcribe audio → text (Sarvam ASR)
        2. Extract entities: time series name, analysis type, parameters
        3. Map intent to sktime operation
        4. Execute forecasting/classification/detection
        5. Format response
        6. Synthesize response → audio (Sarvam TTS)
        
        Returns: {
            "transcribed_text": "...",
            "intent": "forecast",
            "time_series_name": "temperature",
            "result": {...},  # sktime result
            "response_text": "...",
            "response_audio_base64": "..."
        }
        """
```

#### 2. `ASRService` (asr_service.py)
```python
class ASRService:
    """Wrapper around Sarvam ASR API."""
    
    async def transcribe(self, audio_base64: str, language: str = "hi") -> str:
        """
        Convert speech to text.
        Languages: hi (Hindi), kn (Kannada), pa (Punjabi), te (Telugu), en (English)
        """
```

#### 3. `EntityExtractor` (entity_extractor.py)
```python
class EntityExtractor:
    """Parse voice queries to extract structured entities."""
    
    def extract_entities(self, text: str, language: str) -> dict:
        """
        Extract from text:
        - time_series_name: "temperature", "rainfall", "price"
        - analysis_type: "forecast", "classify", "anomaly_detect"
        - time_horizon: "next_week", "next_month", "next_quarter"
        - confidence_level: "high", "medium", "low"
        - parameters: {"seasonality": "yearly", "trend": "growing"}
        
        Example:
        Input: "Agle 2 hafton mein rainfall ka forecast do"
        Output: {
            "time_series_name": "rainfall",
            "analysis_type": "forecast",
            "time_horizon": 14,  # days
            "confidence": 0.8
        }
        """
```

#### 4. `IntentMapper` (intent_mapper.py)
```python
class IntentMapper:
    """Map natural language intents to sktime operations."""
    
    INTENT_MAP = {
        "forecast": {
            "estimators": ["ExponentialSmoothing", "ARIMA", "StatsForecast"],
            "module": "sktime.forecasting"
        },
        "classify": {
            "estimators": ["ShapeDTW", "TimeSeriesForestClassifier"],
            "module": "sktime.classification"
        },
        "anomaly_detect": {
            "estimators": ["IForest"],
            "module": "sktime.detection"
        },
        "trend_analysis": {
            "estimators": ["STLSeasonal", "KalmanFilter"],
            "module": "sktime.transformations"
        }
    }
    
    def get_estimator(self, intent: str, data_shape: tuple) -> BaseForecaster:
        """Auto-select best estimator for voice query."""
```

#### 5. `ResponseFormatter` (response_formatter.py)
```python
class ResponseFormatter:
    """Format sktime results for voice response."""
    
    def format_forecast_response(self, forecast_result, language: str) -> str:
        """
        Convert forecast result to human-readable text.
        
        Example:
        Input: forecast array [23.4, 23.8, 24.1, 24.5, 25.0]
        Output (Hindi): "Agle 5 din mein temperature 23.4 se 25 degree tak jayega"
        """
```

---

## Integration Points with Existing sktime Modules

### 1. **Forecasting**
```python
from sktime.voice import VoiceQueryEngine
from sktime.datasets import load_airline

engine = VoiceQueryEngine(language="hi")

# Voice input: "Agle 12 mahinon mein airline passengers ka forecast"
result = await engine.process_voice_query(audio_bytes)

# Internally:
# - Extracts: time_series="airline", horizon=12, type="forecast"
# - Loads dataset
# - Fits ExponentialSmoothing
# - Returns forecast + voice response
```

### 2. **Classification**
```python
# Voice: "Ye time series series kis category mein aata hai?"
# Engine identifies time series type (growth, cyclic, random walk, etc.)
```

### 3. **Anomaly Detection**
```python
# Voice: "Mere data mein koi anomaly hai?"
# Engine detects outliers/changepoints
```

---

## Configuration

### `sktime/voice/config.py`
```python
VOICE_CONFIG = {
    "sarvam": {
        "api_base_url": "https://api.sarvam.ai/v1",
        "asr_model": "Shaktiman",  # Multi-lingual ASR
        "tts_model": "Bulbul",      # Indian languages TTS
        "supported_languages": ["hi", "kn", "pa", "te", "en"],
        "timeout": 30,              # seconds
    },
    "entity_extraction": {
        "confidence_threshold": 0.7,
        "supported_time_series": [
            "temperature", "rainfall", "price", "demand",
            "stock_index", "sales", "passengers", "custom"
        ],
        "supported_operations": [
            "forecast", "classify", "anomaly_detect", "trend_analysis"
        ]
    },
    "estimator_selection": {
        "auto_select": True,
        "prefer_interpretable": True,  # For voice explanations
        "timeout_seconds": 60,
    }
}
```

### Environment Variables
```bash
# .env
SARVAM_API_KEY=your_api_key_here
SARVAM_LANGUAGE=hi  # default language
SKTIME_VOICE_ENABLED=true
SKTIME_VOICE_LOG_LEVEL=INFO
```

---

## Phase 1: MVP (Weeks 1-2)

### Deliverables
1. ✅ `sktime.voice` module structure
2. ✅ `ASRService` wrapper for Sarvam (mock + real API)
3. ✅ `EntityExtractor` for Hindi voice queries
4. ✅ `VoiceQueryEngine` orchestrator
5. ✅ Basic forecasting support (ExponentialSmoothing)
6. ✅ Integration tests with sample voice queries
7. ✅ Documentation + usage examples

### Success Criteria
- [ ] Voice query "Agle 3 mahinon mein kya forecast hai?" correctly triggers forecasting
- [ ] System returns forecast + voice response in < 3 seconds
- [ ] Entity extraction accuracy > 85% on test dataset
- [ ] Works offline (cached models) and online (Sarvam API)

---

## Phase 2: Enhancement (Weeks 3-4)

### Features
1. Multi-language support (Kannada, Punjabi, Telugu)
2. Classification voice queries
3. Anomaly detection voice interface
4. Model explanations in voice (why did we forecast this value?)
5. Interactive voice conversations (follow-up questions)

### Estimators to Support
- Forecasting: ARIMA, StatsForecast, NeuralNetwork
- Classification: ShapeDTW, InceptionTime
- Anomaly Detection: IForest, LOF

---

## Phase 3: Production (Weeks 5+)

### Deployment
1. Docker containerization
2. Kubernetes deployment
3. API gateway for voice requests
4. Monitoring + error handling
5. Cache layer for model inference

### Scalability
- [ ] Support 100+ concurrent voice queries
- [ ] Sub-2-second response time for forecast queries
- [ ] Cost optimization (Sarvam API rate limiting, model caching)

---

## Implementation Roadmap

### Week 1
- [ ] Day 1: Create module structure, ASRService, config
- [ ] Day 2: Entity extraction (Hindi)
- [ ] Day 3: Intent mapping + forecasting integration
- [ ] Day 4: Response formatting + TTS integration
- [ ] Day 5: Testing + documentation

### Week 2+
- [ ] Multi-language support
- [ ] Classification + Anomaly detection
- [ ] Deployment + optimization

---

## Testing Strategy

### Unit Tests
```python
# tests/test_entity_extractor.py
def test_extract_rainfall_forecast():
    text = "Agle 2 hafte mein paddy ke liye kya rainfall hogi?"
    entities = extractor.extract_entities(text, language="hi")
    assert entities["time_series_name"] == "rainfall"
    assert entities["analysis_type"] == "forecast"
    assert entities["crop_type"] == "paddy"

def test_extract_temperature_classification():
    text = "Ye temperature pattern kis season ka hai?"
    entities = extractor.extract_entities(text, language="hi")
    assert entities["analysis_type"] == "classify"
```

### Integration Tests
```python
# tests/test_voice_query_engine.py
async def test_voice_forecast_query():
    engine = VoiceQueryEngine(language="hi")
    
    # Mock Sarvam response
    audio_bytes = b"..."  # Hindi: "Agle 12 din ka forecast"
    
    result = await engine.process_voice_query(audio_bytes)
    
    assert "forecast" in result["result"]
    assert result["response_text"]  # Hindi response
    assert result["response_audio_base64"]  # Audio response
```

### End-to-End Tests
- Real Sarvam API tests (gated behind API key)
- Sample queries in 4 languages
- Latency benchmarks

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Sarvam API outage | Fallback to text-based queries, cache models |
| Entity extraction fails | Ask clarifying questions via voice |
| Model inference slow | Pre-load models, use faster estimators |
| Language not supported | Graceful fallback to English |
| Poor audio quality | Noise detection + request retry with guidance |

---

## Dependencies

### New Dependencies
```
sarvam-sdk>=0.1.0  # Sarvam AI API SDK
```

### Existing sktime Dependencies
```
pandas, numpy, scikit-learn
sktime.forecasting, sktime.classification, sktime.detection
```

---

## API Examples

### Python API
```python
from sktime.voice import VoiceQueryEngine

# Initialize
engine = VoiceQueryEngine(language="hi")

# Voice query
result = await engine.process_voice_query(audio_bytes)

print(f"Transcribed: {result['transcribed_text']}")
print(f"Intent: {result['intent']}")
print(f"Forecast: {result['result']}")
print(f"Response: {result['response_text']}")
```

### REST API (Future)
```
POST /api/v1/voice/query
{
  "audio_base64": "...",
  "language": "hi",
  "time_series_id": "rainfall_mandya"
}

Response:
{
  "transcribed_text": "...",
  "forecast": [...],
  "response_text": "...",
  "response_audio_base64": "..."
}
```

---

## Accessibility & Inclusion

### Target Users
1. **Smallholder farmers** in India (250M+ farming households)
2. **Field agents** collecting data on mobile phones
3. **Non-technical analysts** who need quick forecasts
4. **Regional language speakers** who prefer not to use English

### Language Support
- Hindi (Devanagari)
- Kannada (Karnataka)
- Punjabi (Punjab)
- Telugu (Andhra Pradesh)
- English (fallback)

### Offline Capability
- Works with cached models when Sarvam API unavailable
- Progressive enhancement (voice when available, text fallback)

---

## Success Metrics

### Phase 1 MVP
- [ ] 3 voice queries/day average (beta users)
- [ ] 85%+ entity extraction accuracy
- [ ] < 3 second response time
- [ ] 0 critical bugs in first week of deployment

### Phase 2+
- [ ] 100+ daily voice queries
- [ ] Support 4+ languages
- [ ] Integration with 3+ sktime modules (forecasting, classification, detection)
- [ ] 95%+ user satisfaction (voice accuracy, response quality)

---

## Conclusion

Sarvam voice integration transforms sktime from a technical library into an **accessible platform for agricultural and social impact**. By adding voice support for Indian languages, we enable millions of farmers to leverage advanced time series analysis for better decisions—without requiring technical expertise or English proficiency.

This aligns with sktime's mission: *"A unified interface for machine learning with time series"* — now including **voice as a first-class interface**.

---

## Next Steps

1. **Approve Plan**: Review and approve this roadmap
2. **Set up Development Environment**: Install Sarvam SDK, configure API key
3. **Week 1 Sprint**: Implement MVP module structure and ASR service
4. **Community Feedback**: Present plan to sktime community (Discord, GitHub Discussions)
5. **Deploy Beta**: Launch voice feature with beta users (farmers in pilot regions)

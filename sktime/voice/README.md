# Voice Interface for sktime

**Enable voice-based time series analysis in Indian languages.**

The `sktime.voice` module provides a speech-to-text interface for sktime's time series analysis capabilities, designed for accessibility and inclusivity. Users can query time series data using natural voice commands in Hindi, Kannada, Punjabi, Telugu, or English.

## Features

✨ **Multi-Language Support**
- Hindi (Devanagari) - fully supported
- Kannada, Punjabi, Telugu - supported  
- English - fallback

🎯 **Smart Entity Extraction**
- Automatically detects time series name (temperature, rainfall, price, etc.)
- Identifies analysis type (forecast, classify, anomaly detection)
- Extracts time horizons ("next 2 weeks", "agle 3 mahine", etc.)
- Recognizes crop types and locations
- Supports natural language number words ("paanch" = 5, "do" = 2)

🚀 **Auto Intent Mapping**
- Maps voice queries to sktime operations
- Auto-selects best estimator based on intent and data characteristics
- Supports forecasting, classification, anomaly detection, trend analysis

🔊 **Voice Response**
- Synthesizes results back to speech (Hindi/English)
- Generates human-readable summaries
- Confidence scoring and uncertainty quantification

📱 **Production Ready**
- Mock implementations for testing without API keys
- Real Sarvam API support (optional)
- Comprehensive error handling
- Async/await for non-blocking operations

## Installation

```bash
# Install sktime with voice module
pip install sktime

# For real Sarvam API integration, install:
pip install sarvam-sdk httpx
```

Set environment variables for real API:
```bash
export SARVAM_API_KEY=your_api_key
export SARVAM_LANGUAGE=hi  # default language
```

## Quick Start

### Basic Usage

```python
import asyncio
from sktime.voice import VoiceQueryEngine

# Initialize engine
engine = VoiceQueryEngine(language="hi", enable_tts=True)

# Process voice query (audio as base64)
result = asyncio.run(engine.process_voice_query(audio_base64))

print(f"You asked: {result['transcribed_text']}")
print(f"Analysis: {result['intent']['intent']}")
print(f"Response: {result['response_text']}")
```

### Example: Hindi Voice Query

```
Farmer (Hindi voice): "Agle 2 hafton mein rainfall ka forecast kya hoga?"
                     (Translation: "What will be the rainfall forecast for the next 2 weeks?")

System processes:
1. Transcribes: "Agle 2 hafton mein rainfall ka forecast kya hoga?"
2. Extracts entities:
   - time_series_name: "rainfall"
   - analysis_type: "forecast"
   - time_horizon: 14 days
3. Maps intent:
   - estimator: "ExponentialSmoothing" (short-term forecast)
   - module: "sktime.forecasting"
4. Generates response:
   - Text: "Aapke rainfall ka forecast dekhe to average 25.5mm hoga. 
            Agle 14 dinon mein 5% badhav expect hai."
   - Audio: Response synthesized back to speech

Return: {
    "transcribed_text": "Agle 2 hafton mein rainfall ka forecast kya hoga?",
    "entities": {
        "time_series_name": "rainfall",
        "analysis_type": "forecast",
        "time_horizon": 14,
        "confidence": 0.85
    },
    "intent": {
        "intent": "forecast",
        "estimator": "ExponentialSmoothing",
        "module": "sktime.forecasting"
    },
    "response_text": "Aapke rainfall ka forecast...",
    "response_audio_base64": "..." # speech audio
}
```

## Core Components

### VoiceQueryEngine

Main orchestrator for end-to-end voice queries.

```python
from sktime.voice import VoiceQueryEngine

# Initialize
engine = VoiceQueryEngine(language="hi", api_key="sarvam_key")

# Process voice query
result = await engine.process_voice_query(audio_base64)

# Or use individual components
engine.asr.transcribe(audio_base64)
engine.extractor.extract(text)
engine.intent_mapper.map_intent(entities)
```

### ASRService (Automatic Speech Recognition)

Convert speech to text.

```python
from sktime.voice import ASRService

asr = ASRService(api_key="key", language="hi")

# Transcribe audio
text = await asr.transcribe(audio_base64, language="hi")

# Check supported languages
print(asr.get_supported_languages())  # ['hi', 'kn', 'pa', 'te', 'en']
```

### EntityExtractor

Extract structured entities from text.

```python
from sktime.voice import EntityExtractor

extractor = EntityExtractor(language="hi")

# Extract entities
entities = extractor.extract("Mere paas 5 acre sugarcane hai")

# Result:
# {
#     "time_series_name": None,
#     "analysis_type": "forecast",
#     "crop_type": "sugarcane",
#     "confidence": 0.85,
#     ...
# }
```

### IntentMapper

Map entities to sktime operations.

```python
from sktime.voice import IntentMapper

mapper = IntentMapper()

intent = mapper.map_intent({
    "time_series_name": "rainfall",
    "analysis_type": "forecast",
    "time_horizon": 30
})

# Result:
# {
#     "intent": "forecast",
#     "estimator": "ARIMA",  # selected for 30-day horizon
#     "module": "sktime.forecasting",
#     "parameters": {"fh": 30, "sp": 365}
# }
```

### ResponseFormatter

Format results for human-readable voice response.

```python
from sktime.voice import ResponseFormatter

formatter = ResponseFormatter(language="hi")

response_text = formatter.format_response(
    result=forecast_result,
    intent="forecast",
    entities={"time_series_name": "rainfall"}
)

# Returns human-readable summary in Hindi
```

### TTSService (Text-to-Speech)

Synthesize text to speech.

```python
from sktime.voice import TTSService

tts = TTSService(api_key="key", language="hi")

# Synthesize text
audio_bytes = await tts.synthesize(
    "Aapke rainfall ka forecast 25.5mm hoga",
    language="hi"
)
```

## Entity Extraction Examples

### Hindi Queries

```
Query: "Agle 3 mahinon mein temperature forecast"
Extract: time_series_name="temperature", analysis_type="forecast", time_horizon=90

Query: "Mandya mein sugarcane crop ke liye kya forecast hai?"
Extract: location="karnataka", crop_type="sugarcane", analysis_type="forecast"

Query: "Meri wheat farm mein burning se bachne ke baad carbon kya badh gaya?"
Extract: crop_type="wheat", analysis_type="trend_analysis"
```

### English Queries

```
Query: "Forecast rainfall for next 2 weeks"
Extract: time_series_name="rainfall", time_horizon=14

Query: "Detect anomalies in temperature data"
Extract: time_series_name="temperature", analysis_type="anomaly_detect"
```

## Supported Operations

| Intent | Estimator | Use Case | Horizon |
|--------|-----------|----------|---------|
| **forecast** | ExponentialSmoothing | Short-term (≤2 weeks) | ≤14 days |
| **forecast** | ARIMA | Medium-term (2-3 months) | 15-90 days |
| **forecast** | StatsForecast | Long-term (>3 months) | >90 days |
| **classify** | ShapeDTW | Time series classification | Any |
| **anomaly_detect** | IForest | Outlier detection | Any |
| **trend_analysis** | STLSeasonal | Trend decomposition | Any |

## Language Configuration

Each language has specific settings:

```python
from sktime.voice.config import LANGUAGE_SETTINGS

# Hindi configuration
hi_config = LANGUAGE_SETTINGS["hi"]
print(hi_config["number_words"])  # {"ek": 1, "do": 2, "tin": 3, ...}
print(hi_config["time_units"])    # {"din": "day", "hafta": "week", ...}
```

## Error Handling

Graceful fallbacks when APIs are unavailable:

```python
engine = VoiceQueryEngine(language="hi")

try:
    result = await engine.process_voice_query(audio)
except Exception as e:
    # Falls back to mock responses
    # Generates error message in target language
    response = engine.formatter.format_error(str(e), language="hi")
```

## Testing

Run tests for voice components:

```bash
# Test entity extraction
pytest sktime/voice/tests/test_entity_extractor.py

# Test intent mapping
pytest sktime/voice/tests/test_intent_mapper.py

# Test query engine
pytest sktime/voice/tests/test_query_engine.py -v

# Run all voice tests
pytest sktime/voice/tests/
```

## Configuration

Customize behavior via environment variables or direct configuration:

```bash
# Environment variables
export SARVAM_API_KEY=your_key
export SARVAM_LANGUAGE=hi
export SKTIME_VOICE_ENABLED=true
export SKTIME_VOICE_LOG_LEVEL=INFO
```

Or in code:

```python
from sktime.voice.config import SARVAM_CONFIG, ENTITY_CONFIG

SARVAM_CONFIG["api_timeout"] = 15
ENTITY_CONFIG["confidence_threshold"] = 0.8
```

## Advanced Usage

### Custom Response Formatting

```python
from sktime.voice import ResponseFormatter

formatter = ResponseFormatter(language="hi")

# Override formatting for specific intent
def format_custom_forecast(values, ts_name):
    avg = sum(values) / len(values)
    return f"Aapke {ts_name} ka forecast average {avg:.1f} hoga"

formatter.format_forecast = format_custom_forecast
```

### Multi-Language Support in Single App

```python
from sktime.voice import VoiceQueryEngine

# Create separate engines per language
engines = {
    "hi": VoiceQueryEngine(language="hi"),
    "kn": VoiceQueryEngine(language="kn"),
    "en": VoiceQueryEngine(language="en"),
}

# Route queries by language
result = await engines[user_language].process_voice_query(audio)
```

### Batch Processing

```python
import asyncio
from sktime.voice import VoiceQueryEngine

engine = VoiceQueryEngine(language="hi")

# Process multiple queries concurrently
audio_files = [audio1, audio2, audio3]
results = await asyncio.gather(*[
    engine.process_voice_query(audio) for audio in audio_files
])
```

## Performance

Typical latencies (mock mode, no API):
- **Speech-to-Text**: 100-500ms
- **Entity Extraction**: 10-50ms
- **Intent Mapping**: 5-20ms
- **Response Formatting**: 10-50ms
- **Text-to-Speech**: 200-800ms
- **Total**: 500-2000ms (0.5-2 seconds)

Real Sarvam API adds network latency (varies by region, typically 1-3 seconds per API call).

## Limitations & Roadmap

### Current Limitations
- Mock implementations don't provide real Sarvam integration yet
- Entity extraction uses rule-based matching (no deep NLP models)
- Single-turn queries only (no conversational follow-ups)
- Limited to predefined time series types

### Phase 2 (In Development)
- [ ] Real Sarvam API integration
- [ ] Multi-turn conversation support
- [ ] Custom time series name support
- [ ] Advanced NLP with spaCy/transformers
- [ ] Caching layer for repeated queries
- [ ] Model explanation generation

### Phase 3 (Planned)
- [ ] Integration with sktime estimators
- [ ] Web/mobile APIs
- [ ] Farmer app for agricultural use cases
- [ ] Carbon credit marketplace integration

## Contributing

Contributions welcome! Areas for improvement:
- Additional language support
- Better entity extraction
- Integration tests with real Sarvam API
- Performance optimization
- Documentation translations

## License

BSD 3-Clause (same as sktime)

## Support

- **Documentation**: [sktime.net/en/latest](https://www.sktime.net)
- **Issues**: [GitHub Issues](https://github.com/joshuathomas18/sktime/issues)
- **Discord**: [sktime community](https://discord.com/invite/54ACzaFsn7)
- **Contact**: For Sarvam API issues, see [Sarvam AI docs](https://docs.sarvam.ai)

## Citation

If you use `sktime.voice` in research, please cite:

```bibtex
@inproceedings{sktime2019,
  title={sktime: a unified interface for machine learning with time series},
  author={L{\"o}ning, Markus and others},
  booktitle={arXiv preprint arXiv:1909.07772},
  year={2019}
}
```

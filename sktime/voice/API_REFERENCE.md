# API Reference - sktime.voice

Complete API documentation for the voice interface module.

---

## VoiceQueryEngine

Main orchestrator for voice-based time series queries.

### Constructor

```python
VoiceQueryEngine(language: str = "hi", api_key: Optional[str] = None, enable_tts: bool = True)
```

**Parameters:**
- `language` (str, default="hi"): Default language code
  - "hi": Hindi
  - "kn": Kannada
  - "pa": Punjabi
  - "te": Telugu
  - "en": English
- `api_key` (str, optional): Sarvam API key. If None, uses mock mode
- `enable_tts` (bool, default=True): Enable text-to-speech responses

**Example:**
```python
from sktime.voice import VoiceQueryEngine

engine = VoiceQueryEngine(language="hi", api_key="your_key", enable_tts=True)
```

### Methods

#### process_voice_query

```python
async def process_voice_query(
    audio_base64: str,
    language: Optional[str] = None
) -> Dict[str, Any]
```

Process complete voice query pipeline.

**Parameters:**
- `audio_base64` (str): Base64-encoded audio data
- `language` (str, optional): Language override for this query

**Returns:**
Dict with structure:
```python
{
    "transcribed_text": str,      # Original voice input as text
    "entities": {                 # Extracted entities
        "time_series_name": str,
        "analysis_type": str,
        "time_horizon": int,      # days
        "confidence": float,      # 0.0-1.0
        "crop_type": Optional[str],
        "location": Optional[str],
        "practices": List[str]
    },
    "intent": {                   # Mapped intent
        "intent": str,
        "estimator": str,
        "module": str,
        "parameters": Dict[str, Any],
        "confidence": float
    },
    "response_text": str,         # Human-readable response
    "response_audio_base64": Optional[str],  # Audio response
    "confidence": float,          # Overall confidence
    "success": bool,
    "error": Optional[str]
}
```

**Example:**
```python
import asyncio
import base64

audio_bytes = b"your_audio_data"
audio_base64 = base64.b64encode(audio_bytes).decode()

result = asyncio.run(engine.process_voice_query(audio_base64))
print(f"You asked: {result['transcribed_text']}")
print(f"Response: {result['response_text']}")
```

#### set_language

```python
def set_language(language: str) -> None
```

Set default language for all components.

**Parameters:**
- `language` (str): Language code

**Raises:**
- ValueError: If language not supported

**Example:**
```python
engine.set_language("en")  # Switch to English
```

#### get_supported_languages

```python
def get_supported_languages() -> List[str]
```

Get list of supported languages.

**Returns:**
List of language codes

**Example:**
```python
languages = engine.get_supported_languages()
# ['hi', 'kn', 'pa', 'te', 'en']
```

#### get_supported_intents

```python
def get_supported_intents() -> List[str]
```

Get list of supported analysis intents.

**Returns:**
List of intent types

**Example:**
```python
intents = engine.get_supported_intents()
# ['forecast', 'classify', 'anomaly_detect', 'trend_analysis']
```

#### validate_audio

```python
def validate_audio(audio_base64: str) -> bool
```

Validate audio input format.

**Parameters:**
- `audio_base64` (str): Base64-encoded audio to validate

**Returns:**
bool: True if valid base64, False otherwise

---

## ASRService

Automatic Speech Recognition service.

### Constructor

```python
ASRService(api_key: Optional[str] = None, language: str = "hi")
```

**Parameters:**
- `api_key` (str, optional): Sarvam API key
- `language` (str, default="hi"): Default language

### Methods

#### transcribe

```python
async def transcribe(
    audio_base64: str,
    language: Optional[str] = None
) -> str
```

Transcribe audio to text.

**Parameters:**
- `audio_base64` (str): Base64-encoded audio
- `language` (str, optional): Language override

**Returns:**
Transcribed text

**Raises:**
- ValueError: If language not supported
- TypeError: If audio format invalid

**Example:**
```python
text = await asr.transcribe(audio_base64, language="hi")
print(text)  # "Agle 3 mahine mein forecast"
```

#### validate_audio

```python
def validate_audio(audio_base64: str) -> bool
```

Validate audio format.

**Parameters:**
- `audio_base64` (str): Audio to validate

**Returns:**
bool: True if valid

#### get_supported_languages

```python
def get_supported_languages() -> List[str]
```

Get supported languages.

**Returns:**
List of language codes

#### set_language

```python
def set_language(language: str) -> None
```

Set default language.

**Parameters:**
- `language` (str): Language code

**Raises:**
- ValueError: If not supported

---

## EntityExtractor

Extract structured entities from text.

### Constructor

```python
EntityExtractor(language: str = "hi")
```

**Parameters:**
- `language` (str, default="hi"): Language for extraction

### Methods

#### extract

```python
def extract(text: str) -> Dict[str, Any]
```

Extract entities from text.

**Parameters:**
- `text` (str): Input text

**Returns:**
Dict with extracted entities:
```python
{
    "time_series_name": Optional[str],     # temperature, rainfall, price, etc.
    "analysis_type": str,                  # forecast, classify, anomaly_detect, etc.
    "time_horizon": int,                   # days
    "confidence": float,                   # 0.0-1.0
    "crop_type": Optional[str],            # wheat, rice, sugarcane, etc.
    "location": Optional[str],             # haryana, karnataka, etc.
    "practices": List[str]                 # burning, residue_retention, etc.
}
```

**Example:**
```python
entities = extractor.extract("Agle 2 hafton mein rainfall")
# {
#     "time_series_name": "rainfall",
#     "analysis_type": "forecast",
#     "time_horizon": 14,
#     "confidence": 0.85,
#     ...
# }
```

---

## IntentMapper

Map entities to sktime operations.

### Methods

#### map_intent

```python
def map_intent(entities: Dict[str, Any]) -> Dict[str, Any]
```

Map entities to intent and operation.

**Parameters:**
- `entities` (dict): Extracted entities

**Returns:**
Dict with intent mapping:
```python
{
    "intent": str,                 # forecast, classify, etc.
    "estimator": str,              # ExponentialSmoothing, ARIMA, etc.
    "module": str,                 # sktime module path
    "parameters": Dict[str, Any],  # Operation parameters
    "confidence": float            # 0.0-1.0
}
```

**Example:**
```python
intent = mapper.map_intent({
    "time_series_name": "rainfall",
    "analysis_type": "forecast",
    "time_horizon": 30
})
# {
#     "intent": "forecast",
#     "estimator": "ARIMA",
#     "module": "sktime.forecasting",
#     "parameters": {"fh": 30, "sp": 365},
#     "confidence": 0.8
# }
```

#### get_supported_intents

```python
def get_supported_intents() -> List[str]
```

Get supported intents.

**Returns:**
List of intent types

#### validate_intent

```python
def validate_intent(intent: str) -> bool
```

Check if intent is supported.

**Parameters:**
- `intent` (str): Intent to validate

**Returns:**
bool: True if supported

#### get_estimator_help

```python
def get_estimator_help(intent: str) -> str
```

Get help for intent estimators.

**Parameters:**
- `intent` (str): Intent

**Returns:**
Help text

---

## ResponseFormatter

Format results for voice response.

### Constructor

```python
ResponseFormatter(language: str = "hi")
```

**Parameters:**
- `language` (str, default="hi"): Response language

### Methods

#### format_response

```python
def format_response(
    result: Dict[str, Any],
    intent: Optional[str] = None,
    entities: Optional[Dict[str, Any]] = None
) -> str
```

Format result as voice response.

**Parameters:**
- `result` (dict): Analysis result
- `intent` (str, optional): Intent type
- `entities` (dict, optional): Context entities

**Returns:**
Formatted response text

**Example:**
```python
response = formatter.format_response(
    result=forecast_array,
    intent="forecast",
    entities={"time_series_name": "rainfall"}
)
# "Aapke rainfall ka forecast dekhe to..."
```

#### format_error

```python
def format_error(error: str, language: Optional[str] = None) -> str
```

Format error message.

**Parameters:**
- `error` (str): Error message
- `language` (str, optional): Response language

**Returns:**
Formatted error text

#### round_values

```python
def round_values(values: List[float], decimals: int = 2) -> List[float]
```

Round values for display.

**Parameters:**
- `values` (list): Values to round
- `decimals` (int, default=2): Decimal places

**Returns:**
Rounded values

---

## TTSService

Text-to-Speech service.

### Constructor

```python
TTSService(api_key: Optional[str] = None, language: str = "hi")
```

**Parameters:**
- `api_key` (str, optional): Sarvam API key
- `language` (str, default="hi"): Default language

### Methods

#### synthesize

```python
async def synthesize(
    text: str,
    language: Optional[str] = None
) -> bytes
```

Synthesize text to audio.

**Parameters:**
- `text` (str): Text to synthesize
- `language` (str, optional): Language override

**Returns:**
Audio bytes (MP3)

**Raises:**
- ValueError: If text empty or language not supported

**Example:**
```python
audio = await tts.synthesize("Aapka forecast ready hai", language="hi")
# Returns MP3 audio bytes
```

#### estimate_audio_duration

```python
def estimate_audio_duration(text: str) -> float
```

Estimate audio duration.

**Parameters:**
- `text` (str): Text

**Returns:**
Estimated duration in seconds

#### get_supported_languages

```python
def get_supported_languages() -> List[str]
```

Get supported languages.

**Returns:**
List of language codes

#### set_language

```python
def set_language(language: str) -> None
```

Set default language.

**Parameters:**
- `language` (str): Language code

---

## Configuration

### SARVAM_CONFIG

```python
from sktime.voice.config import SARVAM_CONFIG

SARVAM_CONFIG = {
    "api_base_url": str,          # Sarvam API endpoint
    "api_key": Optional[str],     # API key from environment
    "asr_model": str,             # "Shaktiman"
    "tts_model": str,             # "Bulbul"
    "supported_languages": List[str],
    "asr_timeout": int,           # seconds
    "tts_timeout": int            # seconds
}
```

### ENTITY_CONFIG

```python
from sktime.voice.config import ENTITY_CONFIG

ENTITY_CONFIG = {
    "confidence_threshold": float,
    "supported_time_series": List[str],
    "supported_operations": List[str],
    "supported_crops": List[str]
}
```

### LANGUAGE_SETTINGS

```python
from sktime.voice.config import LANGUAGE_SETTINGS

LANGUAGE_SETTINGS = {
    "hi": {
        "name": "Hindi",
        "code": "hi",
        "script": "Devanagari",
        "number_words": {
            "ek": 1,
            "do": 2,
            "tin": 3,
            # ...
        },
        "time_units": {
            "din": "day",
            "hafta": "week",
            # ...
        }
    },
    # ... other languages
}
```

---

## Error Handling

Common exceptions:

### ValueError

Raised when:
- Language not supported
- Text is empty
- Intent not supported

```python
try:
    engine.set_language("invalid")
except ValueError as e:
    print(f"Error: {e}")
```

### TypeError

Raised when:
- Invalid audio format
- Wrong parameter type

```python
try:
    await asr.transcribe(None)
except TypeError as e:
    print(f"Error: {e}")
```

### NotImplementedError

Raised when:
- Real Sarvam API not available
- Feature not yet implemented

```python
try:
    await asr._call_sarvam_asr(audio, "hi")
except NotImplementedError as e:
    print(f"Use mock mode: {e}")
```

---

## Usage Patterns

### Pattern 1: Simple Voice Query

```python
result = await engine.process_voice_query(audio_base64)
print(result["response_text"])
```

### Pattern 2: Component-by-Component

```python
# Use individual services
text = await asr.transcribe(audio_base64)
entities = extractor.extract(text)
intent = mapper.map_intent(entities)
response = formatter.format_response(entities)
```

### Pattern 3: Multi-Language

```python
for language in ["hi", "kn", "en"]:
    engine.set_language(language)
    result = await engine.process_voice_query(audio_base64)
    print(f"{language}: {result['response_text']}")
```

### Pattern 4: Batch Processing

```python
results = await asyncio.gather(*[
    engine.process_voice_query(audio)
    for audio in audio_list
])
```

---

## See Also

- [README](README.md) - User guide and examples
- [Configuration Guide](../config.py) - Detailed configuration options
- [sktime Documentation](https://www.sktime.net) - Main library docs

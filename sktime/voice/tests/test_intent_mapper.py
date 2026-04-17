"""Tests for intent mapping."""

import pytest
from sktime.voice.intent_mapper import IntentMapper


class TestIntentMapper:
    """Test intent mapping."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mapper = IntentMapper()

    def test_map_forecast_intent(self):
        """Test mapping forecast intent."""
        entities = {
            "time_series_name": "rainfall",
            "analysis_type": "forecast",
            "time_horizon": 30,
            "confidence": 0.85,
        }

        result = self.mapper.map_intent(entities)

        assert result["intent"] == "forecast"
        assert result["estimator"] in ["ExponentialSmoothing", "ARIMA"]
        assert result["module"] == "sktime.forecasting"
        assert "fh" in result["parameters"]
        assert result["parameters"]["fh"] == 30

    def test_select_estimator_short_term(self):
        """Test estimator selection for short-term forecast."""
        entities = {
            "analysis_type": "forecast",
            "time_horizon": 7,
        }

        result = self.mapper.map_intent(entities)

        # Short-term should use ExponentialSmoothing
        assert result["estimator"] == "ExponentialSmoothing"

    def test_select_estimator_medium_term(self):
        """Test estimator selection for medium-term forecast."""
        entities = {
            "analysis_type": "forecast",
            "time_horizon": 60,
        }

        result = self.mapper.map_intent(entities)

        # Medium-term should use ARIMA
        assert result["estimator"] == "ARIMA"

    def test_select_estimator_long_term(self):
        """Test estimator selection for long-term forecast."""
        entities = {
            "analysis_type": "forecast",
            "time_horizon": 365,
        }

        result = self.mapper.map_intent(entities)

        # Long-term should use StatsForecast
        assert result["estimator"] == "StatsForecast"

    def test_map_classification_intent(self):
        """Test mapping classification intent."""
        entities = {
            "analysis_type": "classify",
        }

        result = self.mapper.map_intent(entities)

        assert result["intent"] == "classify"
        assert result["estimator"] == "ShapeDTW"
        assert result["module"] == "sktime.classification"

    def test_map_anomaly_intent(self):
        """Test mapping anomaly detection intent."""
        entities = {
            "analysis_type": "anomaly_detect",
        }

        result = self.mapper.map_intent(entities)

        assert result["intent"] == "anomaly_detect"
        assert result["estimator"] == "IForest"
        assert result["module"] == "sktime.detection"

    def test_get_supported_intents(self):
        """Test getting supported intents."""
        intents = self.mapper.get_supported_intents()

        assert "forecast" in intents
        assert "classify" in intents
        assert "anomaly_detect" in intents
        assert "trend_analysis" in intents

    def test_validate_intent(self):
        """Test intent validation."""
        assert self.mapper.validate_intent("forecast") is True
        assert self.mapper.validate_intent("classify") is True
        assert self.mapper.validate_intent("unknown_intent") is False

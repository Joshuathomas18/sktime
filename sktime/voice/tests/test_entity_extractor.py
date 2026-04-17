"""Tests for entity extraction."""

import pytest
from sktime.voice.entity_extractor import EntityExtractor


class TestEntityExtractorHindi:
    """Test Hindi entity extraction."""

    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = EntityExtractor(language="hi")

    def test_extract_rainfall_forecast(self):
        """Test extracting rainfall forecast query."""
        text = "Agle 2 hafton mein rainfall ka forecast"
        entities = self.extractor.extract(text)

        assert entities["time_series_name"] == "rainfall"
        assert entities["analysis_type"] == "forecast"
        assert entities["time_horizon"] == 14  # 2 weeks

    def test_extract_temperature_query(self):
        """Test extracting temperature query."""
        text = "Mere ghar ke temperature mein trend kya hai?"
        entities = self.extractor.extract(text)

        assert entities["time_series_name"] == "temperature"

    def test_extract_crop_type(self):
        """Test extracting crop type."""
        text = "Mere 5 acre sugarcane farm mein crop forecast"
        entities = self.extractor.extract(text)

        assert entities["crop_type"] == "sugarcane"

    def test_extract_time_horizon_days(self):
        """Test extracting time horizon in days."""
        text = "Agle 7 dinon ka forecast"
        entities = self.extractor.extract(text)

        assert entities["time_horizon"] == 7

    def test_extract_time_horizon_weeks(self):
        """Test extracting time horizon in weeks."""
        text = "Agle 3 hafton mein forecast"
        entities = self.extractor.extract(text)

        assert entities["time_horizon"] == 21  # 3 weeks

    def test_extract_location(self):
        """Test extracting location."""
        text = "Mandya mein rainfall pattern kya hai?"
        entities = self.extractor.extract(text)

        assert entities["location"] == "karnataka"  # Mandya is in Karnataka


class TestEntityExtractorEnglish:
    """Test English entity extraction."""

    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = EntityExtractor(language="en")

    def test_extract_forecast_query(self):
        """Test extracting English forecast query."""
        text = "What will be the temperature forecast for next month?"
        entities = self.extractor.extract(text)

        assert entities["time_series_name"] == "temperature"
        assert entities["analysis_type"] == "forecast"
        assert entities["time_horizon"] == 30

    def test_extract_rainfall_query(self):
        """Test extracting rainfall query."""
        text = "Show me rainfall for next 3 months"
        entities = self.extractor.extract(text)

        assert entities["time_series_name"] == "rainfall"
        assert entities["time_horizon"] == 90


class TestEntityExtractorGeneric:
    """Test generic/fallback entity extraction."""

    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = EntityExtractor(language="pa")  # Punjabi (uses generic)

    def test_extract_from_unknown_language(self):
        """Test extraction from unsupported language."""
        text = "Something in Punjabi"
        entities = self.extractor.extract(text)

        # Should return empty result with defaults
        assert entities["analysis_type"] == "forecast"
        assert entities["time_horizon"] == 30

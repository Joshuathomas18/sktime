"""Intent mapping from entities to sktime operations."""

import logging
from typing import Any, Dict, Optional, Type

from sktime.voice.base import IntentMapperBase
from sktime.voice.config import INTENT_CONFIG

logger = logging.getLogger(__name__)


class IntentMapper(IntentMapperBase):
    """Map voice query intents to sktime operations and estimators.

    Handles:
    - intent classification (forecast, classify, anomaly_detect, etc.)
    - auto-selection of appropriate estimators based on data shape and intent
    - parameter extraction and defaults
    """

    # Mapping of intent to available estimators in sktime
    INTENT_ESTIMATORS = {
        "forecast": {
            "module": "sktime.forecasting",
            "estimators": [
                "ExponentialSmoothing",
                "ARIMA",
                "StatsForecast",
                "AutoARIMA",
            ],
            "default": "ExponentialSmoothing",
        },
        "classify": {
            "module": "sktime.classification",
            "estimators": [
                "ShapeDTW",
                "TimeSeriesForestClassifier",
                "InceptionTime",
            ],
            "default": "ShapeDTW",
        },
        "anomaly_detect": {
            "module": "sktime.detection",
            "estimators": ["IForest", "LOF"],
            "default": "IForest",
        },
        "trend_analysis": {
            "module": "sktime.transformations",
            "estimators": ["STLSeasonal", "KalmanFilter"],
            "default": "STLSeasonal",
        },
    }

    def __init__(self):
        """Initialize intent mapper."""
        self.intent_config = INTENT_CONFIG

    def map_intent(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Map entities to intent and operation.

        Parameters
        ----------
        entities : dict
            Extracted entities from voice query

        Returns
        -------
        dict
            Intent mapping with operation details:
            {
                "intent": str,
                "estimator": str,
                "module": str,
                "parameters": dict,
                "confidence": float,
            }
        """
        analysis_type = entities.get("analysis_type", "forecast")
        time_horizon = entities.get("time_horizon", 30)

        # Get intent configuration
        intent_info = self.INTENT_ESTIMATORS.get(
            analysis_type, self.INTENT_ESTIMATORS["forecast"]
        )

        # Select appropriate estimator
        estimator = self._select_estimator(
            analysis_type, time_horizon, entities
        )

        # Build operation parameters
        parameters = self._build_parameters(analysis_type, entities, time_horizon)

        result = {
            "intent": analysis_type,
            "estimator": estimator,
            "module": intent_info["module"],
            "parameters": parameters,
            "confidence": entities.get("confidence", 0.5),
        }

        logger.debug(f"Intent mapped: {result}")
        return result

    def _select_estimator(
        self, intent: str, time_horizon: int, entities: Dict[str, Any]
    ) -> str:
        """Select best estimator for given intent and data characteristics.

        Parameters
        ----------
        intent : str
            Analysis intent (forecast, classify, etc.)
        time_horizon : int
            Forecast horizon in days
        entities : dict
            Extracted entities

        Returns
        -------
        str
            Selected estimator name
        """
        intent_info = self.INTENT_ESTIMATORS.get(intent)
        if not intent_info:
            return self.INTENT_ESTIMATORS["forecast"]["default"]

        # For forecasting, select based on time horizon
        if intent == "forecast":
            if time_horizon <= 14:
                # Short-term: prefer ExponentialSmoothing
                return "ExponentialSmoothing"
            elif time_horizon <= 90:
                # Medium-term: ARIMA or StatsForecast
                return "ARIMA"
            else:
                # Long-term: StatsForecast
                return "StatsForecast"

        # For classification, use ShapeDTW
        elif intent == "classify":
            return "ShapeDTW"

        # For anomaly detection, use IForest
        elif intent == "anomaly_detect":
            return "IForest"

        # Default
        return intent_info.get("default", "ExponentialSmoothing")

    def _build_parameters(
        self, intent: str, entities: Dict[str, Any], time_horizon: int
    ) -> Dict[str, Any]:
        """Build operation parameters from entities.

        Parameters
        ----------
        intent : str
            Analysis intent
        entities : dict
            Extracted entities
        time_horizon : int
            Forecast horizon

        Returns
        -------
        dict
            Operation-specific parameters
        """
        parameters = {}

        if intent == "forecast":
            parameters = {
                "fh": time_horizon,  # forecast horizon
                "sp": self._estimate_seasonality(entities),  # seasonal period
            }

        elif intent == "classify":
            parameters = {
                "n_classes": None,  # Will be inferred from data
            }

        elif intent == "anomaly_detect":
            parameters = {
                "contamination": 0.1,  # 10% anomalies
            }

        elif intent == "trend_analysis":
            parameters = {
                "seasonal": True,
                "period": self._estimate_seasonality(entities),
            }

        return parameters

    def _estimate_seasonality(self, entities: Dict[str, Any]) -> int:
        """Estimate seasonality period based on entity information.

        Parameters
        ----------
        entities : dict
            Extracted entities

        Returns
        -------
        int
            Estimated seasonality period (days)
        """
        # For agricultural data, common seasonality is yearly (365 days)
        if entities.get("crop_type"):
            return 365  # Annual crop cycle

        # For temperature/weather, seasonal period is also yearly
        if entities.get("time_series_name") in ["temperature", "rainfall"]:
            return 365

        # For price/market data, monthly seasonality
        if entities.get("time_series_name") == "price":
            return 30

        # Default: no seasonality
        return 1

    def get_estimator_help(self, intent: str) -> str:
        """Get help text for estimators supporting given intent.

        Parameters
        ----------
        intent : str
            Analysis intent

        Returns
        -------
        str
            Help text
        """
        intent_info = self.INTENT_ESTIMATORS.get(intent)
        if not intent_info:
            return f"Intent '{intent}' not found"

        estimators = intent_info["estimators"]
        default = intent_info["default"]

        help_text = f"Intent: {intent}\n"
        help_text += f"Available estimators: {', '.join(estimators)}\n"
        help_text += f"Default: {default}"

        return help_text

    def validate_intent(self, intent: str) -> bool:
        """Validate if intent is supported.

        Parameters
        ----------
        intent : str
            Intent to validate

        Returns
        -------
        bool
            True if supported, False otherwise
        """
        return intent in self.INTENT_ESTIMATORS

    def get_supported_intents(self) -> list:
        """Get list of supported intents.

        Returns
        -------
        list
            Supported intent names
        """
        return list(self.INTENT_ESTIMATORS.keys())

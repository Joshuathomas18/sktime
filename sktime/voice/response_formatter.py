"""Format sktime results for voice response."""

import logging
from typing import Any, Dict, List, Optional

from sktime.voice.base import ResponseFormatterBase
from sktime.voice.config import LANGUAGE_SETTINGS, RESPONSE_CONFIG

logger = logging.getLogger(__name__)


class ResponseFormatter(ResponseFormatterBase):
    """Format sktime analysis results into natural language responses.

    Converts:
    - Forecast arrays → "next month prices will increase by 15%"
    - Classification results → "this time series is classified as GROWTH_TREND"
    - Anomaly detection → "2 anomalies detected on 2024-03-15 and 2024-04-02"
    - Trend analysis → "seasonal pattern detected with period of 365 days"
    """

    def __init__(self, language: str = "hi"):
        """Initialize response formatter.

        Parameters
        ----------
        language : str, default="hi"
            Target language for responses
        """
        super().__init__(language)
        self.language_config = LANGUAGE_SETTINGS.get(language, LANGUAGE_SETTINGS["en"])

    def format_response(
        self,
        result: Dict[str, Any],
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format result for voice response.

        Parameters
        ----------
        result : dict
            Sktime result (forecast, classification, etc.)
        intent : str, optional
            Type of analysis (forecast, classify, etc.)
        entities : dict, optional
            Original extracted entities for context

        Returns
        -------
        str
            Formatted response text
        """
        intent = intent or "forecast"

        if intent == "forecast":
            return self._format_forecast(result, entities)
        elif intent == "classify":
            return self._format_classification(result, entities)
        elif intent == "anomaly_detect":
            return self._format_anomaly(result, entities)
        elif intent == "trend_analysis":
            return self._format_trend(result, entities)
        else:
            return self._format_generic(result)

    def _format_forecast(
        self,
        result: Dict[str, Any],
        entities: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format forecast result as voice response.

        Parameters
        ----------
        result : dict
            Forecast result
        entities : dict, optional
            Context entities

        Returns
        -------
        str
            Formatted forecast response
        """
        try:
            forecast_values = result.get("forecast", [])
            if isinstance(forecast_values, (list, tuple)) and len(forecast_values) > 0:
                first_val = float(forecast_values[0])
                last_val = float(forecast_values[-1])
                change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

                ts_name = entities.get("time_series_name", "value") if entities else "value"

                if self.language == "hi":
                    return self._format_forecast_hindi(
                        forecast_values, change_pct, ts_name
                    )
                elif self.language == "en":
                    return self._format_forecast_english(
                        forecast_values, change_pct, ts_name
                    )
                else:
                    return self._format_forecast_english(
                        forecast_values, change_pct, ts_name
                    )

        except Exception as e:
            logger.error(f"Error formatting forecast: {str(e)}")
            return "Unable to format forecast result"

        return "No forecast data available"

    def _format_forecast_hindi(
        self, values: List[float], change_pct: float, ts_name: str
    ) -> str:
        """Format forecast in Hindi.

        Parameters
        ----------
        values : list
            Forecast values
        change_pct : float
            Percentage change from first to last value
        ts_name : str
            Time series name

        Returns
        -------
        str
            Hindi response
        """
        avg_val = sum(values) / len(values)
        change_direction = "badhega" if change_pct > 0 else "ghatega"
        change_magnitude = abs(change_pct)

        response = f"Aapke {ts_name} ka forecast dekhe to "
        response += f"average maan {avg_val:.1f} hoga. "
        response += f"Agle {len(values)} dinon mein "
        response += f"{change_magnitude:.0f}% {change_direction}. "

        # Add confidence note
        if change_magnitude < 5:
            response += "Yeh estimate thoda unsure hai."
        elif change_magnitude > 20:
            response += "Yeh bada badlav hoga."

        return response

    def _format_forecast_english(
        self, values: List[float], change_pct: float, ts_name: str
    ) -> str:
        """Format forecast in English.

        Parameters
        ----------
        values : list
            Forecast values
        change_pct : float
            Percentage change
        ts_name : str
            Time series name

        Returns
        -------
        str
            English response
        """
        avg_val = sum(values) / len(values)
        change_direction = "increase" if change_pct > 0 else "decrease"
        change_magnitude = abs(change_pct)

        response = f"Based on the data, {ts_name} forecast shows "
        response += f"an average of {avg_val:.1f}. "
        response += f"Over the next {len(values)} days, we expect a "
        response += f"{change_magnitude:.0f}% {change_direction}. "

        if change_magnitude < 5:
            response += "This is a relatively stable forecast. "
        elif change_magnitude > 20:
            response += "This represents a significant change. "

        return response

    def _format_classification(
        self,
        result: Dict[str, Any],
        entities: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format classification result.

        Parameters
        ----------
        result : dict
            Classification result
        entities : dict, optional
            Context

        Returns
        -------
        str
            Formatted response
        """
        predicted_class = result.get("class", "unknown")
        confidence = result.get("confidence", 0.0)

        if self.language == "hi":
            return f"Ye time series {predicted_class} type ka hai. {confidence*100:.0f}% sure."
        else:
            return f"This time series is classified as {predicted_class}. Confidence: {confidence*100:.0f}%"

    def _format_anomaly(
        self,
        result: Dict[str, Any],
        entities: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format anomaly detection result.

        Parameters
        ----------
        result : dict
            Anomaly detection result
        entities : dict, optional
            Context

        Returns
        -------
        str
            Formatted response
        """
        anomalies = result.get("anomalies", [])
        num_anomalies = len(anomalies) if isinstance(anomalies, list) else 0

        if num_anomalies == 0:
            msg_hi = "Aapke data mein koi bhi anomaly nahi dikh raha."
            msg_en = "No anomalies detected in your data."
        else:
            msg_hi = f"Total {num_anomalies} anomalies detect hue."
            msg_en = f"Detected {num_anomalies} anomalies in the data."

        return msg_hi if self.language == "hi" else msg_en

    def _format_trend(
        self,
        result: Dict[str, Any],
        entities: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format trend analysis result.

        Parameters
        ----------
        result : dict
            Trend result
        entities : dict, optional
            Context

        Returns
        -------
        str
            Formatted response
        """
        trend = result.get("trend", "unknown")
        seasonality = result.get("seasonality", None)

        if self.language == "hi":
            response = f"Trend dekhe to {trend} dikhai de raha hai."
            if seasonality:
                response += f" {seasonality} din ka seasonal pattern hai."
            return response
        else:
            response = f"The trend is {trend}."
            if seasonality:
                response += f" Seasonality detected with {seasonality} day period."
            return response

    def _format_generic(self, result: Dict[str, Any]) -> str:
        """Generic result formatting.

        Parameters
        ----------
        result : dict
            Result

        Returns
        -------
        str
            Formatted response
        """
        return "Analysis completed. Please check the detailed results."

    def format_error(self, error: str, language: Optional[str] = None) -> str:
        """Format error message for voice response.

        Parameters
        ----------
        error : str
            Error message
        language : str, optional
            Response language

        Returns
        -------
        str
            Formatted error message
        """
        language = language or self.language

        if language == "hi":
            return f"Maafi chahta hu, ek error aaya: {error}"
        else:
            return f"Sorry, an error occurred: {error}"

    def round_values(self, values: List[float], decimals: int = 2) -> List[float]:
        """Round values for display.

        Parameters
        ----------
        values : list
            Values to round
        decimals : int, default=2
            Number of decimal places

        Returns
        -------
        list
            Rounded values
        """
        return [round(v, decimals) for v in values]

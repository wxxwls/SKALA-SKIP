"""Carbon forecasting service."""
from typing import List, Dict

import pandas as pd

from ai.models.forecast_carbon import CarbonForecastModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class CarbonForecastService:
    """Service for carbon emission and price forecasting."""

    def __init__(self) -> None:
        self._model = CarbonForecastModel()

    def forecast_emissions(
        self,
        historical_data: pd.DataFrame,
        periods: int = 12,
    ) -> List[Dict]:
        """Forecast carbon emissions."""
        logger.info(f"Forecasting emissions for {periods} periods")
        return self._model.predict_emissions(historical_data, periods)

    def forecast_price(
        self,
        historical_prices: pd.DataFrame,
        periods: int = 12,
    ) -> List[Dict]:
        """Forecast carbon prices."""
        logger.info(f"Forecasting carbon prices for {periods} periods")
        return self._model.predict_carbon_price(historical_prices, periods)

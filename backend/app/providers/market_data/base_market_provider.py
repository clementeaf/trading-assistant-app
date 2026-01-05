"""
Interfaz base para proveedores de datos de mercado
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.models.market_analysis import PriceCandle


class MarketDataProvider(ABC):
    """Interfaz abstracta para proveedores de datos de mercado"""
    
    @abstractmethod
    async def fetch_historical_candles(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> list[PriceCandle]:
        """
        Obtiene velas históricas para un instrumento
        @param instrument - Símbolo del instrumento (ej: XAUUSD, EURUSD)
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas (1h, 15m, etc.)
        @returns Lista de velas de precio
        """
        pass


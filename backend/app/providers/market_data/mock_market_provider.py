"""
Proveedor mock para datos de mercado (desarrollo y testing)
"""
from datetime import datetime, timedelta, time
from typing import Optional

from app.models.market_analysis import PriceCandle
from app.providers.market_data.base_market_provider import MarketDataProvider


class MockMarketProvider(MarketDataProvider):
    """Proveedor mock que genera datos de mercado simulados"""
    
    async def fetch_historical_candles(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> list[PriceCandle]:
        """
        Genera velas mock para un rango de fechas
        @param instrument - Símbolo del instrumento
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas
        @returns Lista de velas mock
        """
        candles: list[PriceCandle] = []
        
        # Precio base según instrumento
        base_prices = {
            "XAUUSD": 2650.0,
            "EURUSD": 1.0850,
            "NASDAQ": 15000.0,
            "DXY": 104.50,  # Índice del dólar típicamente entre 90-110
            "US10Y": 4.25,  # Rendimiento del bono a 10 años en porcentaje
            "US02Y": 4.50,  # Rendimiento del bono a 2 años en porcentaje
            "US30Y": 4.40   # Rendimiento del bono a 30 años en porcentaje
        }
        base_price = base_prices.get(instrument.upper(), 100.0)
        
        current_time = start_date.replace(minute=0, second=0, microsecond=0)
        price = base_price
        
        while current_time <= end_date:
            # Simular variación de precio
            import random
            change = random.uniform(-0.5, 0.5)  # Cambio de hasta 0.5%
            price_change = price * (change / 100)
            
            open_price = price
            close_price = price + price_change
            high = max(open_price, close_price) + abs(price_change) * 0.3
            low = min(open_price, close_price) - abs(price_change) * 0.3
            
            candle = PriceCandle(
                timestamp=current_time,
                open=round(open_price, 5),
                high=round(high, 5),
                low=round(low, 5),
                close=round(close_price, 5),
                volume=random.uniform(1000, 10000)
            )
            
            candles.append(candle)
            price = close_price
            
            # Avanzar según intervalo
            if interval == "1h":
                current_time += timedelta(hours=1)
            elif interval == "15m":
                current_time += timedelta(minutes=15)
            else:
                current_time += timedelta(hours=1)
        
        return candles


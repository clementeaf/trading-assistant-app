"""
Proveedor de datos de mercado usando Alpha Vantage API
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

from app.models.market_analysis import PriceCandle
from app.providers.market_data.base_market_provider import MarketDataProvider

class AlphaVantageProvider(MarketDataProvider):
    """Proveedor de datos de mercado usando Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    # Mapeo de instrumentos a símbolos de Alpha Vantage
    # NOTA: Esta app está enfocada en XAUUSD (oro) y factores que lo impactan
    INSTRUMENT_MAPPING = {
        "XAUUSD": "XAU/USD",  # Oro - objetivo principal (requiere premium en Alpha Vantage)
        "DXY": "DXY",  # Dollar Index - impacta XAUUSD (inversamente correlacionado)
        "US10Y": "US10Y",  # Bono 10 años - impacta XAUUSD (inversamente correlacionado)
        "US02Y": "US02Y",  # Bono 2 años - impacta XAUUSD
        "US30Y": "US30Y",  # Bono 30 años - impacta XAUUSD
        "NASDAQ": "NASDAQ",  # Índice de riesgo - contexto para XAUUSD
        # Pares de divisas estándar (no nos interesan, solo para referencia)
        "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD",
        "USDJPY": "USD/JPY",
        "AUDUSD": "AUD/USD",
        "USDCAD": "USD/CAD",
        "USDCHF": "USD/CHF",
    }
    
    # Mapeo de intervalos
    INTERVAL_MAPPING = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "60min",
        "4h": "240min",
        "1d": "daily",
    }
    
    def __init__(self, api_key: str):
        """
        Inicializa el proveedor de Alpha Vantage
        @param api_key - API key de Alpha Vantage
        """
        if not api_key:
            raise ValueError("Alpha Vantage API key is required")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    async def fetch_historical_candles(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> list[PriceCandle]:
        """
        Obtiene velas históricas para un instrumento usando Alpha Vantage
        @param instrument - Símbolo del instrumento (ej: XAUUSD, EURUSD)
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas (1h, 15m, etc.)
        @returns Lista de velas de precio
        """
        instrument_upper = instrument.upper()
        symbol = self.INSTRUMENT_MAPPING.get(instrument_upper, instrument_upper)
        
        # Alpha Vantage tiene limitaciones para XAUUSD (nuestro objetivo principal)
        # XAU/USD requiere plan premium en Alpha Vantage
        # DXY, bonos e índices tampoco están disponibles directamente
        # Para estos casos, el servicio usa el mock provider como fallback
        if instrument_upper in ["DXY", "US10Y", "US02Y", "US30Y", "NASDAQ"]:
            logger.warning(
                f"Alpha Vantage may not support {instrument_upper} directly. "
                f"Consider using a different provider for this instrument."
            )
        
        # Alpha Vantage tiene límites: máximo 1000 datos por request
        # Para datos intradía, necesitamos usar TIME_SERIES_INTRADAY
        # Para datos diarios, usamos TIME_SERIES_DAILY
        
        interval_mapped = self.INTERVAL_MAPPING.get(interval.lower(), "60min")
        
        # Determinar si usar intradía o diario
        # Nota: FX_INTRADAY requiere plan premium, así que intentamos primero intradía
        # y si falla, usamos datos diarios
        use_intraday = interval_mapped in ["1min", "5min", "15min", "30min", "60min", "240min"]
        
        candles: list[PriceCandle] = []
        
        try:
            if use_intraday:
                try:
                    candles = await self._fetch_intraday_data(
                        symbol, start_date, end_date, interval_mapped, instrument_upper
                    )
                except ValueError as e:
                    if "premium" in str(e).lower():
                        logger.info(
                            f"FX_INTRADAY requires premium, falling back to daily data for {instrument}"
                        )
                        # Intentar con datos diarios como fallback
                        candles = await self._fetch_daily_data(
                            symbol, start_date, end_date, instrument_upper
                        )
                    else:
                        raise
            else:
                candles = await self._fetch_daily_data(
                    symbol, start_date, end_date, instrument_upper
                )
            
            # Filtrar por rango de fechas
            filtered_candles = [
                candle for candle in candles
                if start_date <= candle.timestamp <= end_date
            ]
            
            logger.info(
                f"Fetched {len(filtered_candles)} candles for {instrument} "
                f"from Alpha Vantage (interval: {interval})"
            )
            
            return sorted(filtered_candles, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error fetching data from Alpha Vantage: {str(e)}")
            raise ValueError(f"Failed to fetch market data from Alpha Vantage: {str(e)}")
    
    @property
    def client(self) -> httpx.AsyncClient:
        """
        Obtiene o crea el cliente HTTP
        @returns Cliente HTTP asíncrono
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def _fetch_intraday_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        original_instrument: str
    ) -> list[PriceCandle]:
        """
        Obtiene datos intradía de Alpha Vantage
        @param symbol - Símbolo del instrumento
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo mapeado
        @returns Lista de velas
        """
        # Alpha Vantage intradía solo devuelve datos del último mes
        # Para datos históricos más antiguos, necesitaríamos usar otro endpoint
        
        # Alpha Vantage soporta forex con FX_INTRADAY
        # Para otros instrumentos, usar TIME_SERIES_INTRADAY (solo acciones)
        is_forex = "/" in symbol
        
        if is_forex:
            params = {
                "function": "FX_INTRADAY",
                "from_symbol": symbol.split("/")[0],
                "to_symbol": symbol.split("/")[1],
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": "full",
                "datatype": "json"
            }
        else:
            # Para instrumentos no-forex, intentar usar TIME_SERIES_INTRADAY
            # Nota: Esto solo funciona para acciones, no para índices o bonos
            # Si no es forex y no es una acción conocida, lanzar error
            if original_instrument in ["DXY", "US10Y", "US02Y", "US30Y", "NASDAQ"]:
                raise ValueError(
                    f"Alpha Vantage does not support {original_instrument} directly. "
                    f"Please use mock provider or a different market data provider."
                )
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": "full",
                "datatype": "json"
            }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verificar errores de API
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
        if "Note" in data:
            raise ValueError(f"Alpha Vantage API rate limit: {data['Note']}")
        
        # Verificar si es un endpoint premium
        if "Information" in data and "premium" in data["Information"].lower():
            logger.warning(f"Alpha Vantage premium endpoint required: {data['Information']}")
            raise ValueError(
                f"Alpha Vantage premium endpoint required. "
                f"FX_INTRADAY requires a premium subscription. "
                f"Falling back to daily data or mock provider."
            )
        
        # Extraer datos de la respuesta
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key or "Time Series FX" in key or "FX Intraday" in key:
                time_series_key = key
                break
        
        if not time_series_key:
            # Log todas las claves disponibles para debugging
            logger.warning(f"Available keys in Alpha Vantage response: {list(data.keys())}")
            raise ValueError("No time series data found in Alpha Vantage response")
        
        time_series = data[time_series_key]
        candles: list[PriceCandle] = []
        
        for timestamp_str, values in time_series.items():
            try:
                # Parsear timestamp (formato puede variar)
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    logger.warning(f"Could not parse timestamp: {timestamp_str}")
                    continue
            
            # Extraer valores OHLC
            open_key = "1. open" if "1. open" in values else "open"
            high_key = "2. high" if "2. high" in values else "high"
            low_key = "3. low" if "3. low" in values else "low"
            close_key = "4. close" if "4. close" in values else "close"
            volume_key = "5. volume" if "5. volume" in values else "volume"
            
            candles.append(PriceCandle(
                timestamp=timestamp,
                open=float(values[open_key]),
                high=float(values[high_key]),
                low=float(values[low_key]),
                close=float(values[close_key]),
                volume=float(values.get(volume_key, 0))
            ))
        
        return candles
    
    async def _fetch_daily_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        original_instrument: str
    ) -> list[PriceCandle]:
        """
        Obtiene datos diarios de Alpha Vantage
        @param symbol - Símbolo del instrumento
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @returns Lista de velas
        """
        # Alpha Vantage soporta forex con FX_DAILY
        # Para otros instrumentos, usar TIME_SERIES_DAILY (solo acciones)
        is_forex = "/" in symbol
        
        if is_forex:
            params = {
                "function": "FX_DAILY",
                "from_symbol": symbol.split("/")[0],
                "to_symbol": symbol.split("/")[1],
                "apikey": self.api_key,
                "outputsize": "full",
                "datatype": "json"
            }
        else:
            # Para instrumentos no-forex, intentar usar TIME_SERIES_DAILY
            # Nota: Esto solo funciona para acciones, no para índices o bonos
            # Si no es forex y no es una acción conocida, lanzar error
            if original_instrument in ["DXY", "US10Y", "US02Y", "US30Y", "NASDAQ"]:
                raise ValueError(
                    f"Alpha Vantage does not support {original_instrument} directly. "
                    f"Please use mock provider or a different market data provider."
                )
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "full",
                "datatype": "json"
            }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verificar errores de API
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
        if "Note" in data:
            raise ValueError(f"Alpha Vantage API rate limit: {data['Note']}")
        
        # Verificar si es un endpoint premium
        if "Information" in data and "premium" in data["Information"].lower():
            logger.warning(f"Alpha Vantage premium endpoint required: {data['Information']}")
            raise ValueError(
                f"Alpha Vantage premium endpoint required. "
                f"FX_INTRADAY requires a premium subscription. "
                f"Falling back to daily data or mock provider."
            )
        
        # Extraer datos de la respuesta
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key or "Time Series FX" in key or "FX Intraday" in key:
                time_series_key = key
                break
        
        if not time_series_key:
            # Log todas las claves disponibles para debugging
            logger.warning(f"Available keys in Alpha Vantage response: {list(data.keys())}")
            raise ValueError("No time series data found in Alpha Vantage response")
        
        time_series = data[time_series_key]
        candles: list[PriceCandle] = []
        
        for date_str, values in time_series.items():
            try:
                timestamp = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                continue
            
            # Extraer valores OHLC
            open_key = "1. open" if "1. open" in values else "open"
            high_key = "2. high" if "2. high" in values else "high"
            low_key = "3. low" if "3. low" in values else "low"
            close_key = "4. close" if "4. close" in values else "close"
            volume_key = "5. volume" if "5. volume" in values else "volume"
            
            candles.append(PriceCandle(
                timestamp=timestamp,
                open=float(values[open_key]),
                high=float(values[high_key]),
                low=float(values[low_key]),
                close=float(values[close_key]),
                volume=float(values.get(volume_key, 0))
            ))
        
        return candles


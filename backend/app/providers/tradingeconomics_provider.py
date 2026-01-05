"""
Proveedor para TradingEconomics API
"""
import logging
from datetime import date, datetime
from typing import Optional

import httpx

from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.providers.base_provider import EconomicCalendarProvider

logger = logging.getLogger(__name__)


class TradingEconomicsProvider(EconomicCalendarProvider):
    """Proveedor para la API de TradingEconomics"""
    
    def __init__(self, api_key: Optional[str], api_url: str):
        """
        Inicializa el proveedor de TradingEconomics
        @param api_key - API key para TradingEconomics
        @param api_url - URL base de la API
        """
        self.api_key = api_key
        self.api_url = api_url
    
    async def fetch_events(
        self,
        target_date: date,
        currency: Optional[str] = None
    ) -> list[EconomicEvent]:
        """
        Obtiene eventos económicos de TradingEconomics para una fecha específica
        @param target_date - Fecha objetivo
        @param currency - Moneda para filtrar (opcional)
        @returns Lista de eventos económicos
        """
        if not self.api_key:
            logger.warning("TradingEconomics API key not configured")
            return []
        
        try:
            params = {
                "d1": target_date.isoformat(),
                "d2": target_date.isoformat(),
            }
            
            if currency:
                params["c"] = currency
            
            params["key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return self._parse_tradingeconomics_response(data)
        except httpx.HTTPStatusError as e:
            logger.error(f"TradingEconomics API error: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"TradingEconomics request error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from TradingEconomics: {str(e)}")
            return []
    
    def _parse_tradingeconomics_response(self, data: list[dict]) -> list[EconomicEvent]:
        """
        Parsea la respuesta de TradingEconomics a objetos EconomicEvent
        @param data - Datos en formato JSON de la API
        @returns Lista de eventos económicos parseados
        """
        events: list[EconomicEvent] = []
        
        for item in data:
            try:
                event_date = self._parse_date(item.get("Date", ""))
                if not event_date:
                    continue
                
                importance_str = item.get("Importance", "low").lower()
                importance = self._parse_importance(importance_str)
                
                event = EconomicEvent(
                    date=event_date,
                    importance=importance,
                    currency=item.get("Currency", ""),
                    description=item.get("Event", ""),
                    country=item.get("Country", None),
                    actual=self._parse_numeric_value(item.get("Actual")),
                    forecast=self._parse_numeric_value(item.get("Forecast")),
                    previous=self._parse_numeric_value(item.get("Previous"))
                )
                events.append(event)
            except (ValueError, KeyError, TypeError) as e:
                logger.debug(f"Error parsing event: {str(e)}")
                continue
        
        return events
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parsea una fecha en diferentes formatos
        @param date_str - String de fecha
        @returns Datetime parseado o None
        """
        if not date_str:
            return None
        
        try:
            if "T" in date_str:
                date_str = date_str.replace("Z", "+00:00")
                return datetime.fromisoformat(date_str)
            else:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                return parsed_date
        except (ValueError, AttributeError):
            return None
    
    def _parse_importance(self, importance_str: str) -> ImpactLevel:
        """
        Parsea el nivel de importancia
        @param importance_str - String de importancia
        @returns ImpactLevel
        """
        importance_map = {
            "low": ImpactLevel.LOW,
            "medium": ImpactLevel.MEDIUM,
            "med": ImpactLevel.MEDIUM,
            "high": ImpactLevel.HIGH,
            "1": ImpactLevel.LOW,
            "2": ImpactLevel.MEDIUM,
            "3": ImpactLevel.HIGH,
        }
        
        normalized = importance_str.lower().strip()
        return importance_map.get(normalized, ImpactLevel.LOW)
    
    def _parse_numeric_value(self, value: Optional[str | float | int]) -> Optional[float]:
        """
        Parsea un valor numérico de diferentes tipos
        @param value - Valor a parsear
        @returns Float o None
        """
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            try:
                return float(value.replace(",", ""))
            except (ValueError, AttributeError):
                return None
        
        return None


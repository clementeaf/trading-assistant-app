"""
Servicio para obtener y filtrar eventos del calendario económico
"""
from datetime import date, datetime
from typing import Optional

import httpx

from app.config.settings import Settings
from app.models.economic_calendar import EconomicEvent, HighImpactNewsResponse, ImpactLevel


class EconomicCalendarService:
    """Servicio para interactuar con APIs de calendario económico"""
    
    def __init__(self, settings: Settings):
        """
        Inicializa el servicio de calendario económico
        @param settings - Configuración de la aplicación
        """
        self.settings = settings
        self.api_key = settings.economic_calendar_api_key
        self.api_url = settings.economic_calendar_api_url
    
    async def get_high_impact_news_today(
        self,
        currency: Optional[str] = None
    ) -> HighImpactNewsResponse:
        """
        Obtiene noticias de alto impacto para el día actual
        @param currency - Moneda para filtrar (opcional, por defecto USD)
        @returns Respuesta con noticias de alto impacto
        """
        today = date.today()
        target_currency = currency or self.settings.default_currency
        
        events = await self._fetch_events_for_date(today, target_currency)
        
        high_impact_events = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
        ]
        
        has_news = len(high_impact_events) > 0
        summary = self._generate_summary(high_impact_events)
        
        return HighImpactNewsResponse(
            has_high_impact_news=has_news,
            count=len(high_impact_events),
            events=high_impact_events,
            summary=summary
        )
    
    async def _fetch_events_for_date(
        self,
        target_date: date,
        currency: Optional[str]
    ) -> list[EconomicEvent]:
        """
        Obtiene eventos económicos para una fecha específica
        @param target_date - Fecha objetivo
        @param currency - Moneda para filtrar (opcional)
        @returns Lista de eventos económicos
        """
        try:
            params = {
                "d1": target_date.isoformat(),
                "d2": target_date.isoformat(),
            }
            
            if currency:
                params["c"] = currency
            
            if self.api_key:
                params["key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return self._parse_events(data)
        except httpx.HTTPError as e:
            return self._get_mock_events_for_date(target_date, currency)
        except Exception:
            return self._get_mock_events_for_date(target_date, currency)
    
    def _parse_events(self, data: list[dict]) -> list[EconomicEvent]:
        """
        Parsea los datos de la API a objetos EconomicEvent
        @param data - Datos en formato JSON de la API
        @returns Lista de eventos económicos parseados
        """
        events: list[EconomicEvent] = []
        
        for item in data:
            try:
                event_date = datetime.fromisoformat(
                    item.get("Date", "").replace("Z", "+00:00")
                )
                
                importance_str = item.get("Importance", "low").lower()
                importance = ImpactLevel(importance_str) if importance_str in [
                    "low", "medium", "high"
                ] else ImpactLevel.LOW
                
                event = EconomicEvent(
                    date=event_date,
                    importance=importance,
                    currency=item.get("Currency", ""),
                    description=item.get("Event", ""),
                    country=item.get("Country", None),
                    actual=item.get("Actual", None),
                    forecast=item.get("Forecast", None),
                    previous=item.get("Previous", None)
                )
                events.append(event)
            except (ValueError, KeyError):
                continue
        
        return events
    
    def _get_mock_events_for_date(
        self,
        target_date: date,
        currency: Optional[str]
    ) -> list[EconomicEvent]:
        """
        Genera eventos mock para desarrollo/testing cuando la API no está disponible
        @param target_date - Fecha objetivo
        @param currency - Moneda para filtrar
        @returns Lista de eventos mock
        """
        mock_events: list[EconomicEvent] = []
        
        if target_date == date.today():
            mock_events.append(
                EconomicEvent(
                    date=datetime.combine(target_date, datetime.min.time()),
                    importance=ImpactLevel.HIGH,
                    currency=currency or "USD",
                    description="NFP - Non-Farm Payrolls",
                    country="US"
                )
            )
            mock_events.append(
                EconomicEvent(
                    date=datetime.combine(target_date, datetime.min.time()),
                    importance=ImpactLevel.HIGH,
                    currency=currency or "USD",
                    description="PMI Manufacturero",
                    country="US"
                )
            )
        
        return mock_events
    
    def _generate_summary(self, events: list[EconomicEvent]) -> str:
        """
        Genera un resumen textual de los eventos de alto impacto
        @param events - Lista de eventos de alto impacto
        @returns Resumen en formato texto
        """
        if not events:
            return "No hay noticias de alto impacto hoy."
        
        event_descriptions = [event.description for event in events]
        unique_descriptions = list(dict.fromkeys(event_descriptions))
        
        if len(unique_descriptions) == 1:
            return f"Hoy hay 1 noticia de alto impacto: {unique_descriptions[0]}."
        
        descriptions_text = ", ".join(unique_descriptions[:-1])
        last_description = unique_descriptions[-1]
        
        return (
            f"Hoy hay {len(events)} noticias de alto impacto: "
            f"{descriptions_text} y {last_description}."
        )


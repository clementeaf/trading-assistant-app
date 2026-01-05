"""
Servicio para obtener y filtrar eventos del calendario económico
"""
import logging
from datetime import date
from typing import Optional

from app.config.settings import Settings
from app.models.economic_calendar import EconomicEvent, HighImpactNewsResponse, ImpactLevel
from app.providers.base_provider import EconomicCalendarProvider
from app.providers.mock_provider import MockProvider
from app.providers.tradingeconomics_provider import TradingEconomicsProvider

logger = logging.getLogger(__name__)


class EconomicCalendarService:
    """Servicio para interactuar con APIs de calendario económico"""
    
    def __init__(self, settings: Settings):
        """
        Inicializa el servicio de calendario económico
        @param settings - Configuración de la aplicación
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
    
    def _create_provider(self, settings: Settings) -> EconomicCalendarProvider:
        """
        Crea el proveedor de calendario económico según la configuración
        @param settings - Configuración de la aplicación
        @returns Instancia del proveedor
        """
        provider_name = settings.economic_calendar_provider.lower()
        
        if provider_name == "tradingeconomics":
            if not settings.economic_calendar_api_key:
                logger.warning(
                    "TradingEconomics provider selected but no API key configured. "
                    "Falling back to mock provider."
                )
                return MockProvider()
            
            return TradingEconomicsProvider(
                api_key=settings.economic_calendar_api_key,
                api_url=settings.economic_calendar_api_url
            )
        elif provider_name == "mock":
            logger.info("Using mock provider for economic calendar")
            return MockProvider()
        else:
            logger.warning(
                f"Unknown provider '{provider_name}'. Using mock provider."
            )
            return MockProvider()
    
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
        
        logger.info(
            f"Fetching high impact news for {today} with currency {target_currency}"
        )
        
        events = await self.provider.fetch_events(today, target_currency)
        
        if not events:
            logger.warning(f"No events found for {today}")
        
        high_impact_events = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
        ]
        
        logger.info(
            f"Found {len(high_impact_events)} high impact events out of "
            f"{len(events)} total events"
        )
        
        has_news = len(high_impact_events) > 0
        summary = self._generate_summary(high_impact_events)
        
        return HighImpactNewsResponse(
            has_high_impact_news=has_news,
            count=len(high_impact_events),
            events=high_impact_events,
            summary=summary
        )
    
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

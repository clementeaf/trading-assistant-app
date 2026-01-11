"""
Servicio para obtener y filtrar eventos del calendario económico
"""
import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.economic_calendar import (
    EconomicEvent,
    EventScheduleItem,
    EventScheduleResponse,
    HighImpactNewsResponse,
    ImpactLevel,
    UpcomingEvent,
    UpcomingEventsResponse,
)
from app.providers.base_provider import EconomicCalendarProvider
from app.providers.mock_provider import MockProvider
from app.providers.tradingeconomics_provider import TradingEconomicsProvider
from app.repositories.economic_events_repository import EconomicEventsRepository
from app.utils.schedule_formatter import ScheduleFormatter
from app.utils.xauusd_filter import XAUUSDFilter
from app.utils.business_days import BusinessDays
from app.utils.geopolitical_analyzer import GeopoliticalAnalyzer
from app.utils.event_categorizer import EventCategorizer

logger = logging.getLogger(__name__)


class EconomicCalendarService:
    """Servicio para interactuar con APIs de calendario económico"""

    def __init__(self, settings: Settings, llm_service: Optional[LLMService] = None, db: Optional[Session] = None):
        """
        Inicializa el servicio de calendario económico
        @param settings - Configuración de la aplicación
        @param llm_service - Servicio LLM para análisis de sentimiento (opcional)
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
        self.llm_service = llm_service
        self.db = db
        self.events_repo = EconomicEventsRepository(db) if db else None

    def _create_provider(self, settings: Settings) -> EconomicCalendarProvider:
        """
        Crea el proveedor de calendario económico según la configuración
        @param settings - Configuración de la aplicación
        @returns Instancia del proveedor
        """
        provider_name = settings.economic_calendar_provider.lower()

        if provider_name == "tradingeconomics":
            if not settings.economic_calendar_api_key:
                raise ValueError(
                    "TradingEconomics provider selected but no API key configured. "
                    "Please set ECONOMIC_CALENDAR_API_KEY environment variable. "
                    "Get your free API key at: https://tradingeconomics.com/api"
                )
            
            # Verificar que la API key no sea un placeholder
            invalid_keys = [
                "your_api_key_here", "your_key_here", "placeholder", ""
            ]
            if settings.economic_calendar_api_key.lower() in invalid_keys:
                raise ValueError(
                    "TradingEconomics API key appears to be a placeholder. "
                    "Please set a valid ECONOMIC_CALENDAR_API_KEY. "
                    "Get your free API key at: https://tradingeconomics.com/api"
                )

            logger.info("Using TradingEconomics provider for economic calendar (real data)")
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
        Obtiene noticias de alto impacto para XAUUSD del día actual
        @param currency - Moneda para filtrar (opcional, por defecto USD)
        @returns Respuesta con noticias de alto impacto relevantes para XAUUSD
        """
        # Usar día hábil actual (la Fed solo opera en días hábiles)
        today = date.today()
        if not BusinessDays.is_business_day(today):
            # Si hoy es fin de semana, usar el último día hábil
            today = BusinessDays.get_last_business_day(today)
            logger.info(f"Today is weekend/holiday, using last business day: {today}")
        
        target_currency = currency or "USD"

        logger.info(
            f"Fetching high impact news for XAUUSD on {today} (business day) "
            f"with currency {target_currency}"
        )

        # Intentar obtener de base de datos primero
        events: list[EconomicEvent] = []
        if self.events_repo:
            try:
                db_events = self.events_repo.get_events_by_date(
                    today, target_currency, ImpactLevel.HIGH
                )
                if db_events:
                    events = [
                        EconomicEvent(
                            date=event.event_date,
                            importance=ImpactLevel(event.importance),
                            currency=event.currency,
                            description=event.description,
                            country=event.country,
                            actual=event.actual,
                            forecast=event.forecast,
                            previous=event.previous,
                        )
                        for event in db_events
                    ]
                    logger.info(f"Found {len(events)} events in database")
            except Exception as e:
                logger.warning(f"Error fetching from database: {str(e)}")

        # Si no hay datos en DB, obtener del proveedor
        if not events:
            events = await self.provider.fetch_events(today, target_currency)
            # Guardar en base de datos
            if self.events_repo and events:
                try:
                    self.events_repo.save_events(events)
                except Exception as e:
                    logger.warning(f"Error saving events to database: {str(e)}")

        if not events:
            logger.warning(f"No events found for {today}")

        # Filtrar solo eventos de alto impacto
        high_impact_events = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
        ]

        # Filtrar eventos relevantes para XAUUSD
        xauusd_events = XAUUSDFilter.filter_xauusd_events(high_impact_events)

        logger.info(
            f"Found {len(xauusd_events)} XAUUSD-relevant high impact events out of "
            f"{len(high_impact_events)} high impact events and {len(events)} total events"
        )

        has_news = len(xauusd_events) > 0
        summary = self._generate_xauusd_summary(xauusd_events)
        
        # Analizar riesgo geopolítico
        geopolitical_risk = None
        try:
            geopolitical_risk = GeopoliticalAnalyzer.analyze_risk(xauusd_events)
            logger.info(
                f"Geopolitical risk: {geopolitical_risk.level.value} "
                f"(score: {geopolitical_risk.score:.2f})"
            )
        except Exception as e:
            logger.warning(f"Could not analyze geopolitical risk: {str(e)}")

        return HighImpactNewsResponse(
            has_high_impact_news=has_news,
            count=len(xauusd_events),
            events=xauusd_events,
            summary=summary,
            instrument="XAUUSD",
            geopolitical_risk=geopolitical_risk
        )

    async def get_event_schedule_today(
        self,
        currency: Optional[str] = None,
        include_gold_impact: bool = True,
        include_sentiment: bool = False,
        sentiment_language: str = "es"
    ) -> EventScheduleResponse:
        """
        Obtiene el calendario de eventos para el día actual, formateado para mostrar horarios
        @param currency - Moneda para filtrar (opcional, por defecto USD)
        @param include_gold_impact - Si incluir estimación de impacto en Gold
        @param include_sentiment - Si incluir análisis de sentimiento LLM (requiere OPENAI_API_KEY)
        @param sentiment_language - Idioma para análisis de sentimiento (es, en)
        @returns Respuesta con el calendario de eventos
        """
        # Usar día hábil actual (la Fed solo opera en días hábiles)
        today = date.today()
        if not BusinessDays.is_business_day(today):
            # Si hoy es fin de semana, usar el último día hábil
            today = BusinessDays.get_last_business_day(today)
            logger.info(f"Today is weekend/holiday, using last business day: {today}")
        
        target_currency = currency or "USD"

        logger.info(
            f"Fetching event schedule for {today} (business day) "
            f"with currency {target_currency}, include_gold_impact={include_gold_impact}"
        )

        # Intentar obtener de base de datos primero
        events: list[EconomicEvent] = []
        if self.events_repo:
            try:
                db_events = self.events_repo.get_events_by_date(
                    today, target_currency, ImpactLevel.HIGH
                )
                if db_events:
                    events = [
                        EconomicEvent(
                            date=event.event_date,
                            importance=ImpactLevel(event.importance),
                            currency=event.currency,
                            description=event.description,
                            country=event.country,
                            actual=event.actual,
                            forecast=event.forecast,
                            previous=event.previous,
                        )
                        for event in db_events
                    ]
            except Exception as e:
                logger.warning(f"Error fetching from database: {str(e)}")

        # Si no hay datos en DB, obtener del proveedor
        if not events:
            events = await self.provider.fetch_events(today, target_currency)
            # Guardar en base de datos
            if self.events_repo and events:
                try:
                    self.events_repo.save_events(events)
                except Exception as e:
                    logger.warning(f"Error saving events to database: {str(e)}")

        if not events:
            logger.warning(f"No events found for {today}")

        # Filtrar solo eventos de alto impacto para el schedule
        high_impact_events = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
        ]

        # Formatear y ordenar eventos
        formatted_events = ScheduleFormatter.format_events_for_schedule(
            high_impact_events,
            target_currency,
            include_gold_impact=include_gold_impact
        )
        
        # Analizar sentimiento con LLM si está habilitado
        if include_sentiment and self.llm_service:
            logger.info(f"Analyzing sentiment for {len(formatted_events)} events")
            for event in formatted_events:
                try:
                    sentiment_str = await self.llm_service.analyze_news_sentiment(
                        news_title=event.description,
                        news_currency=event.currency,
                        language=sentiment_language
                    )
                    event.sentiment = NewsSentiment(sentiment_str.lower())
                    logger.debug(f"Event '{event.description}' sentiment: {event.sentiment}")
                except Exception as e:
                    logger.warning(f"Failed to analyze sentiment for '{event.description}': {str(e)}")
                    event.sentiment = NewsSentiment.NEUTRAL  # Default fallback

        usd_events_count = sum(1 for event in formatted_events if event.affects_usd)

        logger.info(
            f"Found {len(formatted_events)} events for schedule out of "
            f"{len(events)} total events"
        )

        return EventScheduleResponse(
            date=today.isoformat(),
            events=formatted_events,
            usd_events_count=usd_events_count,
            total_events=len(formatted_events)
        )

    async def get_upcoming_high_impact_news(
        self,
        time_window_minutes: int = 120,
        currency: str = "USD"
    ) -> list[EconomicEvent]:
        """
        Obtiene noticias de alto impacto próximas en una ventana de tiempo
        @param time_window_minutes - Ventana de tiempo en minutos
        @param currency - Moneda para filtrar
        @returns Lista de eventos próximos de alto impacto
        """
        from datetime import datetime, timedelta

        now = datetime.now()
        end_time = now + timedelta(minutes=time_window_minutes)
        today = date.today()

        # Intentar obtener de base de datos
        events: list[EconomicEvent] = []
        if self.events_repo:
            try:
                db_events = self.events_repo.get_events_by_date(
                    today, currency, ImpactLevel.HIGH
                )
                if db_events:
                    events = [
                        EconomicEvent(
                            date=event.event_date,
                            importance=ImpactLevel(event.importance),
                            currency=event.currency,
                            description=event.description,
                            country=event.country,
                            actual=event.actual,
                            forecast=event.forecast,
                            previous=event.previous,
                        )
                        for event in db_events
                    ]
            except Exception as e:
                logger.warning(f"Error fetching from database: {str(e)}")

        # Si no hay datos en DB, obtener del proveedor
        if not events:
            events = await self.provider.fetch_events(today, currency)

        upcoming_events = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
            and now <= event.date <= end_time
        ]
        return upcoming_events

    def _generate_xauusd_summary(self, events: list[EconomicEvent]) -> str:
        """
        Genera un resumen textual de los eventos de alto impacto para XAUUSD
        @param events - Lista de eventos de alto impacto relevantes para XAUUSD
        @returns Resumen en formato texto
        """
        if not events:
            return "No hay noticias de alto impacto para XAUUSD hoy."

        event_descriptions = [event.description for event in events]
        unique_descriptions = list(dict.fromkeys(event_descriptions))

        if len(unique_descriptions) == 1:
            return (
                f"Hoy hay 1 noticia de alto impacto para XAUUSD: "
                f"{unique_descriptions[0]}."
            )

        descriptions_text = ", ".join(unique_descriptions[:-1])
        last_description = unique_descriptions[-1]

        return (
            f"Hoy hay {len(events)} noticias de alto impacto para XAUUSD: "
            f"{descriptions_text} y {last_description}."
        )
    
    async def get_upcoming_events(
        self,
        days: int = 7,
        currency: str = "USD",
        min_impact: ImpactLevel = ImpactLevel.MEDIUM
    ) -> UpcomingEventsResponse:
        """
        Obtiene eventos económicos futuros con countdown
        
        Args:
            days: Número de días a consultar (default: 7)
            currency: Moneda para filtrar (default: USD)
            min_impact: Impacto mínimo (default: MEDIUM)
        
        Returns:
            UpcomingEventsResponse: Eventos futuros con countdown y metadata
        """
        from datetime import datetime, timedelta
        
        logger.info(f"Fetching upcoming events for next {days} days (currency={currency}, min_impact={min_impact})")
        
        now = datetime.now()
        today = now.date()
        
        # Obtener eventos de los próximos N días
        all_events: list[EconomicEvent] = []
        
        for i in range(days + 1):
            target_date = today + timedelta(days=i)
            
            # Skip weekends
            if not BusinessDays.is_business_day(target_date):
                continue
            
            try:
                # Obtener eventos del día
                events = await self.provider.fetch_events(target_date, currency)
                
                # Categorizar eventos automáticamente
                for event in events:
                    if not hasattr(event, 'event_type') or event.event_type is None:
                        event.event_type = EventCategorizer.categorize(
                            event.description,
                            event.country
                        )
                
                # Filtrar por impacto mínimo
                filtered_events = [
                    event for event in events
                    if self._meets_min_impact(event.importance, min_impact)
                ]
                
                all_events.extend(filtered_events)
                
            except Exception as e:
                logger.warning(f"Error fetching events for {target_date}: {str(e)}")
                continue
        
        # Crear UpcomingEvent para cada evento
        upcoming_events: list[UpcomingEvent] = []
        
        for event in all_events:
            # Calcular countdown
            time_until = event.date - now
            days_until = time_until.days
            hours_until = int(time_until.total_seconds() / 3600) if days_until < 2 else None
            
            # Calcular flags
            is_today = event.date.date() == today
            is_tomorrow = event.date.date() == (today + timedelta(days=1))
            is_this_week = days_until <= 7
            
            # Obtener tier y hora típica
            tier = EventCategorizer.get_tier(event.event_type)
            typical_time = EventCategorizer.get_typical_time_et(event.event_type)
            
            upcoming_event = UpcomingEvent(
                event=event,
                days_until=days_until,
                hours_until=hours_until,
                is_today=is_today,
                is_tomorrow=is_tomorrow,
                is_this_week=is_this_week,
                tier=tier,
                typical_time_et=typical_time
            )
            
            upcoming_events.append(upcoming_event)
        
        # Ordenar por fecha (más cercano primero)
        upcoming_events.sort(key=lambda e: e.event.date)
        
        # Encontrar próximo evento de alto impacto (Tier 1-2)
        next_high_impact = next(
            (e for e in upcoming_events if e.tier <= 2),
            None
        )
        
        # Generar resumen
        summary = self._generate_upcoming_summary(upcoming_events, next_high_impact)
        
        logger.info(f"Found {len(upcoming_events)} upcoming events in next {days} days")
        
        return UpcomingEventsResponse(
            events=upcoming_events,
            total_events=len(upcoming_events),
            next_high_impact=next_high_impact,
            days_range=days,
            summary=summary
        )
    
    def _meets_min_impact(self, event_impact: ImpactLevel, min_impact: ImpactLevel) -> bool:
        """
        Verifica si un evento cumple con el impacto mínimo requerido
        
        Args:
            event_impact: Impacto del evento
            min_impact: Impacto mínimo requerido
        
        Returns:
            bool: True si cumple con el mínimo
        """
        impact_order = {
            ImpactLevel.LOW: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.HIGH: 3
        }
        
        return impact_order.get(event_impact, 0) >= impact_order.get(min_impact, 0)
    
    def _generate_upcoming_summary(
        self,
        events: list[UpcomingEvent],
        next_high_impact: Optional[UpcomingEvent]
    ) -> str:
        """
        Genera resumen de eventos futuros
        
        Args:
            events: Lista de eventos futuros
            next_high_impact: Próximo evento de alto impacto
        
        Returns:
            str: Resumen textual
        """
        if not events:
            return "No hay eventos económicos significativos en los próximos días."
        
        # Contar eventos por tier
        tier1_count = sum(1 for e in events if e.tier == 1)
        tier2_count = sum(1 for e in events if e.tier == 2)
        
        # Construir resumen
        parts = []
        
        if tier1_count > 0:
            parts.append(f"{tier1_count} evento(s) de máximo impacto")
        
        if tier2_count > 0:
            parts.append(f"{tier2_count} evento(s) de alto impacto")
        
        if not parts:
            return f"Próximos {len(events)} eventos económicos de impacto medio."
        
        summary = f"Próximos {len(events)} eventos: {' y '.join(parts)}."
        
        # Agregar info del próximo evento importante
        if next_high_impact:
            event_name = next_high_impact.event.description
            if next_high_impact.is_today:
                summary += f" Hoy: {event_name}."
            elif next_high_impact.is_tomorrow:
                summary += f" Mañana: {event_name}."
            else:
                summary += f" En {next_high_impact.days_until} días: {event_name}."
        
        return summary

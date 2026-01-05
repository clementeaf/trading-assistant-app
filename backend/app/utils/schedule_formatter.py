"""
Utilidades para formatear eventos en formato de calendario
"""
from datetime import datetime

from app.models.economic_calendar import EconomicEvent, EventScheduleItem, ImpactLevel


class ScheduleFormatter:
    """Formateador de eventos para calendario"""
    
    IMPACT_TRANSLATIONS = {
        ImpactLevel.HIGH: "Alto impacto",
        ImpactLevel.MEDIUM: "Medio impacto",
        ImpactLevel.LOW: "Bajo impacto"
    }
    
    @classmethod
    def format_event(cls, event: EconomicEvent) -> EventScheduleItem:
        """
        Formatea un evento en formato de calendario
        @param event - Evento económico a formatear
        @returns EventScheduleItem formateado
        """
        time_str = event.date.strftime("%H:%M")
        impact_str = cls.IMPACT_TRANSLATIONS.get(event.importance, "Bajo impacto")
        affects_usd = event.currency.upper() == "USD"
        
        full_description = f"{time_str} – {event.description} – {event.currency} – {impact_str}"
        
        return EventScheduleItem(
            time=time_str,
            description=event.description,
            currency=event.currency,
            impact=impact_str,
            affects_usd=affects_usd,
            full_description=full_description
        )
    
    @classmethod
    def format_events(cls, events: list[EconomicEvent]) -> list[EventScheduleItem]:
        """
        Formatea una lista de eventos
        @param events - Lista de eventos económicos
        @returns Lista de EventScheduleItem formateados
        """
        return [cls.format_event(event) for event in events]


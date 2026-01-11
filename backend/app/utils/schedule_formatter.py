"""
Utilidades para formatear eventos en formato de calendario
"""
from datetime import datetime
from typing import Optional

from app.models.economic_calendar import EconomicEvent, EventScheduleItem, ImpactLevel
from app.utils.timezone_converter import TimezoneConverter
from app.utils.gold_impact_calculator import GoldImpactCalculator


class ScheduleFormatter:
    """Formateador de eventos para calendario"""
    
    IMPACT_TRANSLATIONS = {
        ImpactLevel.HIGH: "Alto impacto",
        ImpactLevel.MEDIUM: "Medio impacto",
        ImpactLevel.LOW: "Bajo impacto"
    }
    
    # Zonas horarias por defecto a mostrar
    DEFAULT_TIMEZONES = ["UTC", "ET", "PT"]
    
    @classmethod
    def format_event(
        cls,
        event: EconomicEvent,
        include_timezones: bool = True,
        timezones: Optional[list[str]] = None,
        include_gold_impact: bool = True,
        current_gold_price: Optional[float] = None
    ) -> EventScheduleItem:
        """
        Formatea un evento en formato de calendario
        @param event - Evento económico a formatear
        @param include_timezones - Si incluir conversión de zonas horarias
        @param timezones - Zonas a incluir (default: UTC, ET, PT)
        @param include_gold_impact - Si incluir estimación de impacto en Gold
        @param current_gold_price - Precio actual de Gold (opcional)
        @returns EventScheduleItem formateado
        """
        time_str = event.date.strftime("%H:%M")
        impact_str = cls.IMPACT_TRANSLATIONS.get(event.importance, "Bajo impacto")
        affects_usd = event.currency.upper() == "USD"
        
        full_description = f"{time_str} – {event.description} – {event.currency} – {impact_str}"
        
        # Generar zonas horarias si se solicita
        timezones_dict: dict[str, str] = {}
        formatted_time: Optional[str] = None
        
        if include_timezones:
            tz_list = timezones if timezones is not None else cls.DEFAULT_TIMEZONES
            try:
                timezones_dict = TimezoneConverter.format_multi_timezone(
                    time_str,
                    timezones=tz_list,
                    reference_date=event.date
                )
                formatted_time = TimezoneConverter.format_time_display(timezones_dict)
            except Exception:
                # Si falla conversión, continuar sin timezones
                pass
        
        # Calcular impacto en Gold si se solicita
        gold_impact = None
        if include_gold_impact:
            try:
                gold_impact = GoldImpactCalculator.calculate_impact(
                    event_name=event.description,
                    event_description=None,
                    importance=event.importance.value,
                    current_gold_price=current_gold_price
                )
            except Exception:
                # Si falla cálculo, continuar sin impacto
                pass
        
        return EventScheduleItem(
            time=time_str,
            description=event.description,
            currency=event.currency,
            impact=impact_str,
            affects_usd=affects_usd,
            full_description=full_description,
            timezones=timezones_dict,
            formatted_time=formatted_time,
            gold_impact=gold_impact
        )
    
    
    @classmethod
    def format_events(
        cls,
        events: list[EconomicEvent],
        include_timezones: bool = True,
        timezones: Optional[list[str]] = None,
        include_gold_impact: bool = True,
        current_gold_price: Optional[float] = None
    ) -> list[EventScheduleItem]:
        """
        Formatea una lista de eventos
        @param events - Lista de eventos económicos
        @param include_timezones - Si incluir conversión de zonas horarias
        @param timezones - Zonas a incluir (default: UTC, ET, PT)
        @param include_gold_impact - Si incluir estimación de impacto en Gold
        @param current_gold_price - Precio actual de Gold (opcional)
        @returns Lista de EventScheduleItem formateados
        """
        return [
            cls.format_event(
                event,
                include_timezones,
                timezones,
                include_gold_impact,
                current_gold_price
            )
            for event in events
        ]
    
    @classmethod
    def format_events_for_schedule(
        cls,
        events: list[EconomicEvent],
        currency: str = "USD",
        include_timezones: bool = True,
        timezones: Optional[list[str]] = None,
        include_gold_impact: bool = True,
        current_gold_price: Optional[float] = None
    ) -> list[EventScheduleItem]:
        """
        Formatea eventos para el calendario de eventos
        @param events - Lista de eventos económicos
        @param currency - Moneda para determinar si afecta USD
        @param include_timezones - Si incluir conversión de zonas horarias
        @param timezones - Zonas a incluir (default: UTC, ET, PT)
        @param include_gold_impact - Si incluir estimación de impacto en Gold
        @param current_gold_price - Precio actual de Gold (opcional)
        @returns Lista de EventScheduleItem formateados y ordenados
        """
        formatted = cls.format_events(
            events,
            include_timezones,
            timezones,
            include_gold_impact,
            current_gold_price
        )
        # Ordenar por hora
        formatted.sort(key=lambda x: x.time)
        return formatted


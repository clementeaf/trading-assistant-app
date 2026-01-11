"""
Tests de integración para zonas horarias en calendario económico
"""
import pytest
from datetime import datetime

from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.utils.schedule_formatter import ScheduleFormatter


class TestScheduleFormatterIntegration:
    """Tests de integración del formateador con zonas horarias"""
    
    def test_format_event_with_timezones_default(self):
        """Test formatear evento con zonas horarias default (UTC, ET, PT)"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),  # 10:30 UTC
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="Non-Farm Payrolls"
        )
        
        result = ScheduleFormatter.format_event(event, include_timezones=True)
        
        assert result.time == "10:30"
        assert result.description == "Non-Farm Payrolls"
        assert result.affects_usd is True
        
        # Verificar zonas horarias
        assert "UTC" in result.timezones
        assert "ET" in result.timezones
        assert "PT" in result.timezones
        assert result.timezones["UTC"] == "10:30"
        assert result.timezones["ET"] == "05:30"  # EST es UTC-5 en enero
        assert result.timezones["PT"] == "02:30"  # PST es UTC-8 en enero
        
        # Verificar formato display
        assert result.formatted_time is not None
        assert "10:30 UTC" in result.formatted_time
        assert "05:30 ET" in result.formatted_time
        assert "02:30 PT" in result.formatted_time
    
    def test_format_event_with_custom_timezones(self):
        """Test formatear evento con zonas horarias custom"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 14, 00),  # 14:00 UTC
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="FOMC Decision"
        )
        
        result = ScheduleFormatter.format_event(
            event,
            include_timezones=True,
            timezones=["UTC", "JST", "GMT"]
        )
        
        assert "UTC" in result.timezones
        assert "JST" in result.timezones
        assert "GMT" in result.timezones
        assert result.timezones["UTC"] == "14:00"
        assert result.timezones["JST"] == "23:00"  # JST es UTC+9
        assert result.timezones["GMT"] == "14:00"  # GMT = UTC en invierno
    
    def test_format_event_without_timezones(self):
        """Test formatear evento sin zonas horarias"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),
            importance=ImpactLevel.MEDIUM,
            currency="EUR",
            description="ECB Meeting"
        )
        
        result = ScheduleFormatter.format_event(event, include_timezones=False)
        
        assert result.time == "10:30"
        assert result.timezones == {}
        assert result.formatted_time is None
    
    def test_format_events_list_with_timezones(self):
        """Test formatear lista de eventos con zonas horarias"""
        events = [
            EconomicEvent(
                date=datetime(2026, 1, 11, 8, 30),
                importance=ImpactLevel.HIGH,
                currency="USD",
                description="Jobless Claims"
            ),
            EconomicEvent(
                date=datetime(2026, 1, 11, 10, 30),
                importance=ImpactLevel.HIGH,
                currency="USD",
                description="NFP"
            ),
        ]
        
        results = ScheduleFormatter.format_events(events, include_timezones=True)
        
        assert len(results) == 2
        
        # Verificar primer evento
        assert results[0].time == "08:30"
        assert "UTC" in results[0].timezones
        assert "ET" in results[0].timezones
        
        # Verificar segundo evento
        assert results[1].time == "10:30"
        assert "UTC" in results[1].timezones
        assert "ET" in results[1].timezones
    
    def test_format_events_for_schedule_sorted(self):
        """Test que eventos estén ordenados por hora"""
        events = [
            EconomicEvent(
                date=datetime(2026, 1, 11, 14, 00),
                importance=ImpactLevel.HIGH,
                currency="USD",
                description="FOMC"
            ),
            EconomicEvent(
                date=datetime(2026, 1, 11, 8, 30),
                importance=ImpactLevel.HIGH,
                currency="USD",
                description="Jobless Claims"
            ),
            EconomicEvent(
                date=datetime(2026, 1, 11, 10, 30),
                importance=ImpactLevel.HIGH,
                currency="USD",
                description="NFP"
            ),
        ]
        
        results = ScheduleFormatter.format_events_for_schedule(
            events,
            include_timezones=True
        )
        
        # Verificar orden: 08:30, 10:30, 14:00
        assert results[0].time == "08:30"
        assert results[1].time == "10:30"
        assert results[2].time == "14:00"
        
        # Todos deben tener zonas horarias
        for result in results:
            assert "UTC" in result.timezones
            assert result.formatted_time is not None
    
    def test_format_event_affects_usd(self):
        """Test detección de eventos que afectan USD"""
        usd_event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="NFP"
        )
        
        eur_event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),
            importance=ImpactLevel.HIGH,
            currency="EUR",
            description="ECB Decision"
        )
        
        usd_result = ScheduleFormatter.format_event(usd_event)
        eur_result = ScheduleFormatter.format_event(eur_event)
        
        assert usd_result.affects_usd is True
        assert eur_result.affects_usd is False
    
    def test_format_event_summer_dst(self):
        """Test conversión con DST activo (verano)"""
        # Julio: DST activo en US
        event = EconomicEvent(
            date=datetime(2026, 7, 15, 10, 30),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="CPI"
        )
        
        result = ScheduleFormatter.format_event(event, include_timezones=True)
        
        # EDT es UTC-4 (vs EST que es UTC-5)
        assert result.timezones["ET"] == "06:30"
        # PDT es UTC-7 (vs PST que es UTC-8)
        assert result.timezones["PT"] == "03:30"
    
    def test_format_event_full_description(self):
        """Test descripción completa del evento"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="Non-Farm Payrolls"
        )
        
        result = ScheduleFormatter.format_event(event)
        
        expected = "10:30 – Non-Farm Payrolls – USD – Alto impacto"
        assert result.full_description == expected
    
    def test_format_event_medium_impact(self):
        """Test formateo de evento de impacto medio"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 12, 00),
            importance=ImpactLevel.MEDIUM,
            currency="USD",
            description="Retail Sales"
        )
        
        result = ScheduleFormatter.format_event(event)
        
        assert result.impact == "Medio impacto"
        assert "Medio impacto" in result.full_description
    
    def test_format_event_handles_invalid_timezone_gracefully(self):
        """Test que maneja errores de timezone sin fallar"""
        event = EconomicEvent(
            date=datetime(2026, 1, 11, 10, 30),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="NFP"
        )
        
        # Intentar con zona inválida
        result = ScheduleFormatter.format_event(
            event,
            include_timezones=True,
            timezones=["UTC", "INVALID", "ET"]
        )
        
        # Debe incluir zonas válidas y saltar las inválidas
        assert "UTC" in result.timezones
        assert "ET" in result.timezones
        # INVALID se salta silenciosamente

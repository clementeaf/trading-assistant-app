"""
Tests unitarios para EconomicCalendarService
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.providers.mock_provider import MockProvider
from app.services.economic_calendar_service import EconomicCalendarService


class TestEconomicCalendarService:
    """Tests para EconomicCalendarService"""
    
    @pytest.mark.asyncio
    async def test_get_high_impact_news_today_with_mock_provider(self, test_settings):
        """Test que obtiene noticias de alto impacto con mock provider"""
        service = EconomicCalendarService(test_settings)
        result = await service.get_high_impact_news_today()
        
        assert result.instrument == "XAUUSD"
        assert isinstance(result.has_high_impact_news, bool)
        assert result.count >= 0
        assert isinstance(result.events, list)
        assert "XAUUSD" in result.summary
    
    @pytest.mark.asyncio
    async def test_filters_only_xauusd_events(self, test_settings):
        """Test que filtra solo eventos relevantes para XAUUSD"""
        service = EconomicCalendarService(test_settings)
        result = await service.get_high_impact_news_today()
        
        for event in result.events:
            assert event.currency == "USD" or event.country == "US"
            assert event.importance == ImpactLevel.HIGH
    
    @pytest.mark.asyncio
    async def test_summary_generation_single_event(self, test_settings):
        """Test generación de resumen con un solo evento"""
        service = EconomicCalendarService(test_settings)
        
        mock_provider = MockProvider()
        events = await mock_provider.fetch_events(date.today(), "USD")
        
        summary = service._generate_xauusd_summary(events[:1])
        assert "1 noticia" in summary
        assert "XAUUSD" in summary
    
    @pytest.mark.asyncio
    async def test_summary_generation_no_events(self, test_settings):
        """Test generación de resumen sin eventos"""
        service = EconomicCalendarService(test_settings)
        summary = service._generate_xauusd_summary([])
        
        assert "No hay noticias" in summary
        assert "XAUUSD" in summary
    
    @pytest.mark.asyncio
    async def test_uses_usd_by_default(self, test_settings):
        """Test que usa USD por defecto"""
        service = EconomicCalendarService(test_settings)
        result = await service.get_high_impact_news_today()
        
        for event in result.events:
            assert event.currency == "USD"


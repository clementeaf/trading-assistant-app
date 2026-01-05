"""
Tests unitarios para el filtro XAUUSD
"""
from datetime import datetime

import pytest

from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.utils.xauusd_filter import XAUUSDFilter


class TestXAUUSDFilter:
    """Tests para XAUUSDFilter"""
    
    def test_nfp_event_is_relevant(self):
        """Test que NFP es relevante para XAUUSD"""
        event = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="NFP - Non-Farm Payrolls",
            country="US"
        )
        assert XAUUSDFilter.is_relevant_for_xauusd(event) is True
    
    def test_cpi_event_is_relevant(self):
        """Test que CPI es relevante para XAUUSD"""
        event = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="CPI - Consumer Price Index",
            country="US"
        )
        assert XAUUSDFilter.is_relevant_for_xauusd(event) is True
    
    def test_fomc_event_is_relevant(self):
        """Test que FOMC es relevante para XAUUSD"""
        event = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="FOMC Rate Decision",
            country="US"
        )
        assert XAUUSDFilter.is_relevant_for_xauusd(event) is True
    
    def test_eur_event_is_not_relevant(self):
        """Test que eventos EUR no son relevantes para XAUUSD"""
        event = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="EUR",
            description="GDP",
            country="DE"
        )
        assert XAUUSDFilter.is_relevant_for_xauusd(event) is False
    
    def test_non_usd_event_is_not_relevant(self):
        """Test que eventos no-USD no son relevantes"""
        event = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="GBP",
            description="Interest Rate",
            country="UK"
        )
        assert XAUUSDFilter.is_relevant_for_xauusd(event) is False
    
    def test_filter_multiple_events(self, sample_xauusd_events):
        """Test que filtra correctamente múltiples eventos"""
        non_relevant = EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="EUR",
            description="GDP",
            country="DE"
        )
        
        all_events = sample_xauusd_events + [non_relevant]
        filtered = XAUUSDFilter.filter_xauusd_events(all_events)
        
        assert len(filtered) == 3
        assert all(event.currency == "USD" for event in filtered)
        assert non_relevant not in filtered


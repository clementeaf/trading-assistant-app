"""
Configuración compartida para tests
"""
import pytest
from datetime import date, datetime

from app.config.settings import Settings
from app.models.economic_calendar import EconomicEvent, ImpactLevel


@pytest.fixture
def test_settings() -> Settings:
    """
    Configuración de prueba
    @returns Settings para testing
    """
    return Settings(
        economic_calendar_provider="mock",
        economic_calendar_api_key=None,
        economic_calendar_api_url="https://api.test.com/calendar",
        default_currency="USD"
    )


@pytest.fixture
def sample_high_impact_event() -> EconomicEvent:
    """
    Evento de ejemplo de alto impacto
    @returns EconomicEvent de prueba
    """
    return EconomicEvent(
        date=datetime.now(),
        importance=ImpactLevel.HIGH,
        currency="USD",
        description="NFP - Non-Farm Payrolls",
        country="US"
    )


@pytest.fixture
def sample_low_impact_event() -> EconomicEvent:
    """
    Evento de ejemplo de bajo impacto
    @returns EconomicEvent de prueba
    """
    return EconomicEvent(
        date=datetime.now(),
        importance=ImpactLevel.LOW,
        currency="EUR",
        description="GDP",
        country="DE"
    )


@pytest.fixture
def sample_xauusd_events() -> list[EconomicEvent]:
    """
    Lista de eventos relevantes para XAUUSD
    @returns Lista de EconomicEvent
    """
    return [
        EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="NFP - Non-Farm Payrolls",
            country="US"
        ),
        EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="CPI - Consumer Price Index",
            country="US"
        ),
        EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description="FOMC Rate Decision",
            country="US"
        )
    ]


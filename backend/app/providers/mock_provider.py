"""
Proveedor mock para desarrollo y testing
"""
from datetime import date, datetime
from typing import Optional

from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.providers.base_provider import EconomicCalendarProvider


class MockProvider(EconomicCalendarProvider):
    """Proveedor mock que genera datos de prueba"""
    
    async def fetch_events(
        self,
        target_date: date,
        currency: Optional[str] = None
    ) -> list[EconomicEvent]:
        """
        Genera eventos mock para una fecha específica
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


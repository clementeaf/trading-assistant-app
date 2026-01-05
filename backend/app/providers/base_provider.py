"""
Interfaz base para proveedores de calendario económico
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from app.models.economic_calendar import EconomicEvent


class EconomicCalendarProvider(ABC):
    """Interfaz abstracta para proveedores de calendario económico"""
    
    @abstractmethod
    async def fetch_events(
        self,
        target_date: date,
        currency: Optional[str] = None
    ) -> list[EconomicEvent]:
        """
        Obtiene eventos económicos para una fecha específica
        @param target_date - Fecha objetivo
        @param currency - Moneda para filtrar (opcional)
        @returns Lista de eventos económicos
        """
        pass


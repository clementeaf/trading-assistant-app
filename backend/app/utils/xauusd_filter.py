"""
Utilidades para filtrar eventos relevantes para XAUUSD (Oro vs Dólar)
"""
import re
from typing import Optional

from app.models.economic_calendar import EconomicEvent


class XAUUSDFilter:
    """Filtro para identificar eventos que impactan XAUUSD"""
    
    # Eventos de USD que impactan al oro
    USD_HIGH_IMPACT_KEYWORDS = [
        "NFP", "Non-Farm Payrolls", "Nonfarm Payrolls",
        "CPI", "Consumer Price Index",
        "PPI", "Producer Price Index",
        "FOMC", "Federal Open Market Committee", "Fed Rate Decision",
        "Interest Rate", "Federal Funds Rate",
        "PMI", "Purchasing Managers Index",
        "PCE", "Personal Consumption Expenditures",
        "Retail Sales",
        "GDP", "Gross Domestic Product",
        "Unemployment Rate", "Unemployment",
        "ISM", "Institute for Supply Management",
        "Durable Goods",
        "Consumer Confidence",
        "Housing Starts",
        "Jobless Claims", "Initial Jobless Claims"
    ]
    
    # Eventos específicos de oro
    GOLD_SPECIFIC_KEYWORDS = [
        "Gold Reserves",
        "Gold Production",
        "Central Bank Gold"
    ]
    
    # Países cuyos eventos impactan al dólar (y por ende al XAUUSD)
    USD_RELEVANT_COUNTRIES = ["US", "USA", "United States"]
    
    @classmethod
    def is_relevant_for_xauusd(cls, event: EconomicEvent) -> bool:
        """
        Determina si un evento es relevante para XAUUSD
        @param event - Evento económico a evaluar
        @returns True si el evento impacta XAUUSD, False en caso contrario
        """
        description_upper = event.description.upper()
        
        # Verificar si es un evento de USD (principal factor)
        is_usd_event = (
            event.currency.upper() == "USD" or
            (event.country and event.country.upper() in [
                country.upper() for country in cls.USD_RELEVANT_COUNTRIES
            ])
        )
        
        if not is_usd_event:
            return False
        
        # Verificar keywords de alto impacto
        for keyword in cls.USD_HIGH_IMPACT_KEYWORDS:
            if keyword.upper() in description_upper:
                return True
        
        # Verificar keywords específicos de oro
        for keyword in cls.GOLD_SPECIFIC_KEYWORDS:
            if keyword.upper() in description_upper:
                return True
        
        # Verificar patrones comunes
        patterns = [
            r"FED\s+(RATE|DECISION|MEETING)",
            r"FOMC",
            r"INFLATION",
            r"EMPLOYMENT",
            r"JOBS",
            r"RETAIL",
            r"CONSUMER",
            r"PRODUCER"
        ]
        
        for pattern in patterns:
            if re.search(pattern, description_upper):
                return True
        
        return False
    
    @classmethod
    def filter_xauusd_events(cls, events: list[EconomicEvent]) -> list[EconomicEvent]:
        """
        Filtra eventos relevantes para XAUUSD
        @param events - Lista de eventos económicos
        @returns Lista filtrada de eventos relevantes para XAUUSD
        """
        return [
            event for event in events
            if cls.is_relevant_for_xauusd(event)
        ]


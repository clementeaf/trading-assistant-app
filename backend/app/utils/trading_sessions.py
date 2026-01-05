"""
Utilidades para definir y trabajar con sesiones de trading
"""
from datetime import datetime, time, timedelta
from typing import Optional

from app.models.market_analysis import SessionType


class TradingSessions:
    """Definición de horarios de sesiones de trading en UTC"""
    
    # Horarios en UTC
    ASIA_START = time(0, 0)  # 00:00 UTC
    ASIA_END = time(6, 0)     # 06:00 UTC
    
    LONDON_START = time(7, 0)  # 07:00 UTC
    LONDON_END = time(11, 0)   # 11:00 UTC
    
    NEW_YORK_START = time(12, 0)  # 12:00 UTC
    NEW_YORK_END = time(21, 0)     # 21:00 UTC
    
    @classmethod
    def get_session_for_time(cls, timestamp: datetime) -> Optional[SessionType]:
        """
        Determina a qué sesión pertenece un timestamp
        @param timestamp - Timestamp a analizar (debe estar en UTC)
        @returns Tipo de sesión o None si no pertenece a ninguna
        """
        time_only = timestamp.time()
        
        if cls.ASIA_START <= time_only < cls.ASIA_END:
            return SessionType.ASIA
        elif cls.LONDON_START <= time_only < cls.LONDON_END:
            return SessionType.LONDON
        elif cls.NEW_YORK_START <= time_only < cls.NEW_YORK_END:
            return SessionType.NEW_YORK
        
        return None
    
    @classmethod
    def get_session_bounds(cls, session: SessionType, date: datetime) -> tuple[datetime, datetime]:
        """
        Obtiene los límites de tiempo de una sesión para una fecha específica
        @param session - Tipo de sesión
        @param date - Fecha base
        @returns Tupla (start, end) con los límites de la sesión
        """
        date_only = date.date()
        
        if session == SessionType.ASIA:
            start = datetime.combine(date_only, cls.ASIA_START)
            end = datetime.combine(date_only, cls.ASIA_END)
        elif session == SessionType.LONDON:
            start = datetime.combine(date_only, cls.LONDON_START)
            end = datetime.combine(date_only, cls.LONDON_END)
        elif session == SessionType.NEW_YORK:
            start = datetime.combine(date_only, cls.NEW_YORK_START)
            end = datetime.combine(date_only, cls.NEW_YORK_END)
        else:
            raise ValueError(f"Unknown session type: {session}")
        
        return (start, end)
    
    @classmethod
    def get_session_time_range(cls, session: SessionType) -> tuple[str, str]:
        """
        Obtiene el rango de horas de una sesión en formato string
        @param session - Tipo de sesión
        @returns Tupla (start_time, end_time) en formato "HH:MM"
        """
        if session == SessionType.ASIA:
            return ("00:00", "06:00")
        elif session == SessionType.LONDON:
            return ("07:00", "11:00")
        elif session == SessionType.NEW_YORK:
            return ("12:00", "21:00")
        else:
            raise ValueError(f"Unknown session type: {session}")


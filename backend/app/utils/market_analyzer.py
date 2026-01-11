"""
Utilidades para analizar datos de mercado y generar resúmenes
"""
from datetime import datetime, timedelta
from typing import Optional

from app.models.market_analysis import (
    MarketDirection,
    PriceCandle,
    SessionAnalysis,
    SessionType
)
from app.utils.trading_sessions import TradingSessions
from app.utils.volatility_calculator import VolatilityCalculator
from app.utils.psychological_level_detector import PsychologicalLevelDetector


class MarketAnalyzer:
    """Analizador de datos de mercado"""
    
    @classmethod
    def calculate_direction(
        cls,
        open_price: float,
        close_price: float,
        threshold: float = 0.001
    ) -> MarketDirection:
        """
        Calcula la dirección del mercado basado en apertura y cierre
        @param open_price - Precio de apertura
        @param close_price - Precio de cierre
        @param threshold - Umbral mínimo para considerar movimiento (0.1% por defecto)
        @returns Dirección del mercado
        """
        if open_price == 0:
            return MarketDirection.NEUTRAL
        
        change_percent = ((close_price - open_price) / open_price) * 100
        
        if change_percent > threshold:
            return MarketDirection.BULLISH
        elif change_percent < -threshold:
            return MarketDirection.BEARISH
        else:
            return MarketDirection.NEUTRAL
    
    @classmethod
    def analyze_session(
        cls,
        session: SessionType,
        candles: list[PriceCandle],
        previous_day_high: Optional[float] = None,
        previous_day_low: Optional[float] = None,
        historical_candles: Optional[list[PriceCandle]] = None
    ) -> SessionAnalysis:
        """
        Analiza una sesión de trading
        @param session - Tipo de sesión
        @param candles - Lista de velas de la sesión
        @param previous_day_high - Máximo del día anterior (opcional)
        @param previous_day_low - Mínimo del día anterior (opcional)
        @param historical_candles - Velas históricas para análisis de volatilidad (opcional)
        @returns Análisis de la sesión
        """
        if not candles:
            raise ValueError(f"No candles provided for session {session}")
        
        # Ordenar por timestamp
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        
        open_price = sorted_candles[0].open
        close_price = sorted_candles[-1].close
        high = max(c.high for c in sorted_candles)
        low = min(c.low for c in sorted_candles)
        range_value = high - low
        
        direction = cls.calculate_direction(open_price, close_price)
        change_percent = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0
        
        broke_previous_high = False
        broke_previous_low = False
        
        if previous_day_high is not None and high > previous_day_high:
            broke_previous_high = True
        
        if previous_day_low is not None and low < previous_day_low:
            broke_previous_low = True
        
        start_time, end_time = TradingSessions.get_session_time_range(session)
        
        # Calcular volatilidad de la sesión
        volatility = VolatilityCalculator.analyze_session_volatility(
            session_candles=sorted_candles,
            historical_candles=historical_candles
        )
        
        # Detectar rupturas de niveles psicológicos
        psychological_breaks = PsychologicalLevelDetector.detect_breaks_in_session(
            candles=sorted_candles,
            tolerance=5.0
        )
        
        description = cls._generate_session_description(
            session, direction, range_value, open_price, change_percent,
            broke_previous_high, broke_previous_low, volatility, psychological_breaks
        )
        
        return SessionAnalysis(
            session=session,
            start_time=start_time,
            end_time=end_time,
            open_price=open_price,
            close_price=close_price,
            high=high,
            low=low,
            range_value=range_value,
            direction=direction,
            change_percent=change_percent,
            broke_previous_high=broke_previous_high,
            broke_previous_low=broke_previous_low,
            description=description,
            volatility=volatility,
            psychological_breaks=psychological_breaks
        )
    
    @classmethod
    def _generate_session_description(
        cls,
        session: SessionType,
        direction: MarketDirection,
        range_value: float,
        open_price: float,
        change_percent: float,
        broke_previous_high: bool,
        broke_previous_low: bool,
        volatility: Optional[dict] = None,
        psychological_breaks: Optional[list] = None
    ) -> str:
        """
        Genera una descripción textual de la sesión
        @param session - Tipo de sesión
        @param direction - Dirección del mercado
        @param range_value - Rango de la sesión
        @param open_price - Precio de apertura
        @param change_percent - Cambio porcentual
        @param broke_previous_high - Si rompió máximo anterior
        @param broke_previous_low - Si rompió mínimo anterior
        @param volatility - Análisis de volatilidad (opcional)
        @param psychological_breaks - Rupturas de niveles psicológicos (opcional)
        @returns Descripción textual
        """
        session_names = {
            SessionType.ASIA: "Asia",
            SessionType.LONDON: "Londres",
            SessionType.NEW_YORK: "Nueva York"
        }
        
        session_name = session_names.get(session, session.value)
        
        # Determinar descripción del rango
        range_threshold = open_price * 0.002  # 0.2% del precio
        if range_value < range_threshold:
            range_desc = "rango estrecho"
        elif range_value < range_threshold * 2:
            range_desc = "rango moderado"
        else:
            range_desc = "rango amplio"
        
        # Determinar descripción de dirección
        abs_change = abs(change_percent)
        if direction == MarketDirection.BULLISH:
            if abs_change > 0.5:
                direction_desc = "fuerte impulso alcista"
            else:
                direction_desc = "impulso alcista"
        elif direction == MarketDirection.BEARISH:
            if abs_change > 0.5:
                direction_desc = "fuerte impulso bajista"
            else:
                direction_desc = "impulso bajista"
        else:
            direction_desc = "movimiento lateral"
        
        # Construir descripción base
        description = f"Sesión {session_name}: {range_desc}, {direction_desc}"
        
        # Agregar volatilidad si está disponible
        if volatility:
            vol_level = volatility.get("level", "normal")
            if vol_level != "normal":
                description += f", volatilidad {vol_level}"
        
        if broke_previous_high:
            description += " rompiendo el máximo del día anterior"
        elif broke_previous_low:
            description += " rompiendo el mínimo del día anterior"
        
        # Agregar información de rupturas de niveles psicológicos
        if psychological_breaks:
            breaks_text = PsychologicalLevelDetector.format_breaks_description(psychological_breaks)
            if breaks_text:
                description += f". {breaks_text}"
        
        return description
    
    @classmethod
    def generate_daily_summary(
        cls,
        instrument: str,
        date: str,
        previous_close: float,
        current_close: float,
        sessions: list[SessionAnalysis]
    ) -> str:
        """
        Genera un resumen textual del día completo
        @param instrument - Instrumento analizado
        @param date - Fecha analizada
        @param previous_close - Cierre del día anterior
        @param current_close - Cierre del día actual
        @param sessions - Análisis de sesiones
        @returns Resumen textual
        """
        if previous_close == 0:
            change_percent = 0
        else:
            change_percent = ((current_close - previous_close) / previous_close) * 100
        
        direction = cls.calculate_direction(previous_close, current_close)
        direction_text = "alcista" if direction == MarketDirection.BULLISH else "bajista"
        
        summary = f"Ayer {instrument} cerró {direction_text} ({change_percent:.2f}%).\n"
        
        for session in sessions:
            summary += f"{session.description}.\n"
        
        return summary.strip()


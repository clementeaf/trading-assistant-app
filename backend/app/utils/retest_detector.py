"""
Utilidades para detectar patrones de velas y retesteos
"""
from typing import Optional
from enum import Enum

from app.models.market_analysis import PriceCandle


class CandlePattern(str, Enum):
    """Tipos de patrones de velas"""
    PIN_BAR_BULLISH = "pin_bar_alcista"
    PIN_BAR_BEARISH = "pin_bar_bajista"
    ENGULFING_BULLISH = "envolvente_alcista"
    ENGULFING_BEARISH = "envolvente_bajista"
    DOJI = "doji"
    HAMMER = "martillo"
    SHOOTING_STAR = "estrella_fugaz"
    NONE = "ninguno"


class RetestDetector:
    """Detector de retesteos y patrones de velas"""
    
    @classmethod
    def detect_candle_pattern(
        cls,
        candle: PriceCandle,
        previous_candle: Optional[PriceCandle] = None
    ) -> CandlePattern:
        """
        Detecta patrón de vela individual o con vela anterior
        @param candle - Vela actual
        @param previous_candle - Vela anterior (opcional)
        @returns Patrón detectado
        """
        body = abs(candle.close - candle.open)
        total_range = candle.high - candle.low
        
        if total_range == 0:
            return CandlePattern.DOJI
        
        upper_wick = candle.high - max(candle.open, candle.close)
        lower_wick = min(candle.open, candle.close) - candle.low
        
        # Detectar Pin Bar
        if cls._is_pin_bar(body, total_range, upper_wick, lower_wick):
            if lower_wick > upper_wick * 2:
                return CandlePattern.PIN_BAR_BULLISH
            elif upper_wick > lower_wick * 2:
                return CandlePattern.PIN_BAR_BEARISH
        
        # Detectar Hammer
        if cls._is_hammer(body, total_range, lower_wick, upper_wick):
            return CandlePattern.HAMMER
        
        # Detectar Shooting Star
        if cls._is_shooting_star(body, total_range, upper_wick, lower_wick):
            return CandlePattern.SHOOTING_STAR
        
        # Detectar Doji
        if body < total_range * 0.1:
            return CandlePattern.DOJI
        
        # Detectar Engulfing (requiere vela anterior)
        if previous_candle:
            if cls._is_bullish_engulfing(candle, previous_candle):
                return CandlePattern.ENGULFING_BULLISH
            elif cls._is_bearish_engulfing(candle, previous_candle):
                return CandlePattern.ENGULFING_BEARISH
        
        return CandlePattern.NONE
    
    @classmethod
    def _is_pin_bar(
        cls,
        body: float,
        total_range: float,
        upper_wick: float,
        lower_wick: float
    ) -> bool:
        """
        Verifica si es pin bar
        @param body - Tamaño del cuerpo
        @param total_range - Rango total
        @param upper_wick - Mecha superior
        @param lower_wick - Mecha inferior
        @returns True si es pin bar
        """
        body_ratio = body / total_range if total_range > 0 else 0
        return body_ratio < 0.33 and (lower_wick > body * 2 or upper_wick > body * 2)
    
    @classmethod
    def _is_hammer(
        cls,
        body: float,
        total_range: float,
        lower_wick: float,
        upper_wick: float
    ) -> bool:
        """
        Verifica si es martillo (hammer)
        @param body - Tamaño del cuerpo
        @param total_range - Rango total
        @param lower_wick - Mecha inferior
        @param upper_wick - Mecha superior
        @returns True si es martillo
        """
        if total_range == 0:
            return False
        return lower_wick > body * 2 and upper_wick < body * 0.5
    
    @classmethod
    def _is_shooting_star(
        cls,
        body: float,
        total_range: float,
        upper_wick: float,
        lower_wick: float
    ) -> bool:
        """
        Verifica si es estrella fugaz
        @param body - Tamaño del cuerpo
        @param total_range - Rango total
        @param upper_wick - Mecha superior
        @param lower_wick - Mecha inferior
        @returns True si es estrella fugaz
        """
        if total_range == 0:
            return False
        return upper_wick > body * 2 and lower_wick < body * 0.5
    
    @classmethod
    def _is_bullish_engulfing(
        cls,
        current: PriceCandle,
        previous: PriceCandle
    ) -> bool:
        """
        Verifica si es envolvente alcista
        @param current - Vela actual
        @param previous - Vela anterior
        @returns True si es envolvente alcista
        """
        current_bullish = current.close > current.open
        previous_bearish = previous.close < previous.open
        
        return (
            current_bullish and
            previous_bearish and
            current.open <= previous.close and
            current.close >= previous.open
        )
    
    @classmethod
    def _is_bearish_engulfing(
        cls,
        current: PriceCandle,
        previous: PriceCandle
    ) -> bool:
        """
        Verifica si es envolvente bajista
        @param current - Vela actual
        @param previous - Vela anterior
        @returns True si es envolvente bajista
        """
        current_bearish = current.close < current.open
        previous_bullish = previous.close > previous.open
        
        return (
            current_bearish and
            previous_bullish and
            current.open >= previous.close and
            current.close <= previous.open
        )
    
    @classmethod
    def calculate_bounce_probability(
        cls,
        level_type: str,
        pattern: CandlePattern,
        price_distance: float,
        level_strength: float = 0.5
    ) -> float:
        """
        Calcula probabilidad de rebote basado en patrón y contexto
        @param level_type - Tipo de nivel ('support' o 'resistance')
        @param pattern - Patrón de vela detectado
        @param price_distance - Distancia del precio al nivel (%)
        @param level_strength - Fuerza del nivel (0-1)
        @returns Probabilidad de rebote (0-1)
        """
        base_probability = 0.5
        
        # Ajustar por patrón
        pattern_boost = {
            CandlePattern.PIN_BAR_BULLISH: 0.15,
            CandlePattern.PIN_BAR_BEARISH: 0.15,
            CandlePattern.HAMMER: 0.12,
            CandlePattern.SHOOTING_STAR: 0.12,
            CandlePattern.ENGULFING_BULLISH: 0.10,
            CandlePattern.ENGULFING_BEARISH: 0.10,
            CandlePattern.DOJI: 0.05,
            CandlePattern.NONE: 0.0
        }
        
        probability = base_probability + pattern_boost.get(pattern, 0.0)
        
        # Ajustar por fuerza del nivel
        probability += level_strength * 0.2
        
        # Ajustar por distancia al nivel
        if abs(price_distance) < 0.1:  # Muy cerca del nivel
            probability += 0.1
        
        # Validar coherencia (pin bar alcista en soporte, bajista en resistencia)
        if level_type == "support":
            if pattern in [CandlePattern.PIN_BAR_BULLISH, CandlePattern.HAMMER]:
                probability += 0.1
            elif pattern in [CandlePattern.PIN_BAR_BEARISH, CandlePattern.SHOOTING_STAR]:
                probability -= 0.1
        elif level_type == "resistance":
            if pattern in [CandlePattern.PIN_BAR_BEARISH, CandlePattern.SHOOTING_STAR]:
                probability += 0.1
            elif pattern in [CandlePattern.PIN_BAR_BULLISH, CandlePattern.HAMMER]:
                probability -= 0.1
        
        # Limitar entre 0 y 1
        return max(0.0, min(1.0, probability))

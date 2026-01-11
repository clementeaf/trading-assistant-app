"""
Utilidad para análisis multi-temporalidad
Detecta convergencias/divergencias entre timeframes y zonas calientes
"""
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum

from app.models.market_analysis import PriceCandle, MarketDirection


class TimeframeConvergence(str, Enum):
    """Tipos de convergencia entre timeframes"""
    FULL_BULLISH = "convergencia_alcista_total"
    FULL_BEARISH = "convergencia_bajista_total"
    PARTIAL_BULLISH = "convergencia_alcista_parcial"
    PARTIAL_BEARISH = "convergencia_bajista_parcial"
    DIVERGENT = "divergente"
    NEUTRAL = "neutral"


class HotZone:
    """Zona caliente de reacción reciente"""
    
    def __init__(
        self,
        price_level: float,
        timeframe: str,
        reaction_type: str,
        timestamp: datetime,
        strength: float
    ):
        """
        Inicializa una zona caliente
        @param price_level - Nivel de precio
        @param timeframe - Temporalidad (M5, M15, etc)
        @param reaction_type - Tipo de reacción (bounce, rejection, breakout)
        @param timestamp - Timestamp de la reacción
        @param strength - Fuerza de la reacción (0-1)
        """
        self.price_level = price_level
        self.timeframe = timeframe
        self.reaction_type = reaction_type
        self.timestamp = timestamp
        self.strength = strength
        self.age_minutes = (datetime.now() - timestamp).total_seconds() / 60
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "price_level": self.price_level,
            "timeframe": self.timeframe,
            "reaction_type": self.reaction_type,
            "timestamp": self.timestamp.isoformat(),
            "strength": self.strength,
            "age_minutes": int(self.age_minutes)
        }


class MultiTimeframeAnalyzer:
    """Analizador de múltiples temporalidades"""
    
    @classmethod
    def detect_convergence(
        cls,
        directions: dict[str, MarketDirection]
    ) -> TimeframeConvergence:
        """
        Detecta convergencia entre direcciones de diferentes timeframes
        @param directions - Dict con {timeframe: MarketDirection}
        @returns Tipo de convergencia detectada
        """
        if not directions:
            return TimeframeConvergence.NEUTRAL
        
        # Contar direcciones
        bullish_count = sum(1 for d in directions.values() if d == MarketDirection.BULLISH)
        bearish_count = sum(1 for d in directions.values() if d == MarketDirection.BEARISH)
        neutral_count = sum(1 for d in directions.values() if d == MarketDirection.NEUTRAL)
        
        total = len(directions)
        
        # Convergencia total (100%)
        if bullish_count == total:
            return TimeframeConvergence.FULL_BULLISH
        if bearish_count == total:
            return TimeframeConvergence.FULL_BEARISH
        
        # Convergencia parcial (>=70%)
        if bullish_count / total >= 0.7:
            return TimeframeConvergence.PARTIAL_BULLISH
        if bearish_count / total >= 0.7:
            return TimeframeConvergence.PARTIAL_BEARISH
        
        # Divergencia (mixto sin mayoría clara)
        if bullish_count > 0 and bearish_count > 0:
            return TimeframeConvergence.DIVERGENT
        
        return TimeframeConvergence.NEUTRAL
    
    @classmethod
    def detect_hot_zones(
        cls,
        candles: list[PriceCandle],
        timeframe: str,
        lookback_minutes: int = 60
    ) -> list[HotZone]:
        """
        Detecta zonas calientes (reacciones recientes) en un timeframe
        @param candles - Lista de velas
        @param timeframe - Temporalidad (M5, M15, etc)
        @param lookback_minutes - Minutos hacia atrás para buscar (default: 60)
        @returns Lista de zonas calientes detectadas
        """
        if not candles or len(candles) < 3:
            return []
        
        hot_zones: list[HotZone] = []
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=lookback_minutes)
        
        # Analizar últimas velas buscando reacciones significativas
        for i in range(1, len(candles) - 1):
            candle = candles[i]
            prev_candle = candles[i - 1]
            next_candle = candles[i + 1]
            
            # Filtrar por tiempo
            if candle.timestamp < cutoff_time:
                continue
            
            # Detectar bounce (rebote en low)
            bounce = cls._detect_bounce(candle, prev_candle, next_candle)
            if bounce:
                hot_zones.append(
                    HotZone(
                        price_level=candle.low,
                        timeframe=timeframe,
                        reaction_type="bounce",
                        timestamp=candle.timestamp,
                        strength=bounce
                    )
                )
            
            # Detectar rejection (rechazo en high)
            rejection = cls._detect_rejection(candle, prev_candle, next_candle)
            if rejection:
                hot_zones.append(
                    HotZone(
                        price_level=candle.high,
                        timeframe=timeframe,
                        reaction_type="rejection",
                        timestamp=candle.timestamp,
                        strength=rejection
                    )
                )
        
        # Ordenar por fuerza (más fuerte primero)
        hot_zones.sort(key=lambda z: z.strength, reverse=True)
        
        # Retornar top 5 más relevantes
        return hot_zones[:5]
    
    @classmethod
    def _detect_bounce(
        cls,
        candle: PriceCandle,
        prev_candle: PriceCandle,
        next_candle: PriceCandle
    ) -> Optional[float]:
        """
        Detecta un rebote (precio baja y luego sube)
        @param candle - Vela actual
        @param prev_candle - Vela anterior
        @param next_candle - Vela siguiente
        @returns Fuerza del rebote (0-1) o None
        """
        # Condiciones para bounce:
        # 1. Vela actual tiene low menor que prev
        # 2. Vela actual es alcista (close > open)
        # 3. Vela siguiente continúa al alza
        
        if candle.low >= prev_candle.low:
            return None
        
        is_bullish = candle.close > candle.open
        next_continues = next_candle.close > candle.close
        
        if not is_bullish or not next_continues:
            return None
        
        # Calcular fuerza basada en:
        # - Tamaño del wick inferior
        # - Recuperación de precio
        lower_wick = min(candle.open, candle.close) - candle.low
        body_size = abs(candle.close - candle.open)
        
        if body_size == 0:
            return None
        
        wick_ratio = lower_wick / (lower_wick + body_size)
        recovery = (next_candle.close - candle.low) / (candle.high - candle.low) if candle.high > candle.low else 0
        
        # Fuerza = promedio de wick ratio y recovery
        strength = (wick_ratio + recovery) / 2
        
        return min(strength, 1.0) if strength > 0.3 else None
    
    @classmethod
    def _detect_rejection(
        cls,
        candle: PriceCandle,
        prev_candle: PriceCandle,
        next_candle: PriceCandle
    ) -> Optional[float]:
        """
        Detecta un rechazo (precio sube y luego baja)
        @param candle - Vela actual
        @param prev_candle - Vela anterior
        @param next_candle - Vela siguiente
        @returns Fuerza del rechazo (0-1) o None
        """
        # Condiciones para rejection:
        # 1. Vela actual tiene high mayor que prev
        # 2. Vela actual es bajista (close < open)
        # 3. Vela siguiente continúa a la baja
        
        if candle.high <= prev_candle.high:
            return None
        
        is_bearish = candle.close < candle.open
        next_continues = next_candle.close < candle.close
        
        if not is_bearish or not next_continues:
            return None
        
        # Calcular fuerza basada en:
        # - Tamaño del wick superior
        # - Caída de precio
        upper_wick = candle.high - max(candle.open, candle.close)
        body_size = abs(candle.close - candle.open)
        
        if body_size == 0:
            return None
        
        wick_ratio = upper_wick / (upper_wick + body_size)
        fall = (candle.high - next_candle.close) / (candle.high - candle.low) if candle.high > candle.low else 0
        
        # Fuerza = promedio de wick ratio y fall
        strength = (wick_ratio + fall) / 2
        
        return min(strength, 1.0) if strength > 0.3 else None
    
    @classmethod
    def calculate_convergence_strength(
        cls,
        convergence: TimeframeConvergence,
        num_timeframes: int
    ) -> float:
        """
        Calcula la fuerza de la convergencia
        @param convergence - Tipo de convergencia
        @param num_timeframes - Número de timeframes analizados
        @returns Fuerza de convergencia (0-1)
        """
        if convergence == TimeframeConvergence.FULL_BULLISH:
            return 1.0
        elif convergence == TimeframeConvergence.FULL_BEARISH:
            return 1.0
        elif convergence == TimeframeConvergence.PARTIAL_BULLISH:
            return 0.7
        elif convergence == TimeframeConvergence.PARTIAL_BEARISH:
            return 0.7
        elif convergence == TimeframeConvergence.DIVERGENT:
            return 0.3
        else:
            return 0.0

"""
Utilidad para construir histórico detallado de reacciones en niveles psicológicos
"""
from datetime import datetime
from typing import Optional

from app.models.market_analysis import PriceCandle
from app.models.psychological_levels import (
    LevelReaction,
    ReactionType,
    TradingSession,
    VolatilityLevel
)


class ReactionHistoryBuilder:
    """Constructor de histórico detallado de reacciones en niveles psicológicos"""
    
    @staticmethod
    def determine_trading_session(timestamp: datetime) -> TradingSession:
        """
        Determina la sesión de trading basada en la hora UTC
        @param timestamp - Timestamp en UTC
        @returns Sesión de trading
        """
        hour = timestamp.hour
        
        # Sesiones en UTC:
        # Asia: 23:00 - 08:00 UTC
        # Londres: 08:00 - 16:00 UTC
        # Nueva York: 13:00 - 22:00 UTC
        
        if 23 <= hour or hour < 8:
            return TradingSession.ASIA
        elif 8 <= hour < 13:
            return TradingSession.LONDON
        elif 13 <= hour < 23:
            return TradingSession.NEW_YORK
        else:
            return TradingSession.UNKNOWN
    
    @staticmethod
    def classify_volatility(atr: float, price: float) -> VolatilityLevel:
        """
        Clasifica el nivel de volatilidad basado en ATR
        @param atr - Average True Range
        @param price - Precio actual
        @returns Nivel de volatilidad
        """
        atr_percentage = (atr / price) * 100
        
        if atr_percentage < 0.3:
            return VolatilityLevel.LOW
        elif atr_percentage < 0.6:
            return VolatilityLevel.NORMAL
        elif atr_percentage < 1.0:
            return VolatilityLevel.HIGH
        else:
            return VolatilityLevel.EXTREME
    
    @staticmethod
    def calculate_atr(candles: list[PriceCandle], period: int = 14) -> float:
        """
        Calcula el Average True Range
        @param candles - Lista de velas
        @param period - Período para el cálculo
        @returns Valor de ATR
        """
        if len(candles) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            prev_close = candles[i-1].close
            current_high = candles[i].high
            current_low = candles[i].low
            
            tr = max(
                current_high - current_low,
                abs(current_high - prev_close),
                abs(current_low - prev_close)
            )
            true_ranges.append(tr)
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
        
        # ATR simple: promedio de los últimos 'period' true ranges
        return sum(true_ranges[-period:]) / period
    
    @staticmethod
    def detect_confirmation(
        candles: list[PriceCandle],
        start_index: int,
        direction: str
    ) -> tuple[bool, int]:
        """
        Detecta si una reacción fue confirmada
        @param candles - Lista de velas
        @param start_index - Índice de inicio
        @param direction - Dirección esperada ('up' o 'down')
        @returns Tupla (confirmado, número de velas en dirección)
        """
        count = 0
        max_candles = min(5, len(candles) - start_index - 1)
        
        for i in range(start_index + 1, start_index + 1 + max_candles):
            if i >= len(candles):
                break
            
            candle = candles[i]
            
            if direction == 'up' and candle.close > candle.open:
                count += 1
            elif direction == 'down' and candle.close < candle.open:
                count += 1
            else:
                break
        
        # Confirmado si hay 3 o más velas consecutivas en la dirección
        return count >= 3, count
    
    @classmethod
    def build_reaction(
        cls,
        level: float,
        candles: list[PriceCandle],
        reaction_index: int,
        reaction_type: ReactionType
    ) -> Optional[LevelReaction]:
        """
        Construye un objeto LevelReaction con todos los detalles
        @param level - Nivel psicológico
        @param candles - Lista de velas históricas
        @param reaction_index - Índice de la vela de reacción
        @param reaction_type - Tipo de reacción
        @returns LevelReaction o None si no se puede construir
        """
        if reaction_index >= len(candles):
            return None
        
        reaction_candle = candles[reaction_index]
        
        # Fecha y precio
        date = reaction_candle.timestamp.isoformat()
        price = reaction_candle.close
        
        # Sesión
        session = cls.determine_trading_session(reaction_candle.timestamp)
        
        # Calcular ATR
        atr = cls.calculate_atr(candles[:reaction_index + 1])
        
        # Clasificar volatilidad
        volatility = cls.classify_volatility(atr, price)
        
        # Calcular magnitud de la reacción
        if reaction_type == ReactionType.BOUNCE:
            # Para rebote: medir cuánto se alejó del nivel
            if reaction_index + 3 < len(candles):
                next_candles = candles[reaction_index:reaction_index + 4]
                if price < level:  # Rebote desde abajo
                    max_price = max(c.high for c in next_candles)
                    magnitude_points = max_price - level
                else:  # Rebote desde arriba
                    min_price = min(c.low for c in next_candles)
                    magnitude_points = level - min_price
            else:
                magnitude_points = abs(price - level)
        else:  # BREAK
            # Para ruptura: medir cuánto penetró el nivel
            if reaction_index + 3 < len(candles):
                next_candles = candles[reaction_index:reaction_index + 4]
                if price > level:  # Ruptura al alza
                    max_price = max(c.high for c in next_candles)
                    magnitude_points = max_price - level
                else:  # Ruptura a la baja
                    min_price = min(c.low for c in next_candles)
                    magnitude_points = level - min_price
            else:
                magnitude_points = abs(price - level)
        
        magnitude_percentage = (magnitude_points / level) * 100
        
        # Detectar confirmación
        direction = 'up' if reaction_type == ReactionType.BOUNCE and price < level else 'down'
        if reaction_type == ReactionType.BREAK:
            direction = 'up' if price > level else 'down'
        
        was_confirmed, candles_in_direction = cls.detect_confirmation(
            candles, reaction_index, direction
        )
        
        # Distancia desde el nivel antes de la reacción
        distance_from_level = abs(price - level)
        
        # Generar explicación
        explanation = cls._generate_explanation(
            reaction_type, session, volatility, magnitude_points, was_confirmed
        )
        
        return LevelReaction(
            date=date,
            price=price,
            type=reaction_type,
            session=session,
            magnitude_points=round(magnitude_points, 2),
            magnitude_percentage=round(magnitude_percentage, 2),
            volatility=volatility,
            atr_value=round(atr, 2) if atr > 0 else None,
            was_confirmed=was_confirmed,
            candles_in_direction=candles_in_direction,
            distance_from_level=round(distance_from_level, 2),
            explanation=explanation
        )
    
    @staticmethod
    def _generate_explanation(
        reaction_type: ReactionType,
        session: TradingSession,
        volatility: VolatilityLevel,
        magnitude: float,
        confirmed: bool
    ) -> str:
        """
        Genera explicación breve de la reacción
        @param reaction_type - Tipo de reacción
        @param session - Sesión de trading
        @param volatility - Nivel de volatilidad
        @param magnitude - Magnitud en puntos
        @param confirmed - Si fue confirmada
        @returns Explicación textual
        """
        session_names = {
            TradingSession.ASIA: "Asia",
            TradingSession.LONDON: "Londres",
            TradingSession.NEW_YORK: "NY",
            TradingSession.UNKNOWN: "desconocida"
        }
        
        reaction_text = "Rebote" if reaction_type == ReactionType.BOUNCE else "Ruptura"
        session_text = session_names.get(session, "desconocida")
        confirmed_text = "confirmado" if confirmed else "no confirmado"
        
        return (
            f"{reaction_text} en {session_text}, "
            f"magnitud {magnitude:.0f} pts, "
            f"volatilidad {volatility.value}, "
            f"{confirmed_text}"
        )

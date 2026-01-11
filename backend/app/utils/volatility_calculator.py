"""
Utilidades para calcular volatilidad y ATR (Average True Range)
"""
from typing import Optional

from app.models.market_analysis import PriceCandle, VolatilityLevel


class VolatilityCalculator:
    """Calculador de volatilidad y ATR"""
    
    @classmethod
    def calculate_atr(
        cls,
        candles: list[PriceCandle],
        period: int = 14
    ) -> float:
        """
        Calcula el Average True Range (ATR) para una serie de velas
        @param candles - Lista de velas ordenadas cronológicamente
        @param period - Período para calcular ATR (por defecto 14)
        @returns Valor de ATR
        """
        if len(candles) < 2:
            return 0.0
        
        true_ranges: list[float] = []
        
        for i in range(1, len(candles)):
            current = candles[i]
            previous = candles[i - 1]
            
            # True Range es el mayor de:
            # 1. high - low (rango de la vela actual)
            # 2. abs(high - previous_close)
            # 3. abs(low - previous_close)
            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close)
            )
            true_ranges.append(tr)
        
        if not true_ranges:
            return 0.0
        
        # Calcular ATR como promedio de los últimos N true ranges
        atr_period = min(period, len(true_ranges))
        atr = sum(true_ranges[-atr_period:]) / atr_period
        
        return round(atr, 2)
    
    @classmethod
    def calculate_range_percent(
        cls,
        range_value: float,
        price: float
    ) -> float:
        """
        Calcula el porcentaje de rango respecto al precio
        @param range_value - Rango (high - low)
        @param price - Precio de referencia
        @returns Porcentaje del rango
        """
        if price == 0:
            return 0.0
        
        return round((range_value / price) * 100, 2)
    
    @classmethod
    def classify_volatility(
        cls,
        atr: float,
        average_atr: float
    ) -> VolatilityLevel:
        """
        Clasifica el nivel de volatilidad comparando ATR actual vs promedio
        @param atr - ATR actual
        @param average_atr - ATR promedio histórico
        @returns Nivel de volatilidad
        """
        if average_atr == 0:
            return VolatilityLevel.NORMAL
        
        ratio = atr / average_atr
        
        if ratio >= 1.5:
            return VolatilityLevel.EXTREME
        elif ratio >= 1.2:
            return VolatilityLevel.HIGH
        elif ratio >= 0.8:
            return VolatilityLevel.NORMAL
        else:
            return VolatilityLevel.LOW
    
    @classmethod
    def analyze_session_volatility(
        cls,
        session_candles: list[PriceCandle],
        historical_candles: Optional[list[PriceCandle]] = None,
        period: int = 14
    ) -> dict:
        """
        Analiza la volatilidad de una sesión
        @param session_candles - Velas de la sesión
        @param historical_candles - Velas históricas para comparación (opcional)
        @param period - Período para ATR
        @returns Diccionario con análisis de volatilidad
        """
        if not session_candles:
            return {
                "atr": 0.0,
                "range_percent": 0.0,
                "level": VolatilityLevel.NORMAL.value,
                "description": "Sin datos para calcular volatilidad"
            }
        
        # Calcular ATR de la sesión
        atr = cls.calculate_atr(session_candles, period=min(period, len(session_candles)))
        
        # Calcular rango de la sesión
        session_high = max(c.high for c in session_candles)
        session_low = min(c.low for c in session_candles)
        range_value = session_high - session_low
        
        # Precio promedio de la sesión
        avg_price = sum(c.close for c in session_candles) / len(session_candles)
        range_percent = cls.calculate_range_percent(range_value, avg_price)
        
        # Comparar con histórico si está disponible
        volatility_level = VolatilityLevel.NORMAL
        comparison_text = ""
        
        if historical_candles and len(historical_candles) >= period:
            historical_atr = cls.calculate_atr(historical_candles, period=period)
            volatility_level = cls.classify_volatility(atr, historical_atr)
            
            if historical_atr > 0:
                ratio = (atr / historical_atr) * 100
                comparison_text = f" ({ratio:.0f}% vs promedio {period} días)"
        
        # Generar descripción
        description = f"ATR: {atr:.2f}, Rango: {range_percent:.2f}% del precio"
        if comparison_text:
            description += comparison_text
        
        return {
            "atr": atr,
            "range_percent": range_percent,
            "level": volatility_level.value,
            "description": description,
            "vs_historical": comparison_text.strip() if comparison_text else None
        }

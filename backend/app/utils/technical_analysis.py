"""
Utilidades para análisis técnico avanzado
Incluye cálculo de RSI, identificación de tendencias, soporte/resistencia
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.models.market_analysis import MarketDirection, PriceCandle

logger = logging.getLogger(__name__)


class TechnicalAnalysis:
    """Utilidades para análisis técnico"""
    
    @staticmethod
    def calculate_rsi(candles: list[PriceCandle], period: int = 14) -> Optional[float]:
        """
        Calcula el RSI (Relative Strength Index) para las últimas velas
        @param candles - Lista de velas ordenadas por timestamp
        @param period - Período para cálculo de RSI (default: 14)
        @returns Valor de RSI (0-100) o None si no hay suficientes datos
        """
        if len(candles) < period + 1:
            return None
        
        # Ordenar por timestamp
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        
        # Calcular cambios de precio
        changes: list[float] = []
        for i in range(1, len(sorted_candles)):
            change = sorted_candles[i].close - sorted_candles[i-1].close
            changes.append(change)
        
        if len(changes) < period:
            return None
        
        # Separar ganancias y pérdidas
        gains: list[float] = [max(change, 0) for change in changes[-period:]]
        losses: list[float] = [abs(min(change, 0)) for change in changes[-period:]]
        
        # Calcular promedio de ganancias y pérdidas
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0  # Solo ganancias
        
        # Calcular RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calcular RSI
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def identify_trend(candles: list[PriceCandle], lookback_periods: int = 20) -> MarketDirection:
        """
        Identifica la tendencia en un timeframe
        @param candles - Lista de velas ordenadas por timestamp
        @param lookback_periods - Número de períodos a analizar
        @returns Dirección de la tendencia (alcista, bajista, lateral)
        """
        if len(candles) < lookback_periods:
            lookback_periods = len(candles)
        
        if lookback_periods < 2:
            return MarketDirection.NEUTRAL
        
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        recent_candles = sorted_candles[-lookback_periods:]
        
        # Calcular máximos y mínimos más altos/bajos
        highs = [c.high for c in recent_candles]
        lows = [c.low for c in recent_candles]
        closes = [c.close for c in recent_candles]
        
        # Identificar estructura de máximos y mínimos
        higher_highs = 0
        lower_lows = 0
        higher_lows = 0
        lower_highs = 0
        
        for i in range(1, len(recent_candles)):
            if highs[i] > highs[i-1]:
                higher_highs += 1
            if lows[i] < lows[i-1]:
                lower_lows += 1
            if lows[i] > lows[i-1]:
                higher_lows += 1
            if highs[i] < highs[i-1]:
                lower_highs += 1
        
        # Calcular pendiente promedio
        first_close = closes[0]
        last_close = closes[-1]
        price_change_percent = ((last_close - first_close) / first_close) * 100
        
        # Determinar tendencia
        threshold = 0.5  # 0.5% mínimo para considerar tendencia
        
        if higher_highs > lower_highs and higher_lows > lower_lows and price_change_percent > threshold:
            return MarketDirection.BULLISH
        elif lower_lows > higher_lows and lower_highs > higher_highs and price_change_percent < -threshold:
            return MarketDirection.BEARISH
        else:
            return MarketDirection.NEUTRAL
    
    @staticmethod
    def analyze_impulse_strength(
        candles: list[PriceCandle],
        lookback: int = 2
    ) -> tuple[Optional[MarketDirection], float, bool]:
        """
        Analiza la fuerza del último impulso dominante
        @param candles - Lista de velas ordenadas
        @param lookback - Número de velas a analizar (último cierre vs penúltimo)
        @returns Tupla (dirección, distancia_percent, es_fuerte)
        """
        if len(candles) < lookback + 1:
            return None, 0.0, False
        
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        last_candle = sorted_candles[-1]
        previous_candle = sorted_candles[-lookback]
        
        # Calcular distancia entre cierres
        distance = abs(last_candle.close - previous_candle.close)
        distance_percent = (distance / previous_candle.close) * 100 if previous_candle.close > 0 else 0
        
        # Determinar dirección
        if last_candle.close > previous_candle.close:
            direction = MarketDirection.BULLISH
        elif last_candle.close < previous_candle.close:
            direction = MarketDirection.BEARISH
        else:
            direction = MarketDirection.NEUTRAL
        
        # Considerar fuerte si la distancia es > 0.3% (ajustable según instrumento)
        is_strong = distance_percent > 0.3
        
        return direction, round(distance_percent, 2), is_strong
    
    @staticmethod
    def find_support_resistance(
        candles: list[PriceCandle],
        lookback_periods: int = 50
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Encuentra niveles de soporte y resistencia basados en máximos y mínimos locales
        @param candles - Lista de velas ordenadas
        @param lookback_periods - Períodos a analizar
        @returns Tupla (soporte, resistencia)
        """
        if len(candles) < 10:
            return None, None
        
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        recent_candles = sorted_candles[-lookback_periods:] if len(sorted_candles) > lookback_periods else sorted_candles
        
        # Encontrar máximos y mínimos locales
        highs: list[float] = []
        lows: list[float] = []
        
        for i in range(1, len(recent_candles) - 1):
            # Máximo local: mayor que vecinos
            if (recent_candles[i].high > recent_candles[i-1].high and 
                recent_candles[i].high > recent_candles[i+1].high):
                highs.append(recent_candles[i].high)
            
            # Mínimo local: menor que vecinos
            if (recent_candles[i].low < recent_candles[i-1].low and 
                recent_candles[i].low < recent_candles[i+1].low):
                lows.append(recent_candles[i].low)
        
        # También considerar el máximo y mínimo absolutos del período
        all_highs = [c.high for c in recent_candles]
        all_lows = [c.low for c in recent_candles]
        
        if not highs:
            highs = [max(all_highs)]
        if not lows:
            lows = [min(all_lows)]
        
        # Calcular resistencia como promedio de máximos locales más altos
        # Tomar los 3 máximos más altos
        top_highs = sorted(highs, reverse=True)[:3]
        resistance = sum(top_highs) / len(top_highs) if top_highs else max(all_highs)
        
        # Calcular soporte como promedio de mínimos locales más bajos
        # Tomar los 3 mínimos más bajos
        bottom_lows = sorted(lows)[:3]
        support = sum(bottom_lows) / len(bottom_lows) if bottom_lows else min(all_lows)
        
        return round(support, 2), round(resistance, 2)
    
    @staticmethod
    def is_price_near_level(price: float, level: float, threshold_percent: float = 0.5) -> bool:
        """
        Verifica si el precio está cerca de un nivel (soporte/resistencia)
        @param price - Precio actual
        @param level - Nivel a verificar
        @param threshold_percent - Porcentaje de proximidad (default: 0.5%)
        @returns True si el precio está cerca del nivel
        """
        if level == 0:
            return False
        
        distance_percent = abs((price - level) / level) * 100
        return distance_percent <= threshold_percent
    
    @staticmethod
    def check_rsi_zone(rsi: Optional[float], target_zones: list[float] = [55, 50, 45]) -> Optional[float]:
        """
        Verifica si el RSI está en alguna de las zonas objetivo
        @param rsi - Valor de RSI
        @param target_zones - Zonas objetivo a buscar
        @returns Zona más cercana o None
        """
        if rsi is None:
            return None
        
        # Encontrar la zona más cercana
        closest_zone = None
        min_distance = float('inf')
        
        for zone in target_zones:
            distance = abs(rsi - zone)
            if distance < min_distance:
                min_distance = distance
                closest_zone = zone
        
        # Considerar que está en la zona si está dentro de ±2 puntos
        if min_distance <= 2.0:
            return closest_zone
        
        return None


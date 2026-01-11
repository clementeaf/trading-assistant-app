"""
Utilidades para detectar y analizar rupturas de niveles psicológicos
"""
from typing import Optional

from app.models.market_analysis import PriceCandle, PsychologicalBreak


class PsychologicalLevelDetector:
    """Detector de niveles psicológicos y rupturas"""
    
    @classmethod
    def generate_psychological_levels(
        cls,
        min_price: float,
        max_price: float,
        include_fifties: bool = True
    ) -> list[float]:
        """
        Genera lista de niveles psicológicos en un rango de precios
        @param min_price - Precio mínimo del rango
        @param max_price - Precio máximo del rango
        @param include_fifties - Si incluir niveles de 50 (ej: 4550)
        @returns Lista de niveles psicológicos ordenados
        """
        levels: list[float] = []
        
        # Redondear min y max a múltiplos de 100
        start = int(min_price / 100) * 100
        end = int(max_price / 100) * 100 + 100
        
        # Generar niveles de 100 (ej: 4500, 4600)
        current = start
        while current <= end:
            if min_price <= current <= max_price:
                levels.append(float(current))
            current += 100
        
        # Generar niveles de 50 si se solicita (ej: 4550, 4650)
        if include_fifties:
            current = start + 50
            while current <= end:
                if min_price <= current <= max_price:
                    levels.append(float(current))
                current += 100
        
        return sorted(levels)
    
    @classmethod
    def detect_breaks_in_session(
        cls,
        candles: list[PriceCandle],
        tolerance: float = 5.0
    ) -> list[PsychologicalBreak]:
        """
        Detecta rupturas de niveles psicológicos en una sesión
        @param candles - Velas de la sesión ordenadas cronológicamente
        @param tolerance - Tolerancia en puntos para considerar ruptura
        @returns Lista de rupturas detectadas
        """
        if not candles:
            return []
        
        breaks: list[PsychologicalBreak] = []
        
        # Ordenar velas por tiempo
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        
        # Obtener rango de precios
        session_low = min(c.low for c in sorted_candles)
        session_high = max(c.high for c in sorted_candles)
        
        # Generar niveles psicológicos en el rango
        psychological_levels = cls.generate_psychological_levels(
            session_low - 100,  # Margen inferior
            session_high + 100,  # Margen superior
            include_fifties=True
        )
        
        # Detectar rupturas de cada nivel
        for level in psychological_levels:
            break_info = cls._detect_level_break(sorted_candles, level, tolerance)
            if break_info:
                breaks.append(break_info)
        
        return breaks
    
    @classmethod
    def _detect_level_break(
        cls,
        candles: list[PriceCandle],
        level: float,
        tolerance: float
    ) -> Optional[PsychologicalBreak]:
        """
        Detecta si un nivel específico fue roto en las velas
        @param candles - Velas ordenadas cronológicamente
        @param level - Nivel psicológico a verificar
        @param tolerance - Tolerancia en puntos
        @returns Información de ruptura o None si no hubo ruptura
        """
        if not candles:
            return None
        
        # Verificar si el precio estuvo por debajo y luego rompió al alza
        below_level = False
        above_level = False
        break_candle: Optional[PriceCandle] = None
        break_type: Optional[str] = None
        
        for candle in candles:
            # Verificar si estuvo por debajo del nivel
            if candle.close < level - tolerance:
                below_level = True
            
            # Verificar si rompió al alza
            if below_level and candle.close > level + tolerance:
                above_level = True
                break_candle = candle
                break_type = "alcista"
                break
        
        # Si no rompió al alza, verificar ruptura a la baja
        if not above_level:
            below_level = False
            above_level = False
            
            for candle in candles:
                # Verificar si estuvo por encima del nivel
                if candle.close > level + tolerance:
                    above_level = True
                
                # Verificar si rompió a la baja
                if above_level and candle.close < level - tolerance:
                    below_level = True
                    break_candle = candle
                    break_type = "bajista"
                    break
        
        # Si se detectó ruptura, crear objeto
        if break_candle and break_type:
            # Verificar confirmación: si el precio cerró consistentemente más allá del nivel
            confirmed = cls._is_break_confirmed(
                candles[candles.index(break_candle):],
                level,
                break_type,
                tolerance
            )
            
            return PsychologicalBreak(
                level=level,
                break_type=break_type,
                break_price=break_candle.close,
                confirmed=confirmed
            )
        
        return None
    
    @classmethod
    def _is_break_confirmed(
        cls,
        candles_after_break: list[PriceCandle],
        level: float,
        break_type: str,
        tolerance: float
    ) -> bool:
        """
        Verifica si una ruptura fue confirmada
        @param candles_after_break - Velas después de la ruptura
        @param level - Nivel roto
        @param break_type - Tipo de ruptura ('alcista' o 'bajista')
        @param tolerance - Tolerancia en puntos
        @returns True si la ruptura fue confirmada
        """
        if len(candles_after_break) < 2:
            # No hay suficientes velas para confirmar
            return False
        
        # Tomar las siguientes 2-3 velas para confirmación
        confirmation_candles = candles_after_break[1:min(4, len(candles_after_break))]
        
        if break_type == "alcista":
            # Confirmar si la mayoría de cierres están por encima del nivel
            above_count = sum(1 for c in confirmation_candles if c.close > level)
            return above_count >= len(confirmation_candles) * 0.5
        
        else:  # bajista
            # Confirmar si la mayoría de cierres están por debajo del nivel
            below_count = sum(1 for c in confirmation_candles if c.close < level)
            return below_count >= len(confirmation_candles) * 0.5
    
    @classmethod
    def format_breaks_description(
        cls,
        breaks: list[PsychologicalBreak]
    ) -> str:
        """
        Formatea las rupturas en descripción textual
        @param breaks - Lista de rupturas
        @returns Descripción textual de rupturas
        """
        if not breaks:
            return ""
        
        descriptions: list[str] = []
        
        for break_info in breaks:
            confirmation = "confirmada" if break_info.confirmed else "no confirmada"
            description = (
                f"Ruptura {break_info.break_type} de {break_info.level:.0f} "
                f"({confirmation})"
            )
            descriptions.append(description)
        
        return ", ".join(descriptions)

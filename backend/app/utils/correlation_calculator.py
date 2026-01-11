"""
Calculador de correlaciones entre Gold y otros activos (DXY, Yields)
"""
from typing import Optional
from enum import Enum
from scipy.stats import pearsonr
from pydantic import BaseModel


class CorrelationStrength(str, Enum):
    """
    Clasificación de fuerza de correlación
    """
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"


class CorrelationResult(BaseModel):
    """
    Resultado de cálculo de correlación
    """
    coefficient: float
    p_value: float
    strength: CorrelationStrength
    is_significant: bool
    interpretation: str


class ImpactProjection(BaseModel):
    """
    Proyección de impacto en Gold basado en movimientos de DXY/Yields
    """
    dxy_change_percent: float
    expected_gold_change_percent: float
    expected_gold_change_points: float
    confidence: float
    reasoning: str


class CorrelationCalculator:
    """
    Calculador de correlaciones y proyecciones de impacto
    """
    
    # Thresholds para clasificación de fuerza
    STRENGTH_THRESHOLDS = {
        0.8: CorrelationStrength.VERY_STRONG,
        0.6: CorrelationStrength.STRONG,
        0.4: CorrelationStrength.MODERATE,
        0.2: CorrelationStrength.WEAK,
        0.0: CorrelationStrength.VERY_WEAK,
    }
    
    # Significancia estadística
    SIGNIFICANCE_LEVEL = 0.05
    
    @classmethod
    def calculate_correlation(
        cls,
        gold_prices: list[float],
        other_prices: list[float]
    ) -> CorrelationResult:
        """
        Calcula correlación de Pearson entre Gold y otro activo
        @param gold_prices - Precios históricos de Gold
        @param other_prices - Precios históricos del otro activo
        @returns Resultado con coeficiente, p-value y clasificación
        """
        if len(gold_prices) != len(other_prices):
            raise ValueError(
                f"Longitudes no coinciden: gold={len(gold_prices)}, other={len(other_prices)}"
            )
        
        if len(gold_prices) < 2:
            raise ValueError(
                f"Se necesitan al menos 2 datos, recibidos: {len(gold_prices)}"
            )
        
        # Calcular correlación de Pearson
        coefficient, p_value = pearsonr(gold_prices, other_prices)
        
        # Clasificar fuerza
        strength = cls._classify_strength(abs(coefficient))
        
        # Determinar significancia
        is_significant = p_value < cls.SIGNIFICANCE_LEVEL
        
        # Generar interpretación
        interpretation = cls._generate_interpretation(
            coefficient, strength, is_significant
        )
        
        return CorrelationResult(
            coefficient=coefficient,
            p_value=p_value,
            strength=strength,
            is_significant=is_significant,
            interpretation=interpretation
        )
    
    @classmethod
    def _classify_strength(cls, abs_coefficient: float) -> CorrelationStrength:
        """
        Clasifica la fuerza de correlación basado en coeficiente absoluto
        @param abs_coefficient - Valor absoluto del coeficiente
        @returns Clasificación de fuerza
        """
        for threshold, strength in cls.STRENGTH_THRESHOLDS.items():
            if abs_coefficient >= threshold:
                return strength
        return CorrelationStrength.VERY_WEAK
    
    @classmethod
    def _generate_interpretation(
        cls,
        coefficient: float,
        strength: CorrelationStrength,
        is_significant: bool
    ) -> str:
        """
        Genera interpretación textual de la correlación
        @param coefficient - Coeficiente de correlación
        @param strength - Fuerza de la correlación
        @param is_significant - Si es estadísticamente significativa
        @returns Interpretación legible
        """
        direction = "inversa" if coefficient < 0 else "directa"
        
        strength_text = {
            CorrelationStrength.VERY_STRONG: "muy fuerte",
            CorrelationStrength.STRONG: "fuerte",
            CorrelationStrength.MODERATE: "moderada",
            CorrelationStrength.WEAK: "débil",
            CorrelationStrength.VERY_WEAK: "muy débil",
        }
        
        significance_text = (
            "estadísticamente significativa" if is_significant 
            else "no significativa estadísticamente"
        )
        
        return (
            f"Correlación {direction} {strength_text.get(strength, 'desconocida')} "
            f"({coefficient:.2f}), {significance_text}"
        )
    
    @classmethod
    def project_gold_impact(
        cls,
        correlation_coefficient: float,
        dxy_change_percent: float,
        current_gold_price: float,
        correlation_strength: CorrelationStrength,
        is_significant: bool
    ) -> ImpactProjection:
        """
        Proyecta impacto en Gold basado en cambio esperado en DXY
        @param correlation_coefficient - Coeficiente de correlación Gold-DXY
        @param dxy_change_percent - Cambio esperado en DXY (%)
        @param current_gold_price - Precio actual de Gold
        @param correlation_strength - Fuerza de la correlación
        @param is_significant - Si la correlación es significativa
        @returns Proyección de impacto en Gold
        """
        # Proyectar cambio en Gold (inverso por correlación típicamente negativa)
        expected_gold_change_percent = correlation_coefficient * dxy_change_percent
        
        # Calcular cambio en puntos
        expected_gold_change_points = (
            current_gold_price * expected_gold_change_percent / 100
        )
        
        # Calcular confianza basada en fuerza y significancia
        confidence = cls._calculate_projection_confidence(
            correlation_strength, is_significant
        )
        
        # Generar razonamiento
        reasoning = cls._generate_projection_reasoning(
            dxy_change_percent,
            expected_gold_change_percent,
            correlation_coefficient,
            correlation_strength
        )
        
        return ImpactProjection(
            dxy_change_percent=dxy_change_percent,
            expected_gold_change_percent=expected_gold_change_percent,
            expected_gold_change_points=expected_gold_change_points,
            confidence=confidence,
            reasoning=reasoning
        )
    
    @classmethod
    def _calculate_projection_confidence(
        cls,
        strength: CorrelationStrength,
        is_significant: bool
    ) -> float:
        """
        Calcula confianza de la proyección basado en fuerza y significancia
        @param strength - Fuerza de la correlación
        @param is_significant - Si es estadísticamente significativa
        @returns Confianza (0.0 - 1.0)
        """
        base_confidence = {
            CorrelationStrength.VERY_STRONG: 0.9,
            CorrelationStrength.STRONG: 0.75,
            CorrelationStrength.MODERATE: 0.6,
            CorrelationStrength.WEAK: 0.4,
            CorrelationStrength.VERY_WEAK: 0.2,
        }
        
        confidence = base_confidence.get(strength, 0.5)
        
        # Penalizar si no es significativa
        if not is_significant:
            confidence *= 0.7
        
        return round(confidence, 2)
    
    @classmethod
    def _generate_projection_reasoning(
        cls,
        dxy_change: float,
        gold_change: float,
        coefficient: float,
        strength: CorrelationStrength
    ) -> str:
        """
        Genera razonamiento textual de la proyección
        @param dxy_change - Cambio esperado en DXY
        @param gold_change - Cambio esperado en Gold
        @param coefficient - Coeficiente de correlación
        @param strength - Fuerza de correlación
        @returns Razonamiento legible
        """
        dxy_direction = "sube" if dxy_change > 0 else "baja"
        gold_direction = "subiría" if gold_change > 0 else "bajaría"
        
        strength_text = {
            CorrelationStrength.VERY_STRONG: "muy fuerte",
            CorrelationStrength.STRONG: "fuerte",
            CorrelationStrength.MODERATE: "moderada",
            CorrelationStrength.WEAK: "débil",
            CorrelationStrength.VERY_WEAK: "muy débil",
        }
        
        return (
            f"Si DXY {dxy_direction} {abs(dxy_change):.2f}%, Gold {gold_direction} "
            f"aproximadamente {abs(gold_change):.2f}% basado en correlación "
            f"{strength_text.get(strength, 'desconocida')} ({coefficient:.2f})"
        )

"""
Tests para CorrelationCalculator
"""
import pytest
from app.utils.correlation_calculator import (
    CorrelationCalculator,
    CorrelationStrength,
    CorrelationResult,
    ImpactProjection,
)


class TestCorrelationCalculator:
    """
    Tests para cálculo de correlaciones
    """
    
    def test_calculate_correlation_perfect_negative(self) -> None:
        """
        Correlación perfectamente negativa (-1.0)
        """
        gold = [100.0, 90.0, 80.0, 70.0, 60.0]
        dxy = [50.0, 60.0, 70.0, 80.0, 90.0]
        
        result = CorrelationCalculator.calculate_correlation(gold, dxy)
        
        assert result.coefficient == pytest.approx(-1.0, abs=0.01)
        assert result.strength == CorrelationStrength.VERY_STRONG
        assert result.is_significant is True
        assert "inversa" in result.interpretation
        assert "muy fuerte" in result.interpretation
    
    def test_calculate_correlation_perfect_positive(self) -> None:
        """
        Correlación perfectamente positiva (1.0)
        """
        gold = [100.0, 110.0, 120.0, 130.0, 140.0]
        other = [50.0, 55.0, 60.0, 65.0, 70.0]
        
        result = CorrelationCalculator.calculate_correlation(gold, other)
        
        assert result.coefficient == pytest.approx(1.0, abs=0.01)
        assert result.strength == CorrelationStrength.VERY_STRONG
        assert result.is_significant is True
        assert "directa" in result.interpretation
        assert "muy fuerte" in result.interpretation
    
    def test_calculate_correlation_moderate(self) -> None:
        """
        Correlación moderada
        """
        gold = [100.0, 105.0, 103.0, 110.0, 108.0, 115.0]
        dxy = [95.0, 93.0, 96.0, 90.0, 92.0, 88.0]
        
        result = CorrelationCalculator.calculate_correlation(gold, dxy)
        
        assert -1.0 <= result.coefficient <= 1.0
        assert result.strength in [
            CorrelationStrength.MODERATE,
            CorrelationStrength.STRONG,
            CorrelationStrength.VERY_STRONG,
        ]
        assert result.is_significant is True
    
    def test_calculate_correlation_weak(self) -> None:
        """
        Correlación débil con datos aleatorios
        """
        gold = [100.0, 102.0, 101.0, 103.0, 100.5, 102.5]
        other = [50.0, 49.5, 50.2, 50.1, 49.8, 50.3]
        
        result = CorrelationCalculator.calculate_correlation(gold, other)
        
        assert -1.0 <= result.coefficient <= 1.0
        assert result.p_value >= 0.0
    
    def test_calculate_correlation_different_lengths(self) -> None:
        """
        Error cuando las listas tienen longitudes diferentes
        """
        gold = [100.0, 110.0, 120.0]
        dxy = [95.0, 90.0]
        
        with pytest.raises(ValueError, match="Longitudes no coinciden"):
            CorrelationCalculator.calculate_correlation(gold, dxy)
    
    def test_calculate_correlation_insufficient_data(self) -> None:
        """
        Error cuando hay menos de 2 datos
        """
        gold = [100.0]
        dxy = [95.0]
        
        with pytest.raises(ValueError, match="Se necesitan al menos 2 datos"):
            CorrelationCalculator.calculate_correlation(gold, dxy)
    
    def test_classify_strength_very_strong(self) -> None:
        """
        Clasificación de correlación muy fuerte
        """
        strength = CorrelationCalculator._classify_strength(0.85)
        assert strength == CorrelationStrength.VERY_STRONG
        
        strength = CorrelationCalculator._classify_strength(0.95)
        assert strength == CorrelationStrength.VERY_STRONG
    
    def test_classify_strength_strong(self) -> None:
        """
        Clasificación de correlación fuerte
        """
        strength = CorrelationCalculator._classify_strength(0.65)
        assert strength == CorrelationStrength.STRONG
        
        strength = CorrelationCalculator._classify_strength(0.75)
        assert strength == CorrelationStrength.STRONG
    
    def test_classify_strength_moderate(self) -> None:
        """
        Clasificación de correlación moderada
        """
        strength = CorrelationCalculator._classify_strength(0.45)
        assert strength == CorrelationStrength.MODERATE
        
        strength = CorrelationCalculator._classify_strength(0.55)
        assert strength == CorrelationStrength.MODERATE
    
    def test_classify_strength_weak(self) -> None:
        """
        Clasificación de correlación débil
        """
        strength = CorrelationCalculator._classify_strength(0.25)
        assert strength == CorrelationStrength.WEAK
        
        strength = CorrelationCalculator._classify_strength(0.35)
        assert strength == CorrelationStrength.WEAK
    
    def test_classify_strength_very_weak(self) -> None:
        """
        Clasificación de correlación muy débil
        """
        strength = CorrelationCalculator._classify_strength(0.05)
        assert strength == CorrelationStrength.VERY_WEAK
        
        strength = CorrelationCalculator._classify_strength(0.15)
        assert strength == CorrelationStrength.VERY_WEAK
    
    def test_generate_interpretation_negative_strong(self) -> None:
        """
        Interpretación de correlación negativa fuerte
        """
        interpretation = CorrelationCalculator._generate_interpretation(
            coefficient=-0.75,
            strength=CorrelationStrength.STRONG,
            is_significant=True
        )
        
        assert "inversa" in interpretation
        assert "fuerte" in interpretation
        assert "significativa" in interpretation
    
    def test_generate_interpretation_positive_weak_not_significant(self) -> None:
        """
        Interpretación de correlación positiva débil no significativa
        """
        interpretation = CorrelationCalculator._generate_interpretation(
            coefficient=0.25,
            strength=CorrelationStrength.WEAK,
            is_significant=False
        )
        
        assert "directa" in interpretation
        assert "débil" in interpretation
        assert "no significativa" in interpretation
    
    def test_project_gold_impact_negative_correlation(self) -> None:
        """
        Proyección de impacto con correlación negativa (típico Gold-DXY)
        """
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.8,
            dxy_change_percent=1.0,
            current_gold_price=2000.0,
            correlation_strength=CorrelationStrength.VERY_STRONG,
            is_significant=True
        )
        
        assert projection.dxy_change_percent == 1.0
        assert projection.expected_gold_change_percent == pytest.approx(-0.8, abs=0.01)
        assert projection.expected_gold_change_points == pytest.approx(-16.0, abs=0.1)
        assert projection.confidence >= 0.8
        assert "DXY sube" in projection.reasoning
        assert "Gold bajaría" in projection.reasoning
    
    def test_project_gold_impact_positive_dxy_change(self) -> None:
        """
        Proyección cuando DXY sube
        """
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.7,
            dxy_change_percent=2.5,
            current_gold_price=2100.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True
        )
        
        assert projection.dxy_change_percent == 2.5
        assert projection.expected_gold_change_percent == pytest.approx(-1.75, abs=0.01)
        assert projection.expected_gold_change_points == pytest.approx(-36.75, abs=0.1)
        assert projection.confidence > 0.7
        assert "sube 2.50%" in projection.reasoning
    
    def test_project_gold_impact_negative_dxy_change(self) -> None:
        """
        Proyección cuando DXY baja
        """
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.75,
            dxy_change_percent=-1.5,
            current_gold_price=2050.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True
        )
        
        assert projection.dxy_change_percent == -1.5
        assert projection.expected_gold_change_percent == pytest.approx(1.125, abs=0.01)
        assert projection.expected_gold_change_points == pytest.approx(23.0625, abs=0.1)
        assert projection.confidence > 0.7
        assert "DXY baja" in projection.reasoning
        assert "Gold subiría" in projection.reasoning
    
    def test_calculate_projection_confidence_very_strong_significant(self) -> None:
        """
        Confianza con correlación muy fuerte y significativa
        """
        confidence = CorrelationCalculator._calculate_projection_confidence(
            strength=CorrelationStrength.VERY_STRONG,
            is_significant=True
        )
        
        assert confidence == pytest.approx(0.9, abs=0.01)
    
    def test_calculate_projection_confidence_moderate_not_significant(self) -> None:
        """
        Confianza con correlación moderada no significativa
        """
        confidence = CorrelationCalculator._calculate_projection_confidence(
            strength=CorrelationStrength.MODERATE,
            is_significant=False
        )
        
        assert confidence == pytest.approx(0.42, abs=0.01)
    
    def test_calculate_projection_confidence_weak_significant(self) -> None:
        """
        Confianza con correlación débil pero significativa
        """
        confidence = CorrelationCalculator._calculate_projection_confidence(
            strength=CorrelationStrength.WEAK,
            is_significant=True
        )
        
        assert confidence == pytest.approx(0.4, abs=0.01)
    
    def test_generate_projection_reasoning_dxy_up_gold_down(self) -> None:
        """
        Razonamiento cuando DXY sube y Gold baja
        """
        reasoning = CorrelationCalculator._generate_projection_reasoning(
            dxy_change=1.5,
            gold_change=-1.2,
            coefficient=-0.8,
            strength=CorrelationStrength.VERY_STRONG
        )
        
        assert "DXY sube 1.50%" in reasoning
        assert "Gold bajaría" in reasoning
        assert "1.20%" in reasoning
        assert "muy fuerte" in reasoning
    
    def test_generate_projection_reasoning_dxy_down_gold_up(self) -> None:
        """
        Razonamiento cuando DXY baja y Gold sube
        """
        reasoning = CorrelationCalculator._generate_projection_reasoning(
            dxy_change=-2.0,
            gold_change=1.6,
            coefficient=-0.8,
            strength=CorrelationStrength.VERY_STRONG
        )
        
        assert "DXY baja 2.00%" in reasoning
        assert "Gold subiría" in reasoning
        assert "1.60%" in reasoning

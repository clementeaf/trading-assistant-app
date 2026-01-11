"""
Tests unitarios para proyección de impacto Gold con magnitud estimada
"""
import pytest
from app.utils.correlation_calculator import (
    CorrelationCalculator,
    CorrelationStrength,
    ImpactProjection
)


class TestImpactProjectionWithMagnitude:
    """Tests para proyección de impacto con rango de magnitud"""
    
    def test_impact_projection_model_with_magnitude(self):
        """Verifica que ImpactProjection incluya campos de magnitud"""
        projection = ImpactProjection(
            dxy_change_percent=1.0,
            expected_gold_change_percent=-0.8,
            expected_gold_change_points=-36.0,
            confidence=0.75,
            reasoning="Test projection",
            magnitude_range_min=-1.0,
            magnitude_range_max=-0.6,
            magnitude_explanation="Rango basado en volatilidad 0.5%"
        )
        
        assert projection.magnitude_range_min == -1.0
        assert projection.magnitude_range_max == -0.6
        assert "volatilidad" in projection.magnitude_explanation.lower()
    
    def test_impact_projection_without_magnitude(self):
        """Verifica que campos de magnitud sean opcionales"""
        projection = ImpactProjection(
            dxy_change_percent=1.0,
            expected_gold_change_percent=-0.8,
            expected_gold_change_points=-36.0,
            confidence=0.75,
            reasoning="Test projection"
            # Sin campos de magnitud
        )
        
        assert projection.magnitude_range_min is None
        assert projection.magnitude_range_max is None
        assert projection.magnitude_explanation is None


class TestCalculateMagnitudeRange:
    """Tests para el método _calculate_magnitude_range"""
    
    def test_magnitude_range_very_strong_correlation(self):
        """Verifica rango estrecho para correlación muy fuerte"""
        min_pct, max_pct, explanation = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.VERY_STRONG,
            historical_volatility=0.5
        )
        
        # Correlación muy fuerte = ±15% del cambio esperado
        # -0.8 ± 0.12 = [-0.92, -0.68]
        assert min_pct < max_pct
        assert abs(min_pct - (-0.92)) < 0.05  # Tolerancia
        assert abs(max_pct - (-0.68)) < 0.05
        assert "muy fuerte" in explanation
    
    def test_magnitude_range_strong_correlation(self):
        """Verifica rango medio para correlación fuerte"""
        min_pct, max_pct, explanation = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=0.5
        )
        
        # Correlación fuerte = ±25% del cambio esperado
        # -0.8 ± 0.20 = [-1.0, -0.6]
        assert min_pct < max_pct
        assert abs(min_pct - (-1.0)) < 0.05
        assert abs(max_pct - (-0.6)) < 0.05
        assert "fuerte" in explanation
    
    def test_magnitude_range_moderate_correlation(self):
        """Verifica rango amplio para correlación moderada"""
        min_pct, max_pct, explanation = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.MODERATE,
            historical_volatility=0.5
        )
        
        # Correlación moderada = ±40% del cambio esperado
        # -0.8 ± 0.32 = [-1.12, -0.48]
        assert min_pct < max_pct
        assert abs(min_pct - (-1.12)) < 0.05
        assert abs(max_pct - (-0.48)) < 0.05
        assert "moderada" in explanation
    
    def test_magnitude_range_weak_correlation(self):
        """Verifica rango muy amplio para correlación débil"""
        min_pct, max_pct, explanation = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.WEAK,
            historical_volatility=0.5
        )
        
        # Correlación débil = ±60% del cambio esperado
        # -0.8 ± 0.48 = [-1.28, -0.32]
        assert min_pct < max_pct
        assert abs(min_pct - (-1.28)) < 0.05
        assert abs(max_pct - (-0.32)) < 0.05
        assert "débil" in explanation
    
    def test_magnitude_range_positive_movement(self):
        """Verifica rango para movimiento alcista"""
        min_pct, max_pct, explanation = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=1.2,
            expected_change_points=54.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=0.5
        )
        
        # Movimiento positivo: 1.2 ± 25% = [0.9, 1.5]
        assert min_pct < max_pct
        assert min_pct < 1.2 < max_pct
        assert "alcista" in explanation
    
    def test_magnitude_range_high_volatility(self):
        """Verifica que volatilidad alta amplíe el rango"""
        # Volatilidad normal (0.5%)
        min_normal, max_normal, _ = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=0.5
        )
        
        # Volatilidad alta (1.0%)
        min_high, max_high, _ = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=1.0
        )
        
        # Rango con volatilidad alta debe ser más amplio
        normal_range = max_normal - min_normal
        high_range = max_high - min_high
        assert high_range > normal_range
    
    def test_magnitude_range_low_volatility(self):
        """Verifica que volatilidad baja estreche el rango"""
        # Volatilidad normal (0.5%)
        min_normal, max_normal, _ = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=0.5
        )
        
        # Volatilidad baja (0.2%)
        min_low, max_low, _ = CorrelationCalculator._calculate_magnitude_range(
            expected_change_percent=-0.8,
            expected_change_points=-36.0,
            correlation_strength=CorrelationStrength.STRONG,
            historical_volatility=0.2
        )
        
        # Rango con volatilidad baja debe ser más estrecho
        normal_range = max_normal - min_normal
        low_range = max_low - min_low
        assert low_range < normal_range


class TestProjectGoldImpactWithMagnitude:
    """Tests para project_gold_impact con magnitud"""
    
    def test_project_with_historical_volatility(self):
        """Verifica proyección con volatilidad histórica"""
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.8,
            dxy_change_percent=1.0,
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True,
            historical_volatility=0.5
        )
        
        assert projection.magnitude_range_min is not None
        assert projection.magnitude_range_max is not None
        assert projection.magnitude_explanation is not None
        assert projection.magnitude_range_min < projection.expected_gold_change_percent
        assert projection.expected_gold_change_percent < projection.magnitude_range_max
    
    def test_project_without_historical_volatility(self):
        """Verifica proyección sin volatilidad (usa default 0.5%)"""
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.8,
            dxy_change_percent=1.0,
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True
            # Sin historical_volatility (usa default 0.5%)
        )
        
        assert projection.magnitude_range_min is not None
        assert projection.magnitude_range_max is not None
        assert projection.magnitude_explanation is not None
    
    def test_projection_format_example(self):
        """Verifica formato similar a: 'DXY +0.5%, US10Y +2% → Gold -0.8% a -1.2%'"""
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.8,
            dxy_change_percent=0.5,
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True,
            historical_volatility=0.6
        )
        
        # Verificar que tenemos los datos necesarios para el formato
        assert projection.dxy_change_percent == 0.5
        assert projection.expected_gold_change_percent < 0  # Negativo por correlación inversa
        assert projection.magnitude_range_min is not None
        assert projection.magnitude_range_max is not None
        
        # Construir el mensaje de formato
        format_example = (
            f"DXY {projection.dxy_change_percent:+.1f}% → "
            f"Gold {projection.magnitude_range_min:.1f}% a {projection.magnitude_range_max:.1f}%"
        )
        
        assert "DXY" in format_example
        assert "Gold" in format_example
        assert "%" in format_example
    
    def test_projection_maintains_backwards_compatibility(self):
        """Verifica que campos opcionales no rompan compatibilidad"""
        # Proyección antigua sin volatilidad
        projection_old = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.8,
            dxy_change_percent=1.0,
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True
        )
        
        # Debe tener todos los campos originales
        assert projection_old.dxy_change_percent == 1.0
        assert projection_old.expected_gold_change_percent < 0
        assert projection_old.expected_gold_change_points < 0
        assert projection_old.confidence > 0
        assert len(projection_old.reasoning) > 0
        
        # Y ahora también tiene magnitud
        assert projection_old.magnitude_range_min is not None
        assert projection_old.magnitude_range_max is not None


class TestIntegrationMagnitudeRange:
    """Tests de integración para rango de magnitud"""
    
    def test_full_workflow_dxy_up_gold_down(self):
        """Verifica workflow completo: DXY sube → Gold baja"""
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.75,  # Correlación inversa fuerte
            dxy_change_percent=1.0,          # DXY sube 1%
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True,
            historical_volatility=0.5
        )
        
        # Gold debe bajar (cambio negativo)
        assert projection.expected_gold_change_percent < 0
        assert projection.expected_gold_change_points < 0
        
        # Rango debe ser coherente
        assert projection.magnitude_range_min < 0
        assert projection.magnitude_range_max < 0
        assert projection.magnitude_range_min < projection.expected_gold_change_percent < projection.magnitude_range_max
    
    def test_full_workflow_dxy_down_gold_up(self):
        """Verifica workflow completo: DXY baja → Gold sube"""
        projection = CorrelationCalculator.project_gold_impact(
            correlation_coefficient=-0.75,  # Correlación inversa fuerte
            dxy_change_percent=-1.0,         # DXY baja 1%
            current_gold_price=4500.0,
            correlation_strength=CorrelationStrength.STRONG,
            is_significant=True,
            historical_volatility=0.5
        )
        
        # Gold debe subir (cambio positivo)
        assert projection.expected_gold_change_percent > 0
        assert projection.expected_gold_change_points > 0
        
        # Rango debe ser coherente
        assert projection.magnitude_range_min > 0
        assert projection.magnitude_range_max > 0
        assert projection.magnitude_range_min < projection.expected_gold_change_percent < projection.magnitude_range_max

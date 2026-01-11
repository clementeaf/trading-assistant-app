"""
Tests para ScenarioProbabilityCalculator
"""
import pytest
from app.utils.scenario_probability_calculator import ScenarioProbabilityCalculator
from app.models.scenario_probability import ScenarioType, ConfidenceLevel, get_confidence_level
from app.models.market_analysis import MarketDirection
from app.utils.multi_tf_analyzer import TimeframeConvergence


class TestScenarioProbabilityCalculator:
    """Tests para cálculo de probabilidades por escenario"""
    
    def test_calculate_breakout_bullish_full_convergence(self):
        """Test breakout alcista con convergencia total"""
        result = ScenarioProbabilityCalculator.calculate_breakout_probability(
            direction=MarketDirection.BULLISH,
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.BULLISH,
            level_strength=0.8,
            convergence=TimeframeConvergence.FULL_BULLISH,
            pattern_quality=0.7
        )
        
        assert result.scenario == ScenarioType.BREAKOUT_BULLISH
        assert result.probability > 0.7  # Alta probabilidad por convergencia total
        assert result.confidence == ConfidenceLevel.HIGH.value
        assert "weekly_trend" in result.factors
        assert "convergence" in result.factors
    
    def test_calculate_breakout_bearish_against_weekly(self):
        """Test breakout bajista contra tendencia weekly"""
        result = ScenarioProbabilityCalculator.calculate_breakout_probability(
            direction=MarketDirection.BEARISH,
            weekly_trend=MarketDirection.BULLISH,  # Contra tendencia
            daily_trend=MarketDirection.BEARISH,
            h4_trend=MarketDirection.BEARISH,
            level_strength=0.6,
            convergence=TimeframeConvergence.DIVERGENT
        )
        
        assert result.scenario == ScenarioType.BREAKOUT_BEARISH
        assert result.probability < 0.65  # Baja por ir contra Weekly
        assert "weekly_trend" in result.factors
        assert result.factors["weekly_trend"] < 0  # Penalización
    
    def test_calculate_retest_support_high_strength(self):
        """Test retesteo soporte con nivel fuerte"""
        result = ScenarioProbabilityCalculator.calculate_retest_probability(
            level_type="support",
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.BULLISH,
            level_strength=0.9,
            recent_reactions=5,
            pattern_quality=0.8
        )
        
        assert result.scenario == ScenarioType.RETEST_SUPPORT
        assert result.probability > 0.65  # Alta por alineación y nivel fuerte
        assert result.factors["level_strength"] > 0
        assert result.factors["recent_reactions"] > 0
    
    def test_calculate_retest_resistance_weak_level(self):
        """Test retesteo resistencia con nivel débil"""
        result = ScenarioProbabilityCalculator.calculate_retest_probability(
            level_type="resistance",
            weekly_trend=MarketDirection.NEUTRAL,  # Neutral para nivel débil
            daily_trend=MarketDirection.NEUTRAL,
            h4_trend=MarketDirection.BEARISH,
            level_strength=0.3,  # Nivel débil
            recent_reactions=1
        )
        
        assert result.scenario == ScenarioType.RETEST_RESISTANCE
        assert result.probability < 0.75  # No muy alta por nivel débil
        assert result.factors["level_strength"] < 0.05
    
    def test_calculate_consolidation_all_neutral(self):
        """Test consolidación con todas las tendencias neutrales"""
        result = ScenarioProbabilityCalculator.calculate_consolidation_probability(
            weekly_trend=MarketDirection.NEUTRAL,
            daily_trend=MarketDirection.NEUTRAL,
            h4_trend=MarketDirection.NEUTRAL,
            price_range_pct=0.8,  # Rango estrecho
            volatility_level="low"
        )
        
        assert result.scenario == ScenarioType.CONSOLIDATION
        assert result.probability > 0.60  # Alta por neutralidad y bajo rango
        assert result.factors["neutral_trends"] > 0
        assert result.factors["volatility"] > 0
    
    def test_calculate_consolidation_wide_range(self):
        """Test consolidación con rango amplio"""
        result = ScenarioProbabilityCalculator.calculate_consolidation_probability(
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.BULLISH,
            price_range_pct=3.5,  # Rango amplio
            volatility_level="high"
        )
        
        assert result.scenario == ScenarioType.CONSOLIDATION
        assert result.probability < 0.55  # Baja por tendencias fuertes y rango amplio
    
    def test_analyze_scenarios_bullish_trend(self):
        """Test análisis completo con tendencia alcista"""
        weekly_analysis = {"trend": "alcista"}
        daily_analysis = {"trend": "alcista"}
        h4_analysis = {"trend": "alcista"}
        
        result = ScenarioProbabilityCalculator.analyze_scenarios(
            instrument="XAUUSD",
            current_price=4520.50,
            weekly_analysis=weekly_analysis,
            daily_analysis=daily_analysis,
            h4_analysis=h4_analysis
        )
        
        assert result.instrument == "XAUUSD"
        assert result.current_price == 4520.50
        assert result.primary_scenario is not None
        assert len(result.alternative_scenarios) > 0
        assert result.convergence_strength > 0.7  # Alta por convergencia total
        assert "weekly_trend" in result.market_context
        assert "convergence" in result.market_context
    
    def test_analyze_scenarios_mixed_trends(self):
        """Test análisis con tendencias mixtas"""
        weekly_analysis = {"trend": "alcista"}
        daily_analysis = {"trend": "lateral"}  # Usar "lateral" en vez de "neutral"
        h4_analysis = {"trend": "bajista"}
        
        result = ScenarioProbabilityCalculator.analyze_scenarios(
            instrument="XAUUSD",
            current_price=4500.00,
            weekly_analysis=weekly_analysis,
            daily_analysis=daily_analysis,
            h4_analysis=h4_analysis
        )
        
        assert result.convergence_strength < 0.7  # Baja por divergencia
        assert result.market_context["convergence"] == TimeframeConvergence.DIVERGENT.value
    
    def test_probability_clamping(self):
        """Test que probabilidades están entre 0 y 1"""
        result = ScenarioProbabilityCalculator.calculate_breakout_probability(
            direction=MarketDirection.BULLISH,
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.BULLISH,
            level_strength=1.0,
            convergence=TimeframeConvergence.FULL_BULLISH,
            pattern_quality=1.0
        )
        
        assert 0.0 <= result.probability <= 1.0
    
    def test_scenarios_sorted_by_probability(self):
        """Test que escenarios alternativos están ordenados por probabilidad"""
        weekly_analysis = {"trend": "alcista"}
        daily_analysis = {"trend": "alcista"}
        h4_analysis = {"trend": "lateral"}  # Usar "lateral" en vez de "neutral"
        
        result = ScenarioProbabilityCalculator.analyze_scenarios(
            instrument="XAUUSD",
            current_price=4510.00,
            weekly_analysis=weekly_analysis,
            daily_analysis=daily_analysis,
            h4_analysis=h4_analysis
        )
        
        # Primary debe tener mayor probabilidad que los alternativos
        assert result.primary_scenario.probability >= result.alternative_scenarios[0].probability


class TestConfidenceLevel:
    """Tests para niveles de confianza"""
    
    def test_get_confidence_level_high(self):
        """Test confianza alta (>=0.7)"""
        assert get_confidence_level(0.75) == ConfidenceLevel.HIGH
        assert get_confidence_level(0.9) == ConfidenceLevel.HIGH
        assert get_confidence_level(1.0) == ConfidenceLevel.HIGH
    
    def test_get_confidence_level_medium(self):
        """Test confianza media (0.5-0.7)"""
        assert get_confidence_level(0.5) == ConfidenceLevel.MEDIUM
        assert get_confidence_level(0.65) == ConfidenceLevel.MEDIUM
        assert get_confidence_level(0.69) == ConfidenceLevel.MEDIUM
    
    def test_get_confidence_level_low(self):
        """Test confianza baja (<0.5)"""
        assert get_confidence_level(0.0) == ConfidenceLevel.LOW
        assert get_confidence_level(0.3) == ConfidenceLevel.LOW
        assert get_confidence_level(0.49) == ConfidenceLevel.LOW


class TestScenarioExplanations:
    """Tests para explicaciones generadas"""
    
    def test_breakout_explanation_high_probability(self):
        """Test que explicación sea clara para alta probabilidad"""
        result = ScenarioProbabilityCalculator.calculate_breakout_probability(
            direction=MarketDirection.BULLISH,
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.BULLISH,
            level_strength=0.8,
            convergence=TimeframeConvergence.FULL_BULLISH
        )
        
        assert len(result.explanation) > 20  # Explicación no vacía
        assert "alcista" in result.explanation.lower() or "bullish" in result.explanation.lower()
    
    def test_retest_explanation_includes_reactions(self):
        """Test que explicación de retesteo mencione reacciones"""
        result = ScenarioProbabilityCalculator.calculate_retest_probability(
            level_type="support",
            weekly_trend=MarketDirection.BULLISH,
            daily_trend=MarketDirection.BULLISH,
            h4_trend=MarketDirection.NEUTRAL,
            level_strength=0.7,
            recent_reactions=4
        )
        
        assert len(result.explanation) > 20
        # Debe mencionar soporte y/o reacciones
        exp_lower = result.explanation.lower()
        assert "soporte" in exp_lower or "support" in exp_lower or "reaccion" in exp_lower

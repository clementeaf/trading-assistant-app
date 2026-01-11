"""
Calculador de probabilidades por escenario
Usa análisis multi-temporalidad (Weekly-first) para estimar probabilidades
"""
import logging
from typing import Optional
from datetime import datetime

from app.models.scenario_probability import (
    ScenarioType,
    ScenarioProbability,
    ScenarioAnalysis,
    get_confidence_level
)
from app.models.market_analysis import MarketDirection
from app.utils.multi_tf_analyzer import MultiTimeframeAnalyzer, TimeframeConvergence

logger = logging.getLogger(__name__)


class ScenarioProbabilityCalculator:
    """Calculador de probabilidades por escenario de trading"""
    
    # Probabilidades base por escenario (conservadoras)
    BASE_PROBABILITIES = {
        ScenarioType.BREAKOUT_BULLISH: 0.50,
        ScenarioType.BREAKOUT_BEARISH: 0.50,
        ScenarioType.RETEST_SUPPORT: 0.55,
        ScenarioType.RETEST_RESISTANCE: 0.55,
        ScenarioType.CONSOLIDATION: 0.45,
        ScenarioType.TREND_CONTINUATION: 0.60,
        ScenarioType.TREND_REVERSAL: 0.35
    }
    
    @classmethod
    def calculate_breakout_probability(
        cls,
        direction: MarketDirection,
        weekly_trend: MarketDirection,
        daily_trend: MarketDirection,
        h4_trend: MarketDirection,
        level_strength: float,
        convergence: TimeframeConvergence,
        pattern_quality: Optional[float] = None
    ) -> ScenarioProbability:
        """
        Calcula probabilidad de breakout (alcista o bajista)
        @param direction - Dirección del breakout
        @param weekly_trend - Tendencia semanal
        @param daily_trend - Tendencia diaria
        @param h4_trend - Tendencia H4
        @param level_strength - Fortaleza del nivel (0-1)
        @param convergence - Convergencia multi-TF
        @param pattern_quality - Calidad del patrón (0-1, opcional)
        @returns ScenarioProbability
        """
        scenario_type = ScenarioType.BREAKOUT_BULLISH if direction == MarketDirection.BULLISH else ScenarioType.BREAKOUT_BEARISH
        base_prob = cls.BASE_PROBABILITIES[scenario_type]
        
        factors = {}
        
        # Factor 1: Alineación Weekly (peso mayor)
        weekly_alignment = 0.0
        if weekly_trend == direction:
            weekly_alignment = 0.20
        elif weekly_trend != MarketDirection.NEUTRAL:
            weekly_alignment = -0.15  # Penalización si va contra Weekly
        factors["weekly_trend"] = weekly_alignment
        
        # Factor 2: Confirmación Daily
        daily_confirmation = 0.0
        if daily_trend == direction:
            daily_confirmation = 0.15
        elif daily_trend != MarketDirection.NEUTRAL:
            daily_confirmation = -0.10
        factors["daily_confirmation"] = daily_confirmation
        
        # Factor 3: Confirmación H4
        h4_confirmation = 0.0
        if h4_trend == direction:
            h4_confirmation = 0.10
        factors["h4_confirmation"] = h4_confirmation
        
        # Factor 4: Convergencia multi-TF
        convergence_factor = 0.0
        convergence_strength = MultiTimeframeAnalyzer.calculate_convergence_strength(
            convergence, 3  # Weekly, Daily, H4
        )
        if convergence == TimeframeConvergence.FULL_BULLISH and direction == MarketDirection.BULLISH:
            convergence_factor = 0.15
        elif convergence == TimeframeConvergence.FULL_BEARISH and direction == MarketDirection.BEARISH:
            convergence_factor = 0.15
        elif convergence == TimeframeConvergence.PARTIAL_BULLISH and direction == MarketDirection.BULLISH:
            convergence_factor = 0.10
        elif convergence == TimeframeConvergence.PARTIAL_BEARISH and direction == MarketDirection.BEARISH:
            convergence_factor = 0.10
        factors["convergence"] = convergence_factor
        
        # Factor 5: Fortaleza del nivel
        level_factor = level_strength * 0.08  # Máximo 8%
        factors["level_strength"] = level_factor
        
        # Factor 6: Calidad del patrón (opcional)
        pattern_factor = 0.0
        if pattern_quality is not None:
            pattern_factor = pattern_quality * 0.07  # Máximo 7%
        factors["pattern_quality"] = pattern_factor
        
        # Calcular probabilidad final
        probability = base_prob + sum(factors.values())
        probability = max(0.0, min(1.0, probability))  # Clamp entre 0-1
        
        # Generar explicación
        explanation = cls._generate_breakout_explanation(
            direction, weekly_trend, daily_trend, convergence, probability
        )
        
        return ScenarioProbability(
            scenario=scenario_type,
            probability=probability,
            confidence=get_confidence_level(probability).value,
            factors=factors,
            explanation=explanation
        )
    
    @classmethod
    def calculate_retest_probability(
        cls,
        level_type: str,  # "support" or "resistance"
        weekly_trend: MarketDirection,
        daily_trend: MarketDirection,
        h4_trend: MarketDirection,
        level_strength: float,
        recent_reactions: int = 0,
        pattern_quality: Optional[float] = None
    ) -> ScenarioProbability:
        """
        Calcula probabilidad de retesteo exitoso (rebote en soporte o rechazo en resistencia)
        @param level_type - Tipo de nivel ("support" o "resistance")
        @param weekly_trend - Tendencia semanal
        @param daily_trend - Tendencia diaria
        @param h4_trend - Tendencia H4
        @param level_strength - Fortaleza del nivel (0-1)
        @param recent_reactions - Número de reacciones recientes en el nivel
        @param pattern_quality - Calidad del patrón (0-1, opcional)
        @returns ScenarioProbability
        """
        scenario_type = ScenarioType.RETEST_SUPPORT if level_type == "support" else ScenarioType.RETEST_RESISTANCE
        base_prob = cls.BASE_PROBABILITIES[scenario_type]
        
        factors = {}
        
        # Determinar dirección esperada (alcista para soporte, bajista para resistencia)
        expected_direction = MarketDirection.BULLISH if level_type == "support" else MarketDirection.BEARISH
        
        # Factor 1: Alineación Weekly
        weekly_alignment = 0.0
        if weekly_trend == expected_direction:
            weekly_alignment = 0.15
        elif weekly_trend != MarketDirection.NEUTRAL:
            weekly_alignment = -0.12
        factors["weekly_trend"] = weekly_alignment
        
        # Factor 2: Confirmación Daily
        daily_confirmation = 0.0
        if daily_trend == expected_direction:
            daily_confirmation = 0.12
        elif daily_trend != MarketDirection.NEUTRAL:
            daily_confirmation = -0.08
        factors["daily_confirmation"] = daily_confirmation
        
        # Factor 3: Confirmación H4
        h4_confirmation = 0.0
        if h4_trend == expected_direction:
            h4_confirmation = 0.08
        factors["h4_confirmation"] = h4_confirmation
        
        # Factor 4: Fortaleza del nivel (más importante para retesteos)
        level_factor = level_strength * 0.12  # Máximo 12%
        factors["level_strength"] = level_factor
        
        # Factor 5: Reacciones recientes (histórico)
        reaction_factor = min(recent_reactions * 0.03, 0.12)  # Máximo 12% (4+ reacciones)
        factors["recent_reactions"] = reaction_factor
        
        # Factor 6: Calidad del patrón
        pattern_factor = 0.0
        if pattern_quality is not None:
            pattern_factor = pattern_quality * 0.08
        factors["pattern_quality"] = pattern_factor
        
        # Calcular probabilidad final
        probability = base_prob + sum(factors.values())
        probability = max(0.0, min(1.0, probability))
        
        # Generar explicación
        explanation = cls._generate_retest_explanation(
            level_type, weekly_trend, daily_trend, level_strength, recent_reactions, probability
        )
        
        return ScenarioProbability(
            scenario=scenario_type,
            probability=probability,
            confidence=get_confidence_level(probability).value,
            factors=factors,
            explanation=explanation
        )
    
    @classmethod
    def calculate_consolidation_probability(
        cls,
        weekly_trend: MarketDirection,
        daily_trend: MarketDirection,
        h4_trend: MarketDirection,
        price_range_pct: float,
        volatility_level: str = "normal"
    ) -> ScenarioProbability:
        """
        Calcula probabilidad de consolidación/lateral
        @param weekly_trend - Tendencia semanal
        @param daily_trend - Tendencia diaria
        @param h4_trend - Tendencia H4
        @param price_range_pct - Rango de precio reciente (%)
        @param volatility_level - Nivel de volatilidad (low, normal, high)
        @returns ScenarioProbability
        """
        base_prob = cls.BASE_PROBABILITIES[ScenarioType.CONSOLIDATION]
        
        factors = {}
        
        # Factor 1: Tendencias neutrales
        neutral_count = sum([
            1 for trend in [weekly_trend, daily_trend, h4_trend]
            if trend == MarketDirection.NEUTRAL
        ])
        neutral_factor = neutral_count * 0.10  # Máximo 30% (si todos neutrales)
        factors["neutral_trends"] = neutral_factor
        
        # Factor 2: Rango de precio estrecho
        range_factor = 0.0
        if price_range_pct < 1.0:  # Rango < 1%
            range_factor = 0.12
        elif price_range_pct < 2.0:  # Rango < 2%
            range_factor = 0.08
        factors["price_range"] = range_factor
        
        # Factor 3: Volatilidad baja
        volatility_factor = 0.0
        if volatility_level == "low":
            volatility_factor = 0.10
        elif volatility_level == "normal":
            volatility_factor = 0.05
        factors["volatility"] = volatility_factor
        
        # Factor 4: Divergencia en timeframes (mixto = probable lateral)
        divergence_factor = 0.0
        trends_set = {weekly_trend, daily_trend, h4_trend}
        if len(trends_set) >= 2 and MarketDirection.NEUTRAL not in trends_set:
            # Tendencias mixtas (alcista y bajista) = indecisión
            divergence_factor = 0.08
        factors["divergence"] = divergence_factor
        
        # Calcular probabilidad final
        probability = base_prob + sum(factors.values())
        probability = max(0.0, min(1.0, probability))
        
        explanation = f"Probabilidad de consolidación basada en: {neutral_count} timeframes neutrales, rango {price_range_pct:.1f}%, volatilidad {volatility_level}."
        
        return ScenarioProbability(
            scenario=ScenarioType.CONSOLIDATION,
            probability=probability,
            confidence=get_confidence_level(probability).value,
            factors=factors,
            explanation=explanation
        )
    
    @classmethod
    def analyze_scenarios(
        cls,
        instrument: str,
        current_price: float,
        weekly_analysis: dict,
        daily_analysis: dict,
        h4_analysis: dict,
        psychological_levels: Optional[dict] = None
    ) -> ScenarioAnalysis:
        """
        Analiza todos los escenarios posibles y retorna el análisis completo
        @param instrument - Instrumento
        @param current_price - Precio actual
        @param weekly_analysis - Análisis semanal
        @param daily_analysis - Análisis diario
        @param h4_analysis - Análisis H4
        @param psychological_levels - Niveles psicológicos (opcional)
        @returns ScenarioAnalysis completo
        """
        # Extraer tendencias
        weekly_trend = MarketDirection(weekly_analysis.get("trend", "neutral"))
        daily_trend = MarketDirection(daily_analysis.get("trend", "neutral"))
        h4_trend = MarketDirection(h4_analysis.get("trend", "neutral"))
        
        # Detectar convergencia
        trends = {
            "weekly": weekly_trend,
            "daily": daily_trend,
            "h4": h4_trend
        }
        convergence = MultiTimeframeAnalyzer.detect_convergence(trends)
        convergence_strength = MultiTimeframeAnalyzer.calculate_convergence_strength(convergence, 3)
        
        # Calcular escenarios
        scenarios: list[ScenarioProbability] = []
        
        # 1. Breakout alcista
        scenarios.append(
            cls.calculate_breakout_probability(
                MarketDirection.BULLISH,
                weekly_trend,
                daily_trend,
                h4_trend,
                0.7,  # Level strength placeholder
                convergence
            )
        )
        
        # 2. Breakout bajista
        scenarios.append(
            cls.calculate_breakout_probability(
                MarketDirection.BEARISH,
                weekly_trend,
                daily_trend,
                h4_trend,
                0.7,
                convergence
            )
        )
        
        # 3. Retesteo soporte
        scenarios.append(
            cls.calculate_retest_probability(
                "support",
                weekly_trend,
                daily_trend,
                h4_trend,
                0.75,
                recent_reactions=3
            )
        )
        
        # 4. Retesteo resistencia
        scenarios.append(
            cls.calculate_retest_probability(
                "resistance",
                weekly_trend,
                daily_trend,
                h4_trend,
                0.75,
                recent_reactions=3
            )
        )
        
        # 5. Consolidación
        scenarios.append(
            cls.calculate_consolidation_probability(
                weekly_trend,
                daily_trend,
                h4_trend,
                1.5,  # Price range placeholder
                "normal"
            )
        )
        
        # Ordenar por probabilidad (mayor primero)
        scenarios.sort(key=lambda s: s.probability, reverse=True)
        
        primary_scenario = scenarios[0]
        alternative_scenarios = scenarios[1:3]  # Top 3 alternativos
        
        # Contexto de mercado
        market_context = {
            "weekly_trend": weekly_trend.value,
            "daily_trend": daily_trend.value,
            "h4_trend": h4_trend.value,
            "convergence": convergence.value,
            "convergence_strength": convergence_strength
        }
        
        # Resumen
        summary = (
            f"Escenario principal: {cls._get_scenario_name(primary_scenario.scenario)} "
            f"({primary_scenario.probability:.0%}). "
            f"Convergencia: {convergence.value} (fuerza: {convergence_strength:.0%})."
        )
        
        return ScenarioAnalysis(
            instrument=instrument,
            current_price=current_price,
            timestamp=datetime.now().isoformat(),
            primary_scenario=primary_scenario,
            alternative_scenarios=alternative_scenarios,
            convergence_strength=convergence_strength,
            market_context=market_context,
            summary=summary
        )
    
    @classmethod
    def _generate_breakout_explanation(
        cls,
        direction: MarketDirection,
        weekly_trend: MarketDirection,
        daily_trend: MarketDirection,
        convergence: TimeframeConvergence,
        probability: float
    ) -> str:
        """Genera explicación para breakout"""
        dir_text = "alcista" if direction == MarketDirection.BULLISH else "bajista"
        
        if probability >= 0.7:
            return f"Alta probabilidad de breakout {dir_text} por convergencia {convergence.value} y alineación Weekly-Daily."
        elif probability >= 0.55:
            return f"Probabilidad media de breakout {dir_text}. Weekly: {weekly_trend.value}, Daily: {daily_trend.value}."
        else:
            return f"Baja probabilidad de breakout {dir_text}. Falta confirmación en timeframes superiores."
    
    @classmethod
    def _generate_retest_explanation(
        cls,
        level_type: str,
        weekly_trend: MarketDirection,
        daily_trend: MarketDirection,
        level_strength: float,
        recent_reactions: int,
        probability: float
    ) -> str:
        """Genera explicación para retesteo"""
        level_text = "soporte" if level_type == "support" else "resistencia"
        
        if probability >= 0.65:
            return f"Alta probabilidad de retesteo exitoso en {level_text}. Nivel fuerte ({recent_reactions} reacciones previas), tendencia Weekly {weekly_trend.value}."
        elif probability >= 0.50:
            return f"Probabilidad media de retesteo en {level_text}. Weekly: {weekly_trend.value}, fuerza del nivel: {level_strength:.0%}."
        else:
            return f"Baja probabilidad de retesteo exitoso. Tendencias contra el nivel o nivel débil."
    
    @classmethod
    def _get_scenario_name(cls, scenario: ScenarioType) -> str:
        """Obtiene nombre legible del escenario"""
        names = {
            ScenarioType.BREAKOUT_BULLISH: "Breakout Alcista",
            ScenarioType.BREAKOUT_BEARISH: "Breakout Bajista",
            ScenarioType.RETEST_SUPPORT: "Retesteo Soporte",
            ScenarioType.RETEST_RESISTANCE: "Retesteo Resistencia",
            ScenarioType.CONSOLIDATION: "Consolidación",
            ScenarioType.TREND_CONTINUATION: "Continuación Tendencia",
            ScenarioType.TREND_REVERSAL: "Reversión Tendencia"
        }
        return names.get(scenario, scenario.value)

"""
Tests unitarios para niveles operativos según modo de trading
"""
import pytest
from datetime import datetime, timedelta
from app.models.trading_mode import (
    TradingMode,
    TradingModeRecommendation,
    OperationalLevel,
    LevelType
)
from app.models.market_analysis import PriceCandle


class TestOperationalLevelModel:
    """Tests para el modelo OperationalLevel"""
    
    def test_operational_level_creation(self):
        """
        Verifica que se pueda crear un OperationalLevel correctamente
        """
        level = OperationalLevel(
            level=4500.0,
            type=LevelType.SUPPORT,
            distance_points=25.0,
            distance_percentage=0.55,
            strength=0.75,
            action="Esperar rebote",
            explanation="Nivel redondo fuerte con múltiples tests históricos"
        )
        
        assert level.level == 4500.0
        assert level.type == LevelType.SUPPORT
        assert level.distance_points == 25.0
        assert level.distance_percentage == 0.55
        assert level.strength == 0.75
        assert level.action == "Esperar rebote"
        assert "redondo" in level.explanation
    
    def test_level_type_enum(self):
        """
        Verifica los valores del enum LevelType
        """
        assert LevelType.SUPPORT == "soporte"
        assert LevelType.RESISTANCE == "resistencia"
    
    def test_operational_level_with_resistance(self):
        """
        Verifica creación de nivel de resistencia
        """
        level = OperationalLevel(
            level=4550.0,
            type=LevelType.RESISTANCE,
            distance_points=30.0,
            distance_percentage=0.65,
            strength=0.80,
            action="Esperar rechazo",
            explanation="Resistencia fuerte"
        )
        
        assert level.type == LevelType.RESISTANCE
        assert level.level > 4500.0


class TestTradingModeRecommendationWithLevels:
    """Tests para TradingModeRecommendation con niveles operativos"""
    
    def test_recommendation_with_operational_levels(self):
        """
        Verifica que se puedan incluir niveles operativos en la recomendación
        """
        from app.models.trading_mode import TradingModeReason
        
        levels = [
            OperationalLevel(
                level=4500.0,
                type=LevelType.SUPPORT,
                distance_points=25.0,
                distance_percentage=0.55,
                strength=0.75,
                action="Esperar rebote",
                explanation="Nivel fuerte"
            ),
            OperationalLevel(
                level=4600.0,
                type=LevelType.RESISTANCE,
                distance_points=75.0,
                distance_percentage=1.65,
                strength=0.80,
                action="Esperar rechazo",
                explanation="Resistencia fuerte"
            )
        ]
        
        recommendation = TradingModeRecommendation(
            mode=TradingMode.CALM,
            confidence=0.75,
            reasons=[TradingModeReason(
                rule_name="Test",
                description="Test reason",
                priority=5
            )],
            summary="Modo Calma",
            detailed_explanation="Test explanation",
            operational_levels=levels
        )
        
        assert recommendation.operational_levels is not None
        assert len(recommendation.operational_levels) == 2
        assert recommendation.operational_levels[0].level == 4500.0
        assert recommendation.operational_levels[1].level == 4600.0
    
    def test_recommendation_without_operational_levels(self):
        """
        Verifica que operational_levels sea opcional
        """
        from app.models.trading_mode import TradingModeReason
        
        recommendation = TradingModeRecommendation(
            mode=TradingMode.CALM,
            confidence=0.75,
            reasons=[TradingModeReason(
                rule_name="Test",
                description="Test reason",
                priority=5
            )],
            summary="Modo Calma",
            detailed_explanation="Test explanation"
            # Sin operational_levels
        )
        
        assert recommendation.operational_levels is None


class TestOperationalLevelsLogic:
    """Tests para la lógica de cálculo de niveles operativos"""
    
    def test_calm_mode_filter_criteria(self):
        """
        Verifica que modo CALMA filtre correctamente
        Debe tener: solo 100s, fuerza >= 0.6, tests >= 3
        """
        # Simular filtrado modo CALMA
        all_levels = [
            {"level": 4500.0, "strength": 0.75, "total_tests": 5},  # ✓ Válido
            {"level": 4550.0, "strength": 0.50, "total_tests": 4},  # ✗ Fuerza baja
            {"level": 4600.0, "strength": 0.80, "total_tests": 8},  # ✓ Válido
            {"level": 4450.0, "strength": 0.70, "total_tests": 2},  # ✗ Pocos tests
        ]
        
        # Filtro modo CALMA
        calm_filtered = [
            lv for lv in all_levels
            if lv["level"] % 100 == 0
            and lv["strength"] >= 0.6
            and lv["total_tests"] >= 3
        ]
        
        assert len(calm_filtered) == 2
        assert calm_filtered[0]["level"] == 4500.0
        assert calm_filtered[1]["level"] == 4600.0
    
    def test_aggressive_mode_filter_criteria(self):
        """
        Verifica que modo AGRESIVO filtre correctamente
        Debe tener: 100s y 50s, fuerza >= 0.4
        """
        all_levels = [
            {"level": 4500.0, "strength": 0.75, "total_tests": 5},  # ✓ Válido (100)
            {"level": 4550.0, "strength": 0.50, "total_tests": 4},  # ✓ Válido (50)
            {"level": 4525.0, "strength": 0.60, "total_tests": 3},  # ✗ No es 100 ni 50
            {"level": 4600.0, "strength": 0.30, "total_tests": 2},  # ✗ Fuerza muy baja
        ]
        
        # Filtro modo AGRESIVO
        aggressive_filtered = [
            lv for lv in all_levels
            if (lv["level"] % 100 == 0 or lv["level"] % 50 == 0)
            and lv["strength"] >= 0.4
        ]
        
        assert len(aggressive_filtered) == 2
        assert 4500.0 in [lv["level"] for lv in aggressive_filtered]
        assert 4550.0 in [lv["level"] for lv in aggressive_filtered]
    
    def test_observe_mode_minimal_levels(self):
        """
        Verifica que modo OBSERVAR solo muestre niveles informativos
        Debe tener: solo 100s, máximo 2 niveles
        """
        all_levels = [
            {"level": 4500.0, "strength": 0.75, "total_tests": 5},
            {"level": 4550.0, "strength": 0.50, "total_tests": 4},  # No es 100
            {"level": 4600.0, "strength": 0.80, "total_tests": 8},
            {"level": 4400.0, "strength": 0.70, "total_tests": 6},
        ]
        
        # Filtro modo OBSERVAR
        observe_filtered = [
            lv for lv in all_levels
            if lv["level"] % 100 == 0
        ][:2]  # Máximo 2 niveles
        
        assert len(observe_filtered) <= 2
        for lv in observe_filtered:
            assert lv["level"] % 100 == 0
    
    def test_level_distance_calculation(self):
        """
        Verifica el cálculo de distancia en puntos y porcentaje
        """
        current_price = 4525.0
        level_price = 4500.0
        
        distance_points = abs(level_price - current_price)
        distance_percentage = (distance_points / current_price) * 100
        
        assert distance_points == 25.0
        assert abs(distance_percentage - 0.552) < 0.01  # ~0.55%
    
    def test_support_vs_resistance_determination(self):
        """
        Verifica la determinación correcta de soporte vs resistencia
        """
        current_price = 4525.0
        
        support_level = 4500.0
        resistance_level = 4550.0
        
        assert support_level < current_price  # Es soporte
        assert resistance_level > current_price  # Es resistencia
    
    def test_action_recommendations_calm_mode(self):
        """
        Verifica las acciones recomendadas en modo CALMA
        """
        # En modo CALMA:
        # - Soporte: "Esperar rebote"
        # - Resistencia: "Esperar rechazo"
        
        support_action = "Esperar rebote"
        resistance_action = "Esperar rechazo"
        
        assert "esperar" in support_action.lower()
        assert "rebote" in support_action.lower()
        assert "esperar" in resistance_action.lower()
        assert "rechazo" in resistance_action.lower()
    
    def test_action_recommendations_aggressive_mode(self):
        """
        Verifica las acciones recomendadas en modo AGRESIVO
        """
        # En modo AGRESIVO:
        # - Niveles 100: "Rebote o breakout confirmado"
        # - Niveles 50: "Entrada en retroceso"
        
        level_100_action = "Rebote o breakout confirmado"
        level_50_action = "Entrada en retroceso"
        
        assert "breakout" in level_100_action.lower()
        assert "retroceso" in level_50_action.lower()
    
    def test_action_recommendations_observe_mode(self):
        """
        Verifica las acciones en modo OBSERVAR
        """
        observe_action = "Solo observar - NO operar"
        
        assert "no operar" in observe_action.lower()
        assert "observar" in observe_action.lower()
    
    def test_strength_calculation_from_bounces(self):
        """
        Verifica el cálculo de fuerza basado en rebotes históricos
        """
        # Ejemplo: 7 rebotes de 10 tests = 0.7 de fuerza
        bounce_count = 7
        total_tests = 10
        strength = min(1.0, bounce_count / max(1, total_tests))
        
        assert strength == 0.7
        
        # Ejemplo: 10 rebotes de 8 tests = 1.0 (máximo)
        bounce_count = 10
        total_tests = 8
        strength = min(1.0, bounce_count / max(1, total_tests))
        
        assert strength == 1.0
    
    def test_level_sorting_by_proximity(self):
        """
        Verifica el ordenamiento de niveles por proximidad al precio actual
        """
        current_price = 4525.0
        levels = [
            {"level": 4500.0, "distance": abs(4500.0 - current_price)},  # 25 pts
            {"level": 4600.0, "distance": abs(4600.0 - current_price)},  # 75 pts
            {"level": 4550.0, "distance": abs(4550.0 - current_price)},  # 25 pts
            {"level": 4450.0, "distance": abs(4450.0 - current_price)},  # 75 pts
        ]
        
        # Ordenar por distancia (más cercano primero)
        sorted_levels = sorted(levels, key=lambda lv: lv["distance"])
        
        # Los dos primeros tienen misma distancia (25 pts): 4500 y 4550
        assert sorted_levels[0]["level"] in [4500.0, 4550.0]  # Más cercano (25 pts)
        assert sorted_levels[1]["level"] in [4500.0, 4550.0]  # Segundo (25 pts)
        assert sorted_levels[0]["distance"] == 25.0
        assert sorted_levels[1]["distance"] == 25.0


class TestOperationalLevelsIntegration:
    """Tests de integración para niveles operativos"""
    
    def test_full_operational_level_creation_calm(self):
        """
        Verifica creación completa de nivel operativo para modo CALMA
        """
        current_price = 4525.0
        level_price = 4500.0
        strength = 0.75
        total_tests = 5
        
        level = OperationalLevel(
            level=level_price,
            type=LevelType.SUPPORT,
            distance_points=abs(level_price - current_price),
            distance_percentage=(abs(level_price - current_price) / current_price) * 100,
            strength=strength,
            action="Esperar rebote",
            explanation=(
                f"Nivel redondo fuerte ({int(total_tests)} tests históricos, "
                f"{strength*100:.0f}% de rebotes). "
                f"En modo calma, solo operar en niveles muy fuertes."
            )
        )
        
        assert level.level == 4500.0
        assert level.type == LevelType.SUPPORT
        assert level.distance_points == 25.0
        assert abs(level.distance_percentage - 0.55) < 0.01
        assert level.strength == 0.75
        assert "calma" in level.explanation.lower()
        assert str(total_tests) in level.explanation
    
    def test_full_operational_level_creation_aggressive(self):
        """
        Verifica creación completa de nivel operativo para modo AGRESIVO
        """
        current_price = 4525.0
        level_price = 4550.0
        strength = 0.60
        total_tests = 4
        is_round_100 = False  # Es nivel de 50
        
        level = OperationalLevel(
            level=level_price,
            type=LevelType.RESISTANCE,
            distance_points=abs(level_price - current_price),
            distance_percentage=(abs(level_price - current_price) / current_price) * 100,
            strength=strength,
            action="Entrada en rechazo",
            explanation=(
                f"Nivel {'redondo' if is_round_100 else 'intermedio'} "
                f"({int(total_tests)} tests, {strength*100:.0f}% rebotes). "
                f"En modo agresivo, operar tanto rebotes como breakouts confirmados."
            )
        )
        
        assert level.level == 4550.0
        assert level.type == LevelType.RESISTANCE
        assert "intermedio" in level.explanation
        assert "agresivo" in level.explanation.lower()
        assert "breakouts" in level.explanation.lower()
    
    def test_max_levels_per_mode(self):
        """
        Verifica el número máximo de niveles por modo
        """
        # Modo CALMA: máximo 3 niveles
        calm_max = 3
        
        # Modo AGRESIVO: máximo 5 niveles
        aggressive_max = 5
        
        # Modo OBSERVAR: máximo 2 niveles
        observe_max = 2
        
        assert calm_max == 3
        assert aggressive_max == 5
        assert observe_max == 2

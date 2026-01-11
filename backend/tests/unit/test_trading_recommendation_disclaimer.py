"""
Tests unitarios para disclaimer reforzado y ratio R:R en recomendaciones de trading
"""
import pytest
from app.models.trading_recommendation import (
    RiskRewardDetails,
    TradeRecommendation,
    TradeDirection
)
from app.services.trading_advisor_service import (
    DISCLAIMER_TEXT,
    MINIMUM_RISK_REWARD_RATIO
)


class TestDisclaimerEnhancement:
    """Tests para verificar el disclaimer reforzado"""
    
    def test_disclaimer_text_is_prominent(self):
        """
        Verifica que el texto del disclaimer sea prominente y claro
        """
        assert "⚠️" in DISCLAIMER_TEXT
        assert "ADVERTENCIA LEGAL" in DISCLAIMER_TEXT
        assert "NO ES ASESORÍA FINANCIERA" in DISCLAIMER_TEXT or "NO ES ASESORAMIENTO FINANCIERO" in DISCLAIMER_TEXT.upper()
        assert "RIESGO" in DISCLAIMER_TEXT
        assert "RESPONSABILIDAD" in DISCLAIMER_TEXT
    
    def test_disclaimer_mentions_key_risks(self):
        """
        Verifica que el disclaimer mencione los riesgos clave
        """
        disclaimer_upper = DISCLAIMER_TEXT.upper()
        assert "ALTO" in disclaimer_upper and "RIESGO" in disclaimer_upper
        assert "TODO" in disclaimer_upper and "CAPITAL" in disclaimer_upper
        assert "PERDER" in disclaimer_upper
        assert "RESULTADOS PASADOS" in disclaimer_upper
    
    def test_disclaimer_mentions_responsibility(self):
        """
        Verifica que el disclaimer deje clara la responsabilidad del usuario
        """
        disclaimer_upper = DISCLAIMER_TEXT.upper()
        assert "RESPONSABLE" in disclaimer_upper
        assert "DECISIONES" in disclaimer_upper
        assert "ASESOR" in disclaimer_upper or "PROFESIONAL" in disclaimer_upper
    
    def test_disclaimer_has_minimum_length(self):
        """
        Verifica que el disclaimer tenga longitud suficiente (mínimo 200 caracteres)
        """
        assert len(DISCLAIMER_TEXT) >= 200
    
    def test_minimum_risk_reward_ratio_is_defined(self):
        """
        Verifica que el ratio mínimo esté definido correctamente
        """
        assert MINIMUM_RISK_REWARD_RATIO == 1.5


class TestRiskRewardDetails:
    """Tests para el modelo RiskRewardDetails"""
    
    def test_risk_reward_details_model_creation(self):
        """
        Verifica que se pueda crear un modelo RiskRewardDetails correctamente
        """
        details = RiskRewardDetails(
            ratio="1:2.50",
            risk_points=20.0,
            reward_points=50.0,
            risk_percentage=0.44,
            reward_percentage=1.11,
            explanation="Riesgo: 20 puntos, Recompensa: 50 puntos",
            meets_minimum=True
        )
        
        assert details.ratio == "1:2.50"
        assert details.risk_points == 20.0
        assert details.reward_points == 50.0
        assert details.risk_percentage == 0.44
        assert details.reward_percentage == 1.11
        assert details.meets_minimum is True
        assert "Riesgo" in details.explanation
    
    def test_risk_reward_details_meets_minimum_validation(self):
        """
        Verifica que el campo meets_minimum funcione correctamente
        """
        # Ratio que cumple mínimo (2.5 > 1.5)
        good_details = RiskRewardDetails(
            ratio="1:2.50",
            risk_points=10.0,
            reward_points=25.0,
            risk_percentage=0.5,
            reward_percentage=1.25,
            explanation="Good ratio",
            meets_minimum=True
        )
        assert good_details.meets_minimum is True
        
        # Ratio que NO cumple mínimo (1.2 < 1.5)
        bad_details = RiskRewardDetails(
            ratio="1:1.20",
            risk_points=10.0,
            reward_points=12.0,
            risk_percentage=0.5,
            reward_percentage=0.6,
            explanation="Bad ratio",
            meets_minimum=False
        )
        assert bad_details.meets_minimum is False


class TestTradeRecommendationModel:
    """Tests para verificar el modelo TradeRecommendation mejorado"""
    
    def test_disclaimer_is_first_field(self):
        """
        Verifica que el disclaimer sea el primer campo del modelo
        """
        # Obtener los campos del modelo
        fields = list(TradeRecommendation.model_fields.keys())
        
        # El disclaimer debe estar entre los primeros campos
        disclaimer_index = fields.index('disclaimer')
        assert disclaimer_index < 5, "Disclaimer debería estar entre los primeros 5 campos"
    
    def test_recommendation_requires_disclaimer(self):
        """
        Verifica que el disclaimer sea obligatorio
        """
        # Intentar crear recomendación sin disclaimer (debería fallar)
        with pytest.raises(Exception):  # ValidationError de Pydantic
            TradeRecommendation(
                # Sin disclaimer
                analysis_date="2026-01-11",
                analysis_datetime="2026-01-11T10:00:00",
                current_datetime="2026-01-11T10:00:00",
                direction=TradeDirection.BUY,
                confidence=0.75,
                current_price=4500.0,
                market_context="risk-on",
                trading_mode="agresivo",
                reasons=["test"],
                summary="test",
                detailed_explanation="test",
                risk_reward_ratio="1:2.50",
                confidence_breakdown={
                    "technical_analysis": 0.7,
                    "market_context": 0.6,
                    "news_impact": 0.9,
                    "overall": 0.7
                }
            )
    
    def test_recommendation_with_all_required_fields(self):
        """
        Verifica que se pueda crear una recomendación con todos los campos requeridos
        """
        recommendation = TradeRecommendation(
            disclaimer=DISCLAIMER_TEXT,
            analysis_date="2026-01-11",
            analysis_datetime="2026-01-11T10:00:00",
            current_datetime="2026-01-11T10:00:00",
            direction=TradeDirection.BUY,
            confidence=0.75,
            current_price=4500.0,
            entry_price=4498.0,
            stop_loss=4480.0,
            take_profit_1=4540.0,
            support_level=4475.0,
            resistance_level=4550.0,
            market_context="risk-on",
            trading_mode="agresivo",
            reasons=["Momentum alcista", "DXY débil"],
            summary="Compra en 4498",
            detailed_explanation="Operación de compra recomendada...",
            risk_reward_ratio="1:2.33",
            confidence_breakdown={
                "technical_analysis": 0.7,
                "market_context": 0.6,
                "news_impact": 0.9,
                "overall": 0.73
            }
        )
        
        assert recommendation.disclaimer == DISCLAIMER_TEXT
        assert recommendation.direction == TradeDirection.BUY
        assert recommendation.risk_reward_ratio == "1:2.33"
    
    def test_recommendation_with_risk_reward_details(self):
        """
        Verifica que se puedan incluir detalles completos del R:R
        """
        details = RiskRewardDetails(
            ratio="1:2.50",
            risk_points=18.0,
            reward_points=45.0,
            risk_percentage=0.40,
            reward_percentage=1.00,
            explanation="Riesgo: 18 puntos (0.40%), Recompensa: 45 puntos (1.00%)",
            meets_minimum=True
        )
        
        recommendation = TradeRecommendation(
            disclaimer=DISCLAIMER_TEXT,
            analysis_date="2026-01-11",
            analysis_datetime="2026-01-11T10:00:00",
            current_datetime="2026-01-11T10:00:00",
            direction=TradeDirection.BUY,
            confidence=0.75,
            current_price=4500.0,
            entry_price=4498.0,
            stop_loss=4480.0,
            take_profit_1=4543.0,
            market_context="risk-on",
            trading_mode="agresivo",
            reasons=["test"],
            summary="test",
            detailed_explanation="test",
            risk_reward_ratio="1:2.50",
            risk_reward_details=details,
            confidence_breakdown={
                "technical_analysis": 0.7,
                "market_context": 0.6,
                "news_impact": 0.9,
                "overall": 0.73
            }
        )
        
        assert recommendation.risk_reward_details is not None
        assert recommendation.risk_reward_details.ratio == "1:2.50"
        assert recommendation.risk_reward_details.meets_minimum is True
        assert recommendation.risk_reward_details.risk_points == 18.0
        assert recommendation.risk_reward_details.reward_points == 45.0


class TestTradingAdvisorServiceRiskReward:
    """Tests para el cálculo mejorado de R:R en TradingAdvisorService"""
    
    def test_calculate_risk_reward_with_details_buy(self):
        """
        Verifica el cálculo de R:R con detalles para operación de compra
        """
        from app.services.trading_advisor_service import TradingAdvisorService
        from app.config.settings import Settings
        
        # Crear instancia del servicio (sin dependencias necesarias para este test)
        service = TradingAdvisorService(
            settings=Settings(),
            market_analysis_service=None,
            market_alignment_service=None,
            trading_mode_service=None,
            economic_calendar_service=None
        )
        
        # Calcular R:R para compra
        direction = TradeDirection.BUY
        entry = 4500.0
        stop_loss = 4480.0  # Riesgo: 20 puntos
        take_profit = 4550.0  # Recompensa: 50 puntos
        
        ratio_str, details = service._calculate_risk_reward_with_details(
            direction, entry, stop_loss, take_profit
        )
        
        # Verificar ratio string
        assert ratio_str == "1:2.50"
        
        # Verificar detalles
        assert details.ratio == "1:2.50"
        assert details.risk_points == 20.0
        assert details.reward_points == 50.0
        assert details.meets_minimum is True  # 2.5 > 1.5
        assert "20.00 puntos" in details.explanation
        assert "50.00 puntos" in details.explanation
    
    def test_calculate_risk_reward_with_details_sell(self):
        """
        Verifica el cálculo de R:R con detalles para operación de venta
        """
        from app.services.trading_advisor_service import TradingAdvisorService
        from app.config.settings import Settings
        
        service = TradingAdvisorService(
            settings=Settings(),
            market_analysis_service=None,
            market_alignment_service=None,
            trading_mode_service=None,
            economic_calendar_service=None
        )
        
        # Calcular R:R para venta
        direction = TradeDirection.SELL
        entry = 4500.0
        stop_loss = 4520.0  # Riesgo: 20 puntos
        take_profit = 4460.0  # Recompensa: 40 puntos
        
        ratio_str, details = service._calculate_risk_reward_with_details(
            direction, entry, stop_loss, take_profit
        )
        
        # Verificar ratio string
        assert ratio_str == "1:2.00"
        
        # Verificar detalles
        assert details.ratio == "1:2.00"
        assert details.risk_points == 20.0
        assert details.reward_points == 40.0
        assert details.meets_minimum is True  # 2.0 > 1.5
        assert "VENTA" in details.explanation
    
    def test_calculate_risk_reward_below_minimum(self):
        """
        Verifica que se detecte cuando el ratio NO cumple el mínimo
        """
        from app.services.trading_advisor_service import TradingAdvisorService
        from app.config.settings import Settings
        
        service = TradingAdvisorService(
            settings=Settings(),
            market_analysis_service=None,
            market_alignment_service=None,
            trading_mode_service=None,
            economic_calendar_service=None
        )
        
        # Ratio bajo: 1:1.2 (< 1.5)
        direction = TradeDirection.BUY
        entry = 4500.0
        stop_loss = 4480.0  # Riesgo: 20 puntos
        take_profit = 4524.0  # Recompensa: 24 puntos → ratio 1:1.2
        
        ratio_str, details = service._calculate_risk_reward_with_details(
            direction, entry, stop_loss, take_profit
        )
        
        # Verificar que NO cumple mínimo
        assert details.meets_minimum is False
        assert "⚠️" in details.explanation or "NO cumple" in details.explanation
        assert "1:1.5" in details.explanation or "1.5" in details.explanation
    
    def test_calculate_risk_reward_percentages(self):
        """
        Verifica que se calculen correctamente los porcentajes
        """
        from app.services.trading_advisor_service import TradingAdvisorService
        from app.config.settings import Settings
        
        service = TradingAdvisorService(
            settings=Settings(),
            market_analysis_service=None,
            market_alignment_service=None,
            trading_mode_service=None,
            economic_calendar_service=None
        )
        
        direction = TradeDirection.BUY
        entry = 4500.0
        stop_loss = 4455.0  # Riesgo: 45 puntos = 1% del precio
        take_profit = 4590.0  # Recompensa: 90 puntos = 2% del precio
        
        ratio_str, details = service._calculate_risk_reward_with_details(
            direction, entry, stop_loss, take_profit
        )
        
        # Verificar porcentajes (con tolerancia de ±0.01%)
        assert abs(details.risk_percentage - 1.0) < 0.01
        assert abs(details.reward_percentage - 2.0) < 0.01
        
        # Verificar que los porcentajes estén en la explicación
        assert "%" in details.explanation
    
    def test_legacy_calculate_risk_reward_ratio_still_works(self):
        """
        Verifica que el método legacy aún funcione (compatibilidad)
        """
        from app.services.trading_advisor_service import TradingAdvisorService
        from app.config.settings import Settings
        
        service = TradingAdvisorService(
            settings=Settings(),
            market_analysis_service=None,
            market_alignment_service=None,
            trading_mode_service=None,
            economic_calendar_service=None
        )
        
        ratio_str = service._calculate_risk_reward_ratio(
            entry=4500.0,
            stop_loss=4480.0,
            take_profit=4550.0
        )
        
        assert ratio_str == "1:2.50"

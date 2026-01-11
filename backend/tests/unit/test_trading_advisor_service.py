"""
Tests unitarios para TradingAdvisorService
"""
import pytest
from unittest.mock import MagicMock

from app.services.trading_advisor_service import TradingAdvisorService
from app.config.settings import Settings

@pytest.fixture
def mock_dependencies():
    """Mock dependencies for TradingAdvisorService"""
    settings = Settings(
        economic_calendar_provider="mock",
        market_data_provider="mock",
        default_currency="USD"
    )
    return {
        "settings": settings,
        "market_analysis_service": MagicMock(),
        "market_alignment_service": MagicMock(),
        "trading_mode_service": MagicMock(),
        "economic_calendar_service": MagicMock(),
        "technical_analysis_service": MagicMock()
    }

class TestTradingAdvisorService:
    """Tests para TradingAdvisorService"""
    
    def test_calculate_risk_reward_ratio_buy(self, mock_dependencies):
        """Test cálculo de ratio en compra"""
        service = TradingAdvisorService(**mock_dependencies)
        
        # Risk: 4500 - 4480 = 20
        # Reward: 4540 - 4500 = 40
        # Ratio: 40/20 = 2.0
        result = service._calculate_risk_reward_ratio(
            entry=4500.0,
            stop_loss=4480.0,
            take_profit=4540.0
        )
        
        assert result == "1:2.00"
    
    def test_calculate_risk_reward_ratio_sell(self, mock_dependencies):
        """Test cálculo de ratio en venta"""
        service = TradingAdvisorService(**mock_dependencies)
        
        # Risk: 4520 - 4500 = 20
        # Reward: 4500 - 4460 = 40
        # Ratio: 40/20 = 2.0
        result = service._calculate_risk_reward_ratio(
            entry=4500.0,
            stop_loss=4520.0,
            take_profit=4460.0
        )
        
        assert result == "1:2.00"
    
    def test_calculate_risk_reward_ratio_zero_risk(self, mock_dependencies):
        """Test manejo de riesgo cero"""
        service = TradingAdvisorService(**mock_dependencies)
        
        result = service._calculate_risk_reward_ratio(
            entry=4500.0,
            stop_loss=4500.0,
            take_profit=4520.0
        )
        
        assert result == "1:0.00"

    def test_calculate_risk_reward_ratio_small_values(self, mock_dependencies):
        """Test con valores decimales"""
        service = TradingAdvisorService(**mock_dependencies)
        
        # Risk: 1.5
        # Reward: 2.25
        # Ratio: 1.5
        result = service._calculate_risk_reward_ratio(
            entry=4500.0,
            stop_loss=4498.5,
            take_profit=4502.25
        )
        
        assert result == "1:1.50"

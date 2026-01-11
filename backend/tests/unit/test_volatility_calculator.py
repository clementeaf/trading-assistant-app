"""
Tests unitarios para volatility_calculator
"""
import pytest
from datetime import datetime, timedelta

from app.models.market_analysis import PriceCandle, VolatilityLevel
from app.utils.volatility_calculator import VolatilityCalculator


class TestVolatilityCalculator:
    """Tests para VolatilityCalculator"""
    
    def test_calculate_atr_basic(self):
        """Test cálculo básico de ATR"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=i),
                open=100.0 + i,
                high=102.0 + i,
                low=99.0 + i,
                close=101.0 + i
            )
            for i in range(15)
        ]
        
        atr = VolatilityCalculator.calculate_atr(candles, period=14)
        
        assert atr > 0
        assert isinstance(atr, float)
    
    def test_calculate_atr_empty_candles(self):
        """Test ATR con lista vacía"""
        atr = VolatilityCalculator.calculate_atr([], period=14)
        assert atr == 0.0
    
    def test_calculate_atr_single_candle(self):
        """Test ATR con una sola vela"""
        candles = [
            PriceCandle(
                timestamp=datetime.now(),
                open=100.0,
                high=102.0,
                low=99.0,
                close=101.0
            )
        ]
        
        atr = VolatilityCalculator.calculate_atr(candles, period=14)
        assert atr == 0.0
    
    def test_calculate_range_percent(self):
        """Test cálculo de porcentaje de rango"""
        range_value = 10.0
        price = 1000.0
        
        percent = VolatilityCalculator.calculate_range_percent(range_value, price)
        
        assert percent == 1.0
    
    def test_calculate_range_percent_zero_price(self):
        """Test porcentaje de rango con precio cero"""
        percent = VolatilityCalculator.calculate_range_percent(10.0, 0.0)
        assert percent == 0.0
    
    def test_classify_volatility_extreme(self):
        """Test clasificación de volatilidad extrema"""
        atr = 30.0
        average_atr = 20.0
        
        level = VolatilityCalculator.classify_volatility(atr, average_atr)
        
        assert level == VolatilityLevel.EXTREME
    
    def test_classify_volatility_high(self):
        """Test clasificación de volatilidad alta"""
        atr = 24.0
        average_atr = 20.0
        
        level = VolatilityCalculator.classify_volatility(atr, average_atr)
        
        assert level == VolatilityLevel.HIGH
    
    def test_classify_volatility_normal(self):
        """Test clasificación de volatilidad normal"""
        atr = 18.0
        average_atr = 20.0
        
        level = VolatilityCalculator.classify_volatility(atr, average_atr)
        
        assert level == VolatilityLevel.NORMAL
    
    def test_classify_volatility_low(self):
        """Test clasificación de volatilidad baja"""
        atr = 10.0
        average_atr = 20.0
        
        level = VolatilityCalculator.classify_volatility(atr, average_atr)
        
        assert level == VolatilityLevel.LOW
    
    def test_classify_volatility_zero_average(self):
        """Test clasificación con promedio cero"""
        level = VolatilityCalculator.classify_volatility(10.0, 0.0)
        assert level == VolatilityLevel.NORMAL
    
    def test_analyze_session_volatility(self):
        """Test análisis de volatilidad de sesión"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=i),
                open=4500.0 + i * 2,
                high=4510.0 + i * 2,
                low=4490.0 + i * 2,
                close=4505.0 + i * 2
            )
            for i in range(10)
        ]
        
        result = VolatilityCalculator.analyze_session_volatility(candles)
        
        assert "atr" in result
        assert "range_percent" in result
        assert "level" in result
        assert "description" in result
        assert result["atr"] >= 0
        assert result["range_percent"] >= 0
    
    def test_analyze_session_volatility_empty(self):
        """Test análisis de volatilidad con lista vacía"""
        result = VolatilityCalculator.analyze_session_volatility([])
        
        assert result["atr"] == 0.0
        assert result["range_percent"] == 0.0
        assert result["level"] == VolatilityLevel.NORMAL.value
    
    def test_analyze_session_volatility_with_historical(self):
        """Test análisis de volatilidad con datos históricos"""
        session_candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=i),
                open=4500.0,
                high=4520.0,
                low=4480.0,
                close=4510.0
            )
            for i in range(5)
        ]
        
        historical_candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(days=i),
                open=4500.0,
                high=4510.0,
                low=4490.0,
                close=4505.0
            )
            for i in range(20)
        ]
        
        result = VolatilityCalculator.analyze_session_volatility(
            session_candles,
            historical_candles,
            period=14
        )
        
        assert "vs_historical" in result
        assert result["level"] in [v.value for v in VolatilityLevel]

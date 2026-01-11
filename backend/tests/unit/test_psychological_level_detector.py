"""
Tests unitarios para psychological_level_detector
"""
import pytest
from datetime import datetime, timedelta

from app.models.market_analysis import PriceCandle, PsychologicalBreak
from app.utils.psychological_level_detector import PsychologicalLevelDetector


class TestPsychologicalLevelDetector:
    """Tests para PsychologicalLevelDetector"""
    
    def test_generate_psychological_levels_basic(self):
        """Test generación básica de niveles psicológicos"""
        levels = PsychologicalLevelDetector.generate_psychological_levels(
            min_price=4400.0,
            max_price=4600.0,
            include_fifties=True
        )
        
        assert 4500.0 in levels
        assert 4550.0 in levels
        assert 4600.0 in levels
        assert len(levels) > 0
    
    def test_generate_psychological_levels_no_fifties(self):
        """Test generación sin niveles de 50"""
        levels = PsychologicalLevelDetector.generate_psychological_levels(
            min_price=4400.0,
            max_price=4600.0,
            include_fifties=False
        )
        
        assert 4500.0 in levels
        assert 4550.0 not in levels
        assert 4600.0 in levels
    
    def test_generate_psychological_levels_sorted(self):
        """Test que niveles estén ordenados"""
        levels = PsychologicalLevelDetector.generate_psychological_levels(
            min_price=4000.0,
            max_price=5000.0
        )
        
        assert levels == sorted(levels)
    
    def test_detect_breaks_bullish(self):
        """Test detección de ruptura alcista"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=4),
                open=4490.0,
                high=4495.0,
                low=4485.0,
                close=4492.0
            ),
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=3),
                open=4492.0,
                high=4508.0,
                low=4490.0,
                close=4507.0
            ),
        ]
        
        breaks = PsychologicalLevelDetector.detect_breaks_in_session(candles, tolerance=5.0)
        
        # Debe detectar ruptura del nivel 4500
        assert len(breaks) > 0
        bullish_breaks = [b for b in breaks if b.break_type == "alcista"]
        assert len(bullish_breaks) > 0
    
    def test_detect_breaks_bearish(self):
        """Test detección de ruptura bajista"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=4),
                open=4510.0,
                high=4515.0,
                low=4505.0,
                close=4508.0
            ),
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=3),
                open=4508.0,
                high=4510.0,
                low=4492.0,
                close=4493.0
            ),
        ]
        
        breaks = PsychologicalLevelDetector.detect_breaks_in_session(candles, tolerance=5.0)
        
        # Debe detectar ruptura del nivel 4500
        assert len(breaks) > 0
        bearish_breaks = [b for b in breaks if b.break_type == "bajista"]
        assert len(bearish_breaks) > 0
    
    def test_detect_breaks_no_breaks(self):
        """Test sin rupturas"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=i),
                open=4505.0,
                high=4510.0,
                low=4500.0,
                close=4507.0
            )
            for i in range(5)
        ]
        
        breaks = PsychologicalLevelDetector.detect_breaks_in_session(candles, tolerance=5.0)
        
        # No debe detectar rupturas (solo toca el nivel pero no rompe)
        assert len(breaks) == 0
    
    def test_detect_breaks_empty_candles(self):
        """Test con lista vacía"""
        breaks = PsychologicalLevelDetector.detect_breaks_in_session([])
        assert len(breaks) == 0
    
    def test_format_breaks_description_empty(self):
        """Test formato de descripción vacía"""
        description = PsychologicalLevelDetector.format_breaks_description([])
        assert description == ""
    
    def test_format_breaks_description_single(self):
        """Test formato de descripción con una ruptura"""
        breaks = [
            PsychologicalBreak(
                level=4500.0,
                break_type="alcista",
                break_price=4507.0,
                confirmed=True
            )
        ]
        
        description = PsychologicalLevelDetector.format_breaks_description(breaks)
        
        assert "4500" in description
        assert "alcista" in description
        assert "confirmada" in description
    
    def test_format_breaks_description_multiple(self):
        """Test formato de descripción con múltiples rupturas"""
        breaks = [
            PsychologicalBreak(
                level=4500.0,
                break_type="alcista",
                break_price=4507.0,
                confirmed=True
            ),
            PsychologicalBreak(
                level=4550.0,
                break_type="bajista",
                break_price=4543.0,
                confirmed=False
            )
        ]
        
        description = PsychologicalLevelDetector.format_breaks_description(breaks)
        
        assert "4500" in description
        assert "4550" in description
        assert "alcista" in description
        assert "bajista" in description
    
    def test_break_confirmation_confirmed(self):
        """Test ruptura confirmada"""
        candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=5),
                open=4490.0,
                high=4495.0,
                low=4485.0,
                close=4492.0
            ),
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=4),
                open=4492.0,
                high=4508.0,
                low=4490.0,
                close=4507.0  # Ruptura alcista
            ),
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=3),
                open=4507.0,
                high=4512.0,
                low=4505.0,
                close=4510.0  # Confirmación
            ),
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=2),
                open=4510.0,
                high=4515.0,
                low=4508.0,
                close=4512.0  # Confirmación
            ),
        ]
        
        breaks = PsychologicalLevelDetector.detect_breaks_in_session(candles, tolerance=5.0)
        
        confirmed_breaks = [b for b in breaks if b.confirmed]
        assert len(confirmed_breaks) > 0

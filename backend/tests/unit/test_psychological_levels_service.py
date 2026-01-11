"""
Tests unitarios para PsychologicalLevelsService
"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config.settings import Settings
from app.models.market_analysis import PriceCandle
from app.models.psychological_levels import LevelType, ReactionType
from app.services.psychological_levels_service import PsychologicalLevelsService


@pytest.fixture
def test_settings_with_api_key() -> Settings:
    """Configuración de prueba con API key"""
    return Settings(
        economic_calendar_provider="mock",
        market_data_provider="twelvedata",
        market_data_api_key="test_api_key_12345",
        default_currency="USD"
    )


@pytest.fixture
def sample_candles_at_4500():
    """Velas de ejemplo alrededor del nivel 4500"""
    base_time = datetime.now() - timedelta(days=5)
    return [
        # Vela que rebota en 4500 (soporte)
        PriceCandle(
            timestamp=base_time,
            open=4505.0,
            high=4510.0,
            low=4499.5,  # Toca 4500
            close=4508.0,
            volume=1000
        ),
        # Vela que rebota en 4500 nuevamente
        PriceCandle(
            timestamp=base_time + timedelta(hours=4),
            open=4503.0,
            high=4507.0,
            low=4500.2,  # Toca 4500
            close=4506.0,
            volume=1000
        ),
        # Vela que rompe 4500
        PriceCandle(
            timestamp=base_time + timedelta(hours=8),
            open=4502.0,
            high=4503.0,
            low=4495.0,  # Rompe 4500
            close=4496.0,
            volume=1000
        ),
    ]


@pytest.fixture
def sample_candles_range():
    """Velas de ejemplo en rango 4480-4520"""
    base_time = datetime.now() - timedelta(days=10)
    candles = []
    
    # Generar 50 velas en rango
    for i in range(50):
        price = 4500 + (i % 20 - 10) * 2  # Oscila entre 4480 y 4520
        candles.append(
            PriceCandle(
                timestamp=base_time + timedelta(hours=i),
                open=price,
                high=price + 2,
                low=price - 2,
                close=price + 1,
                volume=1000
            )
        )
    
    return candles


class TestPsychologicalLevelsService:
    """Tests para PsychologicalLevelsService"""
    
    def test_generate_round_levels_around_4500(self):
        """Test generación de niveles redondos alrededor de 4500"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        max_distance = 100.0
        
        levels = service._generate_round_levels(current_price, max_distance)
        
        # Debe incluir niveles de 100: 4500, 4600
        assert 4500.0 in levels
        assert 4600.0 in levels
        
        # Debe incluir niveles de 50: 4450, 4550
        assert 4450.0 in levels
        assert 4550.0 in levels
        
        # No debe incluir niveles muy lejanos
        assert 4700.0 not in levels  # Más de 100 puntos
        assert 4400.0 not in levels  # Más de 100 puntos
        
        # Todos los niveles deben estar dentro de la distancia máxima
        for level in levels:
            assert abs(level - current_price) <= max_distance
    
    def test_generate_round_levels_no_duplicates(self):
        """Test que no haya niveles duplicados"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        levels = service._generate_round_levels(4500.0, 200.0)
        
        # No debe haber duplicados
        assert len(levels) == len(set(levels))
    
    def test_analyze_level_bounce_detection(self, sample_candles_at_4500):
        """Test detección de rebotes en un nivel"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level = 4500.0
        
        analysis = service._analyze_level(level, current_price, sample_candles_at_4500)
        
        # Debe detectar al menos 2 rebotes
        assert analysis.bounce_count >= 2
        assert analysis.reaction_count >= 2
        
        # Debe ser identificado como soporte (nivel está debajo del precio actual)
        assert analysis.type == LevelType.SUPPORT
        
        # Debe tener fuerza > 0
        assert analysis.strength > 0
        
        # Debe ser nivel de 100
        assert analysis.is_round_hundred is True
        assert analysis.is_round_fifty is False
    
    def test_analyze_level_break_detection(self, sample_candles_at_4500):
        """Test detección de rupturas de nivel"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level = 4500.0
        
        analysis = service._analyze_level(level, current_price, sample_candles_at_4500)
        
        # Debe detectar al menos 1 ruptura
        assert analysis.break_count >= 1
    
    def test_analyze_level_strength_calculation(self, sample_candles_range):
        """Test cálculo de fuerza del nivel"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level = 4500.0
        
        analysis = service._analyze_level(level, current_price, sample_candles_range)
        
        # Fuerza debe estar entre 0 y 1
        assert 0.0 <= analysis.strength <= 1.0
        
        # Si hay rebotes, fuerza debe ser > 0
        if analysis.bounce_count > 0:
            assert analysis.strength > 0
    
    def test_analyze_level_distance_calculation(self):
        """Test cálculo de distancia desde precio actual"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level = 4500.0
        
        analysis = service._analyze_level(level, current_price, [])
        
        # Distancia debe ser -10 (nivel está 10 puntos abajo)
        assert analysis.distance_from_current == -10.0
        
        # Porcentaje debe ser negativo
        assert analysis.distance_percent < 0
    
    def test_analyze_level_type_support(self):
        """Test identificación de nivel como soporte"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level_below = 4500.0
        
        analysis = service._analyze_level(level_below, current_price, [])
        
        assert analysis.type == LevelType.SUPPORT
    
    def test_analyze_level_type_resistance(self):
        """Test identificación de nivel como resistencia"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        current_price = 4510.0
        level_above = 4550.0
        
        analysis = service._analyze_level(level_above, current_price, [])
        
        assert analysis.type == LevelType.RESISTANCE
    
    def test_analyze_level_round_hundred_detection(self):
        """Test detección de niveles de 100"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        analysis_4500 = service._analyze_level(4500.0, 4510.0, [])
        analysis_4600 = service._analyze_level(4600.0, 4510.0, [])
        
        assert analysis_4500.is_round_hundred is True
        assert analysis_4500.is_round_fifty is False
        
        assert analysis_4600.is_round_hundred is True
        assert analysis_4600.is_round_fifty is False
    
    def test_analyze_level_round_fifty_detection(self):
        """Test detección de niveles de 50"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        analysis_4550 = service._analyze_level(4550.0, 4510.0, [])
        analysis_4450 = service._analyze_level(4450.0, 4510.0, [])
        
        assert analysis_4550.is_round_fifty is True
        assert analysis_4550.is_round_hundred is False
        
        assert analysis_4450.is_round_fifty is True
        assert analysis_4450.is_round_hundred is False
    
    @pytest.mark.asyncio
    async def test_get_current_price(self, test_settings_with_api_key):
        """Test obtención de precio actual"""
        service = PsychologicalLevelsService(test_settings_with_api_key)
        
        # Mock del provider
        mock_candles = [
            PriceCandle(
                timestamp=datetime.now(),
                open=4500.0,
                high=4510.0,
                low=4495.0,
                close=4505.0,
                volume=1000
            )
        ]
        
        with patch.object(service.provider, 'fetch_historical_candles', 
                         new_callable=AsyncMock, return_value=mock_candles):
            price = await service._get_current_price("XAUUSD")
            
            assert price == 4505.0
    
    @pytest.mark.asyncio
    async def test_get_psychological_levels_integration(self, test_settings_with_api_key):
        """Test integración completa del servicio"""
        service = PsychologicalLevelsService(test_settings_with_api_key)
        
        # Mock del provider
        current_candle = [
            PriceCandle(
                timestamp=datetime.now(),
                open=4500.0,
                high=4510.0,
                low=4495.0,
                close=4505.0,
                volume=1000
            )
        ]
        
        historical_candles = [
            PriceCandle(
                timestamp=datetime.now() - timedelta(hours=i),
                open=4500.0 + i,
                high=4510.0 + i,
                low=4495.0 + i,
                close=4505.0 + i,
                volume=1000
            )
            for i in range(50)
        ]
        
        async def mock_fetch(instrument, start, end, interval):
            # Retornar current_candle para precio actual, historical para análisis
            if (end - start).total_seconds() < 7200:  # < 2 horas
                return current_candle
            return historical_candles
        
        with patch.object(service.provider, 'fetch_historical_candles', 
                         new_callable=AsyncMock, side_effect=mock_fetch):
            result = await service.get_psychological_levels(
                instrument="XAUUSD",
                lookback_days=30,
                max_distance_points=100.0
            )
            
            # Verificar estructura de respuesta
            assert result.instrument == "XAUUSD"
            assert result.current_price == 4505.0
            assert len(result.levels) > 0
            assert result.summary is not None
            
            # Verificar que hay niveles identificados
            assert result.nearest_support is not None or result.nearest_resistance is not None
    
    def test_generate_summary(self):
        """Test generación de resumen"""
        service = PsychologicalLevelsService(test_settings_with_api_key())
        
        from app.models.psychological_levels import PsychologicalLevel
        
        nearest_support = PsychologicalLevel(
            level=4500.0,
            distance_from_current=-10.0,
            distance_percent=-0.22,
            strength=0.8,
            reaction_count=4,
            type=LevelType.SUPPORT,
            bounce_count=4,
            break_count=0,
            is_round_hundred=True,
            is_round_fifty=False
        )
        
        nearest_resistance = PsychologicalLevel(
            level=4550.0,
            distance_from_current=40.0,
            distance_percent=0.88,
            strength=0.6,
            reaction_count=3,
            type=LevelType.RESISTANCE,
            bounce_count=3,
            break_count=0,
            is_round_hundred=False,
            is_round_fifty=True
        )
        
        summary = service._generate_summary(
            4510.0,
            nearest_support,
            nearest_resistance,
            nearest_support,
            nearest_resistance
        )
        
        # Verificar que el resumen contiene información clave
        assert "4510.00" in summary  # Precio actual
        assert "4500.00" in summary  # Soporte
        assert "4550.00" in summary  # Resistencia
        assert "0.80" in summary or "0.8" in summary  # Fuerza del soporte

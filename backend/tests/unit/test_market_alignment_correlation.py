"""
Tests para MarketAlignmentService con correlación Gold-DXY
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.market_alignment_service import MarketAlignmentService
from app.config.settings import Settings
from app.models.market_analysis import PriceCandle
from app.utils.correlation_calculator import CorrelationStrength


class TestMarketAlignmentServiceCorrelation:
    """
    Tests para correlación Gold-DXY en MarketAlignmentService
    """
    
    @pytest.fixture
    def mock_settings(self) -> Settings:
        """
        Settings mock para tests
        """
        settings = MagicMock(spec=Settings)
        settings.market_data_provider = "mock"
        settings.market_data_api_key = "test_key"
        settings.fred_api_key = "test_fred_key"
        return settings
    
    @pytest.fixture
    def service(self, mock_settings: Settings) -> MarketAlignmentService:
        """
        Servicio con settings mock
        """
        return MarketAlignmentService(settings=mock_settings)
    
    def _create_mock_candles(
        self,
        symbol: str,
        days: int,
        start_price: float,
        trend: str = "up"
    ) -> list[PriceCandle]:
        """
        Crea candles mock con tendencia
        """
        candles = []
        base_time = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            if trend == "up":
                price = start_price + (i * 10)
            elif trend == "down":
                price = start_price - (i * 10)
            else:
                price = start_price
            
            candle = PriceCandle(
                timestamp=base_time + timedelta(days=i),
                open=price,
                high=price + 5,
                low=price - 5,
                close=price,
                volume=1000000
            )
            candles.append(candle)
        
        return candles
    
    @pytest.mark.asyncio
    async def test_calculate_gold_dxy_correlation_negative(
        self,
        service: MarketAlignmentService
    ) -> None:
        """
        Correlación negativa Gold-DXY (típica)
        """
        # Gold sube, DXY baja → correlación negativa
        gold_candles = self._create_mock_candles("XAUUSD", 30, 2000.0, "up")
        dxy_candles = self._create_mock_candles("DXY", 30, 100.0, "down")
        
        with patch.object(
            service.provider,
            'fetch_historical_candles',
            new_callable=AsyncMock
        ) as mock_fetch:
            def side_effect(symbol: str, *args, **kwargs) -> list[PriceCandle]:
                if symbol == "XAUUSD":
                    return gold_candles
                elif symbol == "DXY":
                    return dxy_candles
                return []
            
            mock_fetch.side_effect = side_effect
            
            with patch.object(
                service,
                '_get_dxy_bond_provider',
                return_value=service.provider
            ):
                correlation, projection = await service._calculate_gold_dxy_correlation(
                    gold_symbol="XAUUSD",
                    correlation_days=30,
                    dxy_current=100.0
                )
        
        assert correlation.coefficient < 0
        assert correlation.strength in [
            CorrelationStrength.VERY_STRONG,
            CorrelationStrength.STRONG,
            CorrelationStrength.MODERATE
        ]
        assert correlation.is_significant is True
        assert "inversa" in correlation.interpretation
        
        assert projection.dxy_change_percent == 1.0
        assert projection.expected_gold_change_percent < 0
        assert projection.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_gold_dxy_correlation_insufficient_data(
        self,
        service: MarketAlignmentService
    ) -> None:
        """
        Error cuando no hay suficientes datos
        """
        gold_candles = self._create_mock_candles("XAUUSD", 10, 2000.0, "up")
        dxy_candles = self._create_mock_candles("DXY", 10, 100.0, "down")
        
        with patch.object(
            service.provider,
            'fetch_historical_candles',
            new_callable=AsyncMock
        ) as mock_fetch:
            def side_effect(symbol: str, *args, **kwargs) -> list[PriceCandle]:
                if symbol == "XAUUSD":
                    return gold_candles
                elif symbol == "DXY":
                    return dxy_candles
                return []
            
            mock_fetch.side_effect = side_effect
            
            with patch.object(
                service,
                '_get_dxy_bond_provider',
                return_value=service.provider
            ):
                with pytest.raises(ValueError, match="at least 30 days"):
                    await service._calculate_gold_dxy_correlation(
                        gold_symbol="XAUUSD",
                        correlation_days=30,
                        dxy_current=100.0
                    )
    
    @pytest.mark.asyncio
    async def test_analyze_dxy_bond_alignment_with_correlation(
        self,
        service: MarketAlignmentService
    ) -> None:
        """
        Análisis completo con correlación Gold-DXY
        """
        # DXY y bonos
        dxy_candles = self._create_mock_candles("DXY", 30, 100.0, "down")
        bond_candles = self._create_mock_candles("US10Y", 30, 4.0, "down")
        
        # Gold
        gold_candles = self._create_mock_candles("XAUUSD", 30, 2000.0, "up")
        
        with patch.object(
            service,
            '_get_dxy_bond_provider',
            return_value=service.provider
        ):
            with patch.object(
                service.provider,
                'fetch_historical_candles',
                new_callable=AsyncMock
            ) as mock_fetch:
                def side_effect(symbol: str, *args, **kwargs) -> list[PriceCandle]:
                    if symbol == "DXY":
                        return dxy_candles
                    elif symbol == "US10Y":
                        return bond_candles
                    elif symbol == "XAUUSD":
                        return gold_candles
                    return []
                
                mock_fetch.side_effect = side_effect
                
                analysis = await service.analyze_dxy_bond_alignment(
                    bond_symbol="US10Y",
                    include_gold_correlation=True,
                    gold_symbol="XAUUSD",
                    correlation_days=30
                )
        
        assert analysis is not None
        assert analysis.dxy is not None
        assert analysis.bond is not None
        assert analysis.gold_dxy_correlation is not None
        assert analysis.gold_impact_projection is not None
        
        # Verificar correlación
        assert -1.0 <= analysis.gold_dxy_correlation.coefficient <= 1.0
        assert analysis.gold_dxy_correlation.strength is not None
        
        # Verificar proyección
        assert analysis.gold_impact_projection.dxy_change_percent == 1.0
        assert analysis.gold_impact_projection.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_dxy_bond_alignment_without_correlation(
        self,
        service: MarketAlignmentService
    ) -> None:
        """
        Análisis sin correlación Gold-DXY
        """
        dxy_candles = self._create_mock_candles("DXY", 30, 100.0, "down")
        bond_candles = self._create_mock_candles("US10Y", 30, 4.0, "down")
        
        with patch.object(
            service,
            '_get_dxy_bond_provider',
            return_value=service.provider
        ):
            with patch.object(
                service.provider,
                'fetch_historical_candles',
                new_callable=AsyncMock
            ) as mock_fetch:
                def side_effect(symbol: str, *args, **kwargs) -> list[PriceCandle]:
                    if symbol == "DXY":
                        return dxy_candles
                    elif symbol == "US10Y":
                        return bond_candles
                    return []
                
                mock_fetch.side_effect = side_effect
                
                analysis = await service.analyze_dxy_bond_alignment(
                    bond_symbol="US10Y",
                    include_gold_correlation=False
                )
        
        assert analysis is not None
        assert analysis.gold_dxy_correlation is None
        assert analysis.gold_impact_projection is None
    
    @pytest.mark.asyncio
    async def test_analyze_dxy_bond_alignment_correlation_error_handling(
        self,
        service: MarketAlignmentService
    ) -> None:
        """
        Manejo graceful de errores en correlación
        """
        dxy_candles = self._create_mock_candles("DXY", 30, 100.0, "down")
        bond_candles = self._create_mock_candles("US10Y", 30, 4.0, "down")
        
        with patch.object(
            service,
            '_get_dxy_bond_provider',
            return_value=service.provider
        ):
            with patch.object(
                service.provider,
                'fetch_historical_candles',
                new_callable=AsyncMock
            ) as mock_fetch:
                def side_effect(symbol: str, *args, **kwargs) -> list[PriceCandle]:
                    if symbol == "DXY":
                        return dxy_candles
                    elif symbol == "US10Y":
                        return bond_candles
                    elif symbol == "XAUUSD":
                        raise ValueError("Provider error")
                    return []
                
                mock_fetch.side_effect = side_effect
                
                # No debe fallar, solo loguear warning
                analysis = await service.analyze_dxy_bond_alignment(
                    bond_symbol="US10Y",
                    include_gold_correlation=True
                )
        
        assert analysis is not None
        assert analysis.gold_dxy_correlation is None
        assert analysis.gold_impact_projection is None

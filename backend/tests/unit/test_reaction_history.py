"""
Tests unitarios para histórico de reacciones ampliado en psychological levels
"""
import pytest
from datetime import datetime, timedelta
from app.models.psychological_levels import (
    LevelReaction,
    ReactionType,
    TradingSession,
    VolatilityLevel,
    PsychologicalLevel
)
from app.models.market_analysis import PriceCandle
from app.utils.reaction_history_builder import ReactionHistoryBuilder


class TestTradingSession:
    """Tests para la enum TradingSession"""
    
    def test_trading_session_values(self):
        """Verifica los valores de la enum TradingSession"""
        assert TradingSession.ASIA == "asia"
        assert TradingSession.LONDON == "londres"
        assert TradingSession.NEW_YORK == "nueva_york"
        assert TradingSession.UNKNOWN == "desconocida"


class TestVolatilityLevel:
    """Tests para la enum VolatilityLevel"""
    
    def test_volatility_level_values(self):
        """Verifica los valores de la enum VolatilityLevel"""
        assert VolatilityLevel.LOW == "baja"
        assert VolatilityLevel.NORMAL == "normal"
        assert VolatilityLevel.HIGH == "alta"
        assert VolatilityLevel.EXTREME == "extrema"


class TestLevelReaction:
    """Tests para el modelo LevelReaction"""
    
    def test_level_reaction_creation(self):
        """Verifica que se pueda crear un LevelReaction correctamente"""
        reaction = LevelReaction(
            date="2026-01-11T10:00:00",
            price=4500.0,
            type=ReactionType.BOUNCE,
            session=TradingSession.LONDON,
            magnitude_points=25.0,
            magnitude_percentage=0.55,
            volatility=VolatilityLevel.NORMAL,
            atr_value=15.5,
            was_confirmed=True,
            candles_in_direction=4,
            distance_from_level=2.5,
            explanation="Rebote en Londres, magnitud 25 pts"
        )
        
        assert reaction.price == 4500.0
        assert reaction.type == ReactionType.BOUNCE
        assert reaction.session == TradingSession.LONDON
        assert reaction.magnitude_points == 25.0
        assert reaction.was_confirmed is True
        assert reaction.candles_in_direction == 4
    
    def test_level_reaction_with_break(self):
        """Verifica creación de reacción de tipo ruptura"""
        reaction = LevelReaction(
            date="2026-01-11T15:00:00",
            price=4550.0,
            type=ReactionType.BREAK,
            session=TradingSession.NEW_YORK,
            magnitude_points=30.0,
            magnitude_percentage=0.66,
            volatility=VolatilityLevel.HIGH,
            atr_value=20.0,
            was_confirmed=True,
            candles_in_direction=5,
            distance_from_level=1.0,
            explanation="Ruptura en NY, magnitud 30 pts"
        )
        
        assert reaction.type == ReactionType.BREAK
        assert reaction.session == TradingSession.NEW_YORK
        assert reaction.volatility == VolatilityLevel.HIGH


class TestReactionHistoryBuilder:
    """Tests para ReactionHistoryBuilder"""
    
    def test_determine_trading_session_asia(self):
        """Verifica determinación de sesión Asia"""
        # 02:00 UTC = Asia
        timestamp = datetime(2026, 1, 11, 2, 0, 0)
        session = ReactionHistoryBuilder.determine_trading_session(timestamp)
        assert session == TradingSession.ASIA
        
        # 23:00 UTC = Asia
        timestamp = datetime(2026, 1, 11, 23, 0, 0)
        session = ReactionHistoryBuilder.determine_trading_session(timestamp)
        assert session == TradingSession.ASIA
    
    def test_determine_trading_session_london(self):
        """Verifica determinación de sesión Londres"""
        # 10:00 UTC = Londres
        timestamp = datetime(2026, 1, 11, 10, 0, 0)
        session = ReactionHistoryBuilder.determine_trading_session(timestamp)
        assert session == TradingSession.LONDON
    
    def test_determine_trading_session_newyork(self):
        """Verifica determinación de sesión Nueva York"""
        # 15:00 UTC = Nueva York
        timestamp = datetime(2026, 1, 11, 15, 0, 0)
        session = ReactionHistoryBuilder.determine_trading_session(timestamp)
        assert session == TradingSession.NEW_YORK
    
    def test_classify_volatility_low(self):
        """Verifica clasificación de volatilidad baja"""
        atr = 10.0
        price = 4500.0
        # ATR/Precio = 0.22% < 0.3% → LOW
        volatility = ReactionHistoryBuilder.classify_volatility(atr, price)
        assert volatility == VolatilityLevel.LOW
    
    def test_classify_volatility_normal(self):
        """Verifica clasificación de volatilidad normal"""
        atr = 20.0
        price = 4500.0
        # ATR/Precio = 0.44% (0.3-0.6%) → NORMAL
        volatility = ReactionHistoryBuilder.classify_volatility(atr, price)
        assert volatility == VolatilityLevel.NORMAL
    
    def test_classify_volatility_high(self):
        """Verifica clasificación de volatilidad alta"""
        atr = 35.0
        price = 4500.0
        # ATR/Precio = 0.78% (0.6-1.0%) → HIGH
        volatility = ReactionHistoryBuilder.classify_volatility(atr, price)
        assert volatility == VolatilityLevel.HIGH
    
    def test_classify_volatility_extreme(self):
        """Verifica clasificación de volatilidad extrema"""
        atr = 50.0
        price = 4500.0
        # ATR/Precio = 1.11% > 1.0% → EXTREME
        volatility = ReactionHistoryBuilder.classify_volatility(atr, price)
        assert volatility == VolatilityLevel.EXTREME
    
    def test_calculate_atr_simple(self):
        """Verifica cálculo básico de ATR"""
        candles = [
            PriceCandle(
                timestamp=datetime(2026, 1, 10, i, 0, 0),
                open=4500.0 + i,
                high=4520.0 + i,
                low=4490.0 + i,
                close=4510.0 + i,
                volume=1000
            )
            for i in range(20)
        ]
        
        atr = ReactionHistoryBuilder.calculate_atr(candles, period=14)
        
        # ATR debe ser > 0
        assert atr > 0
        # Para este caso específico, el rango es ~30 puntos
        assert 20 < atr < 40
    
    def test_detect_confirmation_uptrend(self):
        """Verifica detección de confirmación en tendencia alcista"""
        candles = [
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 10, 0, 0),
                open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=1000
            ),
            # 3 velas alcistas consecutivas
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 11, 0, 0),
                open=4505.0, high=4515.0, low=4500.0, close=4512.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 12, 0, 0),
                open=4512.0, high=4520.0, low=4510.0, close=4518.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 13, 0, 0),
                open=4518.0, high=4525.0, low=4515.0, close=4523.0, volume=1000
            ),
        ]
        
        confirmed, count = ReactionHistoryBuilder.detect_confirmation(candles, 0, 'up')
        
        assert confirmed is True
        assert count == 3
    
    def test_detect_confirmation_downtrend(self):
        """Verifica detección de confirmación en tendencia bajista"""
        candles = [
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 10, 0, 0),
                open=4500.0, high=4505.0, low=4490.0, close=4495.0, volume=1000
            ),
            # 3 velas bajistas consecutivas
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 11, 0, 0),
                open=4495.0, high=4500.0, low=4485.0, close=4488.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 12, 0, 0),
                open=4488.0, high=4492.0, low=4480.0, close=4482.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 13, 0, 0),
                open=4482.0, high=4485.0, low=4475.0, close=4477.0, volume=1000
            ),
        ]
        
        confirmed, count = ReactionHistoryBuilder.detect_confirmation(candles, 0, 'down')
        
        assert confirmed is True
        assert count == 3
    
    def test_detect_confirmation_not_confirmed(self):
        """Verifica cuando una reacción NO es confirmada"""
        candles = [
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 10, 0, 0),
                open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=1000
            ),
            # Solo 2 velas alcistas, luego bajista
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 11, 0, 0),
                open=4505.0, high=4515.0, low=4500.0, close=4512.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 12, 0, 0),
                open=4512.0, high=4520.0, low=4510.0, close=4518.0, volume=1000
            ),
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 13, 0, 0),
                open=4518.0, high=4520.0, low=4510.0, close=4512.0, volume=1000  # Bajista
            ),
        ]
        
        confirmed, count = ReactionHistoryBuilder.detect_confirmation(candles, 0, 'up')
        
        assert confirmed is False
        assert count == 2
    
    def test_build_reaction_bounce(self):
        """Verifica construcción completa de reacción tipo rebote"""
        candles = [
            # Velas previas para ATR
            *[PriceCandle(
                timestamp=datetime(2026, 1, 10, i, 0, 0),
                open=4500.0, high=4520.0, low=4490.0, close=4510.0, volume=1000
            ) for i in range(15)],
            # Rebote en nivel 4500
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 15, 0, 0),
                open=4505.0, high=4510.0, low=4498.0, close=4508.0, volume=1000
            ),
            # Velas confirmación
            *[PriceCandle(
                timestamp=datetime(2026, 1, 10, 16 + i, 0, 0),
                open=4508.0 + i*2, high=4515.0 + i*2, low=4505.0 + i*2, close=4512.0 + i*2, volume=1000
            ) for i in range(3)]
        ]
        
        reaction = ReactionHistoryBuilder.build_reaction(
            level=4500.0,
            candles=candles,
            reaction_index=15,
            reaction_type=ReactionType.BOUNCE
        )
        
        assert reaction is not None
        assert reaction.type == ReactionType.BOUNCE
        assert reaction.price == 4508.0
        assert reaction.session in [TradingSession.ASIA, TradingSession.LONDON, TradingSession.NEW_YORK]
        assert reaction.magnitude_points > 0
        assert reaction.atr_value is not None
        assert reaction.was_confirmed in [True, False]
    
    def test_build_reaction_break(self):
        """Verifica construcción completa de reacción tipo ruptura"""
        candles = [
            # Velas previas
            *[PriceCandle(
                timestamp=datetime(2026, 1, 10, i, 0, 0),
                open=4500.0, high=4520.0, low=4490.0, close=4510.0, volume=1000
            ) for i in range(15)],
            # Ruptura del nivel 4500
            PriceCandle(
                timestamp=datetime(2026, 1, 10, 15, 0, 0),
                open=4505.0, high=4530.0, low=4500.0, close=4525.0, volume=1000
            ),
            # Velas confirmación
            *[PriceCandle(
                timestamp=datetime(2026, 1, 10, 16 + i, 0, 0),
                open=4525.0 + i*3, high=4535.0 + i*3, low=4520.0 + i*3, close=4530.0 + i*3, volume=1000
            ) for i in range(3)]
        ]
        
        reaction = ReactionHistoryBuilder.build_reaction(
            level=4500.0,
            candles=candles,
            reaction_index=15,
            reaction_type=ReactionType.BREAK
        )
        
        assert reaction is not None
        assert reaction.type == ReactionType.BREAK
        assert reaction.magnitude_points > 0


class TestPsychologicalLevelWithReactionHistory:
    """Tests para PsychologicalLevel con histórico de reacciones"""
    
    def test_psychological_level_with_reaction_history(self):
        """Verifica que se pueda crear un nivel con histórico de reacciones"""
        from app.models.psychological_levels import LevelType
        
        reactions = [
            LevelReaction(
                date="2026-01-10T10:00:00",
                price=4500.0,
                type=ReactionType.BOUNCE,
                session=TradingSession.LONDON,
                magnitude_points=25.0,
                magnitude_percentage=0.55,
                volatility=VolatilityLevel.NORMAL,
                atr_value=15.5,
                was_confirmed=True,
                candles_in_direction=4,
                distance_from_level=2.5,
                explanation="Rebote 1"
            ),
            LevelReaction(
                date="2026-01-09T15:00:00",
                price=4502.0,
                type=ReactionType.BOUNCE,
                session=TradingSession.NEW_YORK,
                magnitude_points=30.0,
                magnitude_percentage=0.66,
                volatility=VolatilityLevel.HIGH,
                atr_value=20.0,
                was_confirmed=True,
                candles_in_direction=5,
                distance_from_level=1.0,
                explanation="Rebote 2"
            )
        ]
        
        level = PsychologicalLevel(
            level=4500.0,
            distance_from_current=-25.0,
            distance_percent=-0.55,
            strength=0.8,
            reaction_count=2,
            last_reaction_date="2026-01-10T10:00:00",
            last_reaction_type=ReactionType.BOUNCE,
            type=LevelType.SUPPORT,
            bounce_count=2,
            break_count=0,
            is_round_hundred=True,
            is_round_fifty=False,
            reaction_history=reactions
        )
        
        assert level.reaction_history is not None
        assert len(level.reaction_history) == 2
        assert level.reaction_history[0].type == ReactionType.BOUNCE
        assert level.reaction_history[0].session == TradingSession.LONDON
        assert level.reaction_history[1].session == TradingSession.NEW_YORK
    
    def test_psychological_level_without_reaction_history(self):
        """Verifica que reaction_history sea opcional (lista vacía por defecto)"""
        from app.models.psychological_levels import LevelType
        
        level = PsychologicalLevel(
            level=4500.0,
            distance_from_current=-25.0,
            distance_percent=-0.55,
            strength=0.0,
            reaction_count=0,
            type=LevelType.SUPPORT,
            bounce_count=0,
            break_count=0,
            is_round_hundred=True,
            is_round_fifty=False
            # Sin reaction_history
        )
        
        assert level.reaction_history == []
    
    def test_reaction_history_filtering_by_session(self):
        """Verifica que se puedan filtrar reacciones por sesión"""
        from app.models.psychological_levels import LevelType
        
        reactions = [
            LevelReaction(
                date="2026-01-10T02:00:00",
                price=4500.0,
                type=ReactionType.BOUNCE,
                session=TradingSession.ASIA,
                magnitude_points=15.0,
                magnitude_percentage=0.33,
                volatility=VolatilityLevel.LOW,
                was_confirmed=True,
                candles_in_direction=3,
                distance_from_level=2.0,
                explanation="Rebote Asia"
            ),
            LevelReaction(
                date="2026-01-10T10:00:00",
                price=4500.0,
                type=ReactionType.BOUNCE,
                session=TradingSession.LONDON,
                magnitude_points=25.0,
                magnitude_percentage=0.55,
                volatility=VolatilityLevel.NORMAL,
                was_confirmed=True,
                candles_in_direction=4,
                distance_from_level=2.5,
                explanation="Rebote Londres"
            ),
            LevelReaction(
                date="2026-01-10T15:00:00",
                price=4500.0,
                type=ReactionType.BOUNCE,
                session=TradingSession.NEW_YORK,
                magnitude_points=30.0,
                magnitude_percentage=0.66,
                volatility=VolatilityLevel.HIGH,
                was_confirmed=True,
                candles_in_direction=5,
                distance_from_level=1.0,
                explanation="Rebote NY"
            )
        ]
        
        level = PsychologicalLevel(
            level=4500.0,
            distance_from_current=-25.0,
            distance_percent=-0.55,
            strength=0.9,
            reaction_count=3,
            last_reaction_date="2026-01-10T15:00:00",
            last_reaction_type=ReactionType.BOUNCE,
            type=LevelType.SUPPORT,
            bounce_count=3,
            break_count=0,
            is_round_hundred=True,
            is_round_fifty=False,
            reaction_history=reactions
        )
        
        # Filtrar por sesión de Londres
        london_reactions = [r for r in level.reaction_history if r.session == TradingSession.LONDON]
        assert len(london_reactions) == 1
        assert london_reactions[0].magnitude_points == 25.0
        
        # Filtrar por sesión de NY
        ny_reactions = [r for r in level.reaction_history if r.session == TradingSession.NEW_YORK]
        assert len(ny_reactions) == 1
        assert ny_reactions[0].magnitude_points == 30.0

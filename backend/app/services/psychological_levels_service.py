"""
Servicio para analizar niveles psicológicos de precio
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.db.models import PsychologicalLevelHistoryModel
from app.models.market_analysis import PriceCandle
from app.models.psychological_levels import (
    LevelType,
    PsychologicalLevel,
    PsychologicalLevelsResponse,
    ReactionType,
)
from app.providers.market_data.base_market_provider import MarketDataProvider
from app.providers.market_data.twelve_data_provider import TwelveDataProvider
from app.providers.market_data.mock_market_provider import MockMarketProvider

logger = logging.getLogger(__name__)


class PsychologicalLevelsService:
    """Servicio para analizar niveles psicológicos de precio"""

    def __init__(self, settings: Settings, db: Optional[Session] = None):
        """
        Inicializa el servicio de niveles psicológicos
        @param settings - Configuración de la aplicación
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
        self.db = db

    def _create_provider(self, settings: Settings) -> MarketDataProvider:
        """Crea el proveedor de datos de mercado"""
        provider_name = settings.market_data_provider.lower()

        if provider_name == "twelvedata":
            if not settings.market_data_api_key:
                raise ValueError("Twelve Data API key required")
            return TwelveDataProvider(api_key=settings.market_data_api_key)
        elif provider_name == "mock":
            return MockMarketProvider()
        else:
            raise ValueError(f"Provider '{provider_name}' not supported for psychological levels")

    async def get_psychological_levels(
        self,
        instrument: str = "XAUUSD",
        lookback_days: int = 30,
        max_distance_points: float = 100.0,
    ) -> PsychologicalLevelsResponse:
        """
        Obtiene análisis de niveles psicológicos cercanos al precio actual
        @param instrument - Instrumento a analizar
        @param lookback_days - Días hacia atrás para analizar histórico
        @param max_distance_points - Distancia máxima en puntos para considerar niveles
        @returns Análisis completo de niveles psicológicos
        """
        logger.info(f"Analyzing psychological levels for {instrument}")

        # 1. Obtener precio actual
        current_price = await self._get_current_price(instrument)
        logger.info(f"Current price for {instrument}: {current_price}")

        # 2. Generar niveles redondos cercanos
        round_levels = self._generate_round_levels(current_price, max_distance_points)
        logger.info(f"Generated {len(round_levels)} round levels")

        # 3. Obtener datos históricos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        historical_candles = await self.provider.fetch_historical_candles(
            instrument, start_date, end_date, "1h"
        )
        logger.info(f"Fetched {len(historical_candles)} historical candles")

        # 4. Analizar cada nivel
        analyzed_levels: list[PsychologicalLevel] = []
        for level_price in round_levels:
            level_analysis = self._analyze_level(
                level_price, current_price, historical_candles
            )
            analyzed_levels.append(level_analysis)

        # 5. Identificar niveles más fuertes y cercanos
        supports = [l for l in analyzed_levels if l.type in [LevelType.SUPPORT, LevelType.BOTH]]
        resistances = [l for l in analyzed_levels if l.type in [LevelType.RESISTANCE, LevelType.BOTH]]

        strongest_support = max(supports, key=lambda x: x.strength) if supports else None
        strongest_resistance = max(resistances, key=lambda x: x.strength) if resistances else None

        nearest_support = min(
            [l for l in supports if l.level < current_price],
            key=lambda x: abs(x.distance_from_current),
            default=None
        )
        nearest_resistance = min(
            [l for l in resistances if l.level > current_price],
            key=lambda x: abs(x.distance_from_current),
            default=None
        )

        # 6. Generar resumen
        summary = self._generate_summary(
            current_price, nearest_support, nearest_resistance, strongest_support, strongest_resistance
        )

        return PsychologicalLevelsResponse(
            instrument=instrument,
            current_price=current_price,
            analysis_datetime=datetime.now().isoformat(),
            levels=analyzed_levels,
            strongest_support=strongest_support,
            strongest_resistance=strongest_resistance,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            summary=summary,
            lookback_days=lookback_days,
            max_distance_points=max_distance_points,
        )

    async def _get_current_price(self, instrument: str) -> float:
        """Obtiene el precio actual del instrumento"""
        # Obtener última vela de 1h
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=2)
        candles = await self.provider.fetch_historical_candles(
            instrument, start_date, end_date, "1h"
        )
        if not candles:
            raise ValueError(f"No data available for {instrument}")
        return candles[-1].close

    def _generate_round_levels(
        self, current_price: float, max_distance: float
    ) -> list[float]:
        """
        Genera niveles redondos cercanos al precio actual
        @param current_price - Precio actual
        @param max_distance - Distancia máxima en puntos
        @returns Lista de niveles redondos
        """
        levels = []

        # Niveles de 100 (ej: 4500, 4600)
        base_hundred = (int(current_price) // 100) * 100
        for offset in range(-500, 600, 100):
            level = base_hundred + offset
            if abs(level - current_price) <= max_distance:
                levels.append(float(level))

        # Niveles de 50 (ej: 4550, 4650)
        base_fifty = (int(current_price) // 50) * 50
        for offset in range(-500, 600, 50):
            level = base_fifty + offset
            if abs(level - current_price) <= max_distance and level not in levels:
                levels.append(float(level))

        return sorted(levels)

    def _analyze_level(
        self, level: float, current_price: float, candles: list[PriceCandle]
    ) -> PsychologicalLevel:
        """
        Analiza un nivel psicológico específico
        @param level - Precio del nivel
        @param current_price - Precio actual
        @param candles - Velas históricas
        @returns Análisis del nivel
        """
        # Tolerancia para considerar que el precio tocó el nivel (0.5 puntos)
        tolerance = 0.5

        bounce_count = 0
        break_count = 0
        last_reaction_date = None
        last_reaction_type = None

        # Analizar cada vela
        for i, candle in enumerate(candles):
            # Verificar si la vela tocó el nivel
            touched_level = (candle.low - tolerance <= level <= candle.high + tolerance)

            if touched_level:
                # Determinar tipo de reacción
                if candle.close > level and candle.low <= level + tolerance:
                    # Rebote alcista desde el nivel (soporte)
                    bounce_count += 1
                    last_reaction_type = ReactionType.BOUNCE
                    last_reaction_date = candle.timestamp.isoformat()
                elif candle.close < level and candle.high >= level - tolerance:
                    # Rebote bajista desde el nivel (resistencia)
                    bounce_count += 1
                    last_reaction_type = ReactionType.BOUNCE
                    last_reaction_date = candle.timestamp.isoformat()
                else:
                    # Posible ruptura
                    if i < len(candles) - 1:
                        next_candle = candles[i + 1]
                        # Confirmar ruptura si la siguiente vela cierra del otro lado
                        if (candle.close < level < next_candle.close) or (
                            candle.close > level > next_candle.close
                        ):
                            break_count += 1
                            last_reaction_type = ReactionType.BREAK
                            last_reaction_date = candle.timestamp.isoformat()

        reaction_count = bounce_count + break_count

        # Calcular fuerza del nivel (más rebotes = más fuerte)
        strength = min(bounce_count / 5.0, 1.0) if reaction_count > 0 else 0.0

        # Determinar tipo de nivel
        if level < current_price:
            level_type = LevelType.SUPPORT
        elif level > current_price:
            level_type = LevelType.RESISTANCE
        else:
            level_type = LevelType.BOTH

        # Calcular distancia
        distance_from_current = level - current_price
        distance_percent = (distance_from_current / current_price) * 100

        # Determinar si es nivel de 100 o 50
        is_round_hundred = (level % 100 == 0)
        is_round_fifty = (level % 50 == 0) and not is_round_hundred

        return PsychologicalLevel(
            level=level,
            distance_from_current=round(distance_from_current, 2),
            distance_percent=round(distance_percent, 4),
            strength=round(strength, 2),
            reaction_count=reaction_count,
            last_reaction_date=last_reaction_date,
            last_reaction_type=last_reaction_type,
            type=level_type,
            bounce_count=bounce_count,
            break_count=break_count,
            is_round_hundred=is_round_hundred,
            is_round_fifty=is_round_fifty,
        )

    def _generate_summary(
        self,
        current_price: float,
        nearest_support: Optional[PsychologicalLevel],
        nearest_resistance: Optional[PsychologicalLevel],
        strongest_support: Optional[PsychologicalLevel],
        strongest_resistance: Optional[PsychologicalLevel],
    ) -> str:
        """Genera resumen textual del análisis"""
        parts = [f"Precio actual: {current_price:.2f}."]

        if nearest_support:
            parts.append(
                f"Soporte más cercano: {nearest_support.level:.2f} "
                f"({nearest_support.distance_from_current:+.2f} puntos, "
                f"fuerza {nearest_support.strength:.2f})."
            )

        if nearest_resistance:
            parts.append(
                f"Resistencia más cercana: {nearest_resistance.level:.2f} "
                f"({nearest_resistance.distance_from_current:+.2f} puntos, "
                f"fuerza {nearest_resistance.strength:.2f})."
            )

        if strongest_support and strongest_support != nearest_support:
            parts.append(
                f"Soporte más fuerte: {strongest_support.level:.2f} "
                f"(fuerza {strongest_support.strength:.2f}, "
                f"{strongest_support.bounce_count} rebotes)."
            )

        if strongest_resistance and strongest_resistance != nearest_resistance:
            parts.append(
                f"Resistencia más fuerte: {strongest_resistance.level:.2f} "
                f"(fuerza {strongest_resistance.strength:.2f}, "
                f"{strongest_resistance.bounce_count} rebotes)."
            )

        return " ".join(parts)

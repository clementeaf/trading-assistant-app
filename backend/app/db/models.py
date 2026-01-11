"""
Modelos de base de datos SQLAlchemy
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class EconomicEventModel(Base):
    """Modelo de evento económico en base de datos"""
    __tablename__ = "economic_events"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    importance = Column(String(20), nullable=False, index=True)
    currency = Column(String(10), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    country = Column(String(10), nullable=True)
    actual = Column(Float, nullable=True)
    forecast = Column(Float, nullable=True)
    previous = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MarketDataModel(Base):
    """Modelo de datos de mercado (velas OHLCV)"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    interval = Column(String(10), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {"comment": "Datos históricos de mercado (velas OHLCV)"},
    )


class DailyAnalysisModel(Base):
    """Modelo de análisis diario guardado"""
    __tablename__ = "daily_analyses"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String(20), nullable=False, index=True)
    analysis_date = Column(DateTime, nullable=False, index=True)
    previous_day_close = Column(Float, nullable=False)
    current_day_close = Column(Float, nullable=False)
    daily_change_percent = Column(Float, nullable=False)
    daily_direction = Column(String(20), nullable=False)
    previous_day_high = Column(Float, nullable=False)
    previous_day_low = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    analysis_data = Column(Text, nullable=True)  # JSON serializado de sesiones
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {"comment": "Análisis diarios de mercado guardados"},
    )


class TradingModeRecommendationModel(Base):
    """Modelo de recomendación de modo de trading guardada"""
    __tablename__ = "trading_mode_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String(20), nullable=False, index=True)
    bond_symbol = Column(String(10), nullable=False)
    recommendation_date = Column(DateTime, nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    detailed_explanation = Column(Text, nullable=True)
    reasons_data = Column(Text, nullable=True)  # JSON serializado de razones
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {"comment": "Recomendaciones de modo de trading históricas"},
    )


class MarketAlignmentModel(Base):
    """Modelo de alineación de mercado guardada"""
    __tablename__ = "market_alignments"

    id = Column(Integer, primary_key=True, index=True)
    alignment_date = Column(DateTime, nullable=False, index=True)
    dxy_price = Column(Float, nullable=False)
    dxy_previous_price = Column(Float, nullable=False)
    dxy_change_percent = Column(Float, nullable=False)
    bond_symbol = Column(String(10), nullable=False)
    bond_price = Column(Float, nullable=False)
    bond_previous_price = Column(Float, nullable=False)
    bond_change_percent = Column(Float, nullable=False)
    alignment_status = Column(String(20), nullable=False)
    market_bias = Column(String(20), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {"comment": "Alineaciones DXY-Bonos históricas"},
    )


class PsychologicalLevelHistoryModel(Base):
    """Modelo de histórico de reacciones en niveles psicológicos"""
    __tablename__ = "psychological_levels_history"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String(20), nullable=False, index=True)
    level = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # 1h, 4h, 1d, etc.
    
    # Tipo de reacción
    reaction_type = Column(String(20), nullable=False)  # bounce, break, ignore
    
    # Datos de la vela que reaccionó
    candle_open = Column(Float, nullable=False)
    candle_high = Column(Float, nullable=False)
    candle_low = Column(Float, nullable=False)
    candle_close = Column(Float, nullable=False)
    
    # Patrón de vela detectado (opcional)
    candle_pattern = Column(String(50), nullable=True)  # pin_bar, engulfing, doji, etc.
    
    # Fuerza de la reacción
    reaction_strength = Column(Float, nullable=True)  # 0-1, basado en tamaño de mecha, cuerpo, etc.
    
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        {"comment": "Histórico de reacciones del precio en niveles psicológicos"},
    )


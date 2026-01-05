"""
Repositorio para datos de mercado
"""
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.db.models import MarketDataModel
from app.models.market_analysis import PriceCandle

logger = logging.getLogger(__name__)


class MarketDataRepository:
    """Repositorio para gestionar datos de mercado en base de datos"""

    def __init__(self, db: Optional[Session]):
        """
        Inicializa el repositorio
        @param db - Sesión de base de datos (puede ser None)
        """
        self.db = db

    def save_candles(
        self,
        instrument: str,
        candles: List[PriceCandle],
        interval: str = "1h"
    ) -> List[MarketDataModel]:
        """
        Guarda velas de mercado en la base de datos
        @param instrument - Símbolo del instrumento
        @param candles - Lista de velas a guardar
        @param interval - Intervalo de las velas
        @returns Lista de modelos guardados
        """
        if not self.db:
            return []
        
        saved_models: List[MarketDataModel] = []

        for candle in candles:
            existing = self.db.query(MarketDataModel).filter(
                and_(
                    MarketDataModel.instrument == instrument.upper(),
                    MarketDataModel.timestamp == candle.timestamp,
                    MarketDataModel.interval == interval,
                )
            ).first()

            if existing:
                existing.open_price = candle.open
                existing.high_price = candle.high
                existing.low_price = candle.low
                existing.close_price = candle.close
                existing.volume = candle.volume
                saved_models.append(existing)
            else:
                new_candle = MarketDataModel(
                    instrument=instrument.upper(),
                    timestamp=candle.timestamp,
                    interval=interval,
                    open_price=candle.open,
                    high_price=candle.high,
                    low_price=candle.low,
                    close_price=candle.close,
                    volume=candle.volume,
                )
                self.db.add(new_candle)
                saved_models.append(new_candle)

        try:
            self.db.commit()
            logger.info(f"Saved {len(saved_models)} candles for {instrument} to database")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving candles: {str(e)}")
            raise

        return saved_models

    def get_candles(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> List[MarketDataModel]:
        """
        Obtiene velas de mercado por rango de fechas
        @param instrument - Símbolo del instrumento
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas
        @returns Lista de velas
        """
        if not self.db:
            return []
        
        return self.db.query(MarketDataModel).filter(
            and_(
                MarketDataModel.instrument == instrument.upper(),
                MarketDataModel.timestamp >= start_date,
                MarketDataModel.timestamp <= end_date,
                MarketDataModel.interval == interval,
            )
        ).order_by(MarketDataModel.timestamp).all()

    def get_latest_price(self, instrument: str) -> Optional[MarketDataModel]:
        """
        Obtiene el precio más reciente de un instrumento
        @param instrument - Símbolo del instrumento
        @returns Última vela o None
        """
        if not self.db:
            return None
        
        return self.db.query(MarketDataModel).filter(
            MarketDataModel.instrument == instrument.upper()
        ).order_by(desc(MarketDataModel.timestamp)).first()


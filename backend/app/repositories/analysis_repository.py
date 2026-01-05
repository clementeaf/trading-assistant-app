"""
Repositorio para análisis y recomendaciones
"""
import json
import logging
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.db.models import (
    DailyAnalysisModel,
    TradingModeRecommendationModel,
    MarketAlignmentModel,
)
from app.models.market_analysis import DailyMarketAnalysis
from app.models.trading_mode import TradingModeRecommendation
from app.models.market_alignment import MarketAlignmentAnalysis

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """Repositorio para gestionar análisis y recomendaciones en base de datos"""

    def __init__(self, db: Optional[Session]):
        """
        Inicializa el repositorio
        @param db - Sesión de base de datos (puede ser None)
        """
        self.db = db

    def save_daily_analysis(
        self,
        analysis: DailyMarketAnalysis,
        instrument: str
    ) -> Optional[DailyAnalysisModel]:
        """
        Guarda un análisis diario en la base de datos
        @param analysis - Análisis diario a guardar
        @param instrument - Símbolo del instrumento
        @returns Modelo guardado o None si no hay DB
        """
        if not self.db:
            return None
        
        analysis_date = datetime.fromisoformat(analysis.date).date()

        existing = self.db.query(DailyAnalysisModel).filter(
            and_(
                DailyAnalysisModel.instrument == instrument.upper(),
                func.date(DailyAnalysisModel.analysis_date) == analysis_date,
            )
        ).first()

        sessions_data = json.dumps([s.dict() for s in analysis.sessions])

        if existing:
            existing.previous_day_close = analysis.previous_day_close
            existing.current_day_close = analysis.current_day_close
            existing.daily_change_percent = analysis.daily_change_percent
            existing.daily_direction = analysis.daily_direction.value
            existing.previous_day_high = analysis.previous_day_high
            existing.previous_day_low = analysis.previous_day_low
            existing.summary = analysis.summary
            existing.analysis_data = sessions_data
            model = existing
        else:
            model = DailyAnalysisModel(
                instrument=instrument.upper(),
                analysis_date=datetime.combine(analysis_date, datetime.min.time()),
                previous_day_close=analysis.previous_day_close,
                current_day_close=analysis.current_day_close,
                daily_change_percent=analysis.daily_change_percent,
                daily_direction=analysis.daily_direction.value,
                previous_day_high=analysis.previous_day_high,
                previous_day_low=analysis.previous_day_low,
                summary=analysis.summary,
                analysis_data=sessions_data,
            )
            self.db.add(model)

        try:
            self.db.commit()
            logger.info(f"Saved daily analysis for {instrument} on {analysis_date}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving daily analysis: {str(e)}")
            raise

        return model

    def get_daily_analysis(
        self,
        instrument: str,
        target_date: date
    ) -> Optional[DailyAnalysisModel]:
        """
        Obtiene un análisis diario por fecha
        @param instrument - Símbolo del instrumento
        @param target_date - Fecha del análisis
        @returns Análisis o None
        """
        return self.db.query(DailyAnalysisModel).filter(
            and_(
                DailyAnalysisModel.instrument == instrument.upper(),
                func.date(DailyAnalysisModel.analysis_date) == target_date,
            )
        ).first()

    def save_trading_mode_recommendation(
        self,
        recommendation: TradingModeRecommendation,
        instrument: str,
        bond_symbol: str
    ) -> Optional[TradingModeRecommendationModel]:
        """
        Guarda una recomendación de modo de trading
        @param recommendation - Recomendación a guardar
        @param instrument - Símbolo del instrumento
        @param bond_symbol - Símbolo del bono
        @returns Modelo guardado o None si no hay DB
        """
        if not self.db:
            return None
        
        reasons_data = json.dumps([r.dict() for r in recommendation.reasons])
        recommendation_date = datetime.utcnow().date()

        existing = self.db.query(TradingModeRecommendationModel).filter(
            and_(
                TradingModeRecommendationModel.instrument == instrument.upper(),
                func.date(TradingModeRecommendationModel.recommendation_date) == recommendation_date,
            )
        ).first()

        if existing:
            existing.mode = recommendation.mode.value
            existing.confidence = recommendation.confidence
            existing.summary = recommendation.summary
            existing.detailed_explanation = recommendation.detailed_explanation
            existing.reasons_data = reasons_data
            model = existing
        else:
            model = TradingModeRecommendationModel(
                instrument=instrument.upper(),
                bond_symbol=bond_symbol,
                recommendation_date=datetime.combine(recommendation_date, datetime.min.time()),
                mode=recommendation.mode.value,
                confidence=recommendation.confidence,
                summary=recommendation.summary,
                detailed_explanation=recommendation.detailed_explanation,
                reasons_data=reasons_data,
            )
            self.db.add(model)

        try:
            self.db.commit()
            logger.info(f"Saved trading mode recommendation for {instrument} on {recommendation_date}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving recommendation: {str(e)}")
            raise

        return model

    def get_trading_mode_recommendations(
        self,
        instrument: str,
        days: int = 30
    ) -> List[TradingModeRecommendationModel]:
        """
        Obtiene recomendaciones históricas
        @param instrument - Símbolo del instrumento
        @param days - Número de días hacia atrás
        @returns Lista de recomendaciones
        """
        cutoff_date = datetime.utcnow().date() - date.resolution * days
        return self.db.query(TradingModeRecommendationModel).filter(
            and_(
                TradingModeRecommendationModel.instrument == instrument.upper(),
                TradingModeRecommendationModel.recommendation_date >= cutoff_date,
            )
        ).order_by(desc(TradingModeRecommendationModel.recommendation_date)).all()

    def save_market_alignment(
        self,
        alignment: MarketAlignmentAnalysis,
        bond_symbol: str
    ) -> Optional[MarketAlignmentModel]:
        """
        Guarda un análisis de alineación de mercado
        @param alignment - Análisis de alineación
        @param bond_symbol - Símbolo del bono
        @returns Modelo guardado o None si no hay DB
        """
        if not self.db:
            return None
        
        alignment_date = datetime.utcnow().date()

        existing = self.db.query(MarketAlignmentModel).filter(
            and_(
                MarketAlignmentModel.bond_symbol == bond_symbol,
                func.date(MarketAlignmentModel.alignment_date) == alignment_date,
            )
        ).first()

        if existing:
            existing.dxy_price = alignment.dxy.price
            existing.dxy_previous_price = alignment.dxy.previous_price
            existing.dxy_change_percent = alignment.dxy.change_percent
            existing.bond_price = alignment.bond.price
            existing.bond_previous_price = alignment.bond.previous_price
            existing.bond_change_percent = alignment.bond.change_percent
            existing.alignment_status = alignment.alignment.value
            existing.market_bias = alignment.market_bias.value
            existing.summary = alignment.summary
            model = existing
        else:
            model = MarketAlignmentModel(
                alignment_date=datetime.combine(alignment_date, datetime.min.time()),
                dxy_price=alignment.dxy.price,
                dxy_previous_price=alignment.dxy.previous_price,
                dxy_change_percent=alignment.dxy.change_percent,
                bond_symbol=bond_symbol,
                bond_price=alignment.bond.price,
                bond_previous_price=alignment.bond.previous_price,
                bond_change_percent=alignment.bond.change_percent,
                alignment_status=alignment.alignment.value,
                market_bias=alignment.market_bias.value,
                summary=alignment.summary,
            )
            self.db.add(model)

        try:
            self.db.commit()
            logger.info(f"Saved market alignment for {bond_symbol} on {alignment_date}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving alignment: {str(e)}")
            raise

        return model


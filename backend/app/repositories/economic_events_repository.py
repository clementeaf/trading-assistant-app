"""
Repositorio para eventos económicos
"""
import logging
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.models import EconomicEventModel
from app.models.economic_calendar import EconomicEvent, ImpactLevel

logger = logging.getLogger(__name__)


class EconomicEventsRepository:
    """Repositorio para gestionar eventos económicos en base de datos"""

    def __init__(self, db: Optional[Session]):
        """
        Inicializa el repositorio
        @param db - Sesión de base de datos (puede ser None)
        """
        self.db = db

    def save_events(self, events: List[EconomicEvent]) -> List[EconomicEventModel]:
        """
        Guarda eventos económicos en la base de datos
        @param events - Lista de eventos a guardar
        @returns Lista de modelos guardados
        """
        if not self.db:
            return []
        
        saved_models: List[EconomicEventModel] = []

        for event in events:
            existing = self.db.query(EconomicEventModel).filter(
                and_(
                    EconomicEventModel.event_date == event.date,
                    EconomicEventModel.description == event.description,
                    EconomicEventModel.currency == event.currency,
                )
            ).first()

            if existing:
                existing.importance = event.importance.value
                existing.country = event.country
                existing.actual = event.actual
                existing.forecast = event.forecast
                existing.previous = event.previous
                existing.updated_at = datetime.utcnow()
                saved_models.append(existing)
            else:
                new_event = EconomicEventModel(
                    event_date=event.date,
                    importance=event.importance.value,
                    currency=event.currency,
                    description=event.description,
                    country=event.country,
                    actual=event.actual,
                    forecast=event.forecast,
                    previous=event.previous,
                )
                self.db.add(new_event)
                saved_models.append(new_event)

        try:
            self.db.commit()
            logger.info(f"Saved {len(saved_models)} economic events to database")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving events: {str(e)}")
            raise

        return saved_models

    def get_events_by_date(
        self,
        target_date: date,
        currency: Optional[str] = None,
        importance: Optional[ImpactLevel] = None
    ) -> List[EconomicEventModel]:
        """
        Obtiene eventos económicos por fecha
        @param target_date - Fecha objetivo
        @param currency - Moneda para filtrar (opcional)
        @param importance - Nivel de importancia para filtrar (opcional)
        @returns Lista de eventos
        """
        if not self.db:
            return []
        
        query = self.db.query(EconomicEventModel).filter(
            func.date(EconomicEventModel.event_date) == target_date
        )

        if currency:
            query = query.filter(EconomicEventModel.currency == currency.upper())

        if importance:
            query = query.filter(EconomicEventModel.importance == importance.value)

        return query.order_by(EconomicEventModel.event_date).all()

    def get_recent_events(self, days: int = 7) -> List[EconomicEventModel]:
        """
        Obtiene eventos económicos recientes
        @param days - Número de días hacia atrás
        @returns Lista de eventos
        """
        if not self.db:
            return []
        
        cutoff_date = datetime.utcnow().date() - date.resolution * days
        return self.db.query(EconomicEventModel).filter(
            EconomicEventModel.event_date >= cutoff_date
        ).order_by(EconomicEventModel.event_date.desc()).all()


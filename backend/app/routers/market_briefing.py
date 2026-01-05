"""
Router para el servicio de briefing de mercado
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config.settings import Settings, get_settings
from app.models.economic_calendar import HighImpactNewsResponse
from app.services.economic_calendar_service import EconomicCalendarService
from app.utils.validators import CurrencyValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market-briefing", tags=["Market Briefing"])


def get_economic_calendar_service(
    settings: Settings = Depends(get_settings)
) -> EconomicCalendarService:
    """
    Dependency para obtener el servicio de calendario económico
    @param settings - Configuración de la aplicación
    @returns Instancia del servicio de calendario económico
    """
    return EconomicCalendarService(settings)


@router.get(
    "/high-impact-news",
    response_model=HighImpactNewsResponse,
    summary="Obtiene noticias de alto impacto para XAUUSD del día",
    description="Verifica si hay noticias económicas de alto impacto hoy relevantes para XAUUSD (NFP, CPI, Fed, PMI...)"
)
async def get_high_impact_news_today(
    currency: Optional[str] = Query(
        None,
        description="Código de moneda ISO 4217 (ej: USD, EUR). Por defecto USD.",
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$"
    ),
    service: EconomicCalendarService = Depends(get_economic_calendar_service)
) -> HighImpactNewsResponse:
    """
    Endpoint para obtener noticias de alto impacto del día actual relevantes para XAUUSD
    @param currency - Moneda para filtrar (opcional, por defecto USD). Debe ser código ISO 4217 de 3 letras.
    @param service - Servicio de calendario económico
    @returns Respuesta con noticias de alto impacto relevantes para XAUUSD
    """
    try:
        validated_currency = None
        if currency:
            try:
                validated_currency = CurrencyValidator.validate_currency(currency)
            except ValueError as e:
                logger.warning(f"Invalid currency parameter: {currency} - {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
        
        logger.info(f"Fetching high impact news for XAUUSD with currency: {validated_currency or 'USD'}")
        result = await service.get_high_impact_news_today(currency=validated_currency)
        logger.info(f"Successfully retrieved {result.count} high impact events for XAUUSD")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching high impact news for XAUUSD: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener noticias de alto impacto para XAUUSD"
        )


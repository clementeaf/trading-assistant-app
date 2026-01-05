"""
Router para el servicio de briefing de mercado
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.config.settings import Settings, get_settings
from app.models.economic_calendar import HighImpactNewsResponse
from app.services.economic_calendar_service import EconomicCalendarService

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
    summary="Obtiene noticias de alto impacto del día",
    description="Verifica si hay noticias económicas de alto impacto hoy (NFP, CPI, Fed, PMI...)"
)
async def get_high_impact_news_today(
    currency: Optional[str] = None,
    service: EconomicCalendarService = Depends(get_economic_calendar_service)
) -> HighImpactNewsResponse:
    """
    Endpoint para obtener noticias de alto impacto del día actual
    @param currency - Moneda para filtrar (opcional, por defecto USD)
    @param service - Servicio de calendario económico
    @returns Respuesta con noticias de alto impacto
    """
    try:
        return await service.get_high_impact_news_today(currency=currency)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener noticias de alto impacto: {str(e)}"
        )


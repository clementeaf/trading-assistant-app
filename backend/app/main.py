"""
Aplicación FastAPI principal para Trading Assistant App
"""
from fastapi import FastAPI

from app.routers import market_briefing

app = FastAPI(
    title="Trading Assistant App",
    description="Aplicación de asistente para trading con briefing de mercado",
    version="1.0.0"
)

app.include_router(market_briefing.router)


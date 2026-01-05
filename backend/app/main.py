"""
Aplicación FastAPI principal para Trading Assistant App
"""
import os

from fastapi import FastAPI

from app.routers import market_briefing
from app.utils.logging_config import setup_logging

setup_logging(os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Trading Assistant App",
    description="Aplicación de asistente para trading con briefing de mercado",
    version="1.0.0"
)

app.include_router(market_briefing.router)


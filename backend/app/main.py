"""
Aplicación FastAPI principal para Trading Assistant App
"""
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import market_briefing
from app.utils.logging_config import setup_logging

setup_logging(os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Trading Assistant App",
    description="Aplicación de asistente para trading con briefing de mercado",
    version="1.0.0"
)

# Configurar CORS
allowed_origins: List[str] = [
    "http://localhost:30500",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:30500",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Agregar origen de producción si está definido
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_briefing.router)


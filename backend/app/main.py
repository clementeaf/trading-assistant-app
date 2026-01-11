"""
Aplicación FastAPI principal para Trading Assistant App
"""
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.models import Base
from app.db.session import engine
from app.routers import market_briefing
from app.utils.logging_config import setup_logging

# Configurar logging (estructurado en producción, simple en desarrollo)
is_production = os.getenv("STAGE", "dev") == "prod"
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    structured=is_production
)

# Crear tablas si no existen (solo en desarrollo y si hay DB configurada)
if engine and os.getenv("STAGE", "dev") == "dev":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables automatically: {e}")
        print("Run 'alembic upgrade head' to create tables")

app = FastAPI(
    title="Trading Assistant API",
    description="""
## Trading Assistant - API de Análisis de Mercado para XAU/USD

API completa para análisis probabilístico de mercado enfocada en Gold (XAU/USD).

### 🎯 Características Principales

* **Calendario Económico**: Noticias de alto impacto con análisis geopolítico
* **Análisis de Sesiones**: Volatilidad y breaks psicológicos por sesión (Asia, Londres, NY)
* **Correlaciones**: Gold-DXY con proyección de impacto y rango de magnitud
* **Niveles Psicológicos**: Detección de 100s y 50s con histórico de reacciones detallado
* **Modo de Trading**: Recomendación CALM/AGGRESSIVE/OBSERVE con niveles operativos
* **Recomendaciones**: Buy/Sell/Wait con Risk/Reward detallado y disclaimer
* **Análisis Técnico**: Multi-timeframe (Daily, H4, H1) con RSI, EMAs, y estructura

### 📊 Mejoras Fase 2.5 (Refinamiento Backend)

1. **Disclaimer Reforzado + R:R Detallado**: Cada recomendación incluye disclaimer prominente y desglose completo de riesgo/recompensa
2. **Niveles Operativos Dinámicos**: Soporte/resistencia filtrados según modo de trading actual
3. **Histórico de Reacciones**: Cada nivel psicológico incluye sesión, volatilidad, magnitud y confirmación
4. **Rango de Magnitud en Proyecciones**: Impacto Gold incluye rango min-max basado en correlación y volatilidad histórica

### ⚠️ Importante

Esta API proporciona **análisis probabilístico basado en datos históricos y patrones técnicos**.  
**NO es consejo financiero**. Úsala como herramienta de apoyo para tus propias decisiones.

### 🔗 Links Útiles

* [Documentación E2E](https://github.com/tu-repo/docs/TESTS_E2E.md)
* [Guía de Optimización](https://github.com/tu-repo/docs/PERFORMANCE_OPTIMIZATION.md)
* [Roadmap de Mejoras](https://github.com/tu-repo/MEJORAS_SISTEMA.md)

### 📞 Contacto

¿Preguntas o sugerencias? Abre un issue en el repositorio.
    """,
    version="2.5.0",
    contact={
        "name": "Trading Assistant Team",
        "url": "https://github.com/tu-repo",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Market Briefing",
            "description": "Endpoints para análisis de mercado y recomendaciones de trading",
        },
    ]
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


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint para monitoreo
    
    Returns:
        dict: Estado del sistema y versión
    """
    return {
        "status": "healthy",
        "version": "2.5.0",
        "service": "trading-assistant-api"
    }


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint con información básica
    
    Returns:
        dict: Información de bienvenida y links útiles
    """
    return {
        "message": "Trading Assistant API",
        "version": "2.5.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }



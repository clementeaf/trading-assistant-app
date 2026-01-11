"""
Modelos de datos para niveles psicológicos de precio
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LevelType(str, Enum):
    """Tipo de nivel psicológico"""
    SUPPORT = "soporte"
    RESISTANCE = "resistencia"
    BOTH = "ambos"


class ReactionType(str, Enum):
    """Tipo de reacción del precio en un nivel"""
    BOUNCE = "rebote"
    BREAK = "ruptura"
    IGNORE = "ignorado"


class PsychologicalLevel(BaseModel):
    """Nivel psicológico individual con su análisis"""
    level: float = Field(..., description="Precio del nivel redondo")
    distance_from_current: float = Field(..., description="Distancia desde precio actual en puntos")
    distance_percent: float = Field(..., description="Distancia desde precio actual en porcentaje")
    
    strength: float = Field(..., ge=0.0, le=1.0, description="Fuerza del nivel (0-1) basado en histórico")
    reaction_count: int = Field(..., ge=0, description="Cantidad de reacciones en últimos 30 días")
    
    last_reaction_date: Optional[str] = Field(None, description="Última fecha de reacción (ISO format)")
    last_reaction_type: Optional[ReactionType] = Field(None, description="Tipo de última reacción")
    
    type: LevelType = Field(..., description="Tipo de nivel (soporte/resistencia/ambos)")
    
    # Estadísticas históricas
    bounce_count: int = Field(default=0, description="Cantidad de rebotes históricos")
    break_count: int = Field(default=0, description="Cantidad de rupturas históricas")
    
    # Contexto adicional
    is_round_hundred: bool = Field(default=False, description="Si es un nivel de 100 (ej: 4500, 4600)")
    is_round_fifty: bool = Field(default=False, description="Si es un nivel de 50 (ej: 4550, 4650)")


class PsychologicalLevelsResponse(BaseModel):
    """Respuesta con análisis de niveles psicológicos"""
    instrument: str = Field(..., description="Instrumento analizado")
    current_price: float = Field(..., description="Precio actual del instrumento")
    analysis_datetime: str = Field(..., description="Fecha y hora del análisis (ISO format)")
    
    # Niveles cercanos
    levels: list[PsychologicalLevel] = Field(..., description="Lista de niveles psicológicos cercanos")
    
    # Niveles más fuertes
    strongest_support: Optional[PsychologicalLevel] = Field(None, description="Soporte más fuerte cercano")
    strongest_resistance: Optional[PsychologicalLevel] = Field(None, description="Resistencia más fuerte cercana")
    
    # Niveles inmediatos
    nearest_support: Optional[PsychologicalLevel] = Field(None, description="Soporte más cercano")
    nearest_resistance: Optional[PsychologicalLevel] = Field(None, description="Resistencia más cercana")
    
    # Resumen
    summary: str = Field(..., description="Resumen del análisis de niveles")
    
    # Configuración del análisis
    lookback_days: int = Field(default=30, description="Días analizados para histórico")
    max_distance_points: float = Field(default=100.0, description="Distancia máxima considerada en puntos")

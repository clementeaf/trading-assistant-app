"""
Calculador de impacto de eventos económicos en Gold
"""
import re
from typing import Optional
from app.models.gold_impact import (
    GoldImpactEstimate,
    ImpactDirection,
    ImpactMagnitude
)


class GoldImpactCalculator:
    """
    Calcula el impacto esperado de eventos económicos en Gold
    """
    
    # Tipos de eventos y sus probabilidades base
    EVENT_PROBABILITIES = {
        "NFP": 0.95,
        "CPI": 0.90,
        "FOMC": 0.95,
        "INTEREST_RATE": 0.95,
        "GDP": 0.75,
        "UNEMPLOYMENT": 0.85,
        "RETAIL_SALES": 0.60,
        "PMI": 0.70,
        "PCE": 0.85,
        "JOBLESS_CLAIMS": 0.65,
        "ISM": 0.70,
        "PPI": 0.75,
        "CONSUMER_CONFIDENCE": 0.55,
        "HOUSING": 0.50,
    }
    
    # Magnitudes por tipo de evento (min_points, max_points)
    EVENT_MAGNITUDES = {
        "NFP": (50, 150),
        "CPI": (40, 120),
        "FOMC": (100, 250),
        "INTEREST_RATE": (100, 250),
        "GDP": (30, 80),
        "UNEMPLOYMENT": (40, 100),
        "RETAIL_SALES": (20, 60),
        "PMI": (20, 70),
        "PCE": (40, 100),
        "JOBLESS_CLAIMS": (15, 50),
        "ISM": (20, 70),
        "PPI": (30, 80),
        "CONSUMER_CONFIDENCE": (10, 40),
        "HOUSING": (10, 40),
    }
    
    # Boost por importancia
    IMPORTANCE_BOOST = {
        "high": 0.1,
        "medium": 0.05,
        "low": 0.0,
    }
    
    @classmethod
    def calculate_impact(
        cls,
        event_name: str,
        event_description: Optional[str] = None,
        importance: str = "medium",
        current_gold_price: Optional[float] = None
    ) -> GoldImpactEstimate:
        """
        Calcula el impacto estimado de un evento en Gold
        @param event_name - Nombre del evento
        @param event_description - Descripción del evento (opcional)
        @param importance - Importancia del evento (high/medium/low)
        @param current_gold_price - Precio actual de Gold (opcional)
        @returns Estimación de impacto
        """
        # Detectar tipo de evento
        event_type = cls._detect_event_type(event_name, event_description)
        
        # Calcular probabilidad
        probability = cls._calculate_probability(event_type, importance)
        
        # Estimar dirección
        direction, direction_note = cls._estimate_direction(event_type, event_name)
        
        # Estimar magnitud
        magnitude, magnitude_range = cls._estimate_magnitude(
            event_type, current_gold_price
        )
        
        # Calcular confianza
        confidence = cls._calculate_confidence(event_type, probability)
        
        # Generar razonamiento
        reasoning = cls._generate_reasoning(
            event_type, probability, direction, magnitude_range
        )
        
        return GoldImpactEstimate(
            probability=probability,
            direction=direction,
            direction_note=direction_note,
            magnitude=magnitude,
            magnitude_range=magnitude_range,
            confidence=confidence,
            reasoning=reasoning,
            event_type=event_type
        )
    
    @classmethod
    def _detect_event_type(
        cls,
        event_name: str,
        event_description: Optional[str] = None
    ) -> str:
        """
        Detecta el tipo de evento basado en nombre y descripción
        @param event_name - Nombre del evento
        @param event_description - Descripción del evento
        @returns Tipo de evento detectado
        """
        text = (event_name + " " + (event_description or "")).lower()
        
        # NFP / Non-Farm Payrolls
        if re.search(r'\bnon.?farm|nfp|payroll', text):
            return "NFP"
        
        # CPI / Inflation
        if re.search(r'\bcpi\b|consumer price|inflation rate', text):
            return "CPI"
        
        # FOMC / Fed
        if re.search(r'\bfomc\b|federal open market|fed decision|fed meeting', text):
            return "FOMC"
        
        # Interest Rate
        if re.search(r'interest rate|rate decision|monetary policy', text):
            return "INTEREST_RATE"
        
        # GDP
        if re.search(r'\bgdp\b|gross domestic product', text):
            return "GDP"
        
        # Unemployment
        if re.search(r'unemployment|jobless rate', text):
            return "UNEMPLOYMENT"
        
        # Retail Sales
        if re.search(r'retail sales', text):
            return "RETAIL_SALES"
        
        # PMI
        if re.search(r'\bpmi\b|purchasing managers', text):
            return "PMI"
        
        # PCE
        if re.search(r'\bpce\b|personal consumption', text):
            return "PCE"
        
        # Jobless Claims
        if re.search(r'jobless claims|initial claims', text):
            return "JOBLESS_CLAIMS"
        
        # ISM
        if re.search(r'\bism\b|institute.*supply', text):
            return "ISM"
        
        # PPI
        if re.search(r'\bppi\b|producer price', text):
            return "PPI"
        
        # Consumer Confidence
        if re.search(r'consumer confidence|consumer sentiment', text):
            return "CONSUMER_CONFIDENCE"
        
        # Housing
        if re.search(r'housing|home sales|building permits', text):
            return "HOUSING"
        
        # Unknown
        return "UNKNOWN"
    
    @classmethod
    def _calculate_probability(cls, event_type: str, importance: str) -> float:
        """
        Calcula la probabilidad de impacto
        @param event_type - Tipo de evento
        @param importance - Importancia del evento
        @returns Probabilidad (0.0-1.0)
        """
        base_probability = cls.EVENT_PROBABILITIES.get(event_type, 0.5)
        boost = cls.IMPORTANCE_BOOST.get(importance.lower(), 0.0)
        probability = min(1.0, base_probability + boost)
        return round(probability, 2)
    
    @classmethod
    def _estimate_direction(
        cls,
        event_type: str,
        event_name: str
    ) -> tuple[ImpactDirection, Optional[str]]:
        """
        Estima la dirección del impacto en Gold
        @param event_type - Tipo de evento
        @param event_name - Nombre del evento
        @returns Tupla (dirección, nota condicional)
        """
        if event_type in ["NFP", "UNEMPLOYMENT"]:
            return (
                ImpactDirection.BEARISH,
                "si dato fuerte (economía robusta = menor demanda de refugio)"
            )
        
        if event_type in ["CPI", "PCE", "PPI"]:
            return (
                ImpactDirection.BULLISH,
                "si inflación alta (oro como cobertura inflacionaria)"
            )
        
        if event_type in ["FOMC", "INTEREST_RATE"]:
            return (
                ImpactDirection.BEARISH,
                "si tono hawkish/subida tasas (USD fuerte = oro débil)"
            )
        
        if event_type == "GDP":
            return (
                ImpactDirection.BEARISH,
                "si crecimiento fuerte (menor demanda de refugio)"
            )
        
        if event_type in ["RETAIL_SALES", "PMI", "ISM"]:
            return (
                ImpactDirection.NEUTRAL,
                "depende de desviación vs expectativas"
            )
        
        if event_type in ["CONSUMER_CONFIDENCE", "HOUSING"]:
            return (
                ImpactDirection.NEUTRAL,
                "impacto menor, depende de contexto macro"
            )
        
        return (ImpactDirection.NEUTRAL, "dirección depende del dato específico")
    
    @classmethod
    def _estimate_magnitude(
        cls,
        event_type: str,
        current_gold_price: Optional[float] = None
    ) -> tuple[ImpactMagnitude, str]:
        """
        Estima la magnitud del impacto
        @param event_type - Tipo de evento
        @param current_gold_price - Precio actual de Gold
        @returns Tupla (magnitud enum, rango string)
        """
        min_points, max_points = cls.EVENT_MAGNITUDES.get(event_type, (20, 80))
        magnitude_range = f"{min_points}-{max_points} puntos"
        
        # Clasificar magnitud
        avg_points = (min_points + max_points) / 2
        
        if avg_points >= 150:
            magnitude = ImpactMagnitude.VERY_HIGH
        elif avg_points >= 100:
            magnitude = ImpactMagnitude.HIGH
        elif avg_points >= 50:
            magnitude = ImpactMagnitude.MEDIUM
        elif avg_points >= 30:
            magnitude = ImpactMagnitude.LOW
        else:
            magnitude = ImpactMagnitude.VERY_LOW
        
        return magnitude, magnitude_range
    
    @classmethod
    def _calculate_confidence(cls, event_type: str, probability: float) -> float:
        """
        Calcula la confianza en la estimación
        @param event_type - Tipo de evento
        @param probability - Probabilidad calculada
        @returns Confianza (0.0-1.0)
        """
        if event_type == "UNKNOWN":
            return 0.3
        
        high_confidence_events = ["NFP", "CPI", "FOMC", "INTEREST_RATE"]
        if event_type in high_confidence_events:
            return round(min(0.9, probability), 2)
        
        medium_confidence_events = ["GDP", "UNEMPLOYMENT", "PCE", "PMI"]
        if event_type in medium_confidence_events:
            return round(min(0.75, probability * 0.9), 2)
        
        return round(min(0.6, probability * 0.8), 2)
    
    @classmethod
    def _generate_reasoning(
        cls,
        event_type: str,
        probability: float,
        direction: ImpactDirection,
        magnitude_range: str
    ) -> str:
        """
        Genera razonamiento textual de la estimación
        @param event_type - Tipo de evento
        @param probability - Probabilidad de impacto
        @param direction - Dirección del impacto
        @param magnitude_range - Rango de magnitud
        @returns Razonamiento legible
        """
        direction_text = {
            ImpactDirection.BULLISH: "alcista",
            ImpactDirection.BEARISH: "bajista",
            ImpactDirection.NEUTRAL: "neutral/mixto"
        }
        
        prob_text = "alta" if probability >= 0.8 else "media" if probability >= 0.6 else "moderada"
        
        event_names = {
            "NFP": "Non-Farm Payrolls",
            "CPI": "Índice de Precios al Consumidor",
            "FOMC": "Decisión de la Fed",
            "INTEREST_RATE": "Decisión de tasas de interés",
            "GDP": "PIB",
            "UNEMPLOYMENT": "Tasa de desempleo",
            "PCE": "Gastos de consumo personal",
        }
        
        event_display = event_names.get(event_type, event_type)
        
        return (
            f"{event_display} tiene probabilidad {prob_text} ({probability:.0%}) de impactar Gold. "
            f"Sesgo típico: {direction_text[direction]}. "
            f"Movimiento esperado: {magnitude_range}."
        )

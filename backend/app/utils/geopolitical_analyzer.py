"""
Analizador de riesgo geopolítico en eventos económicos
"""
import re
from datetime import datetime
from typing import Optional
from app.models.geopolitical_risk import GeopoliticalRisk, GeopoliticalRiskLevel
from app.models.economic_calendar import EconomicEvent


class GeopoliticalAnalyzer:
    """
    Analiza el riesgo geopolítico basado en eventos económicos y noticias
    """
    
    # Keywords de alto riesgo (peso: 0.3)
    HIGH_RISK_KEYWORDS = [
        r'\bwar\b', r'\bguerra\b',
        r'\bconflict\b', r'\bconflicto\b',
        r'\binvasion\b', r'\binvasión\b',
        r'\bmilitary action\b', r'\bacción militar\b',
        r'\bsanctions\b', r'\bsanciones\b',
        r'\bcrisis\b',
        r'\battack\b', r'\bataque\b',
        r'\bbombardment\b', r'\bbombardeo\b',
        r'\bstrike\b', r'\bataque aéreo\b',
    ]
    
    # Keywords de riesgo medio (peso: 0.15)
    MEDIUM_RISK_KEYWORDS = [
        r'\btensions\b', r'\btensiones\b',
        r'\bdispute\b', r'\bdisputa\b',
        r'\bthreat\b', r'\bamenaza\b',
        r'\bembargo\b',
        r'\bprotest\b', r'\bprotesta\b',
        r'\bunrest\b', r'\bdisturbios\b',
        r'\binstability\b', r'\binestabilidad\b',
        r'\bterrorism\b', r'\bterrorismo\b',
        r'\bcoup\b', r'\bgolpe de estado\b',
    ]
    
    # Regiones críticas (boost: 0.2)
    CRITICAL_REGIONS = [
        r'\bmiddle east\b', r'\boriente medio\b',
        r'\bukraine\b', r'\bucrania\b',
        r'\brussia\b', r'\brusia\b',
        r'\biran\b', r'\birán\b',
        r'\bisrael\b',
        r'\bpalestine\b', r'\bpalestina\b',
        r'\btaiwan\b',
        r'\bnorth korea\b', r'\bcorea del norte\b',
    ]
    
    # Thresholds para clasificación
    RISK_THRESHOLDS = {
        0.0: GeopoliticalRiskLevel.LOW,
        0.3: GeopoliticalRiskLevel.MEDIUM,
        0.6: GeopoliticalRiskLevel.HIGH,
        0.8: GeopoliticalRiskLevel.CRITICAL,
    }
    
    @classmethod
    def analyze_risk(
        cls,
        events: list[EconomicEvent],
        additional_text: Optional[str] = None
    ) -> GeopoliticalRisk:
        """
        Analiza el riesgo geopolítico basado en eventos económicos
        @param events - Lista de eventos económicos
        @param additional_text - Texto adicional para analizar (opcional)
        @returns Análisis de riesgo geopolítico
        """
        if not events and not additional_text:
            return cls._default_risk()
        
        # Extraer texto de eventos
        text_to_analyze = []
        for event in events:
            text_to_analyze.append(event.description)
            if event.country:
                text_to_analyze.append(event.country)
        
        if additional_text:
            text_to_analyze.append(additional_text)
        
        full_text = " ".join(text_to_analyze).lower()
        
        # Detectar keywords y regiones
        high_risk_matches = cls._detect_keywords(full_text, cls.HIGH_RISK_KEYWORDS)
        medium_risk_matches = cls._detect_keywords(full_text, cls.MEDIUM_RISK_KEYWORDS)
        critical_regions = cls._detect_keywords(full_text, cls.CRITICAL_REGIONS)
        
        # Calcular score base
        base_score = cls._calculate_base_score(
            high_risk_count=len(high_risk_matches),
            medium_risk_count=len(medium_risk_matches)
        )
        
        # Aplicar boost por regiones críticas
        final_score = cls._apply_region_boost(base_score, len(critical_regions))
        
        # Clasificar nivel de riesgo
        risk_level = cls._classify_risk_level(final_score)
        
        # Generar lista de factores
        factors = cls._generate_factors_list(
            high_risk_matches, medium_risk_matches, critical_regions
        )
        
        # Generar descripción
        description = cls._generate_description(risk_level, factors)
        
        return GeopoliticalRisk(
            score=final_score,
            level=risk_level,
            factors=factors,
            description=description,
            last_updated=datetime.now()
        )
    
    @classmethod
    def _default_risk(cls) -> GeopoliticalRisk:
        """
        Retorna riesgo default cuando no hay datos
        @returns Riesgo geopolítico bajo por defecto
        """
        return GeopoliticalRisk(
            score=0.0,
            level=GeopoliticalRiskLevel.LOW,
            factors=[],
            description="No se detectaron factores de riesgo geopolítico",
            last_updated=datetime.now()
        )
    
    @classmethod
    def _detect_keywords(cls, text: str, keywords: list[str]) -> list[str]:
        """
        Detecta keywords en texto
        @param text - Texto a analizar
        @param keywords - Lista de patrones regex
        @returns Lista de keywords encontrados
        """
        matches = []
        for pattern in keywords:
            if re.search(pattern, text, re.IGNORECASE):
                # Extraer palabra detectada
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    matches.append(match.group(0))
        return matches
    
    @classmethod
    def _calculate_base_score(
        cls,
        high_risk_count: int,
        medium_risk_count: int
    ) -> float:
        """
        Calcula score base basado en keywords
        @param high_risk_count - Cantidad de keywords de alto riesgo
        @param medium_risk_count - Cantidad de keywords de riesgo medio
        @returns Score base (0.0-1.0)
        """
        high_risk_score = min(high_risk_count * 0.3, 0.9)
        medium_risk_score = min(medium_risk_count * 0.15, 0.6)
        
        total_score = high_risk_score + medium_risk_score
        return min(total_score, 1.0)
    
    @classmethod
    def _apply_region_boost(cls, base_score: float, region_count: int) -> float:
        """
        Aplica boost por regiones críticas
        @param base_score - Score base
        @param region_count - Cantidad de regiones críticas detectadas
        @returns Score final con boost
        """
        boost = min(region_count * 0.2, 0.4)
        final_score = min(base_score + boost, 1.0)
        return round(final_score, 2)
    
    @classmethod
    def _classify_risk_level(cls, score: float) -> GeopoliticalRiskLevel:
        """
        Clasifica el nivel de riesgo basado en score
        @param score - Score de riesgo
        @returns Nivel de riesgo
        """
        for threshold in sorted(cls.RISK_THRESHOLDS.keys(), reverse=True):
            if score >= threshold:
                return cls.RISK_THRESHOLDS[threshold]
        return GeopoliticalRiskLevel.LOW
    
    @classmethod
    def _generate_factors_list(
        cls,
        high_risk: list[str],
        medium_risk: list[str],
        regions: list[str]
    ) -> list[str]:
        """
        Genera lista de factores detectados
        @param high_risk - Keywords de alto riesgo
        @param medium_risk - Keywords de riesgo medio
        @param regions - Regiones críticas
        @returns Lista de factores
        """
        factors = []
        
        if high_risk:
            factors.extend([f"Alto riesgo: {kw}" for kw in high_risk[:3]])
        
        if medium_risk:
            factors.extend([f"Riesgo medio: {kw}" for kw in medium_risk[:2]])
        
        if regions:
            factors.extend([f"Región crítica: {reg}" for reg in regions[:2]])
        
        return factors
    
    @classmethod
    def _generate_description(
        cls,
        level: GeopoliticalRiskLevel,
        factors: list[str]
    ) -> str:
        """
        Genera descripción textual del riesgo
        @param level - Nivel de riesgo
        @param factors - Factores detectados
        @returns Descripción legible
        """
        level_text = {
            GeopoliticalRiskLevel.LOW: "Riesgo geopolítico bajo",
            GeopoliticalRiskLevel.MEDIUM: "Riesgo geopolítico medio",
            GeopoliticalRiskLevel.HIGH: "Riesgo geopolítico alto",
            GeopoliticalRiskLevel.CRITICAL: "Riesgo geopolítico crítico",
        }
        
        base_desc = level_text[level]
        
        if not factors:
            return f"{base_desc}. No se detectaron factores significativos."
        
        return (
            f"{base_desc}. "
            f"Factores detectados: {', '.join(factors[:3])}."
        )

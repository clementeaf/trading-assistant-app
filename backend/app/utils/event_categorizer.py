"""
Utilidad para categorizar eventos económicos automáticamente
"""
import re
from app.models.economic_calendar import EventType


class EventCategorizer:
    """Categoriza eventos económicos basándose en descripción y metadata"""
    
    # Mapeo de keywords a EventType (orden importa!)
    KEYWORD_PATTERNS = {
        EventType.FOMC: [
            r"fomc",
            r"federal.*open.*market",
            r"fed.*rate.*decision",
            r"interest.*rate.*decision",
            r"monetary.*policy"
        ],
        EventType.NFP: [
            r"non[-\s]?farm",
            r"nonfarm",
            r"employment.*situation"
        ],
        EventType.CPI: [
            r"\bcpi\b",
            r"consumer.*price.*index",
            r"inflation.*rate",
            r"consumer.*inflation"
        ],
        EventType.UNEMPLOYMENT: [
            r"unemployment.*rate",
            r"jobless.*rate"
        ],
        EventType.PCE: [
            r"\bpce\b",
            r"personal.*consumption.*expenditure",
            r"core.*pce"
        ],
        EventType.GDP: [
            r"\bgdp\b",
            r"gross.*domestic.*product",
            r"economic.*growth"
        ],
        EventType.RETAIL_SALES: [
            r"retail.*sales",
            r"consumer.*spending"
        ],
        EventType.PPI: [
            r"\bppi\b",
            r"producer.*price.*index"
        ],
        # ISM debe ir antes que PMI genérico
        EventType.ISM_SERVICES: [
            r"ism.*non[-\s]?manufactur",
            r"ism.*services"
        ],
        EventType.ISM_MANUFACTURING: [
            r"ism.*manufactur(?!ing)",  # manufacturing pero no non-manufacturing
            r"ism.*manufacturing"
        ],
        EventType.PMI: [
            r"\bpmi\b",
            r"purchasing.*manager",
            r"markit.*pmi"
        ],
        EventType.JOLTS: [
            r"jolts",
            r"job.*openings"
        ],
        # ADP debe ir antes que payroll genérico
        EventType.ADP_EMPLOYMENT: [
            r"adp.*employment",
            r"adp.*payroll",
            r"\badp\b"
        ],
        EventType.JOBLESS_CLAIMS: [
            r"initial.*claims",
            r"jobless.*claims",
            r"unemployment.*claims"
        ],
        EventType.DURABLE_GOODS: [
            r"durable.*goods",
            r"factory.*orders"
        ],
        EventType.HOUSING_STARTS: [
            r"housing.*starts",
            r"building.*permits"
        ],
        EventType.CONSUMER_CONFIDENCE: [
            r"consumer.*confidence",
            r"confidence.*index"
        ],
        EventType.ECB: [
            r"\becb\b",
            r"european.*central.*bank"
        ],
        EventType.BOE: [
            r"\bboe\b",
            r"bank.*of.*england"
        ],
        EventType.BOJ: [
            r"\bboj\b",
            r"bank.*of.*japan"
        ],
        EventType.GEOPOLITICAL: [
            r"geopolit",
            r"war",
            r"conflict",
            r"election",
            r"referendum",
            r"summit",
            r"sanctions"
        ],
        EventType.TREASURY_AUCTION: [
            r"treasury.*auction",
            r"bond.*auction",
            r"note.*auction"
        ],
        EventType.FED_SPEECH: [
            r"fed.*speaks?",
            r"powell.*speaks?",
            r"yellen.*speaks?",
            r"jerome.*powell"
        ]
    }
    
    @classmethod
    def categorize(cls, description: str, country: str = None) -> EventType:
        """
        Categoriza un evento basándose en su descripción
        
        Args:
            description: Descripción del evento
            country: País del evento (opcional, para contexto)
        
        Returns:
            EventType: Categoría del evento
        """
        if not description:
            return EventType.OTHER
        
        # Normalizar descripción (lowercase, sin espacios extra)
        description_lower = description.lower().strip()
        
        # Buscar coincidencias con patrones
        for event_type, patterns in cls.KEYWORD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return event_type
        
        # No se encontró categoría específica
        return EventType.OTHER
    
    @classmethod
    def get_tier(cls, event_type: EventType) -> int:
        """
        Obtiene el tier (nivel de importancia) de un tipo de evento
        
        Args:
            event_type: Tipo de evento
        
        Returns:
            int: Tier (1=máximo impacto, 4=impacto medio, 5=otros)
        """
        tier_mapping = {
            # Tier 1: Máximo impacto
            EventType.FOMC: 1,
            EventType.NFP: 1,
            EventType.CPI: 1,
            
            # Tier 2: Alto impacto
            EventType.UNEMPLOYMENT: 2,
            EventType.PCE: 2,
            EventType.GDP: 2,
            EventType.RETAIL_SALES: 2,
            EventType.PPI: 2,
            
            # Tier 3: Impacto medio-alto
            EventType.PMI: 3,
            EventType.ISM_MANUFACTURING: 3,
            EventType.ISM_SERVICES: 3,
            EventType.JOLTS: 3,
            EventType.ADP_EMPLOYMENT: 3,
            
            # Tier 4: Impacto medio
            EventType.JOBLESS_CLAIMS: 4,
            EventType.DURABLE_GOODS: 4,
            EventType.HOUSING_STARTS: 4,
            EventType.CONSUMER_CONFIDENCE: 4,
            
            # Bancos centrales (Tier 1-2 dependiendo)
            EventType.ECB: 2,
            EventType.BOE: 2,
            EventType.BOJ: 3,
            
            # Otros
            EventType.GEOPOLITICAL: 1,  # Puede ser Tier 1 si es grave
            EventType.TREASURY_AUCTION: 3,
            EventType.FED_SPEECH: 2,
            EventType.OTHER: 5
        }
        
        return tier_mapping.get(event_type, 5)
    
    @classmethod
    def get_typical_time_et(cls, event_type: EventType) -> str:
        """
        Obtiene la hora típica de publicación en horario ET
        
        Args:
            event_type: Tipo de evento
        
        Returns:
            str: Hora típica en formato "HH:MM AM/PM ET"
        """
        time_mapping = {
            EventType.FOMC: "2:00 PM ET",
            EventType.NFP: "8:30 AM ET",
            EventType.CPI: "8:30 AM ET",
            EventType.UNEMPLOYMENT: "8:30 AM ET",
            EventType.PCE: "8:30 AM ET",
            EventType.GDP: "8:30 AM ET",
            EventType.RETAIL_SALES: "8:30 AM ET",
            EventType.PPI: "8:30 AM ET",
            EventType.ISM_MANUFACTURING: "10:00 AM ET",
            EventType.ISM_SERVICES: "10:00 AM ET",
            EventType.ADP_EMPLOYMENT: "8:15 AM ET",
            EventType.JOBLESS_CLAIMS: "8:30 AM ET",
            EventType.CONSUMER_CONFIDENCE: "10:00 AM ET",
        }
        
        return time_mapping.get(event_type, "Variable")

# Fase 2 - Plan de Implementación Detallado

**Duración estimada**: 3-4 semanas  
**Tareas**: 4 mejoras principales  
**Objetivo**: Agregar contexto geopolítico, zonas horarias, impacto estimado y correlaciones

---

## Mejora 1: Flag de Riesgo Geopolítico

### Objetivo
Agregar campo `geopolitical_risk` en endpoint `/api/market-briefing/high-impact-news` para indicar nivel de tensión geopolítica actual que afecta a XAUUSD.

### Análisis Técnico

**Archivos a modificar**:
1. `app/models/economic_calendar.py` - Agregar modelo `GeopoliticalRisk`
2. `app/services/economic_calendar_service.py` - Integrar detección de riesgo
3. `app/routers/market_briefing.py` - Actualizar respuesta

**Archivos a crear**:
1. `app/utils/geopolitical_analyzer.py` - Lógica de análisis
2. `tests/unit/test_geopolitical_analyzer.py` - Tests unitarios

### Pasos de Implementación

#### 1.1 Crear modelo de datos

```python
# backend/app/models/economic_calendar.py

class GeopoliticalRiskLevel(str, Enum):
    LOW = "bajo"
    MEDIUM = "medio"
    HIGH = "alto"
    CRITICAL = "crítico"

class GeopoliticalRisk(BaseModel):
    level: GeopoliticalRiskLevel
    score: float = Field(..., ge=0.0, le=1.0, description="Score 0-1")
    factors: list[str] = Field(default_factory=list, description="Factores detectados")
    description: str = Field(..., description="Descripción del contexto")
    last_updated: datetime = Field(..., description="Última actualización")
```

#### 1.2 Crear analizador geopolítico

```python
# backend/app/utils/geopolitical_analyzer.py

class GeopoliticalAnalyzer:
    """
    Analiza contexto geopolítico basado en keywords y fuentes
    """
    
    # Keywords de alto riesgo
    HIGH_RISK_KEYWORDS = [
        "guerra", "conflict", "sanctions", "invasion",
        "military", "nuclear", "coup", "crisis"
    ]
    
    # Keywords de riesgo medio
    MEDIUM_RISK_KEYWORDS = [
        "tensiones", "tensions", "dispute", "embargo",
        "protests", "election", "trade war"
    ]
    
    # Regiones críticas para gold
    CRITICAL_REGIONS = [
        "middle east", "oriente medio", "ukraine", "ucrania",
        "china", "taiwan", "iran", "venezuela"
    ]
    
    @classmethod
    def analyze_risk(
        cls,
        events: list[EconomicEvent],
        additional_sources: Optional[dict] = None
    ) -> GeopoliticalRisk:
        """
        Analiza nivel de riesgo geopolítico
        @param events - Eventos económicos del día
        @param additional_sources - Fuentes adicionales (RSS, APIs)
        @returns Análisis de riesgo geopolítico
        """
        pass  # Implementar lógica
```

#### 1.3 Integrar en servicio

```python
# backend/app/services/economic_calendar_service.py

async def get_high_impact_news_with_geopolitical(
    self,
    currency: str = "USD"
) -> HighImpactNewsResponse:
    # ... código existente ...
    
    # Agregar análisis geopolítico
    geopolitical_risk = GeopoliticalAnalyzer.analyze_risk(
        events=high_impact_events,
        additional_sources=None  # Futuro: RSS feeds
    )
    
    return HighImpactNewsResponse(
        has_high_impact_news=len(high_impact_events) > 0,
        count=len(high_impact_events),
        events=high_impact_events,
        summary=summary,
        instrument="XAUUSD",
        geopolitical_risk=geopolitical_risk  # Nuevo campo
    )
```

#### 1.4 Tests unitarios

```python
# tests/unit/test_geopolitical_analyzer.py

def test_high_risk_detection():
    """Test detección de alto riesgo con keywords"""
    events = [...]  # Eventos con "war", "conflict"
    risk = GeopoliticalAnalyzer.analyze_risk(events)
    assert risk.level == GeopoliticalRiskLevel.HIGH

def test_medium_risk_detection():
    """Test detección de riesgo medio"""
    pass

def test_low_risk_no_keywords():
    """Test riesgo bajo sin keywords"""
    pass

def test_critical_regions_boost():
    """Test boost de riesgo por regiones críticas"""
    pass
```

**Tests esperados**: 8-10 tests  
**Coverage esperado**: 95%+

### Resultado Esperado

**Antes**:
```json
{
  "has_high_impact_news": true,
  "events": [...]
}
```

**Después**:
```json
{
  "has_high_impact_news": true,
  "events": [...],
  "geopolitical_risk": {
    "level": "alto",
    "score": 0.78,
    "factors": ["Tensiones en Oriente Medio", "Sanciones a Irán"],
    "description": "Nivel alto de riesgo geopolítico favorece oro como refugio",
    "last_updated": "2026-01-11T10:00:00Z"
  }
}
```

---

## Mejora 2: Múltiples Zonas Horarias

### Objetivo
Agregar campo `timezones` en endpoint `/api/market-briefing/event-schedule` mostrando eventos en múltiples zonas horarias.

### Análisis Técnico

**Archivos a modificar**:
1. `app/models/economic_calendar.py` - Agregar campo `timezones` en `EventScheduleItem`
2. `app/utils/schedule_formatter.py` - Lógica de conversión de zonas
3. `app/services/economic_calendar_service.py` - Integrar conversión

**Archivos a crear**:
1. `app/utils/timezone_converter.py` - Conversión de zonas horarias
2. `tests/unit/test_timezone_converter.py` - Tests

### Pasos de Implementación

#### 2.1 Crear convertidor de zonas horarias

```python
# backend/app/utils/timezone_converter.py

from datetime import datetime
from zoneinfo import ZoneInfo

class TimezoneConverter:
    """Convierte horarios entre zonas horarias"""
    
    SUPPORTED_TIMEZONES = {
        "UTC": "UTC",
        "ET": "America/New_York",
        "PT": "America/Los_Angeles",
        "GMT": "Europe/London",
        "CET": "Europe/Paris",
        "JST": "Asia/Tokyo",
        "AEST": "Australia/Sydney"
    }
    
    @classmethod
    def convert_time(
        cls,
        time_str: str,
        from_tz: str = "UTC",
        to_tz: str = "America/New_York"
    ) -> str:
        """
        Convierte hora de una zona a otra
        @param time_str - Hora en formato "HH:MM"
        @param from_tz - Zona horaria origen
        @param to_tz - Zona horaria destino
        @returns Hora convertida
        """
        pass
    
    @classmethod
    def format_multi_timezone(
        cls,
        utc_time: str,
        timezones: list[str] = None
    ) -> dict:
        """
        Formatea hora en múltiples zonas
        @param utc_time - Hora UTC
        @param timezones - Zonas a incluir (default: UTC, ET)
        @returns Dict con horas por zona
        """
        if timezones is None:
            timezones = ["UTC", "ET"]
        
        result = {}
        for tz_code in timezones:
            tz_name = cls.SUPPORTED_TIMEZONES.get(tz_code)
            if tz_name:
                result[tz_code] = cls.convert_time(utc_time, "UTC", tz_name)
        
        return result
```

#### 2.2 Actualizar modelo

```python
# backend/app/models/economic_calendar.py

class EventScheduleItem(BaseModel):
    time: str
    description: str
    currency: str
    impact: str
    affects_usd: bool
    full_description: str
    
    # Nuevo campo
    timezones: dict[str, str] = Field(
        default_factory=dict,
        description="Hora en múltiples zonas: {'UTC': '10:30', 'ET': '05:30'}"
    )
```

#### 2.3 Tests

```python
def test_convert_utc_to_et():
    """Test conversión UTC a ET"""
    result = TimezoneConverter.convert_time("10:30", "UTC", "America/New_York")
    assert result == "05:30"  # ET está -5 horas

def test_format_multi_timezone():
    """Test formato múltiples zonas"""
    result = TimezoneConverter.format_multi_timezone(
        "10:30",
        timezones=["UTC", "ET", "PT"]
    )
    assert "UTC" in result
    assert "ET" in result
    assert "PT" in result
```

**Tests esperados**: 6-8 tests  
**Coverage esperado**: 95%+

### Resultado Esperado

**Después**:
```json
{
  "events": [{
    "time": "10:30",
    "description": "NFP",
    "timezones": {
      "UTC": "10:30",
      "ET": "05:30",
      "PT": "02:30"
    },
    "formatted_time": "10:30 UTC (05:30 ET, 02:30 PT)"
  }]
}
```

---

## Mejora 3: Impacto Estimado en Gold

### Objetivo
Agregar campo `gold_impact_probability` en eventos del calendario, estimando probabilidad de movimiento significativo en XAUUSD.

### Análisis Técnico

**Archivos a modificar**:
1. `app/models/economic_calendar.py` - Agregar `GoldImpactEstimate`
2. `app/services/economic_calendar_service.py` - Calcular impacto

**Archivos a crear**:
1. `app/utils/gold_impact_calculator.py` - Cálculo de impacto
2. `tests/unit/test_gold_impact_calculator.py` - Tests

### Pasos de Implementación

#### 3.1 Crear calculador de impacto

```python
# backend/app/utils/gold_impact_calculator.py

class GoldImpactCalculator:
    """
    Calcula probabilidad de impacto en XAUUSD por evento económico
    """
    
    # Probabilidades base por tipo de evento
    EVENT_BASE_PROBABILITIES = {
        "nfp": 0.95,
        "cpi": 0.90,
        "fomc": 0.95,
        "pmi": 0.70,
        "gdp": 0.75,
        "jobless": 0.65,
        "retail": 0.50
    }
    
    # Direcciones esperadas (alcista/bajista para gold)
    EVENT_DIRECTIONS = {
        "nfp": {"strong_data": "bajista", "weak_data": "alcista"},
        "cpi": {"high_inflation": "alcista", "low_inflation": "bajista"}
    }
    
    @classmethod
    def calculate_impact(
        cls,
        event: EconomicEvent,
        historical_correlation: Optional[float] = None
    ) -> dict:
        """
        Calcula probabilidad de impacto en gold
        @param event - Evento económico
        @param historical_correlation - Correlación histórica (opcional)
        @returns Estimación de impacto
        """
        # Detectar tipo de evento
        event_type = cls._detect_event_type(event.event.lower())
        
        # Probabilidad base
        base_prob = cls.EVENT_BASE_PROBABILITIES.get(event_type, 0.50)
        
        # Ajustar por importancia
        if event.importance == "Alto":
            base_prob += 0.1
        
        # Ajustar por correlación histórica si existe
        if historical_correlation:
            base_prob = (base_prob + historical_correlation) / 2
        
        # Dirección esperada
        direction = cls._estimate_direction(event_type, event)
        
        return {
            "probability": min(1.0, base_prob),
            "direction": direction,
            "magnitude_estimate": cls._estimate_magnitude(event_type),
            "confidence": 0.7  # Confidence del modelo
        }
```

#### 3.2 Tests

```python
def test_nfp_high_impact():
    """Test NFP tiene alta probabilidad"""
    event = EconomicEvent(event="Non-Farm Payrolls", importance="Alto")
    impact = GoldImpactCalculator.calculate_impact(event)
    assert impact["probability"] >= 0.90

def test_retail_medium_impact():
    """Test Retail Sales tiene impacto medio"""
    pass

def test_direction_estimation():
    """Test estimación de dirección"""
    pass
```

**Tests esperados**: 8-10 tests  
**Coverage esperado**: 90%+

### Resultado Esperado

```json
{
  "events": [{
    "event": "NFP",
    "importance": "Alto",
    "gold_impact": {
      "probability": 0.95,
      "direction": "alcista_si_debil",
      "magnitude_estimate": "50-100 puntos",
      "confidence": 0.75
    }
  }]
}
```

---

## Mejora 4: Correlación Numérica Gold vs DXY

### Objetivo
Agregar campo `gold_dxy_correlation` en endpoint `/api/market-briefing/dxy-bond-alignment` con correlación histórica calculada.

### Análisis Técnico

**Archivos a modificar**:
1. `app/models/market_alignment.py` - Agregar campo `correlation`
2. `app/services/market_alignment_service.py` - Calcular correlación

**Archivos a crear**:
1. `app/utils/correlation_calculator.py` - Cálculo de correlaciones
2. `tests/unit/test_correlation_calculator.py` - Tests

### Pasos de Implementación

#### 4.1 Crear calculador de correlación

```python
# backend/app/utils/correlation_calculator.py

import numpy as np
from scipy.stats import pearsonr

class CorrelationCalculator:
    """Calcula correlaciones entre instrumentos"""
    
    @classmethod
    def calculate_correlation(
        cls,
        prices_a: list[float],
        prices_b: list[float]
    ) -> dict:
        """
        Calcula correlación de Pearson entre dos series
        @param prices_a - Precios instrumento A
        @param prices_b - Precios instrumento B
        @returns Correlación y metadata
        """
        if len(prices_a) != len(prices_b):
            raise ValueError("Series must have same length")
        
        if len(prices_a) < 2:
            return {
                "correlation": 0.0,
                "p_value": 1.0,
                "strength": "insuficiente",
                "sample_size": len(prices_a)
            }
        
        # Calcular correlación
        corr, p_value = pearsonr(prices_a, prices_b)
        
        # Clasificar fuerza
        strength = cls._classify_strength(abs(corr))
        
        return {
            "correlation": round(corr, 3),
            "p_value": round(p_value, 4),
            "strength": strength,
            "sample_size": len(prices_a),
            "interpretation": cls._interpret_correlation(corr)
        }
    
    @classmethod
    def _classify_strength(cls, abs_corr: float) -> str:
        """Clasifica fuerza de correlación"""
        if abs_corr >= 0.8:
            return "muy_fuerte"
        elif abs_corr >= 0.6:
            return "fuerte"
        elif abs_corr >= 0.4:
            return "moderada"
        elif abs_corr >= 0.2:
            return "débil"
        else:
            return "muy_débil"
```

#### 4.2 Tests

```python
def test_perfect_positive_correlation():
    """Test correlación perfecta positiva"""
    prices_a = [1, 2, 3, 4, 5]
    prices_b = [2, 4, 6, 8, 10]
    result = CorrelationCalculator.calculate_correlation(prices_a, prices_b)
    assert result["correlation"] > 0.99

def test_perfect_negative_correlation():
    """Test correlación perfecta negativa (Gold vs DXY)"""
    prices_gold = [1800, 1850, 1900, 1950, 2000]
    prices_dxy = [105, 103, 101, 99, 97]
    result = CorrelationCalculator.calculate_correlation(prices_gold, prices_dxy)
    assert result["correlation"] < -0.95

def test_no_correlation():
    """Test sin correlación"""
    pass
```

**Tests esperados**: 6-8 tests  
**Coverage esperado**: 95%+

### Resultado Esperado

```json
{
  "dxy": {...},
  "bond": {...},
  "correlation": {
    "gold_vs_dxy": -0.82,
    "strength": "fuerte",
    "interpretation": "Correlación inversa fuerte (cuando DXY sube, Gold baja)",
    "sample_size": 30,
    "period_days": 30
  },
  "gold_projection": {
    "scenario": "DXY +0.5%, US10Y +2% → Gold proyección -0.8% a -1.2%",
    "confidence": 0.75
  }
}
```

---

## Checklist de Implementación Fase 2

### Mejora 1: Geopolítico
- [ ] Crear `GeopoliticalRisk` model
- [ ] Implementar `GeopoliticalAnalyzer`
- [ ] Integrar en `economic_calendar_service`
- [ ] Tests unitarios (8-10 tests)
- [ ] Documentar keywords y scoring

### Mejora 2: Zonas Horarias
- [ ] Crear `TimezoneConverter`
- [ ] Actualizar `EventScheduleItem` model
- [ ] Integrar en `schedule_formatter`
- [ ] Tests unitarios (6-8 tests)
- [ ] Validar DST (horario de verano)

### Mejora 3: Impacto Gold
- [ ] Crear `GoldImpactCalculator`
- [ ] Agregar `GoldImpactEstimate` model
- [ ] Integrar en eventos
- [ ] Tests unitarios (8-10 tests)
- [ ] Calibrar probabilidades con histórico

### Mejora 4: Correlación
- [ ] Crear `CorrelationCalculator`
- [ ] Integrar scipy.stats
- [ ] Actualizar `market_alignment_service`
- [ ] Tests unitarios (6-8 tests)
- [ ] Agregar proyección de impacto

---

## Dependencias Nuevas

```txt
# requirements.txt - Agregar:
scipy>=1.11.0  # Para correlaciones de Pearson
tzdata>=2024.1  # Para zonas horarias
```

---

## Estimación de Tiempo

| Mejora | Implementación | Tests | Documentación | Total |
|--------|---------------|-------|---------------|-------|
| 1. Geopolítico | 6h | 3h | 1h | 10h |
| 2. Zonas horarias | 4h | 2h | 1h | 7h |
| 3. Impacto Gold | 5h | 3h | 1h | 9h |
| 4. Correlación | 4h | 2h | 1h | 7h |
| **Total** | **19h** | **10h** | **4h** | **33h** |

**Semanas estimadas**: 3-4 semanas (8-10h/semana)

---

## Orden de Implementación Recomendado

1. **Semana 1**: Mejora 2 (Zonas horarias) - Más simple, sin dependencias externas
2. **Semana 2**: Mejora 4 (Correlación) - Útil para Mejora 3
3. **Semana 3**: Mejora 3 (Impacto Gold) - Usa correlaciones
4. **Semana 4**: Mejora 1 (Geopolítico) - Más compleja, requiere calibración

---

## Próximos Pasos Inmediatos

1. ✅ Revisar y aprobar plan de Fase 2
2. ⏳ Instalar dependencias nuevas (`scipy`, `tzdata`)
3. ⏳ Comenzar con Mejora 2 (más simple)
4. ⏳ Iterar con tests en cada mejora
5. ⏳ Documentar resultados al finalizar

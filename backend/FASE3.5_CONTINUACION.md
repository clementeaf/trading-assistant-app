# FASE 3.5 - CALENDARIO PREDICTIVO (EN PROGRESO)

**Fecha**: 11 Enero 2026  
**Estado**: 60% Completado  
**Próximo paso**: Completar get_upcoming_events() + endpoint + tests

---

## 🎯 Objetivo

Implementar sistema de calendario económico predictivo que:
- ✅ Categoriza eventos automáticamente (FOMC, NFP, CPI, etc.)
- ✅ Asigna tier de importancia (1-5)
- ✅ Provee countdown (días/horas hasta evento)
- ⏳ Endpoint `/calendar/upcoming` para próximos 7 días
- ⏳ Tests unitarios

---

## ✅ Ya Completado (60%)

### 1. EventType Enum ✅
- 25+ tipos de eventos categorizados
- Tier 1: FOMC, NFP, CPI (máximo impacto)
- Tier 2: PCE, GDP, PPI, Retail Sales
- Tier 3: PMI, ISM, JOLTS, ADP
- Tier 4: Jobless Claims, Durable Goods

### 2. EventCategorizer Utility ✅
**Archivo**: `app/utils/event_categorizer.py`

```python
# Métodos implementados:
- categorize(description, country) → EventType
- get_tier(event_type) → int (1-5)
- get_typical_time_et(event_type) → str

# Features:
- Regex patterns para cada evento
- Mapeo automático: "Non-Farm" → NFP
- Horarios típicos: NFP = "8:30 AM ET"
```

### 3. Modelos de Datos ✅
**Archivo**: `app/models/economic_calendar.py`

```python
class UpcomingEvent:
    event: EconomicEvent
    days_until: int
    hours_until: Optional[int]  # Si es <48h
    is_today: bool
    is_tomorrow: bool
    is_this_week: bool
    tier: int  # 1-5
    typical_time_et: str

class UpcomingEventsResponse:
    events: list[UpcomingEvent]
    total_events: int
    next_high_impact: Optional[UpcomingEvent]  # Próximo Tier 1-2
    days_range: int
    summary: str  # Resumen textual
```

---

## ⏳ Pendiente (40%)

### 4. Service Method ⏳
**Archivo**: `app/services/economic_calendar_service.py`

**Falta completar**:
```python
async def get_upcoming_events(
    self,
    days: int = 7,
    currency: str = "USD",
    min_impact: ImpactLevel = MEDIUM
) -> UpcomingEventsResponse:
    """
    Obtiene eventos futuros con countdown
    """
    # CÓDIGO PARCIALMENTE ESCRITO
    # Necesita agregar al final del archivo
```

**Lógica a implementar**:
1. Iterar próximos N días (skip weekends)
2. Fetch events por día
3. Categorizar automáticamente (EventCategorizer)
4. Filtrar por min_impact
5. Calcular countdown (days_until, hours_until)
6. Ordenar por fecha
7. Identificar next_high_impact (Tier 1-2)
8. Generar resumen

### 5. Endpoint ⏳
**Archivo**: `app/routers/market_briefing.py`

```python
@router.get(
    "/calendar/upcoming",
    response_model=UpcomingEventsResponse,
    summary="Próximos eventos económicos con countdown"
)
async def get_upcoming_calendar(
    days: int = Query(7, ge=1, le=30),
    min_impact: ImpactLevel = Query(ImpactLevel.MEDIUM),
    service: EconomicCalendarService = Depends(...)
) -> UpcomingEventsResponse:
    return await service.get_upcoming_events(days=days, min_impact=min_impact)
```

### 6. Tests ⏳
**Archivo**: `tests/unit/test_event_categorizer.py`

```python
def test_categorize_nfp():
    assert EventCategorizer.categorize("Non-Farm Payrolls") == EventType.NFP

def test_categorize_cpi():
    assert EventCategorizer.categorize("Consumer Price Index") == EventType.CPI

def test_get_tier():
    assert EventCategorizer.get_tier(EventType.FOMC) == 1
    assert EventCategorizer.get_tier(EventType.PMI) == 3

def test_typical_time():
    assert "8:30 AM" in EventCategorizer.get_typical_time_et(EventType.NFP)
```

**Archivo**: `tests/unit/test_upcoming_events.py`
- Test get_upcoming_events()
- Test countdown calculation
- Test tier filtering
- Test summary generation

---

## 📝 Código para Continuar

### Agregar al final de `economic_calendar_service.py`:

```python
async def get_upcoming_events(
    self,
    days: int = 7,
    currency: str = "USD",
    min_impact: ImpactLevel = ImpactLevel.MEDIUM
) -> UpcomingEventsResponse:
    from datetime import datetime, timedelta
    
    now = datetime.now()
    today = now.date()
    all_events: list[EconomicEvent] = []
    
    # Iterar próximos días
    for i in range(days + 1):
        target_date = today + timedelta(days=i)
        if not BusinessDays.is_business_day(target_date):
            continue
        
        try:
            events = await self.provider.fetch_events(target_date, currency)
            
            # Categorizar
            for event in events:
                event.event_type = EventCategorizer.categorize(
                    event.description, event.country
                )
            
            # Filtrar
            filtered = [e for e in events if self._meets_min_impact(e.importance, min_impact)]
            all_events.extend(filtered)
        except Exception as e:
            logger.warning(f"Error fetching {target_date}: {e}")
    
    # Crear UpcomingEvent
    upcoming = []
    for event in all_events:
        time_until = event.date - now
        days_until = time_until.days
        hours_until = int(time_until.total_seconds() / 3600) if days_until < 2 else None
        
        upcoming_event = UpcomingEvent(
            event=event,
            days_until=days_until,
            hours_until=hours_until,
            is_today=(event.date.date() == today),
            is_tomorrow=(event.date.date() == today + timedelta(days=1)),
            is_this_week=(days_until <= 7),
            tier=EventCategorizer.get_tier(event.event_type),
            typical_time_et=EventCategorizer.get_typical_time_et(event.event_type)
        )
        upcoming.append(upcoming_event)
    
    # Ordenar y filtrar
    upcoming.sort(key=lambda e: e.event.date)
    next_high = next((e for e in upcoming if e.tier <= 2), None)
    summary = self._generate_upcoming_summary(upcoming, next_high)
    
    return UpcomingEventsResponse(
        events=upcoming,
        total_events=len(upcoming),
        next_high_impact=next_high,
        days_range=days,
        summary=summary
    )

def _meets_min_impact(self, event_impact, min_impact):
    order = {ImpactLevel.LOW: 1, ImpactLevel.MEDIUM: 2, ImpactLevel.HIGH: 3}
    return order.get(event_impact, 0) >= order.get(min_impact, 0)

def _generate_upcoming_summary(self, events, next_high):
    if not events:
        return "No hay eventos significativos próximos."
    
    tier1 = sum(1 for e in events if e.tier == 1)
    tier2 = sum(1 for e in events if e.tier == 2)
    
    parts = []
    if tier1 > 0: parts.append(f"{tier1} máximo impacto")
    if tier2 > 0: parts.append(f"{tier2} alto impacto")
    
    summary = f"{len(events)} eventos: {' y '.join(parts)}." if parts else f"{len(events)} eventos."
    
    if next_high:
        if next_high.is_today:
            summary += f" Hoy: {next_high.event.description}."
        elif next_high.is_tomorrow:
            summary += f" Mañana: {next_high.event.description}."
        else:
            summary += f" En {next_high.days_until} días: {next_high.event.description}."
    
    return summary
```

---

## 🚀 Plan de Continuación

**Tiempo estimado**: 1-1.5 horas

1. **Completar service method** (30 min)
   - Copiar código de arriba
   - Probar con mock provider

2. **Crear endpoint** (15 min)
   - Agregar a `market_briefing.py`
   - Dependency injection

3. **Tests** (30 min)
   - `test_event_categorizer.py` (10 tests)
   - `test_upcoming_events.py` (5 tests)

4. **Documentación y commit** (15 min)
   - FASE3.5_COMPLETADA.md
   - Actualizar FASE3_PROGRESO.md

---

## 💡 Valor del Feature

Este calendario predictivo permite:

1. **Anticipación**: "NFP en 3 días a las 8:30 AM ET"
2. **Alertas proactivas**: Identificar eventos Tier 1 próximos
3. **Planificación**: Ver próxima semana completa
4. **Countdown**: "Faltan 2 horas para FOMC"
5. **Categorización**: Identificar tipo de evento automáticamente

**Impacto**: Alto valor con bajo esfuerzo (80/20 rule) ✅

---

## 📦 Commit Actual

**Commit**: `0830f52`  
**Branch**: `main`  
**Estado**: Work in progress (60%)

**Para continuar**: Ejecutar código de arriba + endpoint + tests

---

**Próxima sesión**: Completar Fase 3.5 al 100% 🚀

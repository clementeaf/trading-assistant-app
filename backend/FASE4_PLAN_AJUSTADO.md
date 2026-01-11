# FASE 4 - PLAN AJUSTADO (Por Usuario)

**Fecha**: 11 Enero 2026  
**Ajuste**: Usuario NO quiere M5/M15, solo temporalidades mayores  
**Nuevo enfoque**: Weekly, Daily, H4, H1

---

## 🎯 Cambio de Enfoque

### ❌ Plan Original (basado en Grok)
- M5, M15, H1, H4, Daily
- Enfoque en micro-temporalidades
- Reacciones en tiempo real

### ✅ Plan Ajustado (Usuario)
- **Weekly (Semanal)** - Tendencia de largo plazo
- **Daily (Diario)** - Contexto macro
- **H4** - Dirección intermedia
- **H1** - Confirmación (solo validar)

**Razón**: Trading de posición, no scalping. Más alineado con filosofía del sistema.

---

## 📊 Nueva Fase 4: Análisis Multi-TF + Probabilidades

### Tarea 1: Agregar Análisis Semanal (2-3h)
**Objetivo**: Incorporar temporalidad Weekly para contexto de largo plazo

**Componentes**:
1. Modificar `TechnicalAnalysisService`:
   - Agregar análisis Weekly (1 semana = 7 días)
   - Rango: Últimos 52 semanas (1 año de datos)
   - Integrar con análisis existente

2. Actualizar `_get_candles_with_cache()`:
   - Mapeo "1week" → "1w"
   - Threshold actualización: 1 semana

3. Actualizar endpoint:
   - Response incluye "weekly" field
   - Backward compatible

4. Tests:
   - Test análisis semanal
   - Test integración multi-TF

**Archivos**:
- `app/services/technical_analysis_service.py`
- `app/routers/market_briefing.py`
- `tests/unit/test_technical_analysis_service.py`

**Tiempo**: 2-3 horas

---

### Tarea 2: Probabilidades por Escenario (5-6h)
**Sin cambios** - Esta tarea sigue siendo relevante

**Escenarios** (adaptados a TFs mayores):
1. **Breakout Alcista Weekly/Daily** (70-85%)
   - Precio rompe resistencia en Weekly
   - Confirmación en Daily/H4
   - Factores: Tendencia semanal, fuerza, volumen

2. **Breakout Bajista Weekly/Daily** (70-85%)
   - Precio rompe soporte en Weekly
   - Confirmación en Daily/H4

3. **Retesteo Soporte Daily/H4** (55-70%)
   - Rebote en soporte Daily
   - Confirmación en H4/H1
   - Patrón de velas

4. **Retesteo Resistencia Daily/H4** (55-70%)
   - Rechazo en resistencia Daily
   - Confirmación en H4/H1

5. **Consolidación/Rango** (40-60%)
   - Lateral en Weekly/Daily
   - Sin dirección clara

**Fórmula ajustada**:
```python
probability = base_probability 
    + (weekly_trend_alignment * 0.20)   # Tendencia semanal (mayor peso)
    + (daily_confirmation * 0.15)       # Confirmación diaria
    + (h4_confirmation * 0.10)          # Confirmación H4
    + (level_strength * 0.10)           # Fortaleza nivel
    + (pattern_quality * 0.10)          # Patrón velas
    - (counter_trend_penalty * 0.20)    # Penalización contra-tendencia Weekly
```

**Tiempo**: 5-6 horas

---

### Tarea 3: Prompts LLM Mejorados (3-4h)
**Ajustado** - Enfoque en temporalidades mayores

**Estructura del prompt** (ejemplo):
```
Analiza XAU/USD con enfoque en posición (no scalping):

CONTEXTO DE LARGO PLAZO (WEEKLY):
- Precio actual: 4520.50
- Tendencia semanal: Alcista (precio > EMA200 weekly)
- RSI Weekly: 62 (zona alcista sostenible)
- Estructura: Higher highs desde inicio 2025

CONTEXTO MACRO (DAILY):
- Tendencia daily: Alcista (precio > EMA50)
- RSI Daily: 58 (neutral-alcista)
- Último cierre: 4515.20

DIRECCIÓN INTERMEDIA (H4):
- Tendencia H4: Consolidando
- RSI H4: 55
- Rango: 4480-4550

CONFIRMACIÓN (H1):
- Última reacción: Rebote en 4500 (soporte)
- Dirección: Alcista (short-term)

SOPORTES/RESISTENCIAS CLAVE:
- Resistencias: 4550 (Daily), 4600 (Weekly)
- Soportes: 4500 (Daily fuerte), 4450 (H4)

PROBABILIDADES CALCULADAS:
- Breakout alcista (>4550): 72%
- Retesteo soporte (4500): 65%
- Consolidación: 45%

INSTRUCCIONES:
1. Determina dirección más probable (enfoque Weekly/Daily)
2. Identifica escenario de mayor probabilidad
3. Sugiere zona de entrada (Daily/H4), SL (H4), TP (Weekly/Daily)
4. Justifica con convergencia Weekly → Daily → H4 → H1
5. Lenguaje claro, sin promesas

Responde en español, formato estructurado.
```

**Tiempo**: 3-4 horas

---

## 🎯 Ventajas del Nuevo Enfoque

### ✅ Ventajas
1. **Más simple**: 4 TFs en vez de 5
2. **Más alineado**: Trading de posición, no scalping
3. **Menos ruido**: Weekly filtra noise de corto plazo
4. **Mejor filosofía**: "Aumentar probabilidades" con visión macro
5. **Menos costos API**: Menos requests de datos

### ✅ Coherencia con Sistema
- ✅ Ya tenemos Daily, H4, H1
- ✅ Solo falta agregar Weekly
- ✅ Niveles psicológicos funcionan mejor en TFs mayores
- ✅ Stop-loss más amplios = menos whipsaws

---

## 📊 MultiTimeframeAnalyzer - Ajuste

El utility creado sigue siendo útil pero con ajustes:

### ✅ Mantener
- `detect_convergence()` - Funciona perfecto para Weekly/Daily/H4/H1
- `calculate_convergence_strength()` - Sin cambios

### ❌ Remover/Ajustar
- `detect_hot_zones()` - **No necesario** para TFs mayores
  - Hot zones son para M5/M15
  - En Weekly/Daily, usamos niveles psicológicos

### 🔄 Alternativa
- Usar `PsychologicalLevelsService` existente
- Fuerza de niveles basada en Weekly/Daily
- Retesteos en H4/H1

---

## 📋 Plan Revisado - Estimaciones

| Tarea | Descripción | Tiempo |
|-------|-------------|--------|
| **1** | Agregar Weekly analysis | 2-3h |
| **2** | Scenario Probabilities | 5-6h |
| **3** | LLM Prompts (Weekly focus) | 3-4h |
| **Total** | **Fase 4 Ajustada** | **10-13h** |

**Ahorro vs plan original**: 2-2h (menos complejidad M5/M15)

---

## 🚀 Próximos Pasos Inmediatos

### 1. Agregar Weekly Analysis (HOY)
- Modificar `TechnicalAnalysisService`
- Actualizar endpoint
- Tests básicos
- **Tiempo**: 2-3h

### 2. Ajustar MultiTimeframeAnalyzer (Opcional)
- Remover `detect_hot_zones()` si no se usa
- O dejarlo para futuro uso en M5/M15 si cambia de opinión
- **Decisión**: Dejar el código, solo no usarlo

### 3. Scenario Probabilities (MAÑANA)
- Crear modelos
- Calculator con fórmulas Weekly-first
- Integración
- **Tiempo**: 5-6h

---

## 🎯 Resultado Esperado

### Backend Post-Fase 4 Ajustada
- ✅ 4 temporalidades (Weekly, Daily, H4, H1)
- ✅ Convergencia Weekly → Daily → H4 → H1
- ✅ Probabilidades basadas en TFs mayores
- ✅ LLM con enfoque posición (no scalping)
- ✅ Sistema coherente con filosofía "aumentar probabilidades"

### Completitud vs Grok
- **Antes**: 54% (faltaban M5/M15, probabilidades, prompts)
- **Después**: 85%+ (Weekly + probabilidades + prompts mejorados)
- **Gap restante**: M5/M15 (que usuario NO quiere) ✅

---

## ✅ Conclusión

**El nuevo enfoque es MEJOR**:
1. ✅ Más alineado con trading de posición
2. ✅ Menos complejidad técnica
3. ✅ Mejor filosofía (probabilidades macro)
4. ✅ Más rápido de implementar (10-13h vs 12-15h)

**Decisión**: Proceder con Fase 4 Ajustada (Weekly, Daily, H4, H1)

---

**¿Proceder con Tarea 1: Agregar Weekly Analysis?** 🚀

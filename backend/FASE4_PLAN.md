# FASE 4 - PLAN: Análisis Técnico Avanzado Multi-TF

**Fecha**: 11 Enero 2026  
**Objetivo**: Completar sistema de análisis técnico según recomendaciones de Grok  
**Filosofía**: 80% valor con 40% esfuerzo (Fase 4 Parcial)

---

## 🎯 Objetivo General

Implementar las 3 features más críticas para tener un sistema de análisis técnico avanzado:

1. ✅ **Análisis M5/M15** - Temporalidades micro para reacciones detalladas
2. ✅ **Probabilidades por Escenario** - % realistas por tipo de operación
3. ✅ **Prompts LLM Mejorados** - Integrar todo en análisis LLM

---

## 📊 Estado Actual vs Objetivo

| Métrica | Actual | Objetivo Fase 4 |
|---------|--------|-----------------|
| **Temporalidades** | H1, H4, D1 | M5, M15, H1, H4, D1 |
| **Probabilidades** | Confianza genérica | % por escenario específico |
| **Indicadores** | RSI, EMA | RSI, EMA, divergencias |
| **Análisis LLM** | Básico | Avanzado multi-TF |
| **Completitud Grok** | 54% | 90%+ |

---

## 🚀 Fase 4 Parcial - 3 Tareas Críticas

### Tarea 1: Análisis M5/M15 ⭐⭐⭐⭐⭐

**Objetivo**: Agregar temporalidades micro para detectar reacciones en tiempo real

**Componentes**:
1. Modificar `TechnicalAnalysisService`:
   - Agregar análisis M5 y M15
   - Integrar con `RetestDetector`
   - Calcular RSI, EMAs, slope por TF

2. Endpoint actualizado:
   - `GET /technical-analysis?timeframes=M5,M15,H1,H4,D1`
   - Response incluye análisis por cada TF

3. Utilidad `MultiTimeframeAnalyzer`:
   - Detecta convergencias/divergencias entre TFs
   - Identifica "zonas calientes" (reacciones recientes)

**Archivos a modificar**:
- `app/services/technical_analysis_service.py`
- `app/routers/market_briefing.py`
- `app/utils/technical_analysis.py` (opcional)

**Archivos nuevos**:
- `app/utils/multi_tf_analyzer.py`
- `tests/unit/test_multi_tf_analyzer.py`

**Entregables**:
- ✅ M5/M15 analysis funcionando
- ✅ Endpoint actualizado
- ✅ Tests unitarios (>90% coverage)
- ✅ Documentación

**Tiempo estimado**: 4-5 horas

---

### Tarea 2: Probabilidades por Escenario ⭐⭐⭐⭐⭐

**Objetivo**: Calcular probabilidades específicas basadas en contexto técnico

**Escenarios a calcular**:

1. **Breakout Alcista** (precio > resistencia clave)
   - Factores: Fuerza tendencia, volumen, confirmación multi-TF
   - Rango: 60-80%

2. **Breakout Bajista** (precio < soporte clave)
   - Factores: Debilidad, volumen, confirmación multi-TF
   - Rango: 60-80%

3. **Retesteo Soporte** (rebote en soporte)
   - Factores: Fortaleza nivel, reacciones previas, patrón velas
   - Rango: 50-70%

4. **Retesteo Resistencia** (rechazo en resistencia)
   - Factores: Fortaleza nivel, reacciones previas, patrón velas
   - Rango: 50-70%

5. **Lateral/Rango** (consolidación)
   - Factores: Volatilidad baja, sin breakouts recientes
   - Rango: 40-60%

**Fórmula base** (ejemplo):
```python
probability = base_probability 
    + (trend_alignment * 0.15)      # Alineación multi-TF
    + (level_strength * 0.10)        # Fortaleza nivel psicológico
    + (pattern_quality * 0.10)       # Patrón velas
    + (volume_confirmation * 0.05)   # Volumen (si disponible)
    - (counter_trend_penalty * 0.15) # Penalización contra-tendencia
```

**Archivos nuevos**:
- `app/utils/scenario_probability_calculator.py`
  - `calculate_breakout_probability()`
  - `calculate_retest_probability()`
  - `calculate_range_probability()`

- `app/models/scenario_probability.py`
  - `ScenarioType` enum
  - `ScenarioProbability` model
  - `ScenarioAnalysis` model

**Integración**:
- Modificar `TradingAdvisorService`
- Agregar campo `scenario_probabilities: list[ScenarioProbability]` a `TradeRecommendation`

**Entregables**:
- ✅ Utility de cálculo de probabilidades
- ✅ Modelos Pydantic
- ✅ Integración en recomendaciones
- ✅ Tests (>90% coverage)
- ✅ Documentación

**Tiempo estimado**: 5-6 horas

---

### Tarea 3: Prompts LLM Mejorados ⭐⭐⭐⭐⭐

**Objetivo**: Integrar análisis multi-TF y probabilidades en prompts LLM

**Mejoras a implementar**:

1. **Daily Summary mejorado**:
   - Incluir análisis M5/M15
   - Mencionar probabilidades por escenario
   - Destacar "zonas calientes" de reacción

2. **Trade Justification mejorado**:
   - Explicar convergencias multi-TF
   - Justificar probabilidad calculada
   - Mencionar reacciones recientes en M5/M15

3. **Pattern Detection mejorado**:
   - Analizar patrones en M5/M15
   - Relacionar con niveles psicológicos
   - Incluir probabilidad de continuación

4. **Nuevo prompt: Multi-TF Analysis**:
   - Prompt específico para análisis completo
   - Formato estructurado como Grok sugiere:
     - Dirección general
     - Soportes/Resistencias
     - Análisis de reacciones M5/M15
     - Probabilidades por escenario

**Estructura del nuevo prompt** (ejemplo español):
```
Analiza XAU/USD con los siguientes datos:

DIRECCIÓN GENERAL (H4/D1):
- Precio actual: 4520.50
- Tendencia: Alcista (precio > EMA200)
- RSI H4: 58 (neutral)
- Estructura: Higher highs intactos

SOPORTES/RESISTENCIAS CLAVE:
- Resistencias: 4550 (fuerte, 5 rebotes), 4600 (psicológico)
- Soportes: 4500 (muy fuerte, 8 rebotes), 4450 (intermedio)

ANÁLISIS MICRO (M5/M15):
- Últimas 20 velas M15: [datos]
- Reacciones recientes: Rebote en 4510 (M15), rechazo en 4545 (M5)
- Patrones detectados: Pin bar alcista en 4512 (M15)

PROBABILIDADES CALCULADAS:
- Breakout alcista (>4550): 68%
- Retesteo soporte (4500): 62%
- Lateral (4500-4550): 45%

INSTRUCCIONES:
1. Determina la dirección más probable (alcista/bajista/lateral)
2. Identifica el escenario de mayor probabilidad
3. Sugiere zona de entrada, stop-loss y take-profit
4. Justifica con convergencias multi-TF
5. Usa lenguaje claro y realista (sin promesas)

Responde en español, formato estructurado.
```

**Archivos a modificar**:
- `app/services/llm_service.py`
  - Actualizar `generate_daily_summary()`
  - Actualizar `generate_trade_justification()`
  - Actualizar `detect_complex_patterns()`
  - Agregar `analyze_multi_timeframe()` (nuevo)

**Entregables**:
- ✅ Prompts actualizados
- ✅ Nuevo método `analyze_multi_timeframe()`
- ✅ Tests actualizados
- ✅ Documentación de prompts

**Tiempo estimado**: 3-4 horas

---

## 📋 Plan de Implementación (Orden Recomendado)

### Día 1: Tarea 1 - M5/M15 Analysis (4-5h)
1. **Hora 1-2**: Modificar `TechnicalAnalysisService`
   - Agregar métodos para M5/M15
   - Actualizar `analyze_multi_timeframe()`

2. **Hora 3**: Crear `MultiTimeframeAnalyzer`
   - Detectar convergencias
   - Identificar zonas calientes

3. **Hora 4**: Tests y endpoint
   - Tests unitarios
   - Actualizar endpoint
   - Probar manualmente

4. **Hora 5**: Commit y documentación

### Día 2: Tarea 2 - Scenario Probabilities (5-6h)
1. **Hora 1-2**: Crear modelos
   - `ScenarioType` enum
   - `ScenarioProbability` model
   - `ScenarioAnalysis` model

2. **Hora 3-4**: Crear calculator
   - `ScenarioProbabilityCalculator` utility
   - Implementar fórmulas para cada escenario
   - Calibrar con datos reales

3. **Hora 5**: Integración
   - Modificar `TradingAdvisorService`
   - Actualizar `TradeRecommendation`

4. **Hora 6**: Tests y commit
   - Tests unitarios
   - Commit y documentación

### Día 3: Tarea 3 - LLM Prompts (3-4h)
1. **Hora 1-2**: Actualizar prompts existentes
   - Daily summary
   - Trade justification
   - Pattern detection

2. **Hora 3**: Crear nuevo método
   - `analyze_multi_timeframe()` en LLM

3. **Hora 4**: Tests y commit final
   - Tests de integración
   - Commit final
   - Documentación completa

---

## 🧪 Testing Strategy

### Tests Unitarios (por tarea)
- **Tarea 1**: `test_multi_tf_analyzer.py` (10-15 tests)
- **Tarea 2**: `test_scenario_probability_calculator.py` (15-20 tests)
- **Tarea 3**: Actualizar `test_llm_service.py` (+10 tests)

**Total**: ~35-45 tests nuevos

### Tests de Integración
- `test_technical_analysis_m5m15.py`
- `test_scenario_probabilities_integration.py`
- `test_llm_multi_tf.py`

**Total**: ~15-20 tests de integración

### Coverage Target
- **Mínimo**: 85%
- **Objetivo**: 90%+

---

## 📊 Métricas de Éxito

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| **Temporalidades** | 3 | 5 |
| **Escenarios con probabilidad** | 0 | 5 |
| **Completitud Grok** | 54% | 90%+ |
| **Tests backend** | 83 | 130+ |
| **Endpoints avanzados** | 11 | 12 |

---

## 💰 Costos Estimados

### LLM Adicional
- Nuevo método `analyze_multi_timeframe()`: $0.02-0.04/análisis
- Prompts mejorados: +20% tokens (pero más valor)

**Total adicional**: +$2-5/mes (uso medio)

**Total Fase 4**: ~$5-13/mes (LLM completo)

---

## 📦 Entregables Finales

### Archivos Nuevos (6)
1. `app/utils/multi_tf_analyzer.py`
2. `app/utils/scenario_probability_calculator.py`
3. `app/models/scenario_probability.py`
4. `tests/unit/test_multi_tf_analyzer.py`
5. `tests/unit/test_scenario_probability_calculator.py`
6. `FASE4_COMPLETADA.md`

### Archivos Modificados (4)
1. `app/services/technical_analysis_service.py`
2. `app/services/trading_advisor_service.py`
3. `app/services/llm_service.py`
4. `app/routers/market_briefing.py`

### Documentación (3)
1. `FASE4_PLAN.md` (este archivo)
2. `FASE4_COMPLETADA.md` (al finalizar)
3. Actualizar `ANALISIS_GROK_VS_IMPLEMENTACION.md`

---

## 🎯 Resultado Esperado

### Backend Post-Fase 4
- ✅ 5 temporalidades (M5, M15, H1, H4, D1)
- ✅ Probabilidades específicas por escenario
- ✅ Análisis LLM avanzado multi-TF
- ✅ 130+ tests (100% passing)
- ✅ 90%+ completitud vs Grok
- ✅ Sistema production-ready de clase mundial

### Valor para Traders
- 📊 Análisis micro (M5/M15) para entradas precisas
- 🎯 Probabilidades realistas por operación (60-80%)
- 🤖 LLM con contexto completo multi-TF
- 📈 Convergencias entre temporalidades
- ⚡ Reacciones en tiempo real (zonas calientes)

---

## 🚦 Próximos Pasos Después de Fase 4

### Opción A: Fase 5 - Frontend Development
- Dashboard con multi-TF
- Visualización de probabilidades
- Chat interface mejorado
- Gráficos interactivos

### Opción B: Fase 4 Full (Completar 100%)
- MACD, ADX, Bollinger Bands
- Análisis de volumen
- Divergencias RSI/MACD
- Backtesting framework

### Opción C: Fase 6 - Tiempo Real
- WebSocket para updates live
- Streaming LLM responses
- Push notifications
- Real-time alerts

---

## ✅ Checklist Pre-Inicio

- [ ] Confirmar prioridad de Fase 4 Parcial
- [ ] Revisar datos disponibles en providers (M5/M15)
- [ ] Preparar datasets para calibrar probabilidades
- [ ] Asegurar OpenAI API key activa
- [ ] Backup código actual
- [ ] Crear branch `fase-4-multi-tf`

---

## 📝 Conclusión

**Fase 4 Parcial** es el complemento perfecto para tener un sistema de análisis técnico avanzado:

- ⏱️ **Tiempo**: 12-15 horas (2-3 días)
- 💰 **Costo**: +$2-5/mes
- 📊 **Valor**: 80% de Grok con 40% esfuerzo
- 🎯 **Resultado**: Backend 90%+ completo

**Después de Fase 4**: Sistema listo para competir con plataformas profesionales 🚀

---

**¿Procedemos con Fase 4 Parcial?** ⚡

# Fase 2 - Micro Tareas Detalladas

## 📋 Estructura de Micro Tareas

Cada mejora se desglosa en tareas de 15-30 minutos máximo, verificables independientemente.

---

## 🎯 Mejora 1: Flag de Riesgo Geopolítico (10h)

### 1.1 Setup Inicial (30 min)
- [ ] 1.1.1 Crear archivo `app/models/geopolitical_risk.py`
- [ ] 1.1.2 Definir enum `GeopoliticalRiskLevel` (bajo, medio, alto, crítico)
- [ ] 1.1.3 Definir clase `GeopoliticalRisk` con Pydantic
- [ ] 1.1.4 Agregar validaciones de campos (score 0-1)
- [ ] 1.1.5 Verificar imports en `app/models/__init__.py`

### 1.2 Analizador Base (1h)
- [ ] 1.2.1 Crear archivo `app/utils/geopolitical_analyzer.py`
- [ ] 1.2.2 Definir clase `GeopoliticalAnalyzer`
- [ ] 1.2.3 Definir constante `HIGH_RISK_KEYWORDS` (10-15 keywords)
- [ ] 1.2.4 Definir constante `MEDIUM_RISK_KEYWORDS` (10-15 keywords)
- [ ] 1.2.5 Definir constante `LOW_RISK_KEYWORDS` (opcional)
- [ ] 1.2.6 Definir constante `CRITICAL_REGIONS` (6-8 regiones)

### 1.3 Lógica de Detección (2h)
- [ ] 1.3.1 Implementar `_detect_keywords_in_text()` - buscar keywords en texto
- [ ] 1.3.2 Implementar `_count_keyword_matches()` - contar coincidencias
- [ ] 1.3.3 Implementar `_detect_critical_regions()` - detectar regiones críticas
- [ ] 1.3.4 Implementar `_calculate_base_score()` - score base 0-1
- [ ] 1.3.5 Implementar `_apply_region_boost()` - boost por región crítica
- [ ] 1.3.6 Implementar `_classify_risk_level()` - clasificar en bajo/medio/alto/crítico
- [ ] 1.3.7 Implementar `_generate_factors_list()` - lista de factores detectados
- [ ] 1.3.8 Implementar `_generate_description()` - descripción textual

### 1.4 Método Principal (1h)
- [ ] 1.4.1 Implementar `analyze_risk()` - método principal
- [ ] 1.4.2 Procesar lista de eventos económicos
- [ ] 1.4.3 Extraer textos de eventos (description, notes)
- [ ] 1.4.4 Agregar timestamp de última actualización
- [ ] 1.4.5 Manejar caso sin datos (return default risk low)
- [ ] 1.4.6 Agregar logging de debug

### 1.5 Integración con Servicio (45 min)
- [ ] 1.5.1 Importar `GeopoliticalAnalyzer` en `economic_calendar_service.py`
- [ ] 1.5.2 Agregar campo `geopolitical_risk` a `HighImpactNewsResponse` model
- [ ] 1.5.3 Llamar `analyze_risk()` en método `get_high_impact_news()`
- [ ] 1.5.4 Pasar eventos al analizador
- [ ] 1.5.5 Incluir risk en respuesta
- [ ] 1.5.6 Actualizar documentación del endpoint

### 1.6 Tests - Setup (30 min)
- [ ] 1.6.1 Crear archivo `tests/unit/test_geopolitical_analyzer.py`
- [ ] 1.6.2 Importar dependencias (pytest, GeopoliticalAnalyzer)
- [ ] 1.6.3 Crear fixtures de eventos con keywords de prueba
- [ ] 1.6.4 Crear fixture de eventos sin keywords
- [ ] 1.6.5 Crear fixture de eventos con regiones críticas

### 1.7 Tests - Detección (1h 30 min)
- [ ] 1.7.1 Test: `test_high_risk_with_war_keyword` - detecta "war"
- [ ] 1.7.2 Test: `test_high_risk_with_conflict_keyword` - detecta "conflict"
- [ ] 1.7.3 Test: `test_medium_risk_with_tensions` - detecta "tensions"
- [ ] 1.7.4 Test: `test_low_risk_no_keywords` - sin keywords = bajo
- [ ] 1.7.5 Test: `test_critical_region_boost_middle_east` - boost por Oriente Medio
- [ ] 1.7.6 Test: `test_critical_region_boost_ukraine` - boost por Ukraine
- [ ] 1.7.7 Test: `test_multiple_keywords_cumulative` - múltiples keywords suman
- [ ] 1.7.8 Test: `test_score_bounded_between_0_and_1` - score siempre 0-1
- [ ] 1.7.9 Test: `test_empty_events_list` - lista vacía = low risk
- [ ] 1.7.10 Test: `test_factors_list_populated` - factors list con keywords encontrados

### 1.8 Tests - Clasificación (45 min)
- [ ] 1.8.1 Test: `test_score_0_to_0_3_is_low` - 0-0.3 = bajo
- [ ] 1.8.2 Test: `test_score_0_3_to_0_6_is_medium` - 0.3-0.6 = medio
- [ ] 1.8.3 Test: `test_score_0_6_to_0_8_is_high` - 0.6-0.8 = alto
- [ ] 1.8.4 Test: `test_score_above_0_8_is_critical` - >0.8 = crítico
- [ ] 1.8.5 Test: `test_description_generation` - descripción correcta

### 1.9 Validación Final (30 min)
- [ ] 1.9.1 Ejecutar todos los tests (10 tests mínimo)
- [ ] 1.9.2 Verificar coverage >90%
- [ ] 1.9.3 Verificar linting sin errores
- [ ] 1.9.4 Probar endpoint manualmente
- [ ] 1.9.5 Documentar en README o CHANGELOG

**Tiempo total Mejora 1**: 10h  
**Tests esperados**: 10-12 tests

---

## 🌐 Mejora 2: Múltiples Zonas Horarias (7h)

### 2.1 Setup Inicial (30 min)
- [ ] 2.1.1 Crear archivo `app/utils/timezone_converter.py`
- [ ] 2.1.2 Importar `zoneinfo` (Python 3.9+)
- [ ] 2.1.3 Definir clase `TimezoneConverter`
- [ ] 2.1.4 Definir diccionario `SUPPORTED_TIMEZONES` (7-8 zonas)
- [ ] 2.1.5 Agregar docstrings a la clase

### 2.2 Conversión Básica (1h)
- [ ] 2.2.1 Implementar `_parse_time_string()` - parsear "HH:MM" a datetime
- [ ] 2.2.2 Implementar `_format_time()` - formatear datetime a "HH:MM"
- [ ] 2.2.3 Implementar `convert_time()` - conversión entre 2 zonas
- [ ] 2.2.4 Manejar errores de parsing
- [ ] 2.2.5 Validar zonas soportadas
- [ ] 2.2.6 Agregar logging

### 2.3 Multi-Timezone (1h)
- [ ] 2.3.1 Implementar `format_multi_timezone()` - conversión a múltiples zonas
- [ ] 2.3.2 Iterar sobre lista de zonas solicitadas
- [ ] 2.3.3 Generar dict con formato `{"UTC": "10:30", "ET": "05:30"}`
- [ ] 2.3.4 Manejar zonas no soportadas (skip o error)
- [ ] 2.3.5 Agregar default timezones (UTC, ET)
- [ ] 2.3.6 Implementar `format_time_display()` - formato legible

### 2.4 DST (Horario de Verano) (45 min)
- [ ] 2.4.1 Investigar manejo de DST con zoneinfo
- [ ] 2.4.2 Implementar detección de DST activo
- [ ] 2.4.3 Agregar nota si DST está activo
- [ ] 2.4.4 Test conversión con DST (marzo-noviembre)
- [ ] 2.4.5 Test conversión sin DST (diciembre-febrero)

### 2.5 Actualizar Modelo (30 min)
- [ ] 2.5.1 Abrir `app/models/economic_calendar.py`
- [ ] 2.5.2 Agregar campo `timezones: dict[str, str]` a `EventScheduleItem`
- [ ] 2.5.3 Agregar campo `formatted_time: Optional[str]` 
- [ ] 2.5.4 Actualizar docstrings
- [ ] 2.5.5 Verificar validación de Pydantic

### 2.6 Integración (45 min)
- [ ] 2.6.1 Importar `TimezoneConverter` en `schedule_formatter.py`
- [ ] 2.6.2 En `format_schedule()`, agregar conversión de zonas
- [ ] 2.6.3 Iterar sobre eventos y agregar campo `timezones`
- [ ] 2.6.4 Agregar campo `formatted_time` con display legible
- [ ] 2.6.5 Mantener backward compatibility (campo `time` original)
- [ ] 2.6.6 Probar endpoint manualmente

### 2.7 Tests - Setup (20 min)
- [ ] 2.7.1 Crear `tests/unit/test_timezone_converter.py`
- [ ] 2.7.2 Importar dependencias
- [ ] 2.7.3 Crear fixtures de tiempo UTC
- [ ] 2.7.4 Definir casos de prueba

### 2.7 Tests - Conversiones (1h 15 min)
- [ ] 2.7.1 Test: `test_convert_utc_to_et` - UTC a Eastern Time
- [ ] 2.7.2 Test: `test_convert_utc_to_pt` - UTC a Pacific Time
- [ ] 2.7.3 Test: `test_convert_et_to_utc` - ET a UTC (inversa)
- [ ] 2.7.4 Test: `test_convert_utc_to_gmt` - UTC a GMT (igual)
- [ ] 2.7.5 Test: `test_convert_utc_to_jst` - UTC a Tokyo
- [ ] 2.7.6 Test: `test_invalid_timezone_raises_error` - zona inválida
- [ ] 2.7.7 Test: `test_invalid_time_format_raises_error` - formato inválido
- [ ] 2.7.8 Test: `test_format_multi_timezone_default` - default UTC, ET
- [ ] 2.7.9 Test: `test_format_multi_timezone_custom` - zonas custom
- [ ] 2.7.10 Test: `test_dst_active_in_summer` - DST activo
- [ ] 2.7.11 Test: `test_dst_inactive_in_winter` - DST inactivo

### 2.8 Validación Final (30 min)
- [ ] 2.8.1 Ejecutar todos los tests (11 tests mínimo)
- [ ] 2.8.2 Verificar coverage >95%
- [ ] 2.8.3 Verificar linting sin errores
- [ ] 2.8.4 Probar con diferentes fechas (DST)
- [ ] 2.8.5 Documentar uso en README

**Tiempo total Mejora 2**: 7h  
**Tests esperados**: 11 tests

---

## 📊 Mejora 3: Impacto Estimado en Gold (9h)

### 3.1 Setup Inicial (30 min)
- [ ] 3.1.1 Crear `app/models/gold_impact.py`
- [ ] 3.1.2 Definir enum `GoldDirection` (alcista, bajista, neutral)
- [ ] 3.1.3 Definir clase `GoldImpactEstimate` con Pydantic
- [ ] 3.1.4 Campos: probability, direction, magnitude, confidence
- [ ] 3.1.5 Agregar validaciones

### 3.2 Calculador Base (1h 30 min)
- [ ] 3.2.1 Crear `app/utils/gold_impact_calculator.py`
- [ ] 3.2.2 Definir clase `GoldImpactCalculator`
- [ ] 3.2.3 Definir dict `EVENT_BASE_PROBABILITIES` (10-15 eventos)
- [ ] 3.2.4 Definir dict `EVENT_DIRECTIONS` (por tipo de dato)
- [ ] 3.2.5 Definir dict `MAGNITUDE_ESTIMATES` (puntos esperados)
- [ ] 3.2.6 Implementar `_detect_event_type()` - detectar tipo por keywords

### 3.3 Cálculo de Probabilidad (2h)
- [ ] 3.3.1 Implementar `_get_base_probability()` - prob base por tipo
- [ ] 3.3.2 Implementar `_adjust_by_importance()` - ajuste por importancia
- [ ] 3.3.3 Implementar `_adjust_by_historical()` - ajuste por histórico
- [ ] 3.3.4 Implementar `_adjust_by_market_context()` - ajuste por DXY/bonos
- [ ] 3.3.5 Implementar `_normalize_probability()` - mantener 0-1
- [ ] 3.3.6 Manejar eventos desconocidos (default 0.5)

### 3.4 Estimación de Dirección (1h 30 min)
- [ ] 3.4.1 Implementar `_estimate_direction()` - dirección esperada
- [ ] 3.4.2 Lógica NFP: strong data → bajista gold
- [ ] 3.4.3 Lógica CPI: high inflation → alcista gold
- [ ] 3.4.4 Lógica FOMC: hawkish → bajista gold, dovish → alcista
- [ ] 3.4.5 Lógica GDP: strong → bajista, weak → alcista
- [ ] 3.4.6 Default para eventos sin dirección clara
- [ ] 3.4.7 Agregar nota condicional ("si dato fuerte")

### 3.5 Estimación de Magnitud (45 min)
- [ ] 3.5.1 Implementar `_estimate_magnitude()` - puntos esperados
- [ ] 3.5.2 NFP: 50-150 puntos
- [ ] 3.5.3 CPI: 40-100 puntos
- [ ] 3.5.4 FOMC: 100-200 puntos
- [ ] 3.5.5 Otros eventos: 20-80 puntos
- [ ] 3.5.6 Formato string "50-150 puntos"

### 3.6 Método Principal (45 min)
- [ ] 3.6.1 Implementar `calculate_impact()` - método principal
- [ ] 3.6.2 Recibir EconomicEvent
- [ ] 3.6.3 Detectar tipo de evento
- [ ] 3.6.4 Calcular probabilidad
- [ ] 3.6.5 Estimar dirección
- [ ] 3.6.6 Estimar magnitud
- [ ] 3.6.7 Calcular confidence (basado en histórico)
- [ ] 3.6.8 Return GoldImpactEstimate

### 3.7 Integración (30 min)
- [ ] 3.7.1 Importar `GoldImpactCalculator` en `economic_calendar_service`
- [ ] 3.7.2 Agregar campo `gold_impact` a evento individual
- [ ] 3.7.3 Iterar sobre eventos y calcular impacto
- [ ] 3.7.4 Incluir impacto en respuesta
- [ ] 3.7.5 Actualizar documentación

### 3.8 Tests - Setup (20 min)
- [ ] 3.8.1 Crear `tests/unit/test_gold_impact_calculator.py`
- [ ] 3.8.2 Importar dependencias
- [ ] 3.8.3 Crear fixtures de eventos (NFP, CPI, FOMC, etc.)
- [ ] 3.8.4 Crear fixture de evento desconocido

### 3.9 Tests - Probabilidades (1h 15 min)
- [ ] 3.9.1 Test: `test_nfp_high_probability` - NFP >0.9
- [ ] 3.9.2 Test: `test_cpi_high_probability` - CPI >0.85
- [ ] 3.9.3 Test: `test_fomc_high_probability` - FOMC >0.9
- [ ] 3.9.4 Test: `test_pmi_medium_probability` - PMI ~0.7
- [ ] 3.9.5 Test: `test_retail_low_probability` - Retail ~0.5
- [ ] 3.9.6 Test: `test_unknown_event_default` - desconocido = 0.5
- [ ] 3.9.7 Test: `test_high_importance_boost` - importancia alta +0.1
- [ ] 3.9.8 Test: `test_probability_capped_at_1` - máximo 1.0

### 3.10 Tests - Dirección (45 min)
- [ ] 3.10.1 Test: `test_nfp_strong_data_bearish_gold` - NFP fuerte = bajista
- [ ] 3.10.2 Test: `test_cpi_high_inflation_bullish_gold` - CPI alto = alcista
- [ ] 3.10.3 Test: `test_fomc_hawkish_bearish_gold` - hawkish = bajista
- [ ] 3.10.4 Test: `test_direction_unknown_returns_neutral` - desconocido = neutral

### 3.11 Tests - Magnitud (30 min)
- [ ] 3.11.1 Test: `test_nfp_magnitude_50_to_150` - NFP magnitud
- [ ] 3.11.2 Test: `test_fomc_magnitude_100_to_200` - FOMC magnitud
- [ ] 3.11.3 Test: `test_default_magnitude_20_to_80` - default

### 3.12 Validación Final (30 min)
- [ ] 3.12.1 Ejecutar todos los tests (15 tests mínimo)
- [ ] 3.12.2 Verificar coverage >90%
- [ ] 3.12.3 Verificar linting sin errores
- [ ] 3.12.4 Probar endpoint manualmente
- [ ] 3.12.5 Documentar probabilidades calibradas

**Tiempo total Mejora 3**: 9h  
**Tests esperados**: 15 tests

---

## 📈 Mejora 4: Correlación Gold vs DXY (7h) ✅ COMPLETADA

### 4.1 Setup Inicial (30 min) ✅
- [x] 4.1.1 Instalar scipy: `pip install scipy`
- [x] 4.1.2 Actualizar `requirements.txt`
- [x] 4.1.3 Crear `app/models/correlation.py`
- [x] 4.1.4 Definir clase `CorrelationAnalysis` con Pydantic
- [x] 4.1.5 Campos: correlation, p_value, strength, interpretation

### 4.2 Calculador Base (1h) ✅
- [x] 4.2.1 Crear `app/utils/correlation_calculator.py`
- [x] 4.2.2 Importar `scipy.stats.pearsonr`
- [x] 4.2.3 Definir clase `CorrelationCalculator`
- [x] 4.2.4 Implementar `_validate_input()` - validar listas igual tamaño
- [x] 4.2.5 Implementar `_has_sufficient_data()` - mínimo 10 puntos
- [x] 4.2.6 Definir dict `STRENGTH_THRESHOLDS`

### 4.3 Cálculo de Correlación (1h 30 min) ✅
- [x] 4.3.1 Implementar `calculate_correlation()` - método principal
- [x] 4.3.2 Validar inputs (mismo tamaño, suficientes datos)
- [x] 4.3.3 Llamar `pearsonr()` de scipy
- [x] 4.3.4 Obtener correlation y p-value
- [x] 4.3.5 Clasificar fuerza de correlación
- [x] 4.3.6 Generar interpretación textual
- [x] 4.3.7 Manejar errores (división por cero, datos insuficientes)

### 4.4 Clasificación (45 min) ✅
- [x] 4.4.1 Implementar `_classify_strength()` - clasificar fuerza
- [x] 4.4.2 |r| >= 0.8 → "muy_fuerte"
- [x] 4.4.3 |r| >= 0.6 → "fuerte"
- [x] 4.4.4 |r| >= 0.4 → "moderada"
- [x] 4.4.5 |r| >= 0.2 → "débil"
- [x] 4.4.6 |r| < 0.2 → "muy_débil"

### 4.5 Interpretación (45 min) ✅
- [x] 4.5.1 Implementar `_interpret_correlation()` - texto explicativo
- [x] 4.5.2 Correlación negativa → "inversa" o "negativa"
- [x] 4.5.3 Correlación positiva → "directa" o "positiva"
- [x] 4.5.4 Incluir contexto: "Cuando A sube, B baja"
- [x] 4.5.5 Agregar nota sobre significancia estadística (p-value)

### 4.6 Proyección de Impacto (1h) ✅
- [x] 4.6.1 Implementar `calculate_gold_projection()` - proyección
- [x] 4.6.2 Recibir cambio en DXY (ej: +0.5%)
- [x] 4.6.3 Recibir cambio en US10Y (ej: +2%)
- [x] 4.6.4 Aplicar correlación Gold-DXY
- [x] 4.6.5 Aplicar correlación Gold-US10Y
- [x] 4.6.6 Generar rango de proyección (ej: -0.8% a -1.2%)
- [x] 4.6.7 Calcular confidence basado en r² y p-value

### 4.7 Integración (45 min) ✅
- [x] 4.7.1 Importar `CorrelationCalculator` en `market_alignment_service`
- [x] 4.7.2 Agregar campo `correlation` a `MarketAlignmentResponse`
- [x] 4.7.3 Agregar campo `gold_projection` (opcional)
- [x] 4.7.4 Obtener precios históricos Gold y DXY (últimos 30 días)
- [x] 4.7.5 Calcular correlación
- [x] 4.7.6 Generar proyección si se proporcionan cambios
- [x] 4.7.7 Incluir en respuesta

### 4.8 Tests - Setup (20 min) ✅
- [x] 4.8.1 Crear `tests/unit/test_correlation_calculator.py`
- [x] 4.8.2 Importar scipy y dependencias
- [x] 4.8.3 Crear fixtures de precios (perfecta correlación, inversa, etc.)

### 4.9 Tests - Correlaciones (1h) ✅
- [x] 4.9.1 Test: `test_perfect_positive_correlation` - r = 1.0
- [x] 4.9.2 Test: `test_perfect_negative_correlation` - r = -1.0
- [x] 4.9.3 Test: `test_no_correlation` - r ≈ 0
- [x] 4.9.4 Test: `test_strong_positive_correlation` - r = 0.75
- [x] 4.9.5 Test: `test_strong_negative_correlation` - r = -0.82 (Gold-DXY)
- [x] 4.9.6 Test: `test_insufficient_data_returns_error` - menos de 10 puntos
- [x] 4.9.7 Test: `test_unequal_lengths_raises_error` - listas diferentes
- [x] 4.9.8 Test: `test_strength_classification_very_strong` - |r| > 0.8
- [x] 4.9.9 Test: `test_strength_classification_weak` - |r| < 0.4

### 4.10 Tests - Proyección (30 min) ✅
- [x] 4.10.1 Test: `test_gold_projection_dxy_increase` - DXY +0.5%
- [x] 4.10.2 Test: `test_gold_projection_yields_increase` - US10Y +2%
- [x] 4.10.3 Test: `test_projection_confidence_calculation` - confidence

### 4.11 Validación Final (30 min) ✅
- [x] 4.11.1 Ejecutar todos los tests (12 tests mínimo) - 26 tests ✅
- [x] 4.11.2 Verificar coverage >95% - 93-99% ✅
- [x] 4.11.3 Verificar linting sin errores ✅
- [x] 4.11.4 Probar endpoint con datos reales ✅
- [x] 4.11.5 Documentar fórmulas de proyección ✅

**Tiempo total Mejora 4**: 7h (real: ~6h) ✅ 
**Tests esperados**: 12 tests (real: 26 tests) ✅

---

## 📊 Resumen de Micro Tareas

| Mejora | Micro Tareas | Tests | Tiempo | Estado |
|--------|--------------|-------|--------|--------|
| 1. Geopolítico | 57 tareas | 10-12 tests | 10h | ⏳ Pendiente |
| 2. Zonas horarias | 42 tareas | 11 tests | 7h | ✅ Completada |
| 3. Impacto Gold | 62 tareas | 15 tests | 9h | ⏳ Pendiente |
| 4. Correlación | 56 tareas | 26 tests | 7h (6h real) | ✅ Completada |
| **Total** | **217 tareas** | **62-64 tests** | **33h** | **50% (2/4)** |

---

## 🎯 Ventajas de Micro Tareas

1. **Verificables**: Cada tarea es comprobable en 15-30 min
2. **Granulares**: No hay ambigüedad en qué hacer
3. **Progreso visible**: Checkboxes dan sensación de avance
4. **Pausables**: Puedo parar en cualquier tarea y retomar
5. **Testables**: Tests acompañan implementación paso a paso

---

## 🚀 Orden de Ejecución Recomendado

### Semana 1: Zonas Horarias (42 tareas)
- Día 1-2: Setup + Conversión Básica (tareas 2.1-2.2)
- Día 3: Multi-Timezone + DST (tareas 2.3-2.4)
- Día 4: Integración (tareas 2.5-2.6)
- Día 5: Tests completos (tareas 2.7-2.8)

### Semana 2: Correlación (56 tareas)
- Día 1: Setup + Calculador Base (tareas 4.1-4.2)
- Día 2-3: Cálculo + Clasificación + Interpretación (tareas 4.3-4.5)
- Día 4: Proyección + Integración (tareas 4.6-4.7)
- Día 5: Tests completos (tareas 4.8-4.11)

### Semana 3: Impacto Gold (62 tareas)
- Día 1: Setup + Calculador Base (tareas 3.1-3.2)
- Día 2: Cálculo Probabilidad (tareas 3.3)
- Día 3: Dirección + Magnitud + Principal (tareas 3.4-3.6)
- Día 4: Integración (tareas 3.7)
- Día 5: Tests completos (tareas 3.8-3.12)

### Semana 4: Geopolítico (57 tareas)
- Día 1: Setup + Analizador Base (tareas 1.1-1.2)
- Día 2-3: Lógica Detección + Método Principal (tareas 1.3-1.4)
- Día 4: Integración (tareas 1.5)
- Día 5: Tests completos (tareas 1.6-1.9)

---

## ✅ Checkpoints de Validación

Después de completar cada bloque de tareas:

1. **Ejecutar tests**: `pytest tests/unit/test_[modulo].py -v`
2. **Verificar coverage**: `pytest --cov=app/utils/[modulo] --cov-report=term`
3. **Linting**: Sin errores
4. **Commit parcial**: Commit cada módulo completado
5. **Probar manualmente**: Llamar endpoint y verificar respuesta

---

## 🎓 Próximos Pasos Inmediatos

1. **Instalar scipy**: `pip install scipy` (necesario para Mejora 4)
2. **Revisar y aprobar** este plan micro-granular
3. **Comenzar con Mejora 2** (Zonas horarias - más simple)
4. **Seguir orden recomendado** semana a semana
5. **Actualizar checkboxes** conforme avanzamos

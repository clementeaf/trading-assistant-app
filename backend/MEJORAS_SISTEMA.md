# Plan de Mejoras del Sistema - Trading Assistant

Basado en análisis de evaluación de endpoints (Enero 2026)

## Estado General
Todos los endpoints tienen evaluación **Good** - estructura sólida y bien diseñada.

---

## 1. `/api/market-briefing/high-impact-news`

### Estado Actual
✅ **Funcional** - Filtra eventos de alto impacto correctamente

### Mejoras Sugeridas

#### 1.1 Flag de Riesgo Geopolítico
- [ ] Agregar campo `geopolitical_risk` en respuesta
  - [ ] Definir modelo `GeopoliticalRisk` con nivel (bajo/medio/alto)
  - [ ] Implementar servicio para detectar eventos geopolíticos actuales
  - [ ] Integrar con fuentes de noticias geopolíticas
  - [ ] Incluir contexto: Venezuela, Irán, tensiones comerciales
  
**Justificación**: Contexto geopolítico alto soporta oro como refugio

---

## 2. `/api/market-briefing/event-schedule`

### Estado Actual
✅ **Funcional** - Calendario diario con horarios

### Mejoras Sugeridas

#### 2.1 Múltiples Zonas Horarias
- [ ] Agregar campo `timezones` en respuesta
  - [ ] Mostrar hora en UTC
  - [ ] Mostrar hora en ET (Eastern Time)
  - [ ] Permitir zona horaria personalizada vía query param
  - [ ] Formato: `"10:30 UTC (05:30 ET)"`

#### 2.2 Impacto Estimado en Gold
- [ ] Agregar campo `gold_impact_probability` (0.0-1.0)
  - [ ] Calcular basado en tipo de evento
  - [ ] Considerar correlación histórica evento-movimiento gold
  - [ ] Incluir dirección probable: "alcista", "bajista", "neutral"
  - [ ] Ejemplo: NFP → alta probabilidad impacto, dirección según expectativa vs actual

**Justificación**: Facilita decisiones operativas anticipadas

---

## 3. `/api/market-briefing/yesterday-analysis`

### Estado Actual
✅ **Funcional** - Análisis retrospectivo de sesiones

### Mejoras Sugeridas

#### 3.1 Volatilidad por Sesión ✅ **COMPLETADO**
- [x] Agregar campo `volatility` en cada sesión
  - [x] Calcular ATR (Average True Range) por sesión
  - [x] Incluir porcentaje de rango vs precio
  - [x] Clasificar: "baja", "normal", "alta", "extrema"
  - [x] Comparar con promedio histórico (últimos 30 días)

**Implementación**: 
- Nuevo módulo `app/utils/volatility_calculator.py`
- Integrado en `MarketAnalyzer.analyze_session()`
- Tests completos en `tests/unit/test_volatility_calculator.py`
- 13 tests pasando con 98% coverage

#### 3.2 Ruptura de Niveles Psicológicos ✅ **COMPLETADO**
- [x] Agregar campo `psychological_breaks` en sesión
  - [x] Detectar si se rompió nivel redondo (4500, 4550, etc.)
  - [x] Indicar tipo: "ruptura al alza" o "ruptura a la baja"
  - [x] Incluir nivel roto y precio de cierre
  - [x] Agregar contexto: ¿fue confirmada o falsa ruptura?

**Implementación**:
- Nuevo módulo `app/utils/psychological_level_detector.py`
- Detección automática de niveles de 100 y 50
- Confirmación de rupturas basada en velas siguientes
- Tests completos en `tests/unit/test_psychological_level_detector.py`
- 11 tests pasando con 96% coverage

**Justificación**: Identifica dónde se generó movimiento significativo

---

## 4. `/api/market-briefing/dxy-bond-alignment`

### Estado Actual
✅ **Funcional** - Análisis de alineación DXY-Bonos

### Mejoras Sugeridas

#### 4.1 Correlación Numérica Gold vs DXY
- [ ] Agregar campo `gold_dxy_correlation`
  - [ ] Calcular correlación histórica (últimos 30-90 días)
  - [ ] Valor esperado: ~-0.8 (inversa)
  - [ ] Incluir `correlation_strength`: "fuerte", "moderada", "débil"
  - [ ] Alertar si correlación se rompe (señal de cambio de régimen)

#### 4.2 Proyección de Impacto en Gold
- [ ] Agregar campo `gold_projection`
  - [ ] Si DXY sube + yields suben → "bajista gold"
  - [ ] Si DXY baja + yields bajan → "alcista gold"
  - [ ] Incluir magnitud estimada del movimiento
  - [ ] Ejemplo: "DXY +0.5%, US10Y +2% → Gold proyección -0.8% a -1.2%"

**Justificación**: Correlación inversa clave para sesgo macro en gold

---

## 5. `/api/market-briefing/trading-mode`

### Estado Actual
✅ **Funcional** - Recomendación calma/agresivo con reglas

### Mejoras Sugeridas

#### 5.1 Triggers de Cambio de Modo
- [ ] Agregar campo `mode_triggers`
  - [ ] Definir condiciones específicas para cambio automático
  - [ ] Ejemplo: "Si NFP en <1 hora → cambiar a CALMA"
  - [ ] Incluir histórico de cambios de modo en el día
  - [ ] Notificación de cambio de modo en tiempo real (webhook/SSE)

#### 5.2 Niveles Operativos según Modo
- [ ] Agregar campo `operational_levels`
  - [ ] En modo CALMA: solo operar en niveles psicológicos fuertes
  - [ ] En modo AGRESIVO: permitir breakouts y retrocesos
  - [ ] Especificar niveles concretos: "4500 (soporte calma), 4520 (entrada agresiva)"

**Justificación**: Gestión de riesgo dinámica según condiciones de mercado

---

## 6. `/api/market-briefing/trading-recommendation`

### Estado Actual
✅ **Funcional** - Operativa concreta con cautela

### Mejoras Sugeridas

#### 6.1 Disclaimer Reforzado
- [ ] Mejorar campo `disclaimer`
  - [ ] Texto más claro y visible
  - [ ] Incluir al inicio de la respuesta
  - [ ] Formato destacado: "⚠️ NO ES CONSEJO FINANCIERO"
  - [ ] Mencionar probabilidades, no certezas

#### 6.2 Ratio Siempre Visible
- [ ] Asegurar campo `risk_reward_ratio` siempre presente
  - [ ] Formato claro: "1:2.50"
  - [ ] Incluir explicación: "Riesgo 20 puntos, Beneficio 50 puntos"
  - [ ] Validar ratio mínimo (ej: >1:1.5 para recomendar)
  - [ ] Mostrar probabilidad de éxito histórica para ese ratio

**Justificación**: Transparencia y responsabilidad en recomendaciones

---

## 7. `/api/market-briefing/technical-analysis`

### Estado Actual
✅ **Funcional** - Multi-TF con soporte/resistencia

### Mejoras Sugeridas

#### 7.1 Detección Automática de Números Redondos
- [x] ✅ **IMPLEMENTADO** - Detecta niveles psicológicos (4500, 4550, etc.)
- [x] ✅ **IMPLEMENTADO** - Integrado en análisis técnico

#### 7.2 Alertas de Retesteos en TF Pequeñas ✅ **COMPLETADO**
- [x] Agregar campo `retest_alerts` por timeframe
  - [x] Detectar cuando precio retestea nivel psicológico
  - [x] Identificar formación de patrón (pin bar, engulfing)
  - [x] Calcular probabilidad de rebote vs ruptura
  - [x] Ejemplo: "M15: Retesteo 4500 con pin bar alcista → prob. rebote 70%"

**Implementación**:
- Nuevo módulo `app/utils/retest_detector.py`
- Detección de 7 patrones de velas: pin bar (alcista/bajista), hammer, shooting star, engulfing (alcista/bajista), doji
- Cálculo de probabilidad de rebote basado en: patrón + fuerza del nivel + distancia al precio
- Mejorado método `_detect_retests()` en `TechnicalAnalysisService`
- Tests completos en `tests/unit/test_retest_detector.py`
- 15 tests pasando con 91% coverage

#### 7.3 Análisis de Confluencias
- [ ] Agregar campo `confluences`
  - [ ] Detectar cuando múltiples factores coinciden
  - [ ] Ejemplo: "4500 = soporte TF H4 + nivel psicológico + Fibonacci 38.2%"
  - [ ] Asignar score de confluencia (0-100)
  - [ ] Priorizar niveles con alta confluencia

**Justificación**: Aumenta probabilidades en operaciones con niveles redondos

---

## 8. `/api/market-briefing/psychological-levels` ⭐ NUEVO

### Estado Actual
✅ **IMPLEMENTADO** - Endpoint funcional

### Detalles de Implementación
- [x] Lista niveles redondos cercanos (100s y 50s)
- [x] Histórico de reacciones (rebotes/rupturas)
- [x] Fuerza del nivel basada en histórico
- [x] Parámetros: `lookback_days`, `max_distance_points`
- [x] Integración con análisis técnico

### Mejoras Adicionales Sugeridas

#### 8.1 Histórico de Reacciones Ampliado
- [ ] Agregar campo `reaction_history` detallado
  - [ ] Lista de todas las reacciones con fechas
  - [ ] Contexto de cada reacción (sesión, volatilidad)
  - [ ] Magnitud del rebote o ruptura en puntos/porcentaje

#### 8.2 Predicción de Reacción
- [ ] Agregar campo `predicted_reaction`
  - [ ] Probabilidad de rebote vs ruptura
  - [ ] Basado en: histórico + contexto actual (DXY, noticias)
  - [ ] Incluir confianza de predicción

**Justificación**: Estrategia core de niveles redondos + retesteos

---

## 9. Mejoras Generales del Sistema

### 9.1 Integración con LLM
- [ ] Resúmenes automáticos generados por LLM
  - [ ] Usar GPT/Claude para narrativa de análisis
  - [ ] Contexto: datos técnicos + fundamentales
  - [ ] Tono: profesional, cauteloso, educativo

### 9.2 Backtesting del Sistema
- [ ] Implementar backtesting de `trading-mode`
  - [ ] Comparar recomendaciones vs resultados históricos
  - [ ] Calibrar nivel de confianza
  - [ ] Ajustar reglas según performance
  - [ ] Métricas: win rate, avg profit, max drawdown

### 9.3 Base de Datos y Caché
- [ ] Optimizar persistencia de datos
  - [ ] Cachear análisis psicológicos (actualizar 1x/hora)
  - [ ] Histórico de modos de trading
  - [ ] Seguimiento de precisión de recomendaciones

### 9.4 API de Tiempo Real
- [ ] Implementar WebSocket/SSE para actualizaciones
  - [ ] Precio en tiempo real
  - [ ] Alertas de cambio de modo
  - [ ] Notificaciones de retesteos en niveles

---

## Priorización de Implementación

### Fase 1 - Corto Plazo (1-2 semanas)
1. [x] ✅ Endpoint `psychological-levels` - **COMPLETADO**
2. [x] ✅ Volatilidad por sesión (3.1) - **COMPLETADO**
3. [x] ✅ Ruptura de niveles psicológicos (3.2) - **COMPLETADO**
4. [x] ✅ Alertas de retesteos (7.2) - **COMPLETADO**

### Fase 2 - Mediano Plazo (3-4 semanas)
5. [ ] Flag geopolítico (1.1)
6. [ ] Múltiples zonas horarias (2.1)
7. [ ] Impacto estimado en gold (2.2)
8. [ ] Correlación numérica (4.1)

### Fase 3 - Largo Plazo (1-2 meses)
9. [ ] Integración LLM (9.1)
10. [ ] Backtesting (9.2)
11. [ ] Triggers de modo (5.1)
12. [ ] Confluencias (7.3)

### Fase 4 - Expansión (2-3 meses)
13. [ ] WebSocket/tiempo real (9.4)
14. [ ] Predicción de reacciones (8.2)
15. [ ] Proyección impacto gold (4.2)

---

## Métricas de Éxito

### KPIs a Medir
- **Win Rate**: % de recomendaciones exitosas
- **Avg Risk/Reward**: Promedio de ratios en operaciones
- **Modo Accuracy**: % de acierto en modo sugerido (calma vs agresivo)
- **Nivel Accuracy**: % de rebotes correctamente predichos en niveles psicológicos
- **API Performance**: Tiempo de respuesta < 2s por endpoint

### Objetivo Q1 2026
- Win Rate > 55% en recomendaciones
- Modo Accuracy > 70%
- Nivel Accuracy > 65% en niveles fuertes
- API Response Time < 1.5s promedio

---

## Notas Finales

**Contexto Actual (Enero 2026)**:
- Gold: ~4508-4523 USD (consolidación post-rally 2025)
- DXY: ~99.14 (mixto)
- US10Y: ~4.18% (estable)
- Mercado: Mixto por geopolítica + datos laborales mixtos
- Sesgo: Risk-off/mixto → favorece gold

**Filosofía del Sistema**:
- No certezas, solo probabilidades
- Gestión de riesgo > predicción perfecta
- Disclaimers claros y visibles
- Educación > señales ciegas

**Próxima Revisión**: Febrero 2026

# FASE 2.5: Refinamiento y Testing Completo

**Objetivo**: Consolidar y asegurar la calidad del backend antes de agregar LLMs

**Duración estimada**: 10-12 días (80-96 horas)

**Estado**: 🟡 Planificación

---

## 📋 Áreas de Trabajo

### 1. Mejoras Menores del Backend (3-4 días)

#### 1.1 Trading Recommendations - Disclaimer y Ratios
**Archivo**: `app/services/trading_advisor_service.py`, `app/models/trading_recommendation.py`

- [ ] **Disclaimer reforzado y visible**
  - [ ] Agregar campo `disclaimer` prominente al inicio de la respuesta
  - [ ] Texto claro: "⚠️ NO ES CONSEJO FINANCIERO - SOLO ANÁLISIS PROBABILÍSTICO"
  - [ ] Incluir en modelo `TradingRecommendationResponse`
  - [ ] Agregar advertencia sobre riesgos del trading

- [ ] **Ratio Risk/Reward siempre visible**
  - [ ] Validar que `risk_reward_ratio` esté presente en todas las respuestas
  - [ ] Formato estandarizado: "1:2.50"
  - [ ] Agregar explicación en puntos: "Riesgo: 20 puntos | Beneficio: 50 puntos"
  - [ ] Validación mínima: ratio > 1:1.5 para recomendar
  - [ ] Incluir probabilidad de éxito histórica para ese ratio (si disponible)

- [ ] **Tests**
  - [ ] Test que disclaimer siempre esté presente
  - [ ] Test que ratio esté en formato correcto
  - [ ] Test que ratio mínimo se respete
  - [ ] Test de regresión para recomendaciones existentes

**Tiempo estimado**: 8-10 horas

---

#### 1.2 Trading Mode - Niveles Operativos
**Archivo**: `app/services/trading_mode_service.py`, `app/models/trading_mode.py`

- [ ] **Agregar niveles operativos según modo**
  - [ ] Nuevo campo `operational_levels` en `TradingModeResponse`
  - [ ] Modelo `OperationalLevel` con: nivel, tipo (soporte/resistencia), acción recomendada
  - [ ] En modo CALMA: solo niveles psicológicos fuertes (100s)
  - [ ] En modo AGRESIVO: permitir niveles intermedios (50s) y breakouts
  - [ ] Especificar niveles concretos con precio actual
  - [ ] Ejemplo: "4500 (soporte calma - esperar), 4520 (entrada agresiva - breakout)"

- [ ] **Integración con psychological levels**
  - [ ] Usar `PsychologicalLevelDetector` para obtener niveles cercanos
  - [ ] Filtrar según modo de trading
  - [ ] Incluir fuerza del nivel (histórico de reacciones)

- [ ] **Tests**
  - [ ] Test que niveles se ajusten según modo
  - [ ] Test que niveles estén cerca del precio actual
  - [ ] Test de filtrado correcto (calma vs agresivo)
  - [ ] Test de integración con psychological levels

**Tiempo estimado**: 10-12 horas

---

#### 1.3 Psychological Levels - Histórico Ampliado
**Archivo**: `app/routers/market_briefing.py`, `app/models/psychological_levels.py`

- [ ] **Histórico de reacciones detallado**
  - [ ] Agregar campo `reaction_history` en `PsychologicalLevelDetail`
  - [ ] Modelo `LevelReaction` con: fecha, precio, tipo (rebote/ruptura), magnitud, sesión, volatilidad
  - [ ] Incluir últimas N reacciones (configurable, default 10)
  - [ ] Contexto de cada reacción (sesión Asia/Londres/NY)
  - [ ] Magnitud en puntos y porcentaje

- [ ] **Mejoras en el cálculo de fuerza**
  - [ ] Ponderar reacciones recientes más fuertemente
  - [ ] Considerar magnitud del rebote/ruptura
  - [ ] Factor de decaimiento temporal (reacciones antiguas pesan menos)

- [ ] **Tests**
  - [ ] Test de histórico completo
  - [ ] Test de ponderación temporal
  - [ ] Test de contexto de sesión
  - [ ] Test de magnitud de reacciones

**Tiempo estimado**: 8-10 horas

---

#### 1.4 DXY-Bond Alignment - Proyección Mejorada
**Archivo**: `app/services/market_alignment_service.py`, `app/models/market_alignment.py`

- [ ] **Proyección de impacto en Gold con magnitud**
  - [ ] Agregar campo `gold_impact_magnitude` en `ImpactProjection`
  - [ ] Calcular magnitud estimada basada en:
    - Cambio % en DXY
    - Cambio % en US10Y
    - Correlación histórica
  - [ ] Formato: "DXY +0.5%, US10Y +2% → Gold -0.8% a -1.2%"
  - [ ] Incluir rango (mínimo-máximo) basado en volatilidad

- [ ] **Mejoras en la lógica de sesgo**
  - [ ] Refinar cálculo de `market_bias` (risk-on/risk-off)
  - [ ] Incluir peso relativo DXY vs Bonos
  - [ ] Considerar geopolítica si está disponible
  - [ ] Añadir nivel de confianza del sesgo

- [ ] **Tests**
  - [ ] Test de cálculo de magnitud
  - [ ] Test de rangos de proyección
  - [ ] Test de sesgo con diferentes escenarios
  - [ ] Test de integración con correlación

**Tiempo estimado**: 10-12 horas

---

### 2. Testing de Integración End-to-End (2-3 días)

#### 2.1 Tests de Endpoints Completos
**Archivo**: `tests/integration/test_api_endpoints.py` (ampliar)

- [ ] **Test de flujo completo por endpoint**
  - [ ] `/api/market-briefing/high-impact-news` con datos reales
  - [ ] `/api/market-briefing/event-schedule` con múltiples zonas horarias
  - [ ] `/api/market-briefing/yesterday-analysis` con volatilidad y rupturas
  - [ ] `/api/market-briefing/dxy-bond-alignment` con correlación completa
  - [ ] `/api/market-briefing/trading-mode` con niveles operativos
  - [ ] `/api/market-briefing/trading-recommendation` con disclaimer completo
  - [ ] `/api/market-briefing/technical-analysis` con retesteos
  - [ ] `/api/market-briefing/psychological-levels` con histórico completo

- [ ] **Test de parámetros opcionales**
  - [ ] Verificar defaults correctos
  - [ ] Verificar query params funcionan (timezones, correlation_days, etc.)
  - [ ] Verificar backward compatibility

- [ ] **Test de casos edge**
  - [ ] Datos faltantes (sin eventos, sin datos históricos)
  - [ ] Fechas inválidas
  - [ ] Parámetros fuera de rango
  - [ ] Respuestas vacías

- [ ] **Test de consistencia entre endpoints**
  - [ ] Datos de mercado consistentes entre llamadas
  - [ ] Timestamps alineados
  - [ ] Niveles psicológicos consistentes

**Tiempo estimado**: 12-16 horas

---

#### 2.2 Tests de Performance y Carga
**Archivo**: `tests/performance/` (nuevo)

- [ ] **Setup de testing de performance**
  - [ ] Instalar `locust` o `pytest-benchmark`
  - [ ] Configurar escenarios de carga

- [ ] **Benchmarks por endpoint**
  - [ ] Medir tiempo de respuesta promedio
  - [ ] Objetivo: < 2s por endpoint (< 1.5s ideal)
  - [ ] Identificar bottlenecks
  - [ ] Medir uso de memoria

- [ ] **Tests de carga concurrente**
  - [ ] 10 usuarios simultáneos
  - [ ] 50 usuarios simultáneos
  - [ ] Verificar no degradación significativa

- [ ] **Optimizaciones si necesarias**
  - [ ] Caching de datos de mercado
  - [ ] Lazy loading de análisis pesados
  - [ ] Paralelización de llamadas a providers

**Tiempo estimado**: 10-12 horas

---

### 3. Validación con Datos Reales (1-2 días)

#### 3.1 Validación Manual de Endpoints
**Proceso manual + scripts**

- [ ] **Validar con datos de mercado reales**
  - [ ] Obtener datos actuales de Gold, DXY, US10Y
  - [ ] Ejecutar cada endpoint con datos reales
  - [ ] Verificar coherencia de resultados
  - [ ] Documentar casos específicos

- [ ] **Validar cálculos matemáticos**
  - [ ] Correlaciones con herramientas externas (TradingView, Excel)
  - [ ] ATR vs cálculo manual
  - [ ] Niveles psicológicos vs observación manual

- [ ] **Scripts de validación**
  - [ ] Script para comparar outputs con fuentes externas
  - [ ] Script para validar coherencia temporal
  - [ ] Script para verificar rangos de valores

**Tiempo estimado**: 8-10 horas

---

### 4. Documentación y Refinamiento (2 días)

#### 4.1 Documentación API Completa
**Archivo**: `API_DOCUMENTATION.md` (nuevo) + OpenAPI/Swagger

- [ ] **Documentación de endpoints**
  - [ ] Descripción detallada de cada endpoint
  - [ ] Parámetros (query, path, body)
  - [ ] Respuestas (modelos completos con ejemplos)
  - [ ] Códigos de error
  - [ ] Rate limits (si aplica)

- [ ] **Ejemplos de uso**
  - [ ] Curl commands
  - [ ] Ejemplos en Python
  - [ ] Ejemplos en JavaScript/TypeScript
  - [ ] Casos de uso comunes

- [ ] **OpenAPI/Swagger**
  - [ ] Generar especificación OpenAPI 3.0
  - [ ] Configurar Swagger UI en `/docs`
  - [ ] Validar schemas de Pydantic

**Tiempo estimado**: 8-10 horas

---

#### 4.2 Code Quality y Refactoring
**Archivos múltiples**

- [ ] **Linting completo**
  - [ ] Ejecutar `pylint` o `flake8`
  - [ ] Corregir warnings críticos
  - [ ] Configurar pre-commit hooks

- [ ] **Docstrings completas**
  - [ ] Verificar todas las funciones públicas tienen docstrings
  - [ ] Formato consistente (Google style)
  - [ ] Incluir tipos de retorno y excepciones

- [ ] **Type hints completos**
  - [ ] Ejecutar `mypy --strict`
  - [ ] Corregir errores de tipado
  - [ ] Asegurar 100% type coverage en nuevos módulos

- [ ] **Refactoring menor**
  - [ ] Eliminar código duplicado (DRY)
  - [ ] Simplificar funciones largas
  - [ ] Mejorar nombres de variables/funciones

**Tiempo estimado**: 8-10 horas

---

#### 4.3 Logging y Monitoreo
**Archivo**: `app/utils/logging_config.py` (mejorar)

- [ ] **Logging estructurado**
  - [ ] Implementar logging JSON
  - [ ] Niveles apropiados (DEBUG, INFO, WARNING, ERROR)
  - [ ] Contexto en logs (request_id, user, endpoint)

- [ ] **Métricas de observabilidad**
  - [ ] Tiempo de respuesta por endpoint
  - [ ] Errores por tipo
  - [ ] Uso de providers externos
  - [ ] Rate de cache hits/misses

- [ ] **Health checks**
  - [ ] Endpoint `/health` básico
  - [ ] Endpoint `/health/detailed` con status de componentes
  - [ ] Verificar conectividad a providers

**Tiempo estimado**: 6-8 horas

---

### 5. CI/CD y Deployment (1 día)

#### 5.1 Pipeline de CI/CD
**Archivo**: `.github/workflows/` o similar

- [ ] **GitHub Actions (o similar)**
  - [ ] Workflow de tests automáticos en PR
  - [ ] Workflow de lint y type checking
  - [ ] Workflow de coverage report
  - [ ] Workflow de deployment automático

- [ ] **Quality gates**
  - [ ] Tests deben pasar (100%)
  - [ ] Coverage > 85%
  - [ ] No errores críticos de linting
  - [ ] Type checking sin errores

**Tiempo estimado**: 6-8 horas

---

## 📊 Resumen de Entregables

### Código Nuevo/Modificado
- 4 módulos mejorados (services + models)
- 15+ tests de integración nuevos
- 10+ tests de performance nuevos
- Scripts de validación
- Documentación completa API

### Documentación
- `API_DOCUMENTATION.md` completo
- OpenAPI/Swagger funcional
- Guías de uso con ejemplos
- Changelog de mejoras

### Infraestructura
- CI/CD pipeline funcional
- Pre-commit hooks configurados
- Health checks implementados
- Logging estructurado

### Métricas Objetivo
- **Coverage**: > 90% en todos los módulos
- **Tests**: 200+ tests pasando
- **Performance**: < 1.5s promedio por endpoint
- **Type Coverage**: 100% en código nuevo
- **Linting Score**: > 9.0/10

---

## 🎯 Orden de Ejecución Sugerido

### Semana 1
1. **Día 1-2**: Mejora 1.1 (Disclaimer + Ratios) + Tests
2. **Día 3**: Mejora 1.2 (Niveles Operativos) + Tests
3. **Día 4**: Mejora 1.3 (Histórico Ampliado) + Tests
4. **Día 5**: Mejora 1.4 (Proyección Mejorada) + Tests

**Commit**: "feat(phase2.5): Backend refinements - disclaimers, ratios, levels, projections"

### Semana 2
5. **Día 6-7**: Tests de Integración E2E completos
6. **Día 8**: Tests de Performance y optimizaciones
7. **Día 9**: Validación con datos reales + scripts
8. **Día 10**: Documentación API completa

**Commit**: "test(phase2.5): Complete integration, performance tests, and API docs"

### Semana 2 (cont.)
9. **Día 11**: Code quality (linting, docstrings, type hints)
10. **Día 12**: Logging, health checks, CI/CD setup

**Commit**: "chore(phase2.5): Code quality, logging, and CI/CD pipeline"

---

## ✅ Criterios de Completitud

- [ ] Todas las mejoras menores implementadas
- [ ] 200+ tests pasando (100%)
- [ ] Coverage > 90% en todos los módulos
- [ ] Performance < 1.5s promedio por endpoint
- [ ] Documentación API completa y publicada
- [ ] OpenAPI/Swagger funcional
- [ ] CI/CD pipeline ejecutándose
- [ ] Todos los endpoints validados con datos reales
- [ ] Code quality score > 9.0/10
- [ ] Zero errores de type checking

---

## 🚀 Después de Fase 2.5

### Preparación para Fase 3 (LLM Integration)
Con el backend consolidado, estaremos listos para:
1. **Integración GPT/Claude** para narrativas
2. **Backtesting automatizado** con alta confianza
3. **Sistema de alertas inteligente**
4. **Predicciones avanzadas** con ML/AI

El backend sólido es la base para que los LLMs generen insights valiosos y precisos.

---

**Fecha de creación**: 2026-01-11
**Última actualización**: 2026-01-11
**Estado**: 🟡 Listo para comenzar

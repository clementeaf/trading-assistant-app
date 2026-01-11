# Optimizaciones de Performance

## Objetivo

Todos los endpoints deben responder en **< 1.5 segundos** bajo condiciones normales.

## Ejecutar Tests de Performance

```bash
cd backend
python -m pytest tests/performance/test_performance.py -v -s
```

## Optimizaciones Implementadas

### 1. **Reducción de Llamadas a APIs Externas**

**Problema**: Cada endpoint hace múltiples llamadas a APIs externas (TradingEconomics, Twelve Data, etc.).

**Soluciones Implementadas**:
- Uso de providers con rate limiting interno
- Lazy loading de datos (solo se obtienen cuando son necesarios)

**Optimizaciones Pendientes**:
- [ ] Implementar caching de responses de APIs externas (Redis o in-memory con TTL)
- [ ] Batch requests cuando sea posible
- [ ] Usar async/await de forma consistente en todos los providers

### 2. **Cálculos Costosos**

**Problema**: Algunos cálculos son computacionalmente costosos (correlaciones, ATR, RSI).

**Soluciones Implementadas**:
- Cálculo de correlación optimizado con NumPy/SciPy
- ATR calculado solo cuando es necesario (por sesión)
- Detección de niveles psicológicos optimizada con búsqueda binaria

**Optimizaciones Pendientes**:
- [ ] Cachear cálculos técnicos (RSI, EMAs) por timeframe
- [ ] Pre-calcular niveles psicológicos comunes (múltiplos de 50/100)
- [ ] Usar vectorización (NumPy) en lugar de loops cuando sea posible

### 3. **Queries a Base de Datos**

**Problema**: Múltiples queries secuenciales a la base de datos.

**Optimizaciones Pendientes**:
- [ ] Eager loading de relaciones con `joinedload` o `selectinload`
- [ ] Índices en columnas frecuentemente consultadas (timestamp, instrument, importance)
- [ ] Usar `bulk_save` para inserts masivos
- [ ] Connection pooling configurado (ya está con SQLAlchemy)

### 4. **Serialización de Respuestas**

**Problema**: Pydantic serializa objetos complejos que pueden ser lentos.

**Soluciones Implementadas**:
- Uso de `model_dump()` en lugar de `dict()`
- Modelos Pydantic bien tipados

**Optimizaciones Pendientes**:
- [ ] Usar `orjson` en lugar de `json` estándar (más rápido)
- [ ] `response_model_exclude_unset=True` para no enviar campos None innecesarios

### 5. **Paralelización**

**Problema**: Muchas operaciones son independientes pero se ejecutan secuencialmente.

**Optimizaciones Pendientes**:
- [ ] Usar `asyncio.gather()` para ejecutar llamadas independientes en paralelo:
  - Obtener datos de mercado + calendario económico simultáneamente
  - Calcular análisis técnico de múltiples timeframes en paralelo
- [ ] Implementar background tasks para operaciones no críticas

## Ejemplo de Optimización con Asyncio.gather()

**Antes (secuencial)**:
```python
async def analyze(self, instrument: str):
    market_data = await self.get_market_data(instrument)
    calendar = await self.get_calendar()
    alignment = await self.get_alignment()
    
    # Total time = suma de todos los tiempos
```

**Después (paralelo)**:
```python
async def analyze(self, instrument: str):
    # Ejecutar en paralelo
    market_data, calendar, alignment = await asyncio.gather(
        self.get_market_data(instrument),
        self.get_calendar(),
        self.get_alignment()
    )
    
    # Total time = max(tiempos individuales) ← Mucho más rápido
```

## Estrategia de Caching Recomendada

### Redis Cache (Producción)

```python
from redis import asyncio as aioredis
from functools import wraps
import json

redis_client = aioredis.from_url("redis://localhost")

def cached(ttl_seconds: int = 300):
    """Decorator para cachear resultados de funciones async"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Intentar obtener del cache
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Si no está en cache, calcular
            result = await func(*args, **kwargs)
            
            # Guardar en cache
            await redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# Uso:
@cached(ttl_seconds=300)  # Cache por 5 minutos
async def get_high_impact_news_today(self, currency: str = "USD"):
    # ... lógica costosa ...
    return result
```

### In-Memory Cache (Desarrollo)

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache simple para datos que cambian poco
@lru_cache(maxsize=100)
def get_psychological_levels(instrument: str, price: float) -> list:
    # Redondear precio para mejorar cache hits
    rounded_price = round(price, -1)  # Redondear a decenas
    # ... calcular niveles ...
    return levels

# Cache con TTL manual
class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

# Uso global
calendar_cache = TTLCache(ttl_seconds=300)

async def get_event_schedule_today(self, currency: str = "USD"):
    cache_key = f"schedule_{currency}_{datetime.now().date()}"
    cached = calendar_cache.get(cache_key)
    if cached:
        return cached
    
    # Obtener datos
    result = await self._fetch_events(currency)
    calendar_cache.set(cache_key, result)
    return result
```

## Monitoreo de Performance

### 1. Logging de Tiempos

Agrega decoradores para medir tiempos automáticamente:

```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_performance(func):
    """Decorator para loggear tiempos de ejecución"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        logger.info(f"{func.__name__} took {duration:.3f}s")
        
        if duration > 1.0:
            logger.warning(f"SLOW: {func.__name__} took {duration:.3f}s")
        
        return result
    return wrapper

# Uso:
@log_performance
async def get_trading_recommendation(self, instrument: str):
    # ... lógica ...
    return recommendation
```

### 2. Métricas con Prometheus (Opcional)

```python
from prometheus_client import Counter, Histogram

# Métricas
request_duration = Histogram(
    'endpoint_duration_seconds',
    'Duration of endpoint requests',
    ['endpoint']
)

request_count = Counter(
    'endpoint_requests_total',
    'Total endpoint requests',
    ['endpoint', 'status']
)

# Middleware FastAPI
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    endpoint = request.url.path
    request_duration.labels(endpoint=endpoint).observe(duration)
    request_count.labels(endpoint=endpoint, status=response.status_code).inc()
    
    return response
```

## Benchmarks Target

| Endpoint | Target | Actual (sin optimizar) | Actual (optimizado) |
|----------|--------|------------------------|---------------------|
| `/high-impact-news` | < 1.0s | ~2.0s | TBD |
| `/event-schedule` | < 1.0s | ~2.5s | TBD |
| `/yesterday-analysis` | < 1.5s | ~3.0s | TBD |
| `/dxy-bond-alignment` | < 1.5s | ~3.5s | TBD |
| `/trading-mode` | < 1.5s | ~4.0s | TBD |
| `/trading-recommendation` | < 1.5s | ~5.0s | TBD |
| `/technical-analysis` | < 1.5s | ~4.5s | TBD |
| `/psychological-levels` | < 1.0s | ~2.0s | TBD |

## Plan de Acción para Optimización

### Prioridad Alta (Impacto Inmediato)
1. ✅ Implementar tests de performance (Fase 2.5 - Tarea 6)
2. ⏳ Agregar caching in-memory con TTL para calendarios y niveles psicológicos
3. ⏳ Paralelizar llamadas independientes con `asyncio.gather()`
4. ⏳ Optimizar queries a base de datos (índices + eager loading)

### Prioridad Media (Mejoras Incrementales)
5. ⏳ Usar `orjson` para serialización más rápida
6. ⏳ Implementar connection pooling para APIs externas
7. ⏳ Agregar logging de performance con thresholds

### Prioridad Baja (Refinamiento)
8. ⏳ Redis cache para producción
9. ⏳ Métricas con Prometheus
10. ⏳ Load testing con Locust o K6

## Ejecución de Performance Tests

```bash
# Test básico
pytest tests/performance/test_performance.py -v

# Con output detallado
pytest tests/performance/test_performance.py -v -s

# Solo tests que fallan (>1.5s)
pytest tests/performance/test_performance.py -v -x

# Generar reporte HTML
pytest tests/performance/test_performance.py --html=performance_report.html --self-contained-html
```

## Próximos Pasos

1. **Ejecutar baseline de performance**: Correr los tests actuales para obtener métricas base
2. **Identificar bottlenecks**: Usar `cProfile` o `py-spy` para identificar funciones lentas
3. **Aplicar optimizaciones**: Implementar las optimizaciones priorizadas
4. **Re-benchmarkear**: Validar que las optimizaciones funcionan
5. **Iterar**: Repetir hasta que todos los endpoints estén < 1.5s

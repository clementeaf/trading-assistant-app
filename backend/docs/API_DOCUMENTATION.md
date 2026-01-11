# Trading Assistant API - Documentación Completa

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Autenticación](#autenticación)
3. [Endpoints](#endpoints)
4. [Modelos de Datos](#modelos-de-datos)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Errores Comunes](#errores-comunes)
7. [Rate Limiting](#rate-limiting)

---

## Visión General

**Base URL**: `http://localhost:8000` (desarrollo) | `https://api.tradingassistant.com` (producción)

**Versión**: 2.5.0

**Formato**: JSON

**Documentación Interactiva**:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

### Filosofía de la API

Esta API proporciona **análisis probabilístico** para trading de XAU/USD (Gold). No proporciona "señales" ni "consejos financieros", sino que ofrece:

1. **Contexto de Mercado**: ¿Qué está pasando? (noticias, alineación macro)
2. **Análisis Histórico**: ¿Qué ha pasado? (sesiones de ayer, reacciones en niveles)
3. **Probabilidades**: ¿Qué podría pasar? (modo de trading, proyecciones)
4. **Niveles Operativos**: ¿Dónde actuar? (soportes, resistencias, stops)

---

## Autenticación

**Actualmente no requiere autenticación** (API pública en desarrollo).

Para producción, se recomienda implementar:
- API Keys en headers (`X-API-Key`)
- OAuth 2.0 para acceso de usuarios
- Rate limiting por IP/key

---

## Endpoints

### 1. High Impact News

**GET** `/api/market-briefing/high-impact-news`

Obtiene noticias económicas de alto impacto del día actual relevantes para XAU/USD.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `currency` | string | No | USD | Código ISO 4217 (3 letras) |
| `include_geopolitical_risk` | boolean | No | true | Incluir análisis de riesgo geopolítico |

**Response 200**:
```json
{
  "has_high_impact_news": true,
  "count": 2,
  "events": [
    {
      "title": "Non-Farm Payrolls",
      "time": "08:30",
      "country": "United States",
      "importance": "HIGH",
      "currency": "USD",
      "forecast": "200K",
      "previous": "195K"
    }
  ],
  "summary": "2 high impact USD events today: NFP (08:30), FOMC (14:00)",
  "instrument": "XAUUSD",
  "geopolitical_risk": {
    "level": "MEDIUM",
    "score": 0.55,
    "explanation": "Moderate geopolitical tensions detected (2 keywords, Middle East region boost)",
    "keywords_detected": ["tensions", "conflict"]
  }
}
```

**Use Cases**:
- Decidir si operar hoy o no
- Planificar horarios de trading evitando noticias
- Evaluar riesgo geopolítico adicional

---

### 2. Event Schedule

**GET** `/api/market-briefing/event-schedule`

Calendario detallado de eventos económicos con múltiples zonas horarias y estimación de impacto en Gold.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `currency` | string | No | USD | Código ISO 4217 (3 letras) |
| `include_gold_impact` | boolean | No | true | Incluir estimación de impacto en Gold |

**Response 200**:
```json
{
  "total_events": 3,
  "usd_events_count": 2,
  "events": [
    {
      "time": "08:30",
      "title": "Non-Farm Payrolls",
      "importance": "HIGH",
      "affects_usd": true,
      "timezones": {
        "UTC": "13:30",
        "America/New_York": "08:30",
        "Europe/London": "13:30",
        "Asia/Tokyo": "22:30"
      },
      "formatted_time": "08:30 ET | 13:30 UTC | 22:30 JST",
      "gold_impact": {
        "probability": 0.85,
        "direction": "HIGH_VOLATILITY",
        "magnitude_percent": 1.5,
        "explanation": "NFP typically causes high volatility in Gold (85% probability)"
      }
    }
  ],
  "summary": "2 USD events today, 1 high volatility expected"
}
```

**Use Cases**:
- Planificar trading session considerando horarios en tu zona
- Estimar cuánto puede moverse Gold en cada noticia
- Evitar trades justo antes de NFP

---

### 3. Yesterday Analysis

**GET** `/api/market-briefing/yesterday-analysis`

Análisis detallado del día anterior por sesiones de trading (Asia, Londres, NY) con volatilidad y breaks psicológicos.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `instrument` | string | Yes | - | Símbolo (ej: XAUUSD) |

**Response 200**:
```json
{
  "instrument": "XAUUSD",
  "date": "2026-01-10",
  "close_price": 4510.50,
  "change_percent": 1.25,
  "range_high": 4525.00,
  "range_low": 4490.00,
  "sessions": [
    {
      "session_name": "Asia",
      "time_range": "00:00-08:00 UTC",
      "price_action": "Consolidation around 4500",
      "volatility": "LOW",
      "psychological_breaks": []
    },
    {
      "session_name": "London",
      "time_range": "08:00-16:00 UTC",
      "price_action": "Breakout above 4500 with strong volume",
      "volatility": "MEDIUM",
      "psychological_breaks": [
        {
          "level": 4500,
          "type": "BREAK_UP",
          "time": "10:30",
          "confirmation": true
        }
      ]
    },
    {
      "session_name": "New York",
      "time_range": "13:00-21:00 UTC",
      "price_action": "Continuation rally to 4525",
      "volatility": "HIGH",
      "psychological_breaks": []
    }
  ],
  "summary": "Strong bullish day (+1.25%) with breakout above 4500 during London session. High volatility in NY."
}
```

**Use Cases**:
- Entender qué sesión fue más activa (dónde se generó el movimiento)
- Identificar breaks de niveles importantes
- Evaluar si la volatilidad fue normal o extrema

---

### 4. DXY-Bond Alignment

**GET** `/api/market-briefing/dxy-bond-alignment`

Analiza la alineación entre DXY (índice dólar) y rendimientos de bonos, con correlación Gold-DXY y proyección de impacto.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `bond` | string | No | US10Y | Bono a analizar (US02Y, US10Y, US30Y) |
| `include_gold_correlation` | boolean | No | true | Incluir correlación Gold-DXY |
| `gold_symbol` | string | No | XAUUSD | Símbolo de Gold |
| `correlation_days` | integer | No | 30 | Días para calcular correlación (7-90) |

**Response 200**:
```json
{
  "dxy_symbol": "DXY",
  "bond_symbol": "US10Y",
  "dxy_change_percent": 0.50,
  "bond_change_percent": 2.0,
  "alignment": "ALIGNED",
  "market_bias": "RISK_OFF",
  "explanation": "DXY and US10Y both rising → Risk-off sentiment → Favorable for Gold as safe haven",
  "gold_dxy_correlation": {
    "coefficient": -0.78,
    "strength": "STRONG",
    "p_value": 0.001,
    "is_significant": true,
    "days_analyzed": 30,
    "explanation": "Strong negative correlation (-0.78) between Gold and DXY over last 30 days"
  },
  "gold_impact_projection": {
    "dxy_change_percent": 0.50,
    "expected_gold_change_percent": -0.39,
    "direction": "NEGATIVE",
    "explanation": "DXY +0.5% → Gold -0.39% (range: -0.48% to -0.28%)",
    "magnitude_range_percent": {
      "min": -0.48,
      "max": -0.28
    },
    "magnitude_range_points": {
      "min": -21.6,
      "max": -12.6
    }
  }
}
```

**Use Cases**:
- Entender el sesgo macro actual (risk-on vs risk-off)
- Estimar cuánto puede moverse Gold si DXY sube/baja
- Validar setup técnico con contexto fundamental

---

### 5. Trading Mode

**GET** `/api/market-briefing/trading-mode`

Recomienda un modo de trading (CALM, AGGRESSIVE, OBSERVE) con niveles operativos específicos según el modo.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `instrument` | string | No | XAUUSD | Instrumento a analizar |
| `bond` | string | No | US10Y | Bono para análisis de alineación |
| `time_window_minutes` | integer | No | 120 | Ventana para noticias próximas (30-360) |

**Response 200**:
```json
{
  "mode": "CALM",
  "confidence": 0.72,
  "reasoning": "Moderate volatility, no immediate high-impact news (next in 180min), market in consolidation. Trade at key levels only.",
  "factors": {
    "high_impact_news_soon": false,
    "volatility_level": "MEDIUM",
    "market_alignment": "ALIGNED",
    "time_until_news_minutes": 180
  },
  "operational_levels": [
    {
      "level": 4500.0,
      "type": "SUPPORT",
      "distance_points": 8.75,
      "distance_percentage": 0.19,
      "strength": "STRONG",
      "action": "BUY",
      "explanation": "Major 100-level support, 8.75 points away (0.19%). Consider buy limit orders."
    },
    {
      "level": 4550.0,
      "type": "RESISTANCE",
      "distance_points": 41.25,
      "distance_percentage": 0.92,
      "strength": "STRONG",
      "action": "SELL",
      "explanation": "Major 50-level resistance, 41.25 points away (0.92%). Consider sell limit orders."
    }
  ]
}
```

**Use Cases**:
- Decidir si operar agresivamente o esperar
- Obtener niveles de entrada específicos según modo
- Ajustar tamaño de posición según confianza

**Modos Explicados**:
- `CALM`: Operar solo en niveles clave, stops más ajustados
- `AGGRESSIVE`: Aprovechar momentum, stops más amplios
- `OBSERVE`: No operar, esperar claridad (NFP en 30min, conflicto macro)

---

### 6. Trading Recommendation

**GET** `/api/market-briefing/trading-recommendation`

Genera una recomendación operativa completa (BUY/SELL/WAIT) con niveles, disclaimer y R:R detallado.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `instrument` | string | No | XAUUSD | Instrumento a analizar |
| `bond` | string | No | US10Y | Bono para análisis |
| `time_window_minutes` | integer | No | 120 | Ventana para noticias (30-360) |

**Response 200**:
```json
{
  "disclaimer": "⚠️ ANÁLISIS PROBABILÍSTICO - NO ES CONSEJO FINANCIERO ⚠️\n\nEste análisis se basa en probabilidades históricas y patrones técnicos. NO es una recomendación de inversión personalizada. Opera bajo tu propio riesgo y gestión de capital. Consulta con un asesor financiero certificado antes de tomar decisiones de inversión.",
  "direction": "BUY",
  "confidence": 0.68,
  "entry_price": 4505.0,
  "stop_loss": 4485.0,
  "take_profit": 4545.0,
  "justification": "Bullish market bias (DXY-Bonds aligned risk-off), technical support at 4500 (strong psychological level with 12 bounces), no immediate high-impact news. Mode: CALM.",
  "risk_reward_details": {
    "risk_points": 20.0,
    "reward_points": 40.0,
    "risk_percent": 0.44,
    "reward_percent": 0.89,
    "min_ratio_met": true,
    "explanation": "Risk: 20 pts (0.44%) | Reward: 40 pts (0.89%) | Ratio 1:2.00 ✅"
  },
  "confidence_breakdown": {
    "technical_analysis": 0.70,
    "market_context": 0.65,
    "news_impact": 0.70,
    "overall": 0.68
  },
  "invalidation_level": 4480.0
}
```

**Use Cases**:
- Obtener setup completo con entrada, SL, TP
- Validar que el R:R cumple tu criterio mínimo (ej: 1:2)
- Entender por qué se sugiere cada dirección

**Importante**:
- Si `direction` es `WAIT`, no hay niveles de entrada/SL/TP (serán null)
- `risk_reward_details.min_ratio_met` indica si cumple ratio mínimo 1:2
- `confidence` < 0.5 → baja confianza, considerar esperar

---

### 7. Technical Analysis

**GET** `/api/market-briefing/technical-analysis`

Análisis técnico multi-timeframe (Daily, H4, H1) con tendencia, RSI, EMAs y estructura.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `instrument` | string | No | XAUUSD | Instrumento a analizar |

**Response 200**:
```json
{
  "instrument": "XAUUSD",
  "analysis_date": "2026-01-11",
  "daily": {
    "trend": "BULLISH",
    "trend_strength": "STRONG",
    "rsi_14": 62.5,
    "ema_50": 4480.0,
    "ema_200": 4450.0,
    "structure": "HIGHER_HIGHS",
    "current_price": 4508.75,
    "summary": "Strong uptrend, price above EMAs, RSI overbought but not extreme"
  },
  "h4": {
    "trend": "BULLISH",
    "trend_strength": "MODERATE",
    "rsi_14": 58.3,
    "ema_50": 4495.0,
    "ema_200": 4470.0,
    "structure": "CONSOLIDATION",
    "current_price": 4508.75,
    "summary": "Bullish but consolidating, waiting for breakout above 4520"
  },
  "h1": {
    "trend": "NEUTRAL",
    "trend_strength": "WEAK",
    "rsi_14": 51.2,
    "ema_50": 4505.0,
    "ema_200": 4500.0,
    "structure": "RANGE",
    "current_price": 4508.75,
    "summary": "Tight range between 4500-4515, no clear direction"
  },
  "summary": "Multi-timeframe bullish bias. Daily trend intact, H4 consolidating, H1 neutral. Watch for H4 breakout."
}
```

**Use Cases**:
- Confirmar dirección en múltiples timeframes
- Identificar divergencias (ej: daily alcista, H1 bajista)
- Evaluar fuerza de tendencia con RSI y EMAs

---

### 8. Psychological Levels

**GET** `/api/market-briefing/psychological-levels`

Detección de niveles psicológicos (100s y 50s) con histórico detallado de reacciones.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `instrument` | string | No | XAUUSD | Instrumento a analizar |
| `lookback_days` | integer | No | 30 | Días históricos (7-90) |
| `max_distance_points` | float | No | 100.0 | Distancia máxima (20-500) |

**Response 200**:
```json
{
  "instrument": "XAUUSD",
  "current_price": 4508.75,
  "analysis_datetime": "2026-01-11T15:30:00Z",
  "lookback_days": 30,
  "max_distance_points": 100.0,
  "levels": [
    {
      "level": 4500.0,
      "distance_from_current": 8.75,
      "strength": "STRONG",
      "reaction_count": 12,
      "type": "SUPPORT",
      "bounce_count": 10,
      "break_count": 2,
      "is_round_hundred": true,
      "is_round_fifty": false,
      "reaction_history": [
        {
          "timestamp": "2026-01-10T14:30:00Z",
          "session": "NEW_YORK",
          "volatility": "HIGH",
          "magnitude_points": 15.5,
          "magnitude_percent": 0.34,
          "confirmation": true,
          "explanation": "Strong bounce during NY session with high volatility. Price rejected 4500 and rallied +15.5 pts."
        },
        {
          "timestamp": "2026-01-09T10:15:00Z",
          "session": "LONDON",
          "volatility": "MEDIUM",
          "magnitude_points": 8.2,
          "magnitude_percent": 0.18,
          "confirmation": true,
          "explanation": "Confirmed bounce during London session. Moderate move +8.2 pts from 4500."
        }
      ]
    },
    {
      "level": 4550.0,
      "distance_from_current": 41.25,
      "strength": "MODERATE",
      "reaction_count": 8,
      "type": "RESISTANCE",
      "bounce_count": 6,
      "break_count": 2,
      "is_round_hundred": false,
      "is_round_fifty": true,
      "reaction_history": [
        {
          "timestamp": "2026-01-08T16:00:00Z",
          "session": "NEW_YORK",
          "volatility": "MEDIUM",
          "magnitude_points": 12.0,
          "magnitude_percent": 0.26,
          "confirmation": false,
          "explanation": "Rejection at 4550 resistance during NY close. Unconfirmed, needs follow-through."
        }
      ]
    }
  ],
  "strongest_support": 4500.0,
  "strongest_resistance": 4550.0,
  "nearest_support": 4500.0,
  "nearest_resistance": 4550.0,
  "summary": "Strong support at 4500 (10 bounces in 30 days). Next resistance at 4550. Price in middle of range."
}
```

**Use Cases**:
- Identificar niveles clave para entradas/salidas
- Evaluar probabilidad de rebote/ruptura según histórico
- Planificar stops ligeramente por debajo/encima de niveles fuertes

**Interpretación de `reaction_history`**:
- `confirmation: true` → El rebote/rechazo fue seguido de continuación (más fiable)
- `volatility: HIGH` → Reacción fuerte, nivel respetado con convicción
- `session: NEW_YORK` → Considerar la sesión para timing de trades

---

## Modelos de Datos

### GeopoliticalRisk

```python
{
  "level": str,  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  "score": float,  # 0.0 - 1.0
  "explanation": str,
  "keywords_detected": List[str]  # Optional
}
```

### GoldImpactEstimate

```python
{
  "probability": float,  # 0.0 - 1.0
  "direction": str,  # "POSITIVE" | "NEGATIVE" | "HIGH_VOLATILITY" | "INVERSE_USD" | "UNKNOWN"
  "magnitude_percent": float,
  "explanation": str
}
```

### CorrelationResult

```python
{
  "coefficient": float,  # -1.0 - 1.0
  "strength": str,  # "VERY_WEAK" | "WEAK" | "MODERATE" | "STRONG" | "VERY_STRONG"
  "p_value": float,
  "is_significant": bool,
  "days_analyzed": int,
  "explanation": str
}
```

### ImpactProjection

```python
{
  "dxy_change_percent": float,
  "expected_gold_change_percent": float,
  "direction": str,  # "POSITIVE" | "NEGATIVE" | "NEUTRAL"
  "explanation": str,
  "magnitude_range_percent": {
    "min": float,
    "max": float
  },
  "magnitude_range_points": {
    "min": float,
    "max": float
  }
}
```

### RiskRewardDetails

```python
{
  "risk_points": float,
  "reward_points": float,
  "risk_percent": float,
  "reward_percent": float,
  "min_ratio_met": bool,
  "explanation": str
}
```

### OperationalLevel

```python
{
  "level": float,
  "type": str,  # "SUPPORT" | "RESISTANCE" | "BOTH"
  "distance_points": float,
  "distance_percentage": float,
  "strength": str,  # "WEAK" | "MODERATE" | "STRONG"
  "action": str,  # "BUY" | "SELL" | "WATCH"
  "explanation": str
}
```

### LevelReaction

```python
{
  "timestamp": str,  # ISO 8601
  "session": str,  # "ASIA" | "LONDON" | "NEW_YORK" | "OVERLAP"
  "volatility": str,  # "LOW" | "MEDIUM" | "HIGH"
  "magnitude_points": float,
  "magnitude_percent": float,
  "confirmation": bool,
  "explanation": str
}
```

---

## Ejemplos de Uso

### Workflow Completo para Decidir un Trade

```bash
# Paso 1: Revisar si hay noticias importantes hoy
curl http://localhost:8000/api/market-briefing/high-impact-news | jq '.count'
# Si count > 0 → Revisar horarios y planificar

# Paso 2: Analizar contexto macro (DXY-Bonds)
curl 'http://localhost:8000/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true' | jq '.market_bias'
# Si "RISK_OFF" → Favorece Gold

# Paso 3: Obtener modo de trading recomendado
curl 'http://localhost:8000/api/market-briefing/trading-mode' | jq '.mode, .operational_levels'
# Si "CALM" → Operar solo en niveles clave

# Paso 4: Identificar niveles psicológicos cercanos
curl 'http://localhost:8000/api/market-briefing/psychological-levels' | jq '.nearest_support, .nearest_resistance'
# Planificar entrada en soporte, salida en resistencia

# Paso 5: Obtener recomendación completa
curl 'http://localhost:8000/api/market-briefing/trading-recommendation' | jq '.direction, .entry_price, .stop_loss, .take_profit'
# Validar con tu propio análisis
```

### Monitoreo Pre-Market

```python
import requests

def pre_market_check():
    base_url = "http://localhost:8000/api/market-briefing"
    
    # ¿Hay noticias importantes?
    news = requests.get(f"{base_url}/high-impact-news").json()
    if news["count"] > 0:
        print(f"⚠️ {news['count']} high impact news today")
        for event in news["events"]:
            print(f"  - {event['time']}: {event['title']}")
    
    # ¿Cómo cerró ayer?
    yesterday = requests.get(f"{base_url}/yesterday-analysis?instrument=XAUUSD").json()
    print(f"\n📊 Yesterday: {yesterday['change_percent']:+.2f}% (Close: {yesterday['close_price']})")
    
    # ¿Cuál es el sesgo macro?
    alignment = requests.get(f"{base_url}/dxy-bond-alignment?include_gold_correlation=true").json()
    print(f"🌍 Macro: {alignment['market_bias']} (Gold-DXY corr: {alignment['gold_dxy_correlation']['coefficient']:.2f})")
    
    # ¿Qué modo de trading?
    mode = requests.get(f"{base_url}/trading-mode").json()
    print(f"🎯 Mode: {mode['mode']} (confidence: {mode['confidence']:.0%})")
    
    # Niveles clave
    levels = requests.get(f"{base_url}/psychological-levels").json()
    print(f"📍 Nearest Support: {levels['nearest_support']} | Resistance: {levels['nearest_resistance']}")

if __name__ == "__main__":
    pre_market_check()
```

---

## Errores Comunes

### 400 Bad Request

**Causa**: Parámetros inválidos

```json
{
  "detail": "Invalid currency: INVALID. Must be 3-letter ISO 4217 code (e.g. USD, EUR, GBP)"
}
```

**Solución**: Verificar formato de parámetros según documentación.

### 422 Validation Error

**Causa**: Parámetro fuera de rango

```json
{
  "detail": [
    {
      "loc": ["query", "lookback_days"],
      "msg": "ensure this value is less than or equal to 90",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Solución**: Respetar rangos permitidos (ej: `lookback_days` 7-90).

### 500 Internal Server Error

**Causa**: Error del servidor (API externa caída, falta de API key)

```json
{
  "detail": "Error interno al obtener noticias de alto impacto para XAUUSD"
}
```

**Solución**: Revisar logs del servidor. En desarrollo, verificar que las API keys estén configuradas en `.env`.

---

## Rate Limiting

**Actualmente no implementado** (desarrollo).

Para producción, se recomienda:
- **100 requests/minuto** por IP/key
- **1,000 requests/hora** por IP/key
- Headers de respuesta: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

Cuando se implemente, exceder el límite retornará:

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Versiones de la API

| Versión | Fecha | Cambios Principales |
|---------|-------|---------------------|
| 2.5.0 | 2026-01 | Fase 2.5: Disclaimer reforzado, niveles operativos, histórico reacciones, rango magnitud |
| 2.0.0 | 2025-12 | Fase 2: Timezones, correlación Gold-DXY, impacto Gold, riesgo geopolítico |
| 1.0.0 | 2025-11 | Fase 1: Volatilidad por sesión, breaks psicológicos, detección retests |

---

## Contacto y Soporte

- **Documentación E2E**: `/docs/TESTS_E2E.md`
- **Performance**: `/docs/PERFORMANCE_OPTIMIZATION.md`
- **Roadmap**: `/MEJORAS_SISTEMA.md`
- **Issues**: GitHub Issues
- **Email**: support@example.com

---

**Disclaimer Final**: Esta API proporciona análisis probabilístico basado en datos históricos y patrones técnicos. NO es consejo financiero personalizado. Opera bajo tu propio riesgo y gestión de capital.

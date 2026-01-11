# Tests E2E - Guía de Ejecución Manual

## Resumen

Los tests End-to-End (E2E) validan que todos los endpoints de la API funcionan correctamente en un entorno real con datos reales.

## Prerrequisitos

1. **API Keys Configuradas**: Asegúrate de tener configuradas las siguientes API keys en tu `.env`:
   ```bash
   ECONOMIC_CALENDAR_API_KEY=<tu_key_de_tradingeconomics>
   TWELVE_DATA_API_KEY=<tu_key_de_twelve_data>
   ALPHA_VANTAGE_API_KEY=<tu_key_de_alpha_vantage>
   FRED_API_KEY=<tu_key_de_fred>
   ```

2. **Servidor en Ejecución**: El backend debe estar corriendo:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Mercados Abiertos** (Opcional para datos reales): Los tests funcionan mejor durante horario de mercado cuando hay datos frescos.

## Tests E2E por Endpoint

### 1. High Impact News

**Endpoint**: `GET /api/market-briefing/high-impact-news`

**Qué valida**:
- ✅ Respuesta 200
- ✅ Estructura de respuesta correcta
- ✅ Campo `geopolitical_risk` incluido (Fase 2)
- ✅ Eventos de alto impacto filtrados correctamente

**Test manual**:
```bash
curl http://localhost:8000/api/market-briefing/high-impact-news | jq
```

**Validar**:
- `has_high_impact_news`: bool
- `count`: número ≥ 0
- `events`: array de eventos
- `geopolitical_risk`: objeto con `level`, `score`, `explanation`

---

### 2. Event Schedule

**Endpoint**: `GET /api/market-briefing/event-schedule?include_gold_impact=true`

**Qué valida**:
- ✅ Múltiples zonas horarias (Fase 2 - Mejora 1)
- ✅ Estimación de impacto en Gold (Fase 2 - Mejora 3)
- ✅ Calendario formateado correctamente

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/event-schedule?include_gold_impact=true" | jq
```

**Validar**:
- Cada evento tiene `timezones`: dict con al menos UTC y America/New_York
- Cada evento tiene `gold_impact`: objeto con `probability`, `direction`, `magnitude_percent`
- `summary`: string descriptivo

---

### 3. Yesterday Analysis

**Endpoint**: `GET /api/market-briefing/yesterday-analysis?instrument=XAUUSD`

**Qué valida**:
- ✅ Análisis por sesión (Asia, Londres, NY)
- ✅ Volatilidad por sesión (Fase 1 - Mejora 1)
- ✅ Breaks psicológicos por sesión (Fase 1 - Mejora 1)

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/yesterday-analysis?instrument=XAUUSD" | jq
```

**Validar**:
- `sessions`: array con 3 sesiones
- Cada sesión tiene `volatility`: string ("LOW", "MEDIUM", "HIGH")
- Cada sesión tiene `psychological_breaks`: array (puede estar vacío)
- Si hay breaks, cada uno tiene `level`, `type`, `time`

---

### 4. DXY-Bond Alignment

**Endpoint**: `GET /api/market-briefing/dxy-bond-alignment?include_gold_correlation=true&correlation_days=30`

**Qué valida**:
- ✅ Correlación Gold-DXY (Fase 2 - Mejora 2)
- ✅ Proyección de impacto en Gold (Fase 2 - Mejora 2)
- ✅ **Rango de magnitud** (Fase 2.5 - Mejora 4) ← **NUEVO**

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true" | jq
```

**Validar**:
- `gold_dxy_correlation`: objeto con:
  - `coefficient`: float entre -1 y 1
  - `strength`: string ("VERY_WEAK", "WEAK", "MODERATE", "STRONG", "VERY_STRONG")
  - `is_significant`: bool
- `gold_impact_projection`: objeto con:
  - `expected_gold_change_percent`: float
  - `magnitude_range_percent`: dict con `min` y `max` ← **NUEVO EN FASE 2.5**
  - `magnitude_range_points`: dict con `min` y `max` ← **NUEVO EN FASE 2.5**

**Ejemplo de respuesta esperada** (Mejora 4):
```json
{
  "gold_impact_projection": {
    "dxy_change_percent": 0.5,
    "expected_gold_change_percent": -0.38,
    "direction": "NEGATIVE",
    "magnitude_range_percent": {
      "min": -0.48,
      "max": -0.28
    },
    "magnitude_range_points": {
      "min": -21.6,
      "max": -12.6
    },
    "explanation": "DXY +0.5% → Gold -0.38% (rango: -0.48% a -0.28%)"
  }
}
```

---

### 5. Trading Mode

**Endpoint**: `GET /api/market-briefing/trading-mode?instrument=XAUUSD`

**Qué valida**:
- ✅ Modo de trading recomendado (CALM, AGGRESSIVE, OBSERVE)
- ✅ **Niveles operativos** según modo (Fase 2.5 - Mejora 2) ← **NUEVO**

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/trading-mode?instrument=XAUUSD" | jq
```

**Validar**:
- `mode`: string ("CALM", "AGGRESSIVE", "OBSERVE")
- `confidence`: float entre 0 y 1
- `operational_levels`: array de niveles ← **NUEVO EN FASE 2.5**
  - Cada nivel tiene:
    - `level`: float (ej: 4500.0)
    - `type`: string ("SUPPORT", "RESISTANCE", "BOTH")
    - `distance_points`: float
    - `distance_percentage`: float
    - `strength`: string
    - `action`: string ("BUY", "SELL", "WATCH")
    - `explanation`: string

**Ejemplo de respuesta esperada** (Mejora 2):
```json
{
  "mode": "CALM",
  "operational_levels": [
    {
      "level": 4500.0,
      "type": "SUPPORT",
      "distance_points": 8.75,
      "distance_percentage": 0.19,
      "strength": "STRONG",
      "action": "BUY",
      "explanation": "Major 100-level support, 8.75 points away (0.19%)"
    }
  ]
}
```

---

### 6. Trading Recommendation

**Endpoint**: `GET /api/market-briefing/trading-recommendation?instrument=XAUUSD`

**Qué valida**:
- ✅ **Disclaimer prominente** (Fase 2.5 - Mejora 1) ← **NUEVO**
- ✅ **Risk/Reward Details** detallados (Fase 2.5 - Mejora 1) ← **NUEVO**
- ✅ Niveles de entrada, SL, TP
- ✅ Confidence breakdown

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/trading-recommendation?instrument=XAUUSD" | jq
```

**Validar**:
- `disclaimer`: string largo (>100 caracteres) mencionando "riesgo" y "probabilidad" ← **NUEVO EN FASE 2.5**
- `risk_reward_details`: objeto con: ← **NUEVO EN FASE 2.5**
  - `risk_points`: float
  - `reward_points`: float
  - `risk_percent`: float
  - `reward_percent`: float
  - `min_ratio_met`: bool
  - `explanation`: string (ej: "Risk: 20 pts (0.44%) | Reward: 40 pts (0.89%) | Ratio 1:2.00 ✅")
- `direction`: string ("BUY", "SELL", "WAIT")
- `confidence_breakdown`: objeto con `technical_analysis`, `market_context`, `news_impact`, `overall`

**Ejemplo de respuesta esperada** (Mejora 1):
```json
{
  "disclaimer": "⚠️ ANÁLISIS PROBABILÍSTICO - NO ES CONSEJO FINANCIERO ⚠️\n\nEste análisis se basa en probabilidades históricas y patrones técnicos, NO es una recomendación de inversión...",
  "risk_reward_details": {
    "risk_points": 20.0,
    "reward_points": 40.0,
    "risk_percent": 0.44,
    "reward_percent": 0.89,
    "min_ratio_met": true,
    "explanation": "Risk: 20 pts (0.44%) | Reward: 40 pts (0.89%) | Ratio 1:2.00 ✅"
  },
  "direction": "BUY",
  "confidence": 0.68
}
```

---

### 7. Technical Analysis

**Endpoint**: `GET /api/market-briefing/technical-analysis?instrument=XAUUSD`

**Qué valida**:
- ✅ Análisis multi-temporalidad (Daily, H4, H1)
- ✅ Indicadores técnicos (RSI, EMAs)
- ✅ Detección de retests (Fase 1 - Mejora 2)

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/technical-analysis?instrument=XAUUSD" | jq
```

**Validar**:
- Respuesta tiene estructura multi-timeframe
- Al menos un timeframe presente
- Cada timeframe tiene indicadores básicos

---

### 8. Psychological Levels

**Endpoint**: `GET /api/market-briefing/psychological-levels?instrument=XAUUSD&lookback_days=30`

**Qué valida**:
- ✅ Niveles psicológicos (100s y 50s)
- ✅ **Histórico de reacciones ampliado** (Fase 2.5 - Mejora 3) ← **NUEVO**

**Test manual**:
```bash
curl "http://localhost:8000/api/market-briefing/psychological-levels?instrument=XAUUSD&lookback_days=30" | jq
```

**Validar**:
- `levels`: array de niveles
- Cada nivel tiene:
  - `level`: float (ej: 4500.0, 4550.0)
  - `strength`: string
  - `reaction_count`: int
  - `reaction_history`: array ← **NUEVO EN FASE 2.5**
    - Cada reacción tiene:
      - `timestamp`: ISO string
      - `session`: string ("ASIA", "LONDON", "NEW_YORK", "OVERLAP")
      - `volatility`: string ("LOW", "MEDIUM", "HIGH")
      - `magnitude_points`: float
      - `magnitude_percent`: float
      - `confirmation`: bool
      - `explanation`: string

**Ejemplo de respuesta esperada** (Mejora 3):
```json
{
  "levels": [
    {
      "level": 4500.0,
      "reaction_history": [
        {
          "timestamp": "2026-01-10T14:30:00Z",
          "session": "NEW_YORK",
          "volatility": "HIGH",
          "magnitude_points": 15.5,
          "magnitude_percent": 0.34,
          "confirmation": true,
          "explanation": "Strong bounce during NY session with high volatility"
        }
      ]
    }
  ]
}
```

---

## Script de Validación Automatizado

Crea un script `test_e2e.sh` en la raíz del backend:

```bash
#!/bin/bash

# Test E2E para todos los endpoints
# Requiere: servidor corriendo en localhost:8000

BASE_URL="http://localhost:8000/api/market-briefing"

echo "🧪 Running E2E Tests..."
echo "========================"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local url=$2
    local expected_fields=$3
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        # Validar campos esperados
        all_fields_present=true
        for field in $expected_fields; do
            if ! echo "$body" | jq -e ".$field" > /dev/null 2>&1; then
                all_fields_present=false
                break
            fi
        done
        
        if $all_fields_present; then
            echo -e "${GREEN}✓ PASS${NC}"
            return 0
        else
            echo -e "${RED}✗ FAIL (missing fields)${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
        return 1
    fi
}

# Tests
test_endpoint "High Impact News" "$BASE_URL/high-impact-news" "has_high_impact_news count events geopolitical_risk"
test_endpoint "Event Schedule" "$BASE_URL/event-schedule?include_gold_impact=true" "total_events events"
test_endpoint "Yesterday Analysis" "$BASE_URL/yesterday-analysis?instrument=XAUUSD" "instrument sessions"
test_endpoint "DXY-Bond Alignment" "$BASE_URL/dxy-bond-alignment?include_gold_correlation=true" "alignment gold_dxy_correlation gold_impact_projection"
test_endpoint "Trading Mode" "$BASE_URL/trading-mode" "mode confidence operational_levels"
test_endpoint "Trading Recommendation" "$BASE_URL/trading-recommendation" "direction disclaimer risk_reward_details"
test_endpoint "Technical Analysis" "$BASE_URL/technical-analysis" "instrument"
test_endpoint "Psychological Levels" "$BASE_URL/psychological-levels" "levels current_price"

echo "========================"
echo "✅ E2E Tests Complete"
```

**Ejecutar**:
```bash
chmod +x test_e2e.sh
./test_e2e.sh
```

---

## Checklist de Validación Fase 2.5

Valida que las 4 mejoras de Fase 2.5 están funcionando:

- [ ] **Mejora 1**: Disclaimer + Risk/Reward Details
  - [ ] `disclaimer` presente y largo en `/trading-recommendation`
  - [ ] `risk_reward_details` con todos los campos
  - [ ] `min_ratio_met` bool correcto

- [ ] **Mejora 2**: Niveles Operativos por Modo
  - [ ] `operational_levels` en `/trading-mode`
  - [ ] Niveles filtrados por modo (CALM ≠ AGGRESSIVE)
  - [ ] Cada nivel tiene `action` y `explanation`

- [ ] **Mejora 3**: Histórico de Reacciones Ampliado
  - [ ] `reaction_history` en cada nivel de `/psychological-levels`
  - [ ] Cada reacción tiene `session`, `volatility`, `confirmation`
  - [ ] `magnitude_points` y `magnitude_percent` presentes

- [ ] **Mejora 4**: Magnitud Estimada en Proyección Gold
  - [ ] `magnitude_range_percent` con `min`/`max` en `/dxy-bond-alignment`
  - [ ] `magnitude_range_points` con `min`/`max`
  - [ ] Rango coherente (min < expected < max)

---

## Notas

- Los tests E2E requieren datos reales, por lo que pueden fallar fuera de horario de mercado o si las APIs externas tienen problemas.
- Para testing continuo, considera usar el Mock Provider configurando `USE_MOCK_PROVIDER=true` en `.env`.
- Si un endpoint falla, revisa los logs del servidor (`uvicorn`) para detalles del error.

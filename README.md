# Trading Assistant App

Aplicación de asistente para trading con servicio de briefing de mercado.

## Descripción

Esta aplicación proporciona herramientas y funcionalidades para asistir en operaciones de trading, incluyendo un servicio de briefing de mercado que verifica noticias económicas de alto impacto.

## Arquitectura

El proyecto está estructurado de forma modular y escalable, lista para despliegue en AWS Lambda:

```
backend/
├── app/
│   ├── config/          # Configuración de la aplicación
│   ├── models/          # Modelos de datos (Pydantic)
│   ├── routers/         # Endpoints de la API
│   ├── services/        # Lógica de negocio
│   └── utils/           # Utilidades
├── main.py              # Handler para AWS Lambda
└── requirements.txt     # Dependencias
```

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y configura las variables de entorno:

```bash
cp config.example.env .env
```

Edita `.env` y configura tu API key del calendario económico.

## Uso Local

```bash
cd backend
uvicorn app.main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

## Documentación

Una vez que la aplicación esté corriendo, puedes acceder a:
- Documentación interactiva: `http://localhost:8000/docs`
- Documentación alternativa: `http://localhost:8000/redoc`

## Endpoints

### Market Briefing

#### GET `/api/market-briefing/high-impact-news`

Verifica si hay noticias económicas de alto impacto hoy relevantes para XAUUSD (NFP, CPI, Fed, PMI...)

**Parámetros de consulta:**
- `currency` (opcional): Moneda para filtrar (por defecto: USD)

**Ejemplo de respuesta:**
```json
{
  "has_high_impact_news": true,
  "count": 3,
  "events": [...],
  "summary": "Hoy hay 3 noticias de alto impacto para XAUUSD: NFP, PMI manufacturero y Declaración de la Fed.",
  "instrument": "XAUUSD"
}
```

#### GET `/api/market-briefing/event-schedule`

Obtiene el calendario de eventos del día con horarios, indicando cuáles afectan al USD.

**Parámetros de consulta:**
- `currency` (opcional): Moneda para filtrar (por defecto: USD)

**Ejemplo de respuesta:**
```json
{
  "date": "2026-01-05",
  "events": [
    {
      "time": "10:30",
      "description": "NFP - Non-Farm Payrolls",
      "currency": "USD",
      "impact": "Alto impacto",
      "affects_usd": true,
      "full_description": "10:30 – NFP - Non-Farm Payrolls – USD – Alto impacto"
    },
    {
      "time": "12:00",
      "description": "ISM PMI Manufacturero",
      "currency": "USD",
      "impact": "Alto impacto",
      "affects_usd": true,
      "full_description": "12:00 – ISM PMI Manufacturero – USD – Alto impacto"
    }
  ],
  "usd_events_count": 2,
  "total_events": 2
}
```

**Características:**
- Lista ordenada por hora
- Formato: `HH:MM – Descripción – Moneda – Impacto`
- Campo `affects_usd` para identificar eventos que afectan al USD
- Filtro automático por `currency = "USD"` (opcional)

#### GET `/api/market-briefing/yesterday-analysis`

Analiza el cierre del día anterior y las sesiones de trading (Asia, Londres, NY).

**Parámetros de consulta:**
- `instrument` (opcional): Instrumento a analizar (por defecto: XAUUSD). Ejemplos: XAUUSD, EURUSD, NASDAQ

**Ejemplo de respuesta:**
```json
{
  "instrument": "XAUUSD",
  "date": "2026-01-04",
  "previous_day_close": 2650.0,
  "current_day_close": 2648.5,
  "daily_change_percent": -0.06,
  "daily_direction": "bajista",
  "sessions": [
    {
      "session": "asia",
      "start_time": "00:00",
      "end_time": "06:00",
      "open_price": 2650.0,
      "close_price": 2651.5,
      "high": 2652.0,
      "low": 2649.0,
      "range_value": 3.0,
      "direction": "alcista",
      "change_percent": 0.06,
      "broke_previous_high": false,
      "broke_previous_low": false,
      "description": "Sesión Asia: rango estrecho, impulso alcista"
    }
  ],
  "summary": "Ayer XAUUSD cerró bajista (-0.06%).\nSesión Asia: rango estrecho, movimiento lateral.\nSesión Londres: rango amplio, fuerte impulso bajista rompiendo el mínimo del día anterior."
}
```

**Características:**
- Análisis de cierre del día anterior
- Análisis por sesión (Asia: 00:00-06:00 UTC, Londres: 07:00-11:00 UTC, NY: 12:00-21:00 UTC)
- Cálculo de rango, dirección y cambio porcentual por sesión
- Detección de ruptura de máximos/mínimos del día anterior
- Resumen textual automático

## Despliegue en AWS Lambda

El proyecto está configurado para desplegarse en AWS Lambda usando AWS SAM.

### Prerrequisitos

1. AWS CLI instalado y configurado
2. AWS SAM CLI instalado
3. Credenciales de AWS configuradas

### Instalación de dependencias para Lambda

```bash
cd backend
pip install -r requirements-lambda.txt
```

### Construcción y despliegue

```bash
# Construir el proyecto
sam build

# Desplegar (modo guiado)
sam deploy --guided

# O usar el Makefile
make build
make deploy
```

### Configuración de despliegue

El archivo `samconfig.toml` contiene la configuración por defecto. Puedes modificar los parámetros:

- `Stage`: Etapa de despliegue (dev, staging, prod)
- `EconomicCalendarProvider`: Proveedor a usar (tradingeconomics o mock)
- `EconomicCalendarApiKey`: API key (opcional, requerido solo para tradingeconomics)

### Variables de entorno en Lambda

Las siguientes variables se configuran automáticamente:
- `ECONOMIC_CALENDAR_PROVIDER`: Proveedor de calendario económico
- `ECONOMIC_CALENDAR_API_KEY`: API key (si se proporciona)
- `ECONOMIC_CALENDAR_API_URL`: URL de la API
- `DEFAULT_CURRENCY`: Moneda por defecto (USD)
- `LOG_LEVEL`: Nivel de logging (INFO)
- `STAGE`: Etapa de despliegue

### Verificación post-despliegue

Una vez desplegado, obtendrás una URL de API Gateway. Prueba el endpoint:

```bash
curl https://YOUR_API_URL/api/market-briefing/high-impact-news
```

La configuración está en `template.yaml` y `samconfig.toml`.


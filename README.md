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

Verifica si hay noticias económicas de alto impacto hoy (NFP, CPI, Fed, PMI...)

**Parámetros de consulta:**
- `currency` (opcional): Moneda para filtrar (por defecto: USD)

**Ejemplo de respuesta:**
```json
{
  "has_high_impact_news": true,
  "count": 3,
  "events": [...],
  "summary": "Hoy hay 3 noticias de alto impacto: NFP, PMI manufacturero y Declaración de la Fed."
}
```

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


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

El proyecto está configurado para desplegarse en AWS Lambda usando AWS SAM:

```bash
sam build
sam deploy --guided
```

La configuración está en `template.yaml`.


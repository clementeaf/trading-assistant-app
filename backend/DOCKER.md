# Docker Setup - Backend

## Requisitos

- Docker Desktop instalado y corriendo
- Docker Compose (incluido en Docker Desktop)

## Levantar el Backend

### Opción 1: Usando Docker Compose (Recomendado)

```bash
# Construir y levantar el contenedor
docker-compose up --build

# O en modo detached (background)
docker-compose up -d --build
```

El backend estará disponible en: `http://localhost:8000`

### Opción 2: Usando Docker directamente

```bash
# Construir la imagen
docker build -t trading-assistant-backend .

# Ejecutar el contenedor
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e ECONOMIC_CALENDAR_PROVIDER=mock \
  -e MARKET_DATA_PROVIDER=mock \
  -e DEFAULT_CURRENCY=USD \
  -e STAGE=dev \
  trading-assistant-backend
```

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Detener el contenedor
docker-compose down

# Reconstruir sin caché
docker-compose build --no-cache

# Acceder al contenedor
docker-compose exec backend bash
```

## Variables de Entorno

Puedes crear un archivo `.env` en el directorio `backend/` con las siguientes variables:

```env
LOG_LEVEL=INFO
ECONOMIC_CALENDAR_PROVIDER=mock
ECONOMIC_CALENDAR_API_KEY=your_api_key_here
ECONOMIC_CALENDAR_API_URL=https://api.tradingeconomics.com/calendar
MARKET_DATA_PROVIDER=mock
MARKET_DATA_API_KEY=your_market_data_api_key_here
DEFAULT_CURRENCY=USD
STAGE=dev
```

El `docker-compose.yml` ya incluye las variables básicas, pero puedes sobrescribirlas con un archivo `.env`.

## Documentación de la API

Una vez levantado el backend, accede a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Producción

Para producción, usa el `Dockerfile.prod`:

```bash
docker build -f Dockerfile.prod -t trading-assistant-backend:prod .
docker run -p 8000:8000 trading-assistant-backend:prod
```


# Base de Datos - Trading Assistant

## Configuración

La aplicación usa PostgreSQL como base de datos para persistir:
- Eventos económicos históricos
- Datos de mercado (velas OHLCV)
- Análisis diarios
- Recomendaciones de modo de trading
- Alineaciones DXY-Bonos

## Setup Inicial

### 1. Con Docker Compose (Recomendado)

El `docker-compose.yml` ya incluye PostgreSQL:

```bash
docker-compose up -d postgres
```

### 2. Manual

```bash
# Instalar PostgreSQL localmente
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Crear base de datos
createdb trading_assistant

# O con psql:
psql -U postgres
CREATE DATABASE trading_assistant;
```

## Configuración de Variables de Entorno

Agrega a tu `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading_assistant
```

## Migraciones

### Crear una nueva migración

```bash
cd backend
alembic revision --autogenerate -m "descripción del cambio"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Revertir última migración

```bash
alembic downgrade -1
```

## Inicializar Base de Datos

### Opción 1: Con Alembic (Recomendado)

```bash
cd backend
alembic upgrade head
```

### Opción 2: Con script Python

```bash
cd backend
python scripts/init_db.py
```

## Estructura de Tablas

### `economic_events`
Almacena eventos económicos históricos.

### `market_data`
Almacena velas OHLCV de instrumentos.

### `daily_analyses`
Almacena análisis diarios de mercado.

### `trading_mode_recommendations`
Almacena recomendaciones históricas de modo de trading.

### `market_alignments`
Almacena análisis de alineación DXY-Bonos.

## Uso en Desarrollo

Los servicios ahora intentan:
1. Obtener datos de la base de datos primero
2. Si no hay datos, obtener del proveedor (API o mock)
3. Guardar los datos obtenidos en la base de datos

Esto permite:
- Cachear datos de APIs externas
- Tener historial de análisis
- Reducir llamadas a APIs externas
- Mejorar tiempos de respuesta

## Producción

Para producción en AWS, considera:
- **RDS PostgreSQL**: Base de datos gestionada
- **Aurora Serverless**: Escalado automático
- **Connection Pooling**: PgBouncer o RDS Proxy


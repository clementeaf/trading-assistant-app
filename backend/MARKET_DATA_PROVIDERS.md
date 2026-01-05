# Proveedores de Datos de Mercado

## Proveedores Disponibles

### 1. Alpha Vantage (Recomendado para Forex)

**Características:**
- Plan gratuito: 5 llamadas/minuto, 500 llamadas/día
- Soporta datos históricos intradía y diarios
- Excelente para pares de divisas (forex)
- API REST simple

**Instrumentos Soportados:**
- ✅ Forex: XAUUSD, EURUSD, GBPUSD, USDJPY, etc.
- ⚠️ Acciones: Limitado (requiere símbolo de bolsa)
- ❌ Índices: DXY, NASDAQ (no soportados directamente)
- ❌ Bonos: US10Y, US02Y, US30Y (no soportados directamente)

**Configuración:**
```env
MARKET_DATA_PROVIDER=alphavantage
MARKET_DATA_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**
1. Visita https://www.alphavantage.co/support/#api-key
2. Registra tu email
3. Recibirás la API key por email

**Limitaciones:**
- Rate limit: 5 calls/minuto (plan gratuito)
- Datos intradía: Solo últimos 30 días
- Algunos instrumentos no están disponibles

### 2. Mock Provider (Desarrollo/Testing)

**Características:**
- Datos simulados para desarrollo
- No requiere API key
- Útil para testing y desarrollo local

**Configuración:**
```env
MARKET_DATA_PROVIDER=mock
```

## Uso en la Aplicación

La aplicación intenta usar el proveedor configurado. Si falla o no hay API key, automáticamente usa el mock provider.

**Orden de prioridad:**
1. Proveedor configurado (si tiene API key válida)
2. Mock provider (fallback)

## Futuros Proveedores

### Opciones a considerar:
- **Twelve Data**: Excelente para múltiples instrumentos, incluyendo índices y bonos
- **Finnhub**: Buena para acciones y algunos índices
- **OANDA**: Especializado en forex, datos de alta calidad
- **Polygon.io**: Datos de mercado completos, incluyendo crypto

## Integración con Base de Datos

Los datos obtenidos de los proveedores se cachean automáticamente en la base de datos para:
- Reducir llamadas a APIs externas
- Mejorar tiempos de respuesta
- Mantener historial de datos


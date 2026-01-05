# Proveedores de Datos de Mercado

**IMPORTANTE**: Esta aplicación está enfocada exclusivamente en **XAUUSD (oro)** y factores que lo impactan. No nos interesan otros pares de divisas.

## Proveedores Disponibles

### 1. Twelve Data (⭐ Recomendado para XAUUSD)

**Características:**
- Plan gratuito: 800 llamadas/día, 2 llamadas/segundo
- Especializado en metales preciosos, incluyendo XAUUSD
- Datos históricos intradía y diarios disponibles
- API REST simple y bien documentada

**Soporte para XAUUSD:**
- ✅ **Time Series**: Soporta datos históricos para XAU/USD
- ✅ **Múltiples intervalos**: 1min, 5min, 15min, 30min, 1h, 4h, 1day
- ✅ **Datos históricos**: Hasta 5000 velas por request
- ✅ **Plan gratuito**: Funciona para XAUUSD sin necesidad de premium

**Instrumentos Soportados:**
- ✅ XAUUSD (oro) - **Objetivo principal**
- ✅ DXY (Dollar Index)
- ✅ Bonos: US10Y, US02Y, US30Y
- ✅ Índices: NASDAQ (IXIC)

**Configuración:**
```env
MARKET_DATA_PROVIDER=twelvedata
MARKET_DATA_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**
1. Visita https://twelvedata.com/
2. Crea una cuenta gratuita
3. Obtén tu API key desde el dashboard

**Limitaciones:**
- Rate limit: 2 calls/segundo, 800 calls/día (plan gratuito)
- Máximo 5000 velas por request
- Para uso intensivo, considerar plan de pago

### 2. Alpha Vantage (Limitado para XAUUSD)

**Características:**
- Plan gratuito: 5 llamadas/minuto, 500 llamadas/día
- API REST simple

**Soporte para XAUUSD:**
- ❌ **FX_INTRADAY**: Requiere plan premium
- ❌ **FX_DAILY**: Requiere plan premium o tiene rate limits estrictos
- ⚠️ **Conclusión**: Alpha Vantage NO es adecuado para XAUUSD en plan gratuito

**Instrumentos Soportados (plan gratuito):**
- ⚠️ Algunos pares de divisas estándar (EUR/USD, GBP/USD) - pero NO nos interesan
- ❌ XAUUSD requiere plan premium

**Configuración:**
```env
MARKET_DATA_PROVIDER=alphavantage
MARKET_DATA_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**
1. Visita https://www.alphavantage.co/support/#api-key
2. Registra tu email
3. Recibirás la API key por email

**Limitaciones para XAUUSD:**
- ❌ **NO funciona para XAUUSD en plan gratuito**
- `FX_INTRADAY` requiere plan premium
- `FX_DAILY` para XAU/USD requiere plan premium
- La aplicación automáticamente hace fallback al mock provider cuando Alpha Vantage no puede proporcionar datos

**Recomendación**: Alpha Vantage NO es adecuado para XAUUSD. Usar mock provider o buscar proveedores específicos para metales preciosos.

### 3. Mock Provider (Desarrollo/Testing)

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

## Otros Proveedores a Evaluar (Futuro)

### Opciones adicionales para XAUUSD:
- **Metals API**: API específica para metales preciosos (oro, plata, etc.)
- **OANDA**: Tiene XAU/USD disponible, datos de alta calidad (requiere cuenta)
- **Polygon.io**: Datos de mercado completos, puede incluir metales (plan de pago)
- **FXCM Data**: Datos históricos de XAUUSD (requiere cuenta de broker)
- **TradingView API**: Acceso a datos de XAUUSD (requiere suscripción)

**Nota**: Estos proveedores requieren evaluación adicional para verificar:
1. Disponibilidad de datos históricos intradía para XAUUSD
2. Costos y límites del plan gratuito
3. Calidad y latencia de los datos
4. Facilidad de integración

## Integración con Base de Datos

Los datos obtenidos de los proveedores se cachean automáticamente en la base de datos para:
- Reducir llamadas a APIs externas
- Mejorar tiempos de respuesta
- Mantener historial de datos


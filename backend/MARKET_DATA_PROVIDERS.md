# Proveedores de Datos de Mercado

**IMPORTANTE**: Esta aplicación está enfocada exclusivamente en **XAUUSD (oro)** y factores que lo impactan. No nos interesan otros pares de divisas.

## Proveedores Disponibles

### 1. Alpha Vantage (Limitado para XAUUSD)

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

## Futuros Proveedores para XAUUSD

### Opciones a considerar (específicas para oro/metales preciosos):
- **Twelve Data**: Tiene datos de metales preciosos, incluyendo XAUUSD
- **Metals API**: API específica para metales preciosos (oro, plata, etc.)
- **OANDA**: Tiene XAU/USD disponible, datos de alta calidad
- **Polygon.io**: Datos de mercado completos, puede incluir metales
- **FXCM Data**: Datos históricos de XAUUSD
- **TradingView API**: Acceso a datos de XAUUSD (requiere suscripción)

**Nota**: Todos estos proveedores requieren evaluación para verificar:
1. Disponibilidad de datos históricos intradía para XAUUSD
2. Costos y límites del plan gratuito
3. Calidad y latencia de los datos

## Integración con Base de Datos

Los datos obtenidos de los proveedores se cachean automáticamente en la base de datos para:
- Reducir llamadas a APIs externas
- Mejorar tiempos de respuesta
- Mantener historial de datos


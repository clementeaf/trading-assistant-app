# Enfoque en XAUUSD (Oro)

## Objetivo Principal

Esta aplicación está **exclusivamente enfocada en XAUUSD (oro)** y los factores que impactan su precio. No nos interesan otros pares de divisas.

## Factores que Impactan XAUUSD

### 1. DXY (Dollar Index)
- **Correlación**: Inversa (DXY sube → XAUUSD baja, generalmente)
- **Uso en la app**: Análisis de alineación DXY-Bonos para determinar sesgo del mercado

### 2. Bonos (US10Y, US02Y, US30Y)
- **Correlación**: Inversa (rendimientos suben → XAUUSD baja, generalmente)
- **Uso en la app**: Análisis de alineación con DXY para determinar risk-off/risk-on

### 3. Noticias Económicas de Alto Impacto
- **Eventos clave**: NFP, CPI, FOMC, PMI manufacturero
- **Impacto**: Movimientos significativos en XAUUSD cuando se publican
- **Uso en la app**: Determinar modo de trading (calma/agresivo)

### 4. Sesiones de Trading
- **Asia**: 00:00-06:00 UTC
- **Londres**: 07:00-11:00 UTC  
- **Nueva York**: 12:00-21:00 UTC
- **Uso en la app**: Análisis de comportamiento por sesión

## Proveedores de Datos para XAUUSD

### Estado Actual
- **Twelve Data**: ✅ **IMPLEMENTADO** - Funciona para XAUUSD en plan gratuito (800 calls/día)
- **Alpha Vantage**: ❌ NO funciona para XAUUSD en plan gratuito (requiere premium)
- **Mock Provider**: ✅ Funciona para desarrollo/testing (fallback automático)

### Proveedores Implementados
1. **Twelve Data** ✅ - **RECOMENDADO** - Especializado en metales preciosos, incluyendo XAUUSD
   - Plan gratuito: 800 calls/día, 2 calls/segundo
   - Soporta datos históricos intradía y diarios
   - Configuración: `MARKET_DATA_PROVIDER=twelvedata`
   - Obtener API key: https://twelvedata.com/

### Proveedores a Evaluar (Futuro)
1. **Metals API** - Específico para oro y metales
2. **OANDA** - Tiene XAU/USD disponible
3. **Polygon.io** - Datos de mercado completos
4. **FXCM Data** - Datos históricos de XAUUSD

## Prioridades de Desarrollo

1. ✅ Análisis de noticias económicas (alto impacto para XAUUSD)
2. ✅ Análisis de sesiones de trading (Asia, Londres, NY)
3. ✅ Análisis de alineación DXY-Bonos
4. ✅ Recomendación de modo de trading
5. ✅ Proveedor real de datos para XAUUSD (Twelve Data implementado)
6. ⏳ Evaluar y probar Twelve Data con API key real
7. ⏳ Considerar proveedores adicionales si es necesario

## Notas Técnicas

- **Twelve Data** es el proveedor recomendado para XAUUSD (implementado y listo para usar)
- El mock provider genera datos realistas para XAUUSD (rango típico: 1800-2800 USD/oz)
- Alpha Vantage se intenta usar si está configurado, pero hace fallback automático a mock
- Todos los análisis están optimizados para XAUUSD específicamente
- El sistema intenta usar el proveedor configurado y hace fallback automático si falla


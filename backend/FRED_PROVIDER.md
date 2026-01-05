# FRED Provider - DXY y Bonos del Tesoro

## Descripción

FRED (Federal Reserve Economic Data) es una API **GRATUITA** y oficial de la Reserva Federal de St. Louis que proporciona datos económicos de EE.UU., incluyendo:

- **DXY (Dollar Index)**: Índice del dólar estadounidense
- **Bonos del Tesoro**: US10Y, US02Y, US30Y, US05Y

## Obtener API Key (GRATIS)

1. Visita: https://fred.stlouisfed.org/docs/api/api_key.html
2. Completa el formulario con tu información
3. Recibirás la API key por email (gratis, sin tarjeta de crédito)
4. No hay límites estrictos en el plan gratuito

## Configuración

### Variables de Entorno

```env
FRED_API_KEY=tu_api_key_de_fred_aqui
```

### Docker Compose

```yaml
environment:
  - FRED_API_KEY=${FRED_API_KEY:-}
```

### AWS Lambda (SAM)

```yaml
Parameters:
  FredApiKey:
    Type: String
    Default: ""
    Description: API Key for FRED
    NoEcho: true
```

## Instrumentos Soportados

| Instrumento | Series ID FRED | Descripción |
|------------|---------------|-------------|
| DXY | DTWEXBGS | Trade Weighted U.S. Dollar Index: Broad |
| US10Y | DGS10 | 10-Year Treasury Constant Maturity Rate |
| US02Y | DGS2 | 2-Year Treasury Constant Maturity Rate |
| US30Y | DGS30 | 30-Year Treasury Constant Maturity Rate |
| US05Y | DGS5 | 5-Year Treasury Constant Maturity Rate |

## Características

- ✅ **Gratis**: Sin costo, sin tarjeta de crédito
- ✅ **Oficial**: Datos de la Reserva Federal de EE.UU.
- ✅ **Confiable**: Fuente oficial de datos económicos
- ✅ **Datos diarios**: Proporciona valores diarios (no intradía)
- ✅ **Sin límites estrictos**: Plan gratuito generoso

## Limitaciones

- ⚠️ **Solo datos diarios**: FRED no proporciona datos intradía
- ⚠️ **Sin volumen**: No incluye datos de volumen
- ⚠️ **Solo EE.UU.**: Especializado en datos económicos de EE.UU.

## Uso en la Aplicación

El sistema usa FRED automáticamente para DXY y bonos cuando:
1. `FRED_API_KEY` está configurado
2. Se solicita datos de DXY o bonos (US10Y, US02Y, etc.)

**Prioridad de proveedores:**
1. FRED (si está configurado) - para DXY y bonos
2. Proveedor principal (Twelve Data/Alpha Vantage) - para otros instrumentos

## Ejemplo de Uso

```python
from app.providers.market_data.fred_provider import FredProvider

provider = FredProvider(api_key="tu_api_key")
candles = await provider.fetch_historical_candles(
    "DXY",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    interval="1d"
)
```

## Referencias

- **Documentación FRED**: https://fred.stlouisfed.org/docs/api/
- **Obtener API Key**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Explorar Series**: https://fred.stlouisfed.org/


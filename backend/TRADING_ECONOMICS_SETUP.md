# TradingEconomics API - Configuración

## Obtener API Key Gratuita

1. **Visita**: https://tradingeconomics.com/api
2. **Registro**: Crea una cuenta gratuita
3. **API Key**: Obtén tu API key desde el dashboard
4. **Plan Gratuito**: Incluye acceso limitado pero suficiente para calendario económico

## Configuración

### Variables de Entorno

```env
ECONOMIC_CALENDAR_PROVIDER=tradingeconomics
ECONOMIC_CALENDAR_API_KEY=tu_api_key_real_aqui
ECONOMIC_CALENDAR_API_URL=https://api.tradingeconomics.com/calendar
```

### Docker Compose

```yaml
environment:
  - ECONOMIC_CALENDAR_PROVIDER=tradingeconomics
  - ECONOMIC_CALENDAR_API_KEY=${ECONOMIC_CALENDAR_API_KEY}
```

### AWS Lambda (SAM)

```yaml
Parameters:
  EconomicCalendarApiKey:
    Type: String
    Default: ""
    Description: API Key for TradingEconomics
    NoEcho: true
```

## Características

- ✅ **Datos reales** del calendario económico
- ✅ **Solo días hábiles** (la Fed no opera en fines de semana)
- ✅ **Eventos de alto impacto** para XAUUSD
- ✅ **Filtrado automático** por USD y relevancia para oro

## Nota Importante

El sistema ahora **requiere** una API key válida. Si no está configurada o es un placeholder, el backend lanzará un error claro indicando que se necesita configurar la API key.

## Referencias

- **Sitio Web**: https://tradingeconomics.com/
- **API Documentation**: https://tradingeconomics.com/api
- **Registro**: https://tradingeconomics.com/api


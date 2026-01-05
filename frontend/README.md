# Trading Assistant - Frontend

Frontend sencillo y minimalista para visualizar los datos del Market Briefing API.

## Características

- **Diseño limpio y austero**: Interfaz minimalista que muestra la información de manera clara
- **5 secciones principales**:
  - Modo de Trading Recomendado
  - Noticias de Alto Impacto para XAUUSD
  - Calendario de Eventos
  - Análisis del Día Anterior
  - Alineación DXY-Bonos

## Tecnologías

- React 19.2.0
- TypeScript 5.9.3
- Vite 7.2.4

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Build

```bash
npm run build
```

## Configuración

Crea un archivo `.env` basado en `.env.example`:

```env
VITE_API_URL=https://yx1x1mom8i.execute-api.us-east-1.amazonaws.com
```

Por defecto, la aplicación usa la URL de producción si no se especifica `VITE_API_URL`.

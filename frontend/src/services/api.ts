import axios from "axios";
import type {
  DailyMarketAnalysis,
  EventScheduleResponse,
  HighImpactNewsResponse,
  MarketAlignmentAnalysis,
  TradingModeRecommendation,
  TradeRecommendation,
  TechnicalAnalysisResponse,
} from "../types/api";

// SIEMPRE usar endpoint de producción (AWS Lambda)
// NO usar localhost - el frontend siempre debe consumir el backend desplegado en AWS
const API_BASE_URL = "https://yx1x1mom8i.execute-api.us-east-1.amazonaws.com";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Obtiene noticias de alto impacto para XAUUSD del día actual
 * @param currency - Moneda para filtrar (opcional)
 * @returns Respuesta con noticias de alto impacto
 */
export async function getHighImpactNews(
  currency?: string
): Promise<HighImpactNewsResponse> {
  const response = await apiClient.get<HighImpactNewsResponse>(
    "/api/market-briefing/high-impact-news",
    {
      params: currency ? { currency } : undefined,
    }
  );
  return response.data;
}

/**
 * Obtiene el calendario de eventos económicos de alto impacto del día
 * @param currency - Moneda para filtrar (opcional)
 * @returns Respuesta con el calendario de eventos
 */
export async function getEventSchedule(
  currency?: string
): Promise<EventScheduleResponse> {
  const response = await apiClient.get<EventScheduleResponse>(
    "/api/market-briefing/event-schedule",
    {
      params: currency ? { currency } : undefined,
    }
  );
  return response.data;
}

/**
 * Obtiene el análisis de mercado del día anterior para un instrumento
 * @param instrument - Símbolo del instrumento (ej: XAUUSD)
 * @returns Análisis completo del día anterior
 */
export async function getYesterdayAnalysis(
  instrument: string
): Promise<DailyMarketAnalysis> {
  const response = await apiClient.get<DailyMarketAnalysis>(
    "/api/market-briefing/yesterday-analysis",
    {
      params: { instrument },
    }
  );
  return response.data;
}

/**
 * Obtiene el análisis de alineación entre DXY y bonos
 * @param bond - Símbolo del bono (ej: US10Y)
 * @returns Análisis de alineación
 */
export async function getDxyBondAlignment(
  bond: string = "US10Y"
): Promise<MarketAlignmentAnalysis> {
  const response = await apiClient.get<MarketAlignmentAnalysis>(
    "/api/market-briefing/dxy-bond-alignment",
    {
      params: { bond },
    }
  );
  return response.data;
}

/**
 * Obtiene una recomendación del modo de trading para el día
 * @param instrument - Instrumento principal a analizar (ej: XAUUSD)
 * @param bond - Símbolo del bono (ej: US10Y)
 * @param timeWindowMinutes - Ventana de tiempo en minutos para noticias próximas
 * @returns Recomendación del modo de trading
 */
export async function getTradingModeRecommendation(
  instrument: string = "XAUUSD",
  bond: string = "US10Y",
  timeWindowMinutes: number = 120
): Promise<TradingModeRecommendation> {
  const response = await apiClient.get<TradingModeRecommendation>(
    "/api/market-briefing/trading-mode",
    {
      params: {
        instrument,
        bond,
        time_window_minutes: timeWindowMinutes,
      },
    }
  );
  return response.data;
}

/**
 * Obtiene recomendación completa de trading con niveles de precio
 * @param instrument - Instrumento principal a analizar (ej: XAUUSD)
 * @param bond - Símbolo del bono (ej: US10Y)
 * @param timeWindowMinutes - Ventana de tiempo en minutos para noticias próximas
 * @returns Recomendación de trading con niveles de precio
 */
export async function getTradingRecommendation(
  instrument: string = "XAUUSD",
  bond: string = "US10Y",
  timeWindowMinutes: number = 120
): Promise<TradeRecommendation> {
  const response = await apiClient.get<TradeRecommendation>(
    "/api/market-briefing/trading-recommendation",
    {
      params: {
        instrument,
        bond,
        time_window_minutes: timeWindowMinutes,
      },
    }
  );
  return response.data;
}

/**
 * Obtiene análisis técnico avanzado multi-temporalidad (Daily, H4, H1)
 * @param instrument - Instrumento a analizar (ej: XAUUSD)
 * @returns Análisis técnico con RSI, EMAs, soporte/resistencia
 */
export async function getTechnicalAnalysis(
  instrument: string = "XAUUSD"
): Promise<TechnicalAnalysisResponse> {
  const response = await apiClient.get<TechnicalAnalysisResponse>(
    "/api/market-briefing/technical-analysis",
    {
      params: { instrument },
    }
  );
  return response.data;
}


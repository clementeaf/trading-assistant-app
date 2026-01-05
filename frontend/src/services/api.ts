import type {
  DailyMarketAnalysis,
  EventScheduleResponse,
  HighImpactNewsResponse,
  MarketAlignmentAnalysis,
  TradingModeRecommendation,
} from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://yx1x1mom8i.execute-api.us-east-1.amazonaws.com";

/**
 * Obtiene noticias de alto impacto para XAUUSD del día actual
 * @param currency - Moneda para filtrar (opcional)
 * @returns Respuesta con noticias de alto impacto
 */
export async function getHighImpactNews(
  currency?: string
): Promise<HighImpactNewsResponse> {
  const url = new URL(`${API_BASE_URL}/api/market-briefing/high-impact-news`);
  if (currency) {
    url.searchParams.set("currency", currency);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Error fetching high impact news: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene el calendario de eventos económicos de alto impacto del día
 * @param currency - Moneda para filtrar (opcional)
 * @returns Respuesta con el calendario de eventos
 */
export async function getEventSchedule(
  currency?: string
): Promise<EventScheduleResponse> {
  const url = new URL(`${API_BASE_URL}/api/market-briefing/event-schedule`);
  if (currency) {
    url.searchParams.set("currency", currency);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Error fetching event schedule: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene el análisis de mercado del día anterior para un instrumento
 * @param instrument - Símbolo del instrumento (ej: XAUUSD)
 * @returns Análisis completo del día anterior
 */
export async function getYesterdayAnalysis(
  instrument: string
): Promise<DailyMarketAnalysis> {
  const url = new URL(`${API_BASE_URL}/api/market-briefing/yesterday-analysis`);
  url.searchParams.set("instrument", instrument);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Error fetching yesterday analysis: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene el análisis de alineación entre DXY y bonos
 * @param bond - Símbolo del bono (ej: US10Y)
 * @returns Análisis de alineación
 */
export async function getDxyBondAlignment(
  bond: string = "US10Y"
): Promise<MarketAlignmentAnalysis> {
  const url = new URL(`${API_BASE_URL}/api/market-briefing/dxy-bond-alignment`);
  url.searchParams.set("bond", bond);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Error fetching DXY-Bond alignment: ${response.statusText}`);
  }

  return response.json();
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
  const url = new URL(`${API_BASE_URL}/api/market-briefing/trading-mode`);
  url.searchParams.set("instrument", instrument);
  url.searchParams.set("bond", bond);
  url.searchParams.set("time_window_minutes", timeWindowMinutes.toString());

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(
      `Error fetching trading mode recommendation: ${response.statusText}`
    );
  }

  return response.json();
}


export interface EconomicEvent {
  date: string;
  importance: "low" | "medium" | "high";
  currency: string;
  description: string;
  country?: string;
  actual?: number;
  forecast?: number;
  previous?: number;
}

export interface HighImpactNewsResponse {
  has_high_impact_news: boolean;
  count: number;
  events: EconomicEvent[];
  summary: string;
  instrument: string;
}

export interface EventScheduleItem {
  time: string;
  description: string;
  currency: string;
  impact: string;
  affects_usd: boolean;
  full_description: string;
}

export interface EventScheduleResponse {
  date: string;
  events: EventScheduleItem[];
  usd_events_count: number;
  total_events: number;
}

export interface PriceCandle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface SessionAnalysis {
  session: string;
  start_time: string;
  end_time: string;
  open_price: number;
  close_price: number;
  high: number;
  low: number;
  range_value: number;
  direction: "alcista" | "bajista" | "lateral";
  change_percent: number;
  volume_relative?: number;
  broke_previous_high: boolean;
  broke_previous_low: boolean;
  description: string;
}

export interface DailyMarketAnalysis {
  instrument: string;
  date: string;
  previous_day_close: number;
  current_day_close: number;
  daily_change_percent: number;
  daily_direction: "alcista" | "bajista" | "lateral";
  previous_day_high: number;
  previous_day_low: number;
  sessions: SessionAnalysis[];
  summary: string;
}

export interface InstrumentPrice {
  symbol: string;
  price: number;
  previous_price: number;
  change_percent: number;
  direction: "sube" | "baja" | "lateral";
}

export interface MarketAlignmentAnalysis {
  dxy: InstrumentPrice;
  bond: InstrumentPrice;
  alignment: "alineados" | "conflicto";
  market_bias: "risk-on" | "risk-off" | "mixto";
  summary: string;
}

export interface TradingModeReason {
  rule_name: string;
  description: string;
  priority: number;
}

export interface TradingModeRecommendation {
  mode: "calma" | "agresivo" | "muy_calma" | "observar";
  confidence: number;
  reasons: TradingModeReason[];
  summary: string;
  detailed_explanation: string;
}

export interface TradeRecommendation {
  analysis_date: string;
  analysis_datetime: string;
  current_datetime: string;
  direction: "compra" | "venta" | "esperar";
  confidence: number;
  current_price: number;
  entry_price: number | null;
  stop_loss: number | null;
  take_profit_1: number | null;
  take_profit_2: number | null;
  optimal_entry_range: {
    min: number;
    max: number;
  } | null;
  support_level: number | null;
  resistance_level: number | null;
  market_context: "risk-on" | "risk-off" | "mixto";
  trading_mode: "calma" | "agresivo" | "muy_calma" | "observar";
  reasons: string[];
  summary: string;
  detailed_explanation: string;
  warnings: string[];
  // Análisis técnico avanzado
  daily_trend?: string | null;
  h4_trend?: string | null;
  h4_rsi?: number | null;
  h4_rsi_zone?: number | null;
  h4_impulse_direction?: string | null;
  h4_impulse_strong?: boolean | null;
  h4_impulse_distance_percent?: number | null;
  h1_trend?: string | null;
  price_near_support?: boolean | null;
  price_near_resistance?: boolean | null;
  h4_ema_50?: number | null;
  h4_ema_100?: number | null;
  h4_ema_200?: number | null;
}

export interface TechnicalAnalysisResponse {
  instrument: string;
  analysis_date: string;
  daily: {
    timeframe: string;
    current_price: number;
    trend: string;
    support?: number | null;
    resistance?: number | null;
    ema_50?: number | null;
    ema_100?: number | null;
    ema_200?: number | null;
    candles_count: number;
  };
  h4: {
    timeframe: string;
    current_price: number;
    trend: string;
    rsi?: number | null;
    rsi_zone?: number | null;
    impulse_direction?: string | null;
    impulse_distance_percent?: number | null;
    impulse_strong?: boolean | null;
    support?: number | null;
    resistance?: number | null;
    near_support?: boolean | null;
    near_resistance?: boolean | null;
    ema_50?: number | null;
    ema_100?: number | null;
    ema_200?: number | null;
    candles_count: number;
  };
  h1: {
    timeframe: string;
    current_price: number;
    trend: string;
    support?: number | null;
    resistance?: number | null;
    ema_50?: number | null;
    ema_100?: number | null;
    ema_200?: number | null;
    candles_count: number;
  };
  summary: string;
  chart_candles?: PriceCandle[];
}


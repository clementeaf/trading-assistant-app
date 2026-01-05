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


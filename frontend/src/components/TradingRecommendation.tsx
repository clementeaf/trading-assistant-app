import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { TradeRecommendation, TechnicalAnalysisResponse } from "../types/api";
import { getTradingRecommendation, getTechnicalAnalysis } from "../services/api";
import { EntryPointChart } from "./EntryPointChart";

/**
 * Componente que muestra la recomendación completa de trading con niveles de precio
 */
export function TradingRecommendation(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<TradeRecommendation>({
    queryKey: ["tradingRecommendation", "XAUUSD", "US10Y"],
    queryFn: () => getTradingRecommendation("XAUUSD", "US10Y"),
  });

  // Obtener datos técnicos para el chart
  const { data: technicalData } = useQuery<TechnicalAnalysisResponse>({
    queryKey: ["technicalAnalysis", "XAUUSD"],
    queryFn: () => getTechnicalAnalysis("XAUUSD"),
    enabled: !!data, // Solo cargar si hay recomendación
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm p-6">
        <p className="text-red-800 font-medium">Error al cargar recomendación</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : "Error desconocido"}
        </p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const directionLabels: Record<string, { label: string; color: string; bg: string }> = {
    compra: {
      label: "COMPRA",
      color: "text-green-700",
      bg: "bg-green-50 border-green-400",
    },
    venta: {
      label: "VENTA",
      color: "text-red-700",
      bg: "bg-red-50 border-red-400",
    },
    esperar: {
      label: "ESPERAR",
      color: "text-yellow-700",
      bg: "bg-yellow-50 border-yellow-400",
    },
  };

  const directionStyle = directionLabels[data.direction] || directionLabels.esperar;

  // Formatear fechas
  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("es-ES", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const formatDateTime = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString("es-ES", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Recomendación de Trading</h2>
        <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
          Confianza: {(data.confidence * 100).toFixed(0)}%
        </span>
      </div>

      {/* Información temporal del asesoramiento */}
      <div className="bg-blue-50 border-l-4 border-blue-400 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <svg
              className="w-6 h-6 text-blue-600 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-blue-900 mb-2 uppercase tracking-wide">
              Información del Asesoramiento
            </h3>
            <div className="space-y-1 text-sm text-blue-800">
              <p>
                <span className="font-medium">Día analizado:</span> {formatDate(data.analysis_date)}
              </p>
              <p>
                <span className="font-medium">Recomendación generada:</span> {formatDateTime(data.analysis_datetime)}
              </p>
              <p className="text-xs text-blue-600 mt-2">
                Esta recomendación se basa en datos del último día hábil disponible ({data.analysis_date}).
                {new Date(data.analysis_date).toDateString() !== new Date().toDateString() && (
                  <span className="block mt-1 font-medium">
                    Nota: No es el día actual, se está usando el último día hábil con datos disponibles.
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Dirección principal */}
      <div className={`${directionStyle.bg} border-2 ${directionStyle.bg.split("-")[1]}-400 rounded-lg p-6 mb-6`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-3xl font-bold ${directionStyle.color}`}>
            {directionStyle.label}
          </h3>
          <div className="text-right">
            <p className="text-sm text-gray-600">Precio Actual</p>
            <p className="text-xl font-semibold text-gray-900">{data.current_price.toFixed(2)}</p>
          </div>
        </div>
        <p className="text-sm text-gray-700">{data.summary}</p>
      </div>

      {/* Niveles de precio */}
      {data.direction !== "esperar" && data.entry_price && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">Entrada</h4>
            <p className="text-2xl font-bold text-blue-700">{data.entry_price.toFixed(2)}</p>
            {data.optimal_entry_range && (
              <p className="text-xs text-blue-600 mt-1">
                Rango óptimo: {data.optimal_entry_range.min.toFixed(2)} - {data.optimal_entry_range.max.toFixed(2)}
              </p>
            )}
          </div>

          {data.stop_loss && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-red-900 mb-2">Stop Loss</h4>
              <p className="text-2xl font-bold text-red-700">{data.stop_loss.toFixed(2)}</p>
              <p className="text-xs text-red-600 mt-1">
                Riesgo: {Math.abs(((data.stop_loss - data.entry_price!) / data.entry_price!) * 100).toFixed(2)}%
              </p>
            </div>
          )}

          {data.take_profit_1 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-green-900 mb-2">Take Profit 1</h4>
              <p className="text-2xl font-bold text-green-700">{data.take_profit_1.toFixed(2)}</p>
              <p className="text-xs text-green-600 mt-1">
                Ganancia: {Math.abs(((data.take_profit_1 - data.entry_price!) / data.entry_price!) * 100).toFixed(2)}%
              </p>
            </div>
          )}

          {data.take_profit_2 && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-emerald-900 mb-2">Take Profit 2</h4>
              <p className="text-2xl font-bold text-emerald-700">{data.take_profit_2.toFixed(2)}</p>
              <p className="text-xs text-emerald-600 mt-1">
                Ganancia: {Math.abs(((data.take_profit_2 - data.entry_price!) / data.entry_price!) * 100).toFixed(2)}%
              </p>
            </div>
          )}
        </div>
      )}

      {/* Análisis Técnico - RSI, EMAs, S/R */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Análisis Técnico (H4)</h3>
        
        {/* RSI */}
        {data.h4_rsi !== null && data.h4_rsi !== undefined && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">RSI</span>
              <span className={`text-lg font-bold ${
                data.h4_rsi > 70 ? 'text-red-600' : 
                data.h4_rsi < 30 ? 'text-green-600' : 
                'text-gray-700'
              }`}>
                {data.h4_rsi.toFixed(2)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full ${
                  data.h4_rsi > 70 ? 'bg-red-500' : 
                  data.h4_rsi < 30 ? 'bg-green-500' : 
                  'bg-blue-500'
                }`}
                style={{ width: `${data.h4_rsi}%` }}
              ></div>
            </div>
            {data.h4_rsi_zone && (
              <p className="text-xs text-blue-600 mt-1">
                En zona objetivo: {data.h4_rsi_zone}
              </p>
            )}
          </div>
        )}

        {/* EMAs */}
        {(data.h4_ema_50 || data.h4_ema_100 || data.h4_ema_200) && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">EMAs</p>
            <div className="grid grid-cols-3 gap-2">
              {data.h4_ema_50 && (
                <div className="bg-white rounded p-2 border border-gray-200">
                  <p className="text-xs text-gray-500">EMA 50</p>
                  <p className="text-sm font-semibold text-gray-800">
                    {data.h4_ema_50.toFixed(2)}
                  </p>
                </div>
              )}
              {data.h4_ema_100 && (
                <div className="bg-white rounded p-2 border border-gray-200">
                  <p className="text-xs text-gray-500">EMA 100</p>
                  <p className="text-sm font-semibold text-gray-800">
                    {data.h4_ema_100.toFixed(2)}
                  </p>
                </div>
              )}
              {data.h4_ema_200 && (
                <div className="bg-white rounded p-2 border border-gray-200">
                  <p className="text-xs text-gray-500">EMA 200</p>
                  <p className="text-sm font-semibold text-gray-800">
                    {data.h4_ema_200.toFixed(2)}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Soporte y Resistencia */}
        {(data.support_level || data.resistance_level) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.support_level && (
              <div className={`bg-white rounded-lg p-4 border-2 ${
                data.price_near_support ? 'border-green-400 bg-green-50' : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-gray-500">Soporte</p>
                  {data.price_near_support && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Cerca
                    </span>
                  )}
                </div>
                <p className="text-lg font-semibold text-gray-800">
                  {data.support_level.toFixed(2)}
                </p>
              </div>
            )}
            {data.resistance_level && (
              <div className={`bg-white rounded-lg p-4 border-2 ${
                data.price_near_resistance ? 'border-red-400 bg-red-50' : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-gray-500">Resistencia</p>
                  {data.price_near_resistance && (
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                      Cerca
                    </span>
                  )}
                </div>
                <p className="text-lg font-semibold text-gray-800">
                  {data.resistance_level.toFixed(2)}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Tendencias por timeframe */}
        {(data.daily_trend || data.h4_trend || data.h1_trend) && (
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Tendencias</p>
            <div className="flex flex-wrap gap-2">
              {data.daily_trend && (
                <span className="text-xs bg-white px-3 py-1 rounded-full border border-gray-200">
                  Daily: <span className="font-semibold capitalize">{data.daily_trend}</span>
                </span>
              )}
              {data.h4_trend && (
                <span className="text-xs bg-white px-3 py-1 rounded-full border border-gray-200">
                  H4: <span className="font-semibold capitalize">{data.h4_trend}</span>
                </span>
              )}
              {data.h1_trend && (
                <span className="text-xs bg-white px-3 py-1 rounded-full border border-gray-200">
                  H1: <span className="font-semibold capitalize">{data.h1_trend}</span>
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Chart de Niveles con Velas */}
      <EntryPointChart
        currentPrice={data.current_price}
        supportLevel={data.support_level}
        resistanceLevel={data.resistance_level}
        entryPrice={data.entry_price}
        stopLoss={data.stop_loss}
        takeProfit1={data.take_profit_1}
        takeProfit2={data.take_profit_2}
        ema50={data.h4_ema_50}
        ema100={data.h4_ema_100}
        ema200={data.h4_ema_200}
        candles={technicalData?.chart_candles || []}
        onPointAdded={(price, type) => {
          console.log(`Punto agregado: ${type} a ${price.toFixed(2)}`);
        }}
      />

      {/* Contexto del mercado */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Contexto de Mercado</p>
            <p className="text-lg font-semibold text-gray-900 capitalize">{data.market_context}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Modo de Trading</p>
            <p className="text-lg font-semibold text-gray-900 capitalize">{data.trading_mode}</p>
          </div>
        </div>
      </div>

      {/* Razones */}
      {data.reasons.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
            Razones de la Recomendación
          </h3>
          <ul className="space-y-2">
            {data.reasons.map((reason, index) => (
              <li
                key={index}
                className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border-l-3 border-gray-300"
              >
                <span className="text-gray-400 font-bold text-sm mt-0.5">•</span>
                <span className="text-sm text-gray-700 flex-1">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Advertencias */}
      {data.warnings.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-yellow-700 mb-3 uppercase tracking-wide">
            Advertencias
          </h3>
          <div className="space-y-2">
            {data.warnings.map((warning, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-400"
              >
                <span className="text-yellow-600 font-bold text-sm mt-0.5">⚠</span>
                <span className="text-sm text-yellow-800 flex-1">{warning}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Explicación detallada */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
          Análisis Detallado
        </h3>
        <div className="text-sm text-gray-600 space-y-1 whitespace-pre-line">
          {data.detailed_explanation.split("\n").map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </div>
    </section>
  );
}


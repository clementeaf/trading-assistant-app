import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { TradeRecommendation } from "../types/api";
import { getTradingRecommendation } from "../services/api";

/**
 * Componente que muestra la recomendación completa de trading con niveles de precio
 */
export function TradingRecommendation(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<TradeRecommendation>({
    queryKey: ["tradingRecommendation", "XAUUSD", "US10Y"],
    queryFn: () => getTradingRecommendation("XAUUSD", "US10Y"),
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

      {/* Niveles de soporte y resistencia */}
      {(data.support_level || data.resistance_level) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {data.support_level && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-purple-900 mb-2">Soporte</h4>
              <p className="text-xl font-bold text-purple-700">{data.support_level.toFixed(2)}</p>
            </div>
          )}
          {data.resistance_level && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-orange-900 mb-2">Resistencia</h4>
              <p className="text-xl font-bold text-orange-700">{data.resistance_level.toFixed(2)}</p>
            </div>
          )}
        </div>
      )}

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


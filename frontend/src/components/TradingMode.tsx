import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { TradingModeRecommendation } from "../types/api";
import { getTradingModeRecommendation } from "../services/api";

/**
 * Componente que muestra la recomendación del modo de trading
 */
export function TradingMode(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<TradingModeRecommendation>({
    queryKey: ["tradingMode", "XAUUSD", "US10Y"],
    queryFn: () => getTradingModeRecommendation("XAUUSD", "US10Y"),
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

  const modeLabels: Record<string, string> = {
    calma: "Calma",
    agresivo: "Agresivo",
    muy_calma: "Muy Calma",
    observar: "Observar",
  };

  const modeStyles: Record<string, { bg: string; border: string; text: string }> = {
    calma: {
      bg: "bg-yellow-50",
      border: "border-yellow-400",
      text: "text-yellow-800",
    },
    agresivo: {
      bg: "bg-blue-50",
      border: "border-blue-400",
      text: "text-blue-800",
    },
    muy_calma: {
      bg: "bg-red-50",
      border: "border-red-400",
      text: "text-red-800",
    },
    observar: {
      bg: "bg-orange-50",
      border: "border-orange-400",
      text: "text-orange-800",
    },
  };

  const style = modeStyles[data.mode] || modeStyles.calma;

  return (
    <section className={`bg-white rounded-lg shadow-sm border-2 ${style.border} p-6`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Modo de Trading Recomendado</h2>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          Confianza: {(data.confidence * 100).toFixed(0)}%
        </span>
      </div>

      <div className={`${style.bg} ${style.border} border-l-4 rounded-lg p-4 mb-6`}>
        <div className="flex items-center justify-between">
          <h3 className={`text-2xl font-bold ${style.text}`}>
            {modeLabels[data.mode] || data.mode}
          </h3>
        </div>
        <p className="text-sm text-gray-600 mt-2">{data.summary}</p>
      </div>

      {data.reasons.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
            Motivos
          </h3>
          <ul className="space-y-2">
            {data.reasons.map((reason, index) => (
              <li
                key={index}
                className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border-l-3 border-gray-300"
              >
                <span className="text-gray-400 font-bold text-sm mt-0.5">•</span>
                <span className="text-sm text-gray-700 flex-1">{reason.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
          Explicación Detallada
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

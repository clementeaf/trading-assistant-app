import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { DailyMarketAnalysis } from "../types/api";
import { getYesterdayAnalysis } from "../services/api";

/**
 * Componente que muestra el análisis del día anterior
 */
export function YesterdayAnalysis(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<DailyMarketAnalysis>({
    queryKey: ["yesterdayAnalysis", "XAUUSD"],
    queryFn: () => getYesterdayAnalysis("XAUUSD"),
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
        <p className="text-red-800 font-medium">Error al cargar análisis</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : "Error desconocido"}
        </p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const changeClass =
    data.daily_change_percent > 0
      ? "text-green-600"
      : data.daily_change_percent < 0
        ? "text-red-600"
        : "text-gray-600";

  const directionLabels: Record<string, string> = {
    alcista: "↗",
    bajista: "↘",
    lateral: "→",
  };

  return (
    <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Análisis de Ayer - {data.instrument}
          </h2>
          <p className="text-sm text-gray-500 mt-1">Fecha: {data.date}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p className="text-xs text-gray-600 uppercase tracking-wide mb-1">Cierre</p>
          <p className="text-xl font-bold text-gray-900">{data.current_day_close.toFixed(2)}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p className="text-xs text-gray-600 uppercase tracking-wide mb-1">Cambio</p>
          <p className={`text-xl font-bold ${changeClass} flex items-center gap-1`}>
            {data.daily_change_percent > 0 ? "+" : ""}
            {data.daily_change_percent.toFixed(2)}%
            <span className="text-lg">{directionLabels[data.daily_direction]}</span>
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p className="text-xs text-gray-600 uppercase tracking-wide mb-1">Dirección</p>
          <p className="text-xl font-semibold text-gray-700 capitalize">{data.daily_direction}</p>
        </div>
      </div>

      {data.sessions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
            Sesiones de Trading
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.sessions.map((session, index) => {
              const sessionDirection =
                session.direction === "alcista"
                  ? "text-green-600"
                  : session.direction === "bajista"
                    ? "text-red-600"
                    : "text-gray-600";

              return (
                <div
                  key={index}
                  className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900 capitalize">{session.session}</h4>
                    <span className="text-xs text-gray-500">
                      {session.start_time} - {session.end_time}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Rango:</span>
                      <span className="font-medium text-gray-900">{session.range_value.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cambio:</span>
                      <span className={`font-medium ${sessionDirection}`}>
                        {session.change_percent > 0 ? "+" : ""}
                        {session.change_percent.toFixed(2)}%
                      </span>
                    </div>
                    {(session.broke_previous_high || session.broke_previous_low) && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        {session.broke_previous_high && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded mr-1">
                            ↑ Máximo
                          </span>
                        )}
                        {session.broke_previous_low && (
                          <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded">
                            ↓ Mínimo
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-2 italic">{session.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
        <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
          {data.summary}
        </p>
      </div>
    </section>
  );
}

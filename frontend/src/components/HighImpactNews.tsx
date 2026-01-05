import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { HighImpactNewsResponse } from "../types/api";
import { getHighImpactNews } from "../services/api";

/**
 * Componente que muestra las noticias de alto impacto para XAUUSD
 */
export function HighImpactNews(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<HighImpactNewsResponse>({
    queryKey: ["highImpactNews", "USD"],
    queryFn: () => getHighImpactNews("USD"),
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm p-6">
        <p className="text-red-800 font-medium">Error al cargar noticias</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : "Error desconocido"}
        </p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Noticias de Alto Impacto
        </h2>
        {data.has_high_impact_news && (
          <span className="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-1 rounded-full">
            {data.count} evento{data.count !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      <p className="text-gray-700 mb-4 leading-relaxed">{data.summary}</p>

      {data.has_high_impact_news && data.events.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
            Eventos Programados
          </h3>
          <ul className="space-y-2">
            {data.events.map((event, index) => (
              <li
                key={index}
                className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500"
              >
                <div className="flex-1">
                  <span className="font-medium text-gray-900">{event.description}</span>
                  {event.country && (
                    <span className="text-xs text-gray-500 ml-2">({event.country})</span>
                  )}
                </div>
                <span className="text-sm font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded">
                  {new Date(event.date).toLocaleTimeString("es-ES", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!data.has_high_impact_news && (
        <div className="text-center py-4 text-gray-500 text-sm">
          No hay noticias de alto impacto para hoy
        </div>
      )}
    </section>
  );
}

import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { EventScheduleResponse } from "../types/api";
import { getEventSchedule } from "../services/api";

/**
 * Componente que muestra el calendario de eventos económicos
 */
export function EventSchedule(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<EventScheduleResponse>({
    queryKey: ["eventSchedule", "USD"],
    queryFn: () => getEventSchedule("USD"),
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
        <p className="text-red-800 font-medium">Error al cargar calendario</p>
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
        <h2 className="text-lg font-semibold text-gray-900">Calendario de Eventos</h2>
        <div className="flex gap-2 text-xs">
          <span className="bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full">
            {data.total_events} total
          </span>
          {data.usd_events_count > 0 && (
            <span className="bg-red-100 text-red-800 px-2.5 py-1 rounded-full font-semibold">
              {data.usd_events_count} USD
            </span>
          )}
        </div>
      </div>

      {data.events.length > 0 ? (
        <div className="space-y-2">
          <ul className="space-y-2">
            {data.events.map((event, index) => (
              <li
                key={index}
                className={`p-3 rounded-lg border-l-4 ${
                  event.affects_usd
                    ? "bg-red-50 border-red-500"
                    : "bg-gray-50 border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">{event.description}</span>
                      {event.affects_usd && (
                        <span className="bg-red-200 text-red-800 text-xs font-semibold px-1.5 py-0.5 rounded">
                          USD
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-600">
                      {event.currency} • {event.impact}
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-gray-700 bg-white px-2 py-1 rounded border">
                    {event.time}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="text-center py-4 text-gray-500 text-sm">
          No hay eventos programados para hoy
        </div>
      )}
    </section>
  );
}

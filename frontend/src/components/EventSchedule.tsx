import React, { useEffect, useState } from "react";
import type { EventScheduleResponse } from "../types/api";
import { getEventSchedule } from "../services/api";

/**
 * Componente que muestra el calendario de eventos económicos
 */
export function EventSchedule(): React.JSX.Element | null {
  const [data, setData] = useState<EventScheduleResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData(): Promise<void> {
      try {
        setLoading(true);
        const response = await getEventSchedule("USD");
        setData(response);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="section">Cargando calendario...</div>;
  }

  if (error) {
    return <div className="section error">Error: {error}</div>;
  }

  if (!data) {
    return null;
  }

  return (
    <section className="section">
      <h2>Calendario de Eventos</h2>
      <p className="info">
        {data.total_events} eventos totales, {data.usd_events_count} afectan al
        USD
      </p>
      {data.events.length > 0 ? (
        <ul className="schedule-list">
          {data.events.map((event, index) => (
            <li
              key={index}
              className={`schedule-item ${event.affects_usd ? "usd-event" : ""}`}
            >
              {event.full_description}
            </li>
          ))}
        </ul>
      ) : (
        <p>No hay eventos programados para hoy.</p>
      )}
    </section>
  );
}


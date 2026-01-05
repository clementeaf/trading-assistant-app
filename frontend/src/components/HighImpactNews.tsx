import React, { useEffect, useState } from "react";
import type { HighImpactNewsResponse } from "../types/api";
import { getHighImpactNews } from "../services/api";

/**
 * Componente que muestra las noticias de alto impacto para XAUUSD
 */
export function HighImpactNews(): React.JSX.Element | null {
  const [data, setData] = useState<HighImpactNewsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData(): Promise<void> {
      try {
        setLoading(true);
        const response = await getHighImpactNews("USD");
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
    return <div className="section">Cargando noticias...</div>;
  }

  if (error) {
    return <div className="section error">Error: {error}</div>;
  }

  if (!data) {
    return null;
  }

  return (
    <section className="section">
      <h2>Noticias de Alto Impacto para XAUUSD</h2>
      <p className="summary">{data.summary}</p>
      {data.has_high_impact_news && data.events.length > 0 && (
        <ul className="events-list">
          {data.events.map((event, index) => (
            <li key={index} className="event-item">
              <strong>{event.description}</strong>
              <span className="event-time">
                {new Date(event.date).toLocaleTimeString("es-ES", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}


import React, { useEffect, useState } from "react";
import type { DailyMarketAnalysis } from "../types/api";
import { getYesterdayAnalysis } from "../services/api";

/**
 * Componente que muestra el análisis del día anterior
 */
export function YesterdayAnalysis(): React.JSX.Element | null {
  const [data, setData] = useState<DailyMarketAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData(): Promise<void> {
      try {
        setLoading(true);
        const response = await getYesterdayAnalysis("XAUUSD");
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
    return <div className="section">Cargando análisis...</div>;
  }

  if (error) {
    return <div className="section error">Error: {error}</div>;
  }

  if (!data) {
    return null;
  }

  const changeClass =
    data.daily_change_percent > 0
      ? "positive"
      : data.daily_change_percent < 0
        ? "negative"
        : "neutral";

  return (
    <section className="section">
      <h2>Análisis de Ayer - {data.instrument}</h2>
      <div className="daily-summary">
        <p>
          Cierre: <strong>{data.current_day_close.toFixed(2)}</strong>
        </p>
        <p className={changeClass}>
          Cambio: {data.daily_change_percent > 0 ? "+" : ""}
          {data.daily_change_percent.toFixed(2)}% ({data.daily_direction})
        </p>
      </div>
      {data.sessions.length > 0 && (
        <div className="sessions">
          <h3>Sesiones</h3>
          {data.sessions.map((session, index) => (
            <div key={index} className="session-item">
              <p>
                <strong>{session.session}</strong> ({session.start_time} -{" "}
                {session.end_time})
              </p>
              <p className="session-description">{session.description}</p>
            </div>
          ))}
        </div>
      )}
      <p className="summary-text">{data.summary}</p>
    </section>
  );
}


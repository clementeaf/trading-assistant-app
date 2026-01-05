import React, { useEffect, useState } from "react";
import type { TradingModeRecommendation } from "../types/api";
import { getTradingModeRecommendation } from "../services/api";

/**
 * Componente que muestra la recomendación del modo de trading
 */
export function TradingMode(): React.JSX.Element | null {
  const [data, setData] = useState<TradingModeRecommendation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData(): Promise<void> {
      try {
        setLoading(true);
        const response = await getTradingModeRecommendation("XAUUSD", "US10Y");
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
    return <div className="section">Cargando recomendación...</div>;
  }

  if (error) {
    return <div className="section error">Error: {error}</div>;
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

  const modeClass = `mode-${data.mode}`;

  return (
    <section className="section trading-mode">
      <h2>Modo de Trading Recomendado</h2>
      <div className={`mode-badge ${modeClass}`}>
        <strong>{modeLabels[data.mode] || data.mode}</strong>
        <span className="confidence">
          Confianza: {(data.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="reasons">
        <h3>Motivos:</h3>
        <ul>
          {data.reasons.map((reason, index) => (
            <li key={index}>{reason.description}</li>
          ))}
        </ul>
      </div>
      <div className="detailed-explanation">
        {data.detailed_explanation.split("\n").map((line, index) => (
          <p key={index}>{line}</p>
        ))}
      </div>
    </section>
  );
}


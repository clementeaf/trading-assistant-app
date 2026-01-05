import React, { useEffect, useState } from "react";
import type { MarketAlignmentAnalysis } from "../types/api";
import { getDxyBondAlignment } from "../services/api";

/**
 * Componente que muestra el análisis de alineación DXY-Bonos
 */
export function DxyBondAlignment(): React.JSX.Element | null {
  const [data, setData] = useState<MarketAlignmentAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData(): Promise<void> {
      try {
        setLoading(true);
        const response = await getDxyBondAlignment("US10Y");
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
    return <div className="section">Cargando alineación...</div>;
  }

  if (error) {
    return <div className="section error">Error: {error}</div>;
  }

  if (!data) {
    return null;
  }

  const alignmentClass =
    data.alignment === "alineados" ? "aligned" : "conflict";

  return (
    <section className="section">
      <h2>Alineación DXY - Bonos</h2>
      <div className="alignment-data">
        <div className="instrument-data">
          <p>
            <strong>DXY:</strong> {data.dxy.price.toFixed(2)} (
            {data.dxy.change_percent > 0 ? "+" : ""}
            {data.dxy.change_percent.toFixed(2)}%)
          </p>
          <p>
            <strong>{data.bond.symbol}:</strong> {data.bond.price.toFixed(2)} (
            {data.bond.change_percent > 0 ? "+" : ""}
            {data.bond.change_percent.toFixed(2)}%)
          </p>
        </div>
        <p className={`alignment-status ${alignmentClass}`}>
          Estado: {data.alignment === "alineados" ? "Alineados" : "En conflicto"}
        </p>
        <p className="bias">Sesgo: {data.market_bias}</p>
      </div>
      <p className="summary-text">{data.summary}</p>
    </section>
  );
}


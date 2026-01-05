import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { MarketAlignmentAnalysis } from "../types/api";
import { getDxyBondAlignment } from "../services/api";

/**
 * Componente que muestra el análisis de alineación DXY-Bonos
 */
export function DxyBondAlignment(): React.JSX.Element | null {
  const { data, isLoading, error } = useQuery<MarketAlignmentAnalysis>({
    queryKey: ["dxyBondAlignment", "US10Y"],
    queryFn: () => getDxyBondAlignment("US10Y"),
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
        <p className="text-red-800 font-medium">Error al cargar alineación</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : "Error desconocido"}
        </p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const isAligned = data.alignment === "alineados";
  const alignmentBg = isAligned ? "bg-green-50" : "bg-red-50";
  const alignmentBorder = isAligned ? "border-green-500" : "border-red-500";
  const alignmentText = isAligned ? "text-green-800" : "text-red-800";

  const biasLabels: Record<string, { label: string; color: string }> = {
    "risk-on": { label: "Risk-On", color: "bg-blue-100 text-blue-800" },
    "risk-off": { label: "Risk-Off", color: "bg-orange-100 text-orange-800" },
    mixto: { label: "Mixto", color: "bg-gray-100 text-gray-800" },
  };

  const bias = biasLabels[data.market_bias] || biasLabels.mixto;

  return (
    <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Alineación DXY - Bonos</h2>
        <span className={`${bias.color} text-xs font-semibold px-3 py-1 rounded-full`}>
          {bias.label}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">{data.dxy.symbol}</span>
            <span
              className={`text-xs font-semibold px-2 py-1 rounded ${
                data.dxy.change_percent > 0
                  ? "bg-green-100 text-green-800"
                  : data.dxy.change_percent < 0
                    ? "bg-red-100 text-red-800"
                    : "bg-gray-100 text-gray-800"
              }`}
            >
              {data.dxy.change_percent > 0 ? "+" : ""}
              {data.dxy.change_percent.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{data.dxy.price.toFixed(2)}</span>
            <span className="text-xs text-gray-500">
              Anterior: {data.dxy.previous_price.toFixed(2)}
            </span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">{data.bond.symbol}</span>
            <span
              className={`text-xs font-semibold px-2 py-1 rounded ${
                data.bond.change_percent > 0
                  ? "bg-green-100 text-green-800"
                  : data.bond.change_percent < 0
                    ? "bg-red-100 text-red-800"
                    : "bg-gray-100 text-gray-800"
              }`}
            >
              {data.bond.change_percent > 0 ? "+" : ""}
              {data.bond.change_percent.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{data.bond.price.toFixed(2)}</span>
            <span className="text-xs text-gray-500">
              Anterior: {data.bond.previous_price.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      <div className={`${alignmentBg} border-l-4 ${alignmentBorder} rounded-lg p-4`}>
        <div className="flex items-center justify-between mb-2">
          <span className={`font-semibold ${alignmentText} uppercase text-sm tracking-wide`}>
            Estado: {isAligned ? "Alineados" : "En Conflicto"}
          </span>
        </div>
        <p className="text-sm text-gray-700 leading-relaxed">{data.summary}</p>
      </div>
    </section>
  );
}

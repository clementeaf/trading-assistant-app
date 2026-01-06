import React from "react";
import { HighImpactNews } from "./components/HighImpactNews";
import { EventSchedule } from "./components/EventSchedule";
import { YesterdayAnalysis } from "./components/YesterdayAnalysis";
import { DxyBondAlignment } from "./components/DxyBondAlignment";
import { TradingMode } from "./components/TradingMode";
import { TradingRecommendation } from "./components/TradingRecommendation";

/**
 * Componente principal de la aplicación
 */
function App(): React.JSX.Element {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-slate-800 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-semibold">Trading Assistant - Market Briefing</h1>
          <p className="text-slate-300 text-sm mt-1">Análisis de mercado para XAUUSD</p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Sección principal: Recomendación de Trading con niveles */}
          <TradingRecommendation />
          
          {/* Modo de Trading */}
          <TradingMode />
          
          {/* Grid de 2 columnas para información complementaria */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HighImpactNews />
            <EventSchedule />
          </div>
          
          {/* Análisis del día anterior */}
          <YesterdayAnalysis />
          
          {/* Alineación DXY-Bonos */}
          <DxyBondAlignment />
        </div>
      </main>
    </div>
  );
}

export default App;

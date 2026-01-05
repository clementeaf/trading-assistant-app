import React from "react";
import { HighImpactNews } from "./components/HighImpactNews";
import { EventSchedule } from "./components/EventSchedule";
import { YesterdayAnalysis } from "./components/YesterdayAnalysis";
import { DxyBondAlignment } from "./components/DxyBondAlignment";
import { TradingMode } from "./components/TradingMode";
import "./App.css";

/**
 * Componente principal de la aplicación
 */
function App(): React.JSX.Element {
  return (
    <div className="app">
      <header className="header">
        <h1>Trading Assistant - Market Briefing</h1>
      </header>
      <main className="main">
        <TradingMode />
        <HighImpactNews />
        <EventSchedule />
        <YesterdayAnalysis />
        <DxyBondAlignment />
      </main>
    </div>
  );
}

export default App;

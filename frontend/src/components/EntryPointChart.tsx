import React, { useRef, useEffect, useState } from "react";

interface EntryPoint {
  id: string;
  price: number;
  type: "entry" | "stop_loss" | "take_profit";
  x: number;
  y: number;
}

interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface EntryPointChartProps {
  currentPrice: number;
  supportLevel?: number | null;
  resistanceLevel?: number | null;
  entryPrice?: number | null;
  stopLoss?: number | null;
  takeProfit1?: number | null;
  takeProfit2?: number | null;
  ema50?: number | null;
  ema100?: number | null;
  ema200?: number | null;
  candles?: Candle[];
  onPointAdded?: (price: number, type: string) => void;
}

/**
 * Componente de chart para visualizar niveles y dibujar puntos de entrada
 * NO lee datos de broker, solo permite dibujar puntos manualmente
 */
export function EntryPointChart({
  currentPrice,
  supportLevel,
  resistanceLevel,
  entryPrice,
  stopLoss,
  takeProfit1,
  takeProfit2,
  ema50,
  ema100,
  ema200,
  candles = [],
  onPointAdded,
}: EntryPointChartProps): React.JSX.Element {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawnPoints, setDrawnPoints] = useState<EntryPoint[]>([]);

  // Calcular rango de precios para el gráfico
  const allPrices = [
    currentPrice,
    supportLevel,
    resistanceLevel,
    entryPrice,
    stopLoss,
    takeProfit1,
    takeProfit2,
    ema50,
    ema100,
    ema200,
    ...(candles.length > 0 
      ? candles.flatMap(c => [c.high, c.low, c.open, c.close])
      : []
    ),
  ].filter((p): p is number => p !== null && p !== undefined);

  const minPrice = allPrices.length > 0 ? Math.min(...allPrices) * 0.995 : currentPrice * 0.99;
  const maxPrice = allPrices.length > 0 ? Math.max(...allPrices) * 1.005 : currentPrice * 1.01;
  const priceRange = maxPrice - minPrice;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;

    // Limpiar canvas
    ctx.clearRect(0, 0, width, height);

    // Fondo
    ctx.fillStyle = "#f9fafb";
    ctx.fillRect(0, 0, width, height);

    // Función para convertir precio a coordenada Y
    const priceToY = (price: number) => {
      return height - padding - ((price - minPrice) / priceRange) * (height - 2 * padding);
    };

    // Función para convertir coordenada Y a precio
    const yToPrice = (y: number) => {
      return maxPrice - ((y - padding) / (height - 2 * padding)) * priceRange;
    };

    // Dibujar líneas de precio
    const drawPriceLine = (price: number, color: string, label: string, style: string = "solid") => {
      if (price === null || price === undefined) return;

      const y = priceToY(price);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.setLineDash(style === "dashed" ? [5, 5] : []);

      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      // Etiqueta
      ctx.fillStyle = color;
      ctx.font = "12px sans-serif";
      ctx.fillText(`${label}: ${price.toFixed(2)}`, width - padding - 100, y - 5);
    };

    // Dibujar velas japonesas si hay datos
    if (candles.length > 0) {
      const sortedCandles = [...candles].sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
      
      const candleWidth = (width - 2 * padding) / sortedCandles.length;
      const candleSpacing = candleWidth * 0.1;
      const actualCandleWidth = candleWidth - candleSpacing;
      
      sortedCandles.forEach((candle, index) => {
        const x = padding + index * candleWidth + candleSpacing / 2;
        const openY = priceToY(candle.open);
        const closeY = priceToY(candle.close);
        const highY = priceToY(candle.high);
        const lowY = priceToY(candle.low);
        
        const isBullish = candle.close >= candle.open;
        const color = isBullish ? "#10b981" : "#ef4444";
        
        // Sombra (wick)
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x + actualCandleWidth / 2, highY);
        ctx.lineTo(x + actualCandleWidth / 2, lowY);
        ctx.stroke();
        
        // Cuerpo de la vela
        const bodyTop = Math.min(openY, closeY);
        const bodyHeight = Math.abs(closeY - openY) || 1;
        ctx.fillStyle = color;
        ctx.fillRect(x, bodyTop, actualCandleWidth, bodyHeight);
        
        // Borde del cuerpo
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.strokeRect(x, bodyTop, actualCandleWidth, bodyHeight);
      });
    } else {
      // Si no hay velas, dibujar línea de precio
      const sortedCandles = candles.length > 0 
        ? [...candles].sort((a, b) => 
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          )
        : [];
      
      if (sortedCandles.length > 0) {
        ctx.strokeStyle = "#3b82f6";
        ctx.lineWidth = 2;
        ctx.beginPath();
        sortedCandles.forEach((candle, index) => {
          const x = padding + (index / sortedCandles.length) * (width - 2 * padding);
          const y = priceToY(candle.close);
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
      }
    }

    // Dibujar niveles
    if (supportLevel) {
      drawPriceLine(supportLevel, "#10b981", "Soporte", "dashed");
    }
    if (resistanceLevel) {
      drawPriceLine(resistanceLevel, "#ef4444", "Resistencia", "dashed");
    }
    if (ema50) {
      drawPriceLine(ema50, "#3b82f6", "EMA 50", "dashed");
    }
    if (ema100) {
      drawPriceLine(ema100, "#8b5cf6", "EMA 100", "dashed");
    }
    if (ema200) {
      drawPriceLine(ema200, "#f59e0b", "EMA 200", "dashed");
    }

    // Dibujar precio actual
    drawPriceLine(currentPrice, "#1f2937", "Precio Actual", "solid");

    // Dibujar niveles de trading
    if (entryPrice) {
      drawPriceLine(entryPrice, "#3b82f6", "Entrada", "solid");
    }
    if (stopLoss) {
      drawPriceLine(stopLoss, "#ef4444", "Stop Loss", "solid");
    }
    if (takeProfit1) {
      drawPriceLine(takeProfit1, "#10b981", "TP1", "solid");
    }
    if (takeProfit2) {
      drawPriceLine(takeProfit2, "#10b981", "TP2", "solid");
    }

    // Dibujar puntos manuales
    drawnPoints.forEach((point) => {
      ctx.fillStyle =
        point.type === "entry"
          ? "#3b82f6"
          : point.type === "stop_loss"
          ? "#ef4444"
          : "#10b981";
      ctx.beginPath();
      ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Manejar clics para dibujar puntos
    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (x < padding || x > width - padding || y < padding || y > height - padding) {
        return;
      }

      const price = yToPrice(y);
      const newPoint: EntryPoint = {
        id: Date.now().toString(),
        price,
        type: "entry",
        x,
        y,
      };

      setDrawnPoints([...drawnPoints, newPoint]);
      onPointAdded?.(price, "entry");
    };

    canvas.addEventListener("click", handleClick);

    return () => {
      canvas.removeEventListener("click", handleClick);
    };
  }, [
    currentPrice,
    supportLevel,
    resistanceLevel,
    entryPrice,
    stopLoss,
    takeProfit1,
    takeProfit2,
    ema50,
    ema100,
    ema200,
    candles,
    drawnPoints,
    minPrice,
    maxPrice,
    priceRange,
    onPointAdded,
  ]);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Chart de Niveles</h3>
        <p className="text-xs text-gray-500">
          Haz clic en el gráfico para marcar puntos de entrada
        </p>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={400}
        className="w-full border border-gray-200 rounded cursor-crosshair"
      />
      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span>Soporte</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span>Resistencia</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span>EMA 50</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-purple-500 rounded"></div>
          <span>EMA 100</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-orange-500 rounded"></div>
          <span>EMA 200</span>
        </div>
      </div>
    </div>
  );
}


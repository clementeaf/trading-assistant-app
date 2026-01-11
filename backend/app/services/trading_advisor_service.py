"""
Servicio de asesoramiento de trading para XAUUSD
Analiza datos de mercado y genera recomendaciones de operativa con niveles de precio
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.utils.business_days import BusinessDays

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.market_alignment import MarketAlignmentAnalysis
from app.models.market_analysis import DailyMarketAnalysis, PriceCandle
from app.models.trading_mode import TradingMode, TradingModeRecommendation
from app.models.trading_recommendation import (
    TradeDirection, 
    TradeRecommendation, 
    RiskRewardDetails
)
from app.services.economic_calendar_service import EconomicCalendarService
from app.services.market_alignment_service import MarketAlignmentService
from app.services.market_analysis_service import MarketAnalysisService
from app.services.trading_mode_service import TradingModeService
from app.services.technical_analysis_service import TechnicalAnalysisService

logger = logging.getLogger(__name__)

# Disclaimer legal reforzado y prominente para recomendaciones de trading
DISCLAIMER_TEXT = """⚠️ ADVERTENCIA LEGAL IMPORTANTE ⚠️

ESTA NO ES ASESORÍA FINANCIERA - SOLO ANÁLISIS PROBABILÍSTICO

Esta recomendación es únicamente informativa y educativa. NO constituye asesoramiento financiero, de inversión o trading profesional. 

RIESGOS:
• El trading de instrumentos financieros conlleva un ALTO nivel de riesgo
• Puede perder TODO su capital invertido
• Los resultados pasados NO garantizan resultados futuros
• Las probabilidades NO son certezas

RESPONSABILIDAD:
• Usted es el ÚNICO responsable de sus decisiones de trading
• Debe consultar con un asesor financiero profesional antes de operar
• Solo opere con capital que pueda permitirse perder

Esta información se proporciona "tal cual" sin garantías de ningún tipo.
"""

# Ratio mínimo recomendado para operaciones
MINIMUM_RISK_REWARD_RATIO = 1.5


class TradingAdvisorService:
    """Servicio de asesoramiento de trading para XAUUSD"""
    
    def __init__(
        self,
        settings: Settings,
        market_analysis_service: MarketAnalysisService,
        market_alignment_service: MarketAlignmentService,
        trading_mode_service: TradingModeService,
        economic_calendar_service: EconomicCalendarService,
        technical_analysis_service: Optional[TechnicalAnalysisService] = None,
        db: Optional[Session] = None
    ):
        """
        Inicializa el servicio de asesoramiento de trading
        @param settings - Configuración de la aplicación
        @param market_analysis_service - Servicio de análisis de mercado
        @param market_alignment_service - Servicio de alineación de mercado
        @param trading_mode_service - Servicio de modo de trading
        @param economic_calendar_service - Servicio de calendario económico
        @param technical_analysis_service - Servicio de análisis técnico avanzado (opcional)
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.market_analysis_service = market_analysis_service
        self.market_alignment_service = market_alignment_service
        self.trading_mode_service = trading_mode_service
        self.economic_calendar_service = economic_calendar_service
        self.technical_analysis_service = technical_analysis_service
        self.db = db
    
    async def get_trading_recommendation(
        self,
        instrument: str = "XAUUSD",
        bond_symbol: str = "US10Y",
        time_window_minutes: int = 120
    ) -> TradeRecommendation:
        """
        Obtiene recomendación completa de trading con niveles de precio
        @param instrument - Instrumento a analizar (por defecto XAUUSD)
        @param bond_symbol - Símbolo del bono para análisis
        @param time_window_minutes - Ventana de tiempo para noticias próximas
        @returns Recomendación de trading con niveles
        """
        logger.info(f"Generating trading recommendation for {instrument}")
        
        # Obtener todos los datos necesarios
        yesterday_analysis = await self.market_analysis_service.analyze_yesterday_sessions(instrument)
        alignment_analysis = await self.market_alignment_service.analyze_dxy_bond_alignment(bond_symbol)
        trading_mode_rec = await self.trading_mode_service.get_trading_mode_recommendation(
            instrument, bond_symbol, time_window_minutes
        )
        high_impact_news = await self.economic_calendar_service.get_high_impact_news_today()
        
        # Análisis técnico avanzado multi-temporalidad (opcional)
        technical_analysis = None
        if self.technical_analysis_service:
            try:
                technical_analysis = await self.technical_analysis_service.analyze_multi_timeframe(instrument)
                logger.info("Advanced technical analysis completed")
            except Exception as e:
                logger.warning(f"Could not perform advanced technical analysis: {str(e)}")
        
        # Obtener precio actual (último cierre disponible)
        current_price = yesterday_analysis.current_day_close
        
        # Calcular niveles de soporte y resistencia
        support, resistance = self._calculate_support_resistance(yesterday_analysis)
        
        # Determinar dirección de trading
        direction, confidence = self._determine_trade_direction(
            yesterday_analysis,
            alignment_analysis,
            trading_mode_rec,
            current_price,
            support,
            resistance
        )
        
        # Calcular niveles de entrada, stop loss y take profit
        entry_price, stop_loss, take_profit_1, take_profit_2 = self._calculate_price_levels(
            direction,
            current_price,
            support,
            resistance,
            trading_mode_rec,
            yesterday_analysis
        )
        
        # Calcular rango óptimo de entrada
        optimal_range = self._calculate_optimal_entry_range(
            direction,
            entry_price,
            current_price,
            support,
            resistance
        )
        
        # Generar razones y explicación
        reasons, summary, detailed_explanation = self._generate_recommendation_text(
            direction,
            yesterday_analysis,
            alignment_analysis,
            trading_mode_rec,
            current_price,
            entry_price,
            stop_loss,
            take_profit_1,
            support,
            resistance
        )
        
        # Generar advertencias
        warnings = self._generate_warnings(
            high_impact_news,
            trading_mode_rec,
            time_window_minutes
        )
        
        # Obtener información temporal
        now = datetime.now()
        analysis_date = yesterday_analysis.date  # Fecha del último día hábil analizado
        analysis_datetime = now.isoformat()
        current_datetime = now.isoformat()
        
        # Extraer información del análisis técnico avanzado si está disponible
        daily_trend = None
        h4_trend = None
        h4_rsi = None
        h4_rsi_zone = None
        h4_impulse_direction = None
        h4_impulse_strong = None
        h4_impulse_distance_percent = None
        h1_trend = None
        price_near_support = None
        price_near_resistance = None
        
        if technical_analysis:
            daily_trend = technical_analysis.get("daily", {}).get("trend")
            h4_data = technical_analysis.get("h4", {})
            h4_trend = h4_data.get("trend")
            h4_rsi = h4_data.get("rsi")
            h4_rsi_zone = h4_data.get("rsi_zone")
            h4_impulse_direction = h4_data.get("impulse_direction")
            h4_impulse_strong = h4_data.get("impulse_strong")
            h4_impulse_distance_percent = h4_data.get("impulse_distance_percent")
            h1_trend = technical_analysis.get("h1", {}).get("trend")
            price_near_support = h4_data.get("near_support")
            price_near_resistance = h4_data.get("near_resistance")
            
            # EMAs de H4
            h4_ema_50 = h4_data.get("ema_50")
            h4_ema_100 = h4_data.get("ema_100")
            h4_ema_200 = h4_data.get("ema_200")
            
            # Usar soporte/resistencia del análisis técnico si está disponible
            h4_support = h4_data.get("support")
            h4_resistance = h4_data.get("resistance")
            if h4_support and not support:
                support = h4_support
            if h4_resistance and not resistance:
                resistance = h4_resistance
        
        # Calcular campos adicionales
        risk_reward_ratio = "N/A"
        risk_reward_details = None
        invalid_level = None
        
        if entry_price and stop_loss and take_profit_1:
            risk_reward_ratio, risk_reward_details = self._calculate_risk_reward_with_details(
                direction, entry_price, stop_loss, take_profit_1
            )
        
        if direction != TradeDirection.WAIT and stop_loss:
            invalid_level = self._determine_invalidation_level(direction, stop_loss)
            
        # Calcular desglose de confianza (estimado base + ajustes)
        # Base técnica: 50% (tendencia diaria, soporte/resistencia)
        tech_score = 0.5
        if yesterday_analysis.daily_direction.value == direction.value:
            tech_score += 0.2
        if price_near_support and direction == TradeDirection.BUY: 
            tech_score += 0.2
        if price_near_resistance and direction == TradeDirection.SELL:
            tech_score += 0.2
            
        # Base mercado: 30% (alineación, modo trading)
        market_score = 0.5
        if alignment_analysis.alignment.value == "alineados":
            # Si está alineado con la dirección recomendada
            if (alignment_analysis.market_bias.value == "risk-off" and direction == TradeDirection.SELL) or \
               (alignment_analysis.market_bias.value == "risk-on" and direction == TradeDirection.BUY):
                market_score += 0.3
        
        if trading_mode_rec.mode == TradingMode.AGGRESSIVE:
            market_score += 0.1
        elif trading_mode_rec.mode == TradingMode.CALM:
            market_score -= 0.1
            
        # Base noticias: 20%
        news_score = 0.9 if not high_impact_news.has_high_impact_news else 0.5
        
        # Limitar scores a 0-1
        tech_score = min(1.0, max(0.0, tech_score))
        market_score = min(1.0, max(0.0, market_score))
        
        confidence_breakdown = self._calculate_confidence_breakdown(
            tech_score, market_score, news_score
        )
        
        return TradeRecommendation(
            disclaimer=DISCLAIMER_TEXT.strip(),
            analysis_date=analysis_date,
            analysis_datetime=analysis_datetime,
            current_datetime=current_datetime,
            direction=direction,
            confidence=confidence,
            current_price=current_price,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            optimal_entry_range=optimal_range,
            support_level=support,
            resistance_level=resistance,
            market_context=alignment_analysis.market_bias.value,
            trading_mode=trading_mode_rec.mode.value,
            daily_trend=daily_trend,
            h4_trend=h4_trend,
            h4_rsi=h4_rsi,
            h4_rsi_zone=h4_rsi_zone,
            h4_impulse_direction=h4_impulse_direction,
            h4_impulse_strong=h4_impulse_strong,
            h4_impulse_distance_percent=h4_impulse_distance_percent,
            h1_trend=h1_trend,
            price_near_support=price_near_support,
            price_near_resistance=price_near_resistance,
            h4_ema_50=h4_ema_50,
            h4_ema_100=h4_ema_100,
            h4_ema_200=h4_ema_200,
            reasons=reasons,
            summary=summary,
            detailed_explanation=detailed_explanation,
            warnings=warnings,
            risk_reward_ratio=risk_reward_ratio,
            risk_reward_details=risk_reward_details,
            confidence_breakdown=confidence_breakdown,
            invalidation_level=invalid_level
        )
    
    def _calculate_support_resistance(
        self,
        analysis: DailyMarketAnalysis
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Calcula niveles de soporte y resistencia basados en datos históricos
        @param analysis - Análisis del día anterior
        @returns Tupla (support, resistance)
        """
        # Usar mínimo y máximo del día anterior como niveles base
        if analysis.previous_day_low and analysis.previous_day_high:
            support = analysis.previous_day_low
            resistance = analysis.previous_day_high
        else:
            # Si no hay datos del día anterior, usar el rango del día actual
            if analysis.sessions:
                all_lows = [s.low for s in analysis.sessions]
                all_highs = [s.high for s in analysis.sessions]
                support = min(all_lows) if all_lows else None
                resistance = max(all_highs) if all_highs else None
            else:
                support = None
                resistance = None
        
        # Ajustar niveles basándose en el precio actual
        if support and resistance and analysis.current_day_close:
            price = analysis.current_day_close
            # Si el precio está cerca del soporte, ajustar soporte hacia abajo
            if price < support * 1.01:  # Dentro del 1% del soporte
                support = support * 0.995  # Ajustar 0.5% hacia abajo
            # Si el precio está cerca de la resistencia, ajustar resistencia hacia arriba
            if price > resistance * 0.99:  # Dentro del 1% de la resistencia
                resistance = resistance * 1.005  # Ajustar 0.5% hacia arriba
        
        return support, resistance
    
    def _determine_trade_direction(
        self,
        analysis: DailyMarketAnalysis,
        alignment: MarketAlignmentAnalysis,
        trading_mode: TradingModeRecommendation,
        current_price: float,
        support: Optional[float],
        resistance: Optional[float]
    ) -> tuple[TradeDirection, float]:
        """
        Determina la dirección de trading recomendada
        @param analysis - Análisis del día anterior
        @param alignment - Análisis de alineación
        @param trading_mode - Recomendación de modo de trading
        @param current_price - Precio actual
        @param support - Nivel de soporte
        @param resistance - Nivel de resistencia
        @returns Tupla (dirección, confianza)
        """
        # Si el modo es muy calma u observar, recomendar esperar
        if trading_mode.mode in [TradingMode.VERY_CALM, TradingMode.OBSERVE]:
            return TradeDirection.WAIT, 0.7
        
        # Analizar dirección del mercado
        direction_score = 0.0
        buy_signals = 0
        sell_signals = 0
        
        # Señal 1: Dirección del día anterior
        if analysis.daily_direction.value == "alcista":
            buy_signals += 1
            direction_score += 0.3
        elif analysis.daily_direction.value == "bajista":
            sell_signals += 1
            direction_score -= 0.3
        
        # Señal 2: Alineación DXY-Bonos (correlación inversa con XAUUSD)
        if alignment.alignment.value == "alineados":
            if alignment.market_bias.value == "risk-off":
                # DXY y bonos suben → XAUUSD tiende a bajar
                sell_signals += 1
                direction_score -= 0.4
            elif alignment.market_bias.value == "risk-on":
                # DXY y bonos bajan → XAUUSD tiende a subir
                buy_signals += 1
                direction_score += 0.4
        
        # Señal 3: Posición relativa a soporte/resistencia
        if support and resistance:
            price_position = (current_price - support) / (resistance - support)
            if price_position < 0.3:  # Cerca del soporte
                buy_signals += 1
                direction_score += 0.2
            elif price_position > 0.7:  # Cerca de la resistencia
                sell_signals += 1
                direction_score -= 0.2
        
        # Señal 4: Volatilidad y sesiones
        if analysis.sessions:
            bullish_sessions = sum(1 for s in analysis.sessions if s.direction.value == "alcista")
            bearish_sessions = sum(1 for s in analysis.sessions if s.direction.value == "bajista")
            
            if bullish_sessions > bearish_sessions:
                buy_signals += 1
                direction_score += 0.1
            elif bearish_sessions > bullish_sessions:
                sell_signals += 1
                direction_score -= 0.1
        
        # Determinar dirección final
        if direction_score > 0.2:
            direction = TradeDirection.BUY
            confidence = min(0.9, 0.5 + abs(direction_score) * 0.5)
        elif direction_score < -0.2:
            direction = TradeDirection.SELL
            confidence = min(0.9, 0.5 + abs(direction_score) * 0.5)
        else:
            direction = TradeDirection.WAIT
            confidence = 0.6
        
        # Ajustar confianza según modo de trading
        if trading_mode.mode == TradingMode.AGGRESSIVE:
            confidence = min(0.95, confidence + 0.1)
        elif trading_mode.mode == TradingMode.CALM:
            confidence = max(0.4, confidence - 0.1)
        
        return direction, round(confidence, 2)
    
    def _calculate_price_levels(
        self,
        direction: TradeDirection,
        current_price: float,
        support: Optional[float],
        resistance: Optional[float],
        trading_mode_rec: TradingModeRecommendation,
        analysis: DailyMarketAnalysis
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Calcula niveles de entrada, stop loss y take profit
        @param direction - Dirección de trading
        @param current_price - Precio actual
        @param support - Nivel de soporte
        @param resistance - Nivel de resistencia
        @param trading_mode_rec - Recomendación de modo de trading
        @param analysis - Análisis del día anterior
        @returns Tupla (entry, stop_loss, take_profit_1, take_profit_2)
        """
        if direction == TradeDirection.WAIT:
            return None, None, None, None
        
        # Calcular ATR aproximado (rango promedio del día)
        if analysis.sessions:
            avg_range = sum(s.range_value for s in analysis.sessions) / len(analysis.sessions)
        else:
            avg_range = current_price * 0.01  # 1% por defecto
        
        # Calcular niveles según dirección
        if direction == TradeDirection.BUY:
            # Entrada: precio actual o ligeramente por debajo
            entry_price = current_price * 0.9995  # 0.05% por debajo para mejor entrada
            
            # Stop loss: por debajo del soporte o 1.5x ATR
            if support:
                stop_loss = min(support * 0.995, entry_price - avg_range * 1.5)
            else:
                stop_loss = entry_price - avg_range * 1.5
            
            # Take profit 1: resistencia o 1x ATR
            if resistance:
                take_profit_1 = min(resistance * 0.998, entry_price + avg_range)
            else:
                take_profit_1 = entry_price + avg_range
            
            # Take profit 2: 2x ATR o resistencia + margen
            if resistance:
                take_profit_2 = min(resistance * 1.002, entry_price + avg_range * 2)
            else:
                take_profit_2 = entry_price + avg_range * 2
        
        else:  # SELL
            # Entrada: precio actual o ligeramente por encima
            entry_price = current_price * 1.0005  # 0.05% por encima para mejor entrada
            
            # Stop loss: por encima de la resistencia o 1.5x ATR
            if resistance:
                stop_loss = max(resistance * 1.005, entry_price + avg_range * 1.5)
            else:
                stop_loss = entry_price + avg_range * 1.5
            
            # Take profit 1: soporte o 1x ATR
            if support:
                take_profit_1 = max(support * 1.002, entry_price - avg_range)
            else:
                take_profit_1 = entry_price - avg_range
            
            # Take profit 2: 2x ATR o soporte - margen
            if support:
                take_profit_2 = max(support * 0.998, entry_price - avg_range * 2)
            else:
                take_profit_2 = entry_price - avg_range * 2
        
        # Ajustar según modo de trading
        if trading_mode_rec.mode == TradingMode.AGGRESSIVE:
            # Take profit más ambicioso
            if direction == TradeDirection.BUY:
                take_profit_2 = take_profit_2 * 1.1
            else:
                take_profit_2 = take_profit_2 * 0.9
        elif trading_mode_rec.mode == TradingMode.CALM:
            # Stop loss más ajustado
            if direction == TradeDirection.BUY:
                stop_loss = stop_loss * 1.01
            else:
                stop_loss = stop_loss * 0.99
        
        return (
            round(entry_price, 2),
            round(stop_loss, 2),
            round(take_profit_1, 2),
            round(take_profit_2, 2) if take_profit_2 else None
        )
    
    def _calculate_optimal_entry_range(
        self,
        direction: TradeDirection,
        entry_price: Optional[float],
        current_price: float,
        support: Optional[float],
        resistance: Optional[float]
    ) -> Optional[dict[str, float]]:
        """
        Calcula el rango óptimo de entrada
        @param direction - Dirección de trading
        @param entry_price - Precio de entrada recomendado
        @param current_price - Precio actual
        @param support - Nivel de soporte
        @param resistance - Nivel de resistencia
        @returns Diccionario con min y max del rango óptimo
        """
        if direction == TradeDirection.WAIT or entry_price is None:
            return None
        
        # Rango de ±0.1% alrededor del precio de entrada
        range_percent = 0.001  # 0.1%
        
        if direction == TradeDirection.BUY:
            min_price = entry_price * (1 - range_percent)
            max_price = entry_price * (1 + range_percent)
            # Asegurar que no esté por debajo del soporte
            if support:
                min_price = max(min_price, support * 0.999)
        else:  # SELL
            min_price = entry_price * (1 - range_percent)
            max_price = entry_price * (1 + range_percent)
            # Asegurar que no esté por encima de la resistencia
            if resistance:
                max_price = min(max_price, resistance * 1.001)
        
        return {
            "min": round(min_price, 2),
            "max": round(max_price, 2)
        }
    
    def _generate_recommendation_text(
        self,
        direction: TradeDirection,
        analysis: DailyMarketAnalysis,
        alignment: MarketAlignmentAnalysis,
        trading_mode: TradingModeRecommendation,
        current_price: float,
        entry_price: Optional[float],
        stop_loss: Optional[float],
        take_profit_1: Optional[float],
        support: Optional[float],
        resistance: Optional[float]
    ) -> tuple[list[str], str, str]:
        """
        Genera razones, resumen y explicación detallada
        @param direction - Dirección de trading
        @param analysis - Análisis del día anterior
        @param alignment - Análisis de alineación
        @param trading_mode - Recomendación de modo
        @param current_price - Precio actual
        @param entry_price - Precio de entrada
        @param stop_loss - Stop loss
        @param take_profit_1 - Primer take profit
        @param support - Nivel de soporte
        @param resistance - Nivel de resistencia
        @returns Tupla (razones, resumen, explicación detallada)
        """
        reasons: list[str] = []
        
        # Razón 1: Dirección del día anterior
        if analysis.daily_direction.value == "alcista":
            reasons.append("Día anterior alcista, momentum positivo")
        elif analysis.daily_direction.value == "bajista":
            reasons.append("Día anterior bajista, momentum negativo")
        
        # Razón 2: Alineación DXY-Bonos
        if alignment.alignment.value == "alineados":
            if alignment.market_bias.value == "risk-off":
                reasons.append("DXY y bonos alineados (risk-off) → presión bajista en XAUUSD")
            elif alignment.market_bias.value == "risk-on":
                reasons.append("DXY y bonos alineados (risk-on) → presión alcista en XAUUSD")
        
        # Razón 3: Posición relativa a niveles
        if support and resistance:
            price_position = (current_price - support) / (resistance - support)
            if price_position < 0.3:
                reasons.append("Precio cerca del soporte, oportunidad de compra")
            elif price_position > 0.7:
                reasons.append("Precio cerca de la resistencia, oportunidad de venta")
        
        # Razón 4: Modo de trading
        if trading_mode.mode == TradingMode.AGGRESSIVE:
            reasons.append("Modo agresivo recomendado, condiciones favorables")
        elif trading_mode.mode == TradingMode.CALM:
            reasons.append("Modo calma recomendado, operativa conservadora")
        
        # Generar resumen
        direction_text = {
            TradeDirection.BUY: "COMPRA",
            TradeDirection.SELL: "VENTA",
            TradeDirection.WAIT: "ESPERAR"
        }[direction]
        
        summary = f"Recomendación: {direction_text}"
        if entry_price:
            summary += f" en {entry_price:.2f}"
        if stop_loss:
            summary += f" (SL: {stop_loss:.2f})"
        if take_profit_1:
            summary += f" (TP1: {take_profit_1:.2f})"
        
        # Generar explicación detallada
        explanation_parts = [f"Recomendación: {direction_text}"]
        
        if direction != TradeDirection.WAIT:
            explanation_parts.append(f"\nPrecio actual: {current_price:.2f}")
            if entry_price:
                explanation_parts.append(f"Entrada recomendada: {entry_price:.2f}")
            if stop_loss:
                explanation_parts.append(f"Stop Loss: {stop_loss:.2f}")
            if take_profit_1:
                explanation_parts.append(f"Take Profit 1: {take_profit_1:.2f}")
            if support:
                explanation_parts.append(f"Soporte identificado: {support:.2f}")
            if resistance:
                explanation_parts.append(f"Resistencia identificada: {resistance:.2f}")
        
        explanation_parts.append("\nRazones:")
        for reason in reasons:
            explanation_parts.append(f"• {reason}")
        
        explanation_parts.append(f"\nModo de trading: {trading_mode.mode.value}")
        explanation_parts.append(f"Contexto de mercado: {alignment.market_bias.value}")
        
        detailed_explanation = "\n".join(explanation_parts)
        
        return reasons, summary, detailed_explanation
    
    def _generate_warnings(
        self,
        high_impact_news,
        trading_mode: TradingModeRecommendation,
        time_window_minutes: int
    ) -> list[str]:
        """
        Genera advertencias importantes
        @param high_impact_news - Noticias de alto impacto
        @param trading_mode - Recomendación de modo
        @param time_window_minutes - Ventana de tiempo para noticias
        @returns Lista de advertencias
        """
        warnings: list[str] = []
        
        # Advertencia 1: Noticias próximas
        if high_impact_news.has_high_impact_news:
            upcoming_count = len([
                e for e in high_impact_news.events
                if e.importance.value == "high"
            ])
            if upcoming_count > 0:
                warnings.append(
                    f"Atención: {upcoming_count} noticia(s) de alto impacto USD próximas. "
                    "Considerar esperar o reducir tamaño de posición."
                )
        
        # Advertencia 2: Modo muy calma u observar
        if trading_mode.mode in [TradingMode.VERY_CALM, TradingMode.OBSERVE]:
            warnings.append(
                f"Modo {trading_mode.mode.value} activo. "
                "Se recomienda esperar mejores condiciones o reducir exposición."
            )
        
        # Advertencia 3: Baja confianza
        if trading_mode.confidence < 0.6:
            warnings.append(
                "Confianza baja en la recomendación. "
                "Considerar esperar señales más claras antes de operar."
            )
        
        return warnings

    def _calculate_risk_reward_with_details(
        self,
        direction: TradeDirection,
        entry: float,
        stop_loss: float,
        take_profit: float
    ) -> tuple[str, RiskRewardDetails]:
        """
        Calcula el ratio riesgo/recompensa con detalles completos
        @param direction - Dirección del trade
        @param entry - Precio de entrada
        @param stop_loss - Stop loss
        @param take_profit - Take profit
        @returns Tupla (ratio_string, detalles completos)
        """
        # Calcular puntos de riesgo y recompensa
        risk_points = abs(entry - stop_loss)
        reward_points = abs(take_profit - entry)
        
        # Calcular porcentajes
        risk_percentage = (risk_points / entry) * 100
        reward_percentage = (reward_points / entry) * 100
        
        # Calcular ratio
        ratio_value = reward_points / risk_points if risk_points > 0 else 0.0
        ratio_string = f"1:{ratio_value:.2f}"
        
        # Verificar si cumple ratio mínimo
        meets_minimum = ratio_value >= MINIMUM_RISK_REWARD_RATIO
        
        # Generar explicación detallada
        direction_text = "COMPRA" if direction == TradeDirection.BUY else "VENTA"
        explanation = (
            f"Para esta operación de {direction_text}:\n"
            f"• Riesgo: {risk_points:.2f} puntos ({risk_percentage:.2f}% del precio de entrada)\n"
            f"• Recompensa: {reward_points:.2f} puntos ({reward_percentage:.2f}% del precio de entrada)\n"
            f"• Ratio: {ratio_string}\n"
        )
        
        if meets_minimum:
            explanation += f"• ✓ Cumple el ratio mínimo recomendado de 1:{MINIMUM_RISK_REWARD_RATIO:.1f}"
        else:
            explanation += (
                f"• ⚠️ NO cumple el ratio mínimo recomendado de 1:{MINIMUM_RISK_REWARD_RATIO:.1f}\n"
                f"• Considerar ajustar niveles o esperar mejor oportunidad"
            )
        
        details = RiskRewardDetails(
            ratio=ratio_string,
            risk_points=round(risk_points, 2),
            reward_points=round(reward_points, 2),
            risk_percentage=round(risk_percentage, 2),
            reward_percentage=round(reward_percentage, 2),
            explanation=explanation,
            meets_minimum=meets_minimum
        )
        
        return ratio_string, details

    def _calculate_risk_reward_ratio(
        self,
        entry: float,
        stop_loss: float,
        take_profit: float
    ) -> str:
        """
        Calcula el ratio riesgo/recompensa (método legacy - mantener por compatibilidad)
        @param entry - Precio de entrada
        @param stop_loss - Stop loss
        @param take_profit - Take profit
        @returns Ratio formateado como '1:X.XX'
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        ratio = reward / risk if risk > 0 else 0.0
        return f"1:{ratio:.2f}"

    def _calculate_confidence_breakdown(
        self,
        technical_score: float,
        market_score: float,
        news_score: float
    ) -> dict[str, float]:
        """
        Calcula el desglose de confianza por factores
        @param technical_score - Puntuación de análisis técnico (0-1)
        @param market_score - Puntuación de contexto de mercado (0-1)
        @param news_score - Puntuación de impacto de noticias (0-1)
        @returns Diccionario con desglose
        """
        # Pesos ponderados para la confianza general
        # Técnico: 50%, Mercado: 30%, Noticias: 20%
        overall = (
            technical_score * 0.5 +
            market_score * 0.3 +
            news_score * 0.2
        )
        
        return {
            "technical_analysis": round(technical_score, 2),
            "market_context": round(market_score, 2),
            "news_impact": round(news_score, 2),
            "overall": round(overall, 2)
        }

    def _determine_invalidation_level(
        self,
        direction: TradeDirection,
        stop_loss: float
    ) -> float:
        """
        Determina el nivel de invalidación de la tesis
        @param direction - Dirección de trading
        @param stop_loss - Nivel de stop loss recomendado
        @returns Precio de invalidación
        """
        if direction == TradeDirection.BUY:
            # Para compras, invalidación ligeramente por debajo del stop
            return round(stop_loss * 0.998, 2)
        elif direction == TradeDirection.SELL:
            # Para ventas, invalidación ligeramente por encima del stop
            return round(stop_loss * 1.002, 2)
        else:
            return stop_loss


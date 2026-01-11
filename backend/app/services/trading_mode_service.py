"""
Servicio para determinar el modo de trading recomendado
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.economic_calendar import EconomicEvent, ImpactLevel
from app.models.market_alignment import MarketAlignmentAnalysis
from app.models.market_analysis import DailyMarketAnalysis
from app.models.trading_mode import (
    TradingMode,
    TradingModeReason,
    TradingModeRecommendation,
    OperationalLevel,
    LevelType
)
from app.services.economic_calendar_service import EconomicCalendarService
from app.services.market_alignment_service import MarketAlignmentService
from app.services.market_analysis_service import MarketAnalysisService
from app.utils.psychological_level_detector import PsychologicalLevelDetector

logger = logging.getLogger(__name__)


class TradingModeService:
    """Servicio para determinar el modo de trading recomendado"""
    
    def __init__(
        self,
        settings: Settings,
        economic_calendar_service: EconomicCalendarService,
        market_analysis_service: MarketAnalysisService,
        market_alignment_service: MarketAlignmentService,
        db: Optional[Session] = None
    ):
        """
        Inicializa el servicio de modo de trading
        @param settings - Configuración de la aplicación
        @param economic_calendar_service - Servicio de calendario económico
        @param market_analysis_service - Servicio de análisis de mercado
        @param market_alignment_service - Servicio de alineación de mercado
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.economic_calendar_service = economic_calendar_service
        self.market_analysis_service = market_analysis_service
        self.market_alignment_service = market_alignment_service
        self.db = db
        self.level_detector = PsychologicalLevelDetector()
    
    async def get_trading_mode_recommendation(
        self,
        instrument: str = "XAUUSD",
        bond_symbol: str = "US10Y",
        time_window_minutes: int = 120
    ) -> TradingModeRecommendation:
        """
        Obtiene la recomendación de modo de trading
        @param instrument - Instrumento a analizar (por defecto XAUUSD)
        @param bond_symbol - Símbolo del bono para análisis de alineación
        @param time_window_minutes - Ventana de tiempo en minutos para considerar noticias próximas
        @returns Recomendación de modo de trading
        """
        logger.info(f"Generating trading mode recommendation for {instrument}")
        
        # Obtener datos necesarios
        high_impact_news = await self.economic_calendar_service.get_high_impact_news_today()
        yesterday_analysis = await self.market_analysis_service.analyze_yesterday_sessions(instrument)
        alignment_analysis = await self.market_alignment_service.analyze_dxy_bond_alignment(bond_symbol)
        
        # Evaluar reglas
        reasons: list[TradingModeReason] = []
        mode_scores: dict[TradingMode, float] = {
            TradingMode.CALM: 0.0,
            TradingMode.AGGRESSIVE: 0.0,
            TradingMode.VERY_CALM: 0.0,
            TradingMode.OBSERVE: 0.0
        }
        
        # Regla 1: Noticias de alto impacto USD en próximas X horas → CALMA
        hours = time_window_minutes / 60
        upcoming_news = self._get_upcoming_high_impact_news(high_impact_news.events, hours=hours)
        if upcoming_news:
            hours_str = f"{int(hours)} horas" if hours >= 1 else f"{time_window_minutes} minutos"
            reasons.append(TradingModeReason(
                rule_name="Noticias próximas",
                description=f"{len(upcoming_news)} noticia(s) de alto impacto USD en las próximas {hours_str}",
                priority=10
            ))
            mode_scores[TradingMode.CALM] += 8.0
            mode_scores[TradingMode.VERY_CALM] += 5.0
        
        # Regla 2: Rango alto ayer + DXY y bonos alineados → AGRESIVO
        high_volatility = self._is_high_volatility(yesterday_analysis)
        if high_volatility and alignment_analysis.alignment.value == "alineados":
            reasons.append(TradingModeReason(
                rule_name="Volatilidad alta + alineación",
                description=f"Ayer hubo alta volatilidad y DXY/{bond_symbol} están alineados ({alignment_analysis.market_bias.value})",
                priority=9
            ))
            mode_scores[TradingMode.AGGRESSIVE] += 7.0
        
        # Regla 3: DXY y bonos en conflicto + sesiones mixtas + noticias → MUY CALMA/OBSERVAR
        if (alignment_analysis.alignment.value == "conflicto" and 
            self._has_mixed_sessions(yesterday_analysis) and 
            high_impact_news.has_high_impact_news):
            reasons.append(TradingModeReason(
                rule_name="Conflicto + sesiones mixtas + noticias",
                description=f"DXY y {bond_symbol} en conflicto, sesiones mixtas ayer, y hay noticias de alto impacto",
                priority=10
            ))
            mode_scores[TradingMode.VERY_CALM] += 9.0
            mode_scores[TradingMode.OBSERVE] += 8.0
        
        # Regla 4: Múltiples noticias de alto impacto → CALMA
        if high_impact_news.count >= 3:
            reasons.append(TradingModeReason(
                rule_name="Múltiples noticias",
                description=f"{high_impact_news.count} noticias de alto impacto hoy",
                priority=8
            ))
            mode_scores[TradingMode.CALM] += 6.0
        
        # Regla 5: Sin noticias + baja volatilidad + alineación clara → AGRESIVO
        if (not high_impact_news.has_high_impact_news and 
            not high_volatility and 
            alignment_analysis.alignment.value == "alineados"):
            reasons.append(TradingModeReason(
                rule_name="Condiciones favorables",
                description=f"Sin noticias importantes, baja volatilidad, y DXY/{bond_symbol} alineados",
                priority=7
            ))
            mode_scores[TradingMode.AGGRESSIVE] += 5.0
        
        # Determinar modo final
        final_mode = max(mode_scores.items(), key=lambda x: x[1])[0]
        
        # Si no hay razones, usar modo por defecto
        if not reasons:
            final_mode = TradingMode.CALM
            reasons.append(TradingModeReason(
                rule_name="Modo por defecto",
                description="No se aplicaron reglas específicas, usando modo conservador",
                priority=1
            ))
        
        # Calcular confianza basada en la diferencia de scores
        max_score = max(mode_scores.values())
        second_max = sorted(set(mode_scores.values()), reverse=True)[1] if len(set(mode_scores.values())) > 1 else 0
        confidence = min(1.0, (max_score - second_max) / 10.0 + 0.5) if max_score > 0 else 0.5
        
        # Ordenar razones por prioridad
        reasons.sort(key=lambda r: r.priority, reverse=True)
        
        # Calcular niveles operativos según el modo
        operational_levels = await self._calculate_operational_levels(
            mode=final_mode,
            instrument=instrument,
            yesterday_analysis=yesterday_analysis
        )
        
        # Generar resumen y explicación detallada
        summary, detailed_explanation = self._generate_summary(
            final_mode, reasons, upcoming_news, alignment_analysis, yesterday_analysis
        )
        
        recommendation = TradingModeRecommendation(
            mode=final_mode,
            confidence=round(confidence, 2),
            reasons=reasons,
            summary=summary,
            detailed_explanation=detailed_explanation,
            operational_levels=operational_levels
        )
        
        # Guardar recomendación en base de datos si está disponible
        if self.db:
            try:
                from app.repositories.analysis_repository import AnalysisRepository
                analysis_repo = AnalysisRepository(self.db)
                analysis_repo.save_trading_mode_recommendation(
                    recommendation=recommendation,
                    instrument=instrument,
                    bond_symbol=bond_symbol
                )
            except Exception as e:
                logger.warning(f"Error saving recommendation to database: {str(e)}")
        
        return recommendation
    
    def _get_upcoming_high_impact_news(
        self,
        events: list[EconomicEvent],
        hours: int = 2
    ) -> list[EconomicEvent]:
        """
        Obtiene noticias de alto impacto en las próximas horas
        @param events - Lista de eventos
        @param hours - Horas a considerar
        @returns Lista de eventos próximos
        """
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        upcoming = [
            event for event in events
            if event.importance == ImpactLevel.HIGH
            and event.date > now
            and event.date <= cutoff
            and event.currency.upper() == "USD"
        ]
        
        return sorted(upcoming, key=lambda e: e.date)
    
    def _is_high_volatility(self, analysis: DailyMarketAnalysis) -> bool:
        """
        Determina si hubo alta volatilidad ayer
        @param analysis - Análisis del día anterior
        @returns True si hubo alta volatilidad
        """
        if not analysis.sessions:
            return False
        
        # Calcular ATR aproximado (rango promedio de sesiones)
        avg_range = sum(s.range_value for s in analysis.sessions) / len(analysis.sessions)
        avg_price = analysis.current_day_close
        
        # Considerar alta volatilidad si el rango promedio es > 0.5% del precio
        volatility_threshold = avg_price * 0.005
        return avg_range > volatility_threshold
    
    def _has_mixed_sessions(self, analysis: DailyMarketAnalysis) -> bool:
        """
        Determina si las sesiones fueron mixtas (direcciones diferentes)
        @param analysis - Análisis del día anterior
        @returns True si hubo sesiones mixtas
        """
        if len(analysis.sessions) < 2:
            return False
        
        directions = [s.direction for s in analysis.sessions]
        unique_directions = set(directions)
        
        # Mixto si hay más de una dirección diferente
        return len(unique_directions) > 1
    
    def _generate_summary(
        self,
        mode: TradingMode,
        reasons: list[TradingModeReason],
        upcoming_news: list[EconomicEvent],
        alignment: MarketAlignmentAnalysis,
        yesterday_analysis: DailyMarketAnalysis
    ) -> tuple[str, str]:
        """
        Genera el resumen y explicación detallada
        @param mode - Modo recomendado
        @param reasons - Lista de razones
        @param upcoming_news - Noticias próximas
        @param alignment - Análisis de alineación
        @param yesterday_analysis - Análisis de ayer
        @returns Tupla (summary, detailed_explanation)
        """
        mode_names = {
            TradingMode.CALM: "Calma",
            TradingMode.AGGRESSIVE: "Agresivo",
            TradingMode.VERY_CALM: "Muy Calma",
            TradingMode.OBSERVE: "Observar"
        }
        
        mode_name = mode_names.get(mode, "Calma")
        summary = f"Modo sugerido hoy: {mode_name}."
        
        # Construir explicación detallada
        explanation_parts = [f"Modo sugerido hoy: {mode_name}.\nMotivos:"]
        
        # Agregar noticias próximas con formato específico
        if upcoming_news:
            for event in upcoming_news[:2]:  # Máximo 2 noticias próximas
                time_str = event.date.strftime("%H:%M")
                hours_until = (event.date - datetime.now()).total_seconds() / 3600
                if hours_until <= 2:
                    explanation_parts.append(f"• {event.description} en {int(hours_until * 60)} minutos (alto impacto USD)")
                else:
                    explanation_parts.append(f"• {event.description} a las {time_str} (alto impacto USD)")
        
        # Agregar información de alineación
        if alignment.alignment.value == "conflicto":
            explanation_parts.append(f"• DXY y {alignment.bond.symbol} en conflicto.")
        elif alignment.alignment.value == "alineados":
            explanation_parts.append(f"• DXY y {alignment.bond.symbol} alineados ({alignment.market_bias.value}).")
        
        # Agregar información de volatilidad y sesiones
        if self._is_high_volatility(yesterday_analysis):
            # Buscar sesión con mayor volatilidad
            max_range_session = max(yesterday_analysis.sessions, key=lambda s: s.range_value)
            session_names = {
                "asia": "Asia",
                "london": "Londres",
                "new_york": "NY"
            }
            session_name = session_names.get(max_range_session.session.value, max_range_session.session.value)
            explanation_parts.append(f"• Ayer hubo alta volatilidad en {session_name} con rango amplio.")
        
        # Agregar otras razones importantes
        for reason in reasons:
            if reason.rule_name not in ["Noticias próximas", "Volatilidad alta + alineación", "Conflicto + sesiones mixtas + noticias"]:
                explanation_parts.append(f"• {reason.description}")
        
        detailed_explanation = "\n".join(explanation_parts)
        
        return summary, detailed_explanation

    async def _calculate_operational_levels(
        self,
        mode: TradingMode,
        instrument: str,
        yesterday_analysis: DailyMarketAnalysis
    ) -> list[OperationalLevel]:
        """
        Calcula niveles operativos recomendados según el modo de trading
        @param mode - Modo de trading recomendado
        @param instrument - Instrumento analizado
        @param yesterday_analysis - Análisis del día anterior
        @returns Lista de niveles operativos recomendados
        """
        # Obtener precio actual
        current_price = yesterday_analysis.current_day_close
        
        # Obtener datos históricos para detectar niveles
        try:
            from app.providers.market_data.mock_market_provider import MockMarketDataProvider
            provider = MockMarketDataProvider()
            
            # Obtener últimos 30 días de datos
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            historical_data = await provider.get_historical_data(
                symbol=instrument,
                interval="1h",
                start_date=start_date,
                end_date=end_date
            )
            
            if not historical_data:
                logger.warning("No historical data available for operational levels")
                return []
            
        except Exception as e:
            logger.warning(f"Error fetching historical data for operational levels: {str(e)}")
            return []
        
        # Detectar niveles psicológicos cercanos
        levels_info = self.level_detector.detect_nearby_levels(
            current_price=current_price,
            max_distance_points=200.0
        )
        
        if not levels_info:
            return []
        
        # Calcular fuerza de niveles basada en reacciones históricas
        levels_with_strength = []
        for level_price in levels_info:
            # Detectar rupturas en el histórico para calcular fuerza
            breaks = self.level_detector.detect_level_breaks(
                candles=historical_data,
                level=level_price
            )
            
            # Calcular fuerza: más reacciones = más fuerte
            bounce_count = sum(1 for b in breaks if b.break_type == "bounce")
            total_tests = len(breaks)
            strength = min(1.0, bounce_count / max(1, total_tests))
            
            levels_with_strength.append({
                "level": level_price,
                "strength": strength,
                "total_tests": total_tests
            })
        
        # Filtrar y ordenar según el modo
        operational_levels: list[OperationalLevel] = []
        
        if mode == TradingMode.CALM or mode == TradingMode.VERY_CALM:
            # Modo CALMA: Solo niveles fuertes (100s) con alta fuerza
            strong_levels = [
                lv for lv in levels_with_strength
                if lv["level"] % 100 == 0  # Solo niveles de 100
                and lv["strength"] >= 0.6  # Fuerza alta
                and lv["total_tests"] >= 3  # Mínimo 3 tests históricos
            ]
            
            # Tomar máximo 3 niveles más cercanos
            strong_levels.sort(key=lambda lv: abs(lv["level"] - current_price))
            selected_levels = strong_levels[:3]
            
            for lv in selected_levels:
                level_price = lv["level"]
                is_support = level_price < current_price
                
                operational_levels.append(OperationalLevel(
                    level=level_price,
                    type=LevelType.SUPPORT if is_support else LevelType.RESISTANCE,
                    distance_points=abs(level_price - current_price),
                    distance_percentage=(abs(level_price - current_price) / current_price) * 100,
                    strength=lv["strength"],
                    action="Esperar rebote" if is_support else "Esperar rechazo",
                    explanation=(
                        f"Nivel redondo fuerte ({int(lv['total_tests'])} tests históricos, "
                        f"{lv['strength']*100:.0f}% de rebotes). "
                        f"En modo {mode.value}, solo operar en niveles muy fuertes."
                    )
                ))
        
        elif mode == TradingMode.AGGRESSIVE:
            # Modo AGRESIVO: Niveles de 100s y 50s, permitir breakouts
            all_strong_levels = [
                lv for lv in levels_with_strength
                if (lv["level"] % 100 == 0 or lv["level"] % 50 == 0)  # 100s y 50s
                and lv["strength"] >= 0.4  # Fuerza media-alta
            ]
            
            # Tomar máximo 5 niveles más cercanos
            all_strong_levels.sort(key=lambda lv: abs(lv["level"] - current_price))
            selected_levels = all_strong_levels[:5]
            
            for lv in selected_levels:
                level_price = lv["level"]
                is_support = level_price < current_price
                is_round_100 = level_price % 100 == 0
                
                if is_round_100:
                    action = "Rebote o breakout confirmado" if is_support else "Rechazo o breakout confirmado"
                else:
                    action = "Entrada en retroceso" if is_support else "Entrada en rechazo"
                
                operational_levels.append(OperationalLevel(
                    level=level_price,
                    type=LevelType.SUPPORT if is_support else LevelType.RESISTANCE,
                    distance_points=abs(level_price - current_price),
                    distance_percentage=(abs(level_price - current_price) / current_price) * 100,
                    strength=lv["strength"],
                    action=action,
                    explanation=(
                        f"Nivel {'redondo' if is_round_100 else 'intermedio'} "
                        f"({int(lv['total_tests'])} tests, {lv['strength']*100:.0f}% rebotes). "
                        f"En modo agresivo, operar tanto rebotes como breakouts confirmados."
                    )
                ))
        
        elif mode == TradingMode.OBSERVE:
            # Modo OBSERVAR: Niveles informativos solamente
            all_levels = [
                lv for lv in levels_with_strength
                if lv["level"] % 100 == 0  # Solo 100s para observar
            ]
            
            all_levels.sort(key=lambda lv: abs(lv["level"] - current_price))
            selected_levels = all_levels[:2]
            
            for lv in selected_levels:
                level_price = lv["level"]
                is_support = level_price < current_price
                
                operational_levels.append(OperationalLevel(
                    level=level_price,
                    type=LevelType.SUPPORT if is_support else LevelType.RESISTANCE,
                    distance_points=abs(level_price - current_price),
                    distance_percentage=(abs(level_price - current_price) / current_price) * 100,
                    strength=lv["strength"],
                    action="Solo observar - NO operar",
                    explanation=(
                        f"Nivel clave para observar. "
                        f"En modo observar, NO se recomienda operar. "
                        f"Esperar mejores condiciones de mercado."
                    )
                ))
        
        return operational_levels

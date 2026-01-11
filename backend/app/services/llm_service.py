"""
Servicio para integración con LLM (OpenAI GPT)
"""
import logging
import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.config.settings import Settings
from app.models.daily_summary import DailySummary, MarketContext

logger = logging.getLogger(__name__)


class LLMService:
    """
    Servicio para interactuar con modelos de lenguaje (OpenAI GPT)
    """
    
    def __init__(self, settings: Settings):
        """
        Inicializa el servicio LLM
        
        Args:
            settings: Configuración de la aplicación
        """
        self.settings = settings
        self.client: Optional[AsyncOpenAI] = None
        
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            logger.warning("OpenAI API key not configured. LLM features will be disabled.")
    
    async def generate_daily_summary(
        self,
        context: MarketContext,
        yesterday_close: float,
        yesterday_change_percent: float,
        current_price: float,
        language: str = "es",
        detail_level: str = "standard"
    ) -> DailySummary:
        """
        Genera un resumen ejecutivo diario del mercado usando LLM
        
        Args:
            context: Contexto de mercado (noticias, bias, modo, correlación)
            yesterday_close: Precio de cierre de ayer
            yesterday_change_percent: Cambio porcentual de ayer
            current_price: Precio actual
            language: Idioma del resumen (es, en)
            detail_level: Nivel de detalle (brief, standard, detailed)
        
        Returns:
            DailySummary: Resumen ejecutivo generado
        
        Raises:
            ValueError: Si el servicio LLM no está configurado
            Exception: Si falla la generación del resumen
        """
        if not self.client:
            raise ValueError(
                "LLM service not configured. Please set OPENAI_API_KEY in environment."
            )
        
        # Construir el prompt
        prompt = self._build_daily_summary_prompt(
            context=context,
            yesterday_close=yesterday_close,
            yesterday_change_percent=yesterday_change_percent,
            current_price=current_price,
            language=language,
            detail_level=detail_level
        )
        
        try:
            logger.info(f"Generating daily summary with {self.settings.openai_model}")
            
            # Llamar a OpenAI
            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Extraer respuesta
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"LLM response received (tokens: {tokens_used})")
            
            # Parsear JSON response
            summary_data = json.loads(content)
            
            # Construir DailySummary
            summary = DailySummary(
                summary=summary_data["summary"],
                key_points=summary_data["key_points"],
                market_sentiment=summary_data["market_sentiment"],
                recommended_action=summary_data["recommended_action"],
                confidence_level=summary_data["confidence_level"],
                context=context,
                model_used=self.settings.openai_model,
                tokens_used=tokens_used
            )
            
            return summary
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise Exception(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate daily summary: {str(e)}")
    
    async def generate_trade_justification(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        current_price: float,
        confidence: float,
        market_context: str,
        trading_mode: str,
        reasons: list[str],
        technical_summary: str,
        news_impact: str,
        language: str = "es"
    ) -> str:
        """
        Genera justificación detallada de una recomendación de trade usando LLM
        
        Args:
            direction: Dirección del trade (BUY, SELL, WAIT)
            entry_price: Precio de entrada recomendado
            stop_loss: Stop loss
            take_profit: Take profit
            current_price: Precio actual
            confidence: Nivel de confianza (0-1)
            market_context: Contexto de mercado (RISK_ON, RISK_OFF, etc)
            trading_mode: Modo de trading (CALM, AGGRESSIVE, OBSERVE)
            reasons: Lista de razones principales
            technical_summary: Resumen técnico (EMAs, RSI, estructura)
            news_impact: Impacto de noticias esperado
            language: Idioma (es, en)
        
        Returns:
            str: Justificación en lenguaje natural (100-150 palabras)
        
        Raises:
            ValueError: Si el servicio LLM no está configurado
            Exception: Si falla la generación
        """
        if not self.client:
            raise ValueError(
                "LLM service not configured. Please set OPENAI_API_KEY in environment."
            )
        
        # Construir prompt
        prompt = self._build_trade_justification_prompt(
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            current_price=current_price,
            confidence=confidence,
            market_context=market_context,
            trading_mode=trading_mode,
            reasons=reasons,
            technical_summary=technical_summary,
            news_impact=news_impact,
            language=language
        )
        
        try:
            logger.info(f"Generating trade justification ({direction}) with {self.settings.openai_model}")
            
            # Llamar a OpenAI
            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_trade_justification_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.openai_temperature,
                max_tokens=250  # ~100-150 palabras
            )
            
            # Extraer justificación
            justification = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"Trade justification generated (tokens: {tokens_used})")
            
            return justification
            
        except Exception as e:
            logger.error(f"Error generating trade justification: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate trade justification: {str(e)}")
    
    async def analyze_news_sentiment(
        self,
        news_title: str,
        news_currency: str = "USD",
        language: str = "es"
    ) -> str:
        """
        Analiza el sentimiento de una noticia económica para Gold
        
        Args:
            news_title: Título de la noticia (ej: "NFP Better Than Expected")
            news_currency: Moneda del evento (USD, EUR, etc)
            language: Idioma de análisis (es, en)
        
        Returns:
            str: Sentimiento ("BULLISH", "BEARISH", "NEUTRAL")
        
        Raises:
            ValueError: Si el servicio LLM no está configurado
            Exception: Si falla el análisis
        """
        if not self.client:
            raise ValueError(
                "LLM service not configured. Please set OPENAI_API_KEY in environment."
            )
        
        # Construir prompt
        prompt = self._build_sentiment_analysis_prompt(
            news_title=news_title,
            news_currency=news_currency,
            language=language
        )
        
        try:
            logger.info(f"Analyzing sentiment for news: '{news_title[:50]}...'")
            
            # Llamar a OpenAI con max_tokens bajo (solo necesitamos una palabra)
            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_sentiment_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Baja temperatura para respuestas más consistentes
                max_tokens=10     # Solo necesitamos "BULLISH", "BEARISH" o "NEUTRAL"
            )
            
            # Extraer sentimiento
            sentiment_raw = response.choices[0].message.content.strip().upper()
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # Normalizar respuesta (el LLM podría agregar puntuación o espacios)
            if "BULLISH" in sentiment_raw:
                sentiment = "BULLISH"
            elif "BEARISH" in sentiment_raw:
                sentiment = "BEARISH"
            else:
                sentiment = "NEUTRAL"
            
            logger.info(f"Sentiment analysis result: {sentiment} (tokens: {tokens_used})")
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {str(e)}", exc_info=True)
            # En caso de error, retornar NEUTRAL por defecto
            logger.warning("Defaulting to NEUTRAL sentiment due to error")
            return "NEUTRAL"
    
    def _get_sentiment_system_prompt(self, language: str) -> str:
        """
        Obtiene el system prompt para análisis de sentimiento
        
        Args:
            language: Código de idioma (es, en)
        
        Returns:
            str: System prompt
        """
        if language == "es":
            return """Eres un analista experto de mercados financieros especializado en Gold (XAU/USD).

Tu tarea es analizar el sentimiento de noticias económicas y determinar su impacto en Gold.

IMPORTANTE:
- Responde SOLO con una palabra: BULLISH, BEARISH o NEUTRAL
- NO agregues explicaciones, puntos ni texto extra
- BULLISH = La noticia favorece alza de Gold (ej: USD débil, risk-off, inflación alta)
- BEARISH = La noticia favorece baja de Gold (ej: USD fuerte, risk-on, tasas altas)
- NEUTRAL = Sin dirección clara o impacto mixto

Recuerda: Gold tiene correlación INVERSA con USD. Si USD sube → Gold baja."""
        else:  # English
            return """You are an expert financial market analyst specialized in Gold (XAU/USD).

Your task is to analyze the sentiment of economic news and determine its impact on Gold.

IMPORTANT:
- Respond with ONLY one word: BULLISH, BEARISH, or NEUTRAL
- DO NOT add explanations, periods, or extra text
- BULLISH = News favors Gold rise (e.g., weak USD, risk-off, high inflation)
- BEARISH = News favors Gold decline (e.g., strong USD, risk-on, high rates)
- NEUTRAL = No clear direction or mixed impact

Remember: Gold has INVERSE correlation with USD. If USD rises → Gold falls."""
    
    def _build_sentiment_analysis_prompt(
        self,
        news_title: str,
        news_currency: str,
        language: str
    ) -> str:
        """
        Construye el prompt para analizar sentimiento de noticia
        
        Args:
            news_title: Título de la noticia
            news_currency: Moneda del evento
            language: Idioma
        
        Returns:
            str: Prompt completo
        """
        if language == "es":
            prompt = f"""Analiza el sentimiento de esta noticia económica para Gold (XAU/USD):

NOTICIA: "{news_title}"
MONEDA: {news_currency}

¿Cómo afecta esta noticia a Gold?

Responde SOLO: BULLISH, BEARISH o NEUTRAL"""
        
        else:  # English
            prompt = f"""Analyze the sentiment of this economic news for Gold (XAU/USD):

NEWS: "{news_title}"
CURRENCY: {news_currency}

How does this news affect Gold?

Respond ONLY: BULLISH, BEARISH, or NEUTRAL"""
        
        return prompt
    
    def _get_trade_justification_system_prompt(self, language: str) -> str:
        """
        Obtiene el system prompt para justificación de trades
        
        Args:
            language: Código de idioma (es, en)
        
        Returns:
            str: System prompt
        """
        if language == "es":
            return """Eres un analista experto de trading especializado en Gold (XAU/USD).

Tu tarea es justificar recomendaciones de trading (BUY/SELL/WAIT) de forma clara y profesional.

IMPORTANTE:
- Usa lenguaje directo y específico
- Explica POR QUÉ esta recomendación tiene sentido
- Menciona factores clave: técnico, fundamental, contexto macro
- Sé honesto sobre riesgos y limitaciones
- 100-150 palabras (conciso pero completo)
- NO uses formato JSON, solo texto natural

Estructura sugerida:
1. Decisión principal y por qué (30-40 palabras)
2. Factores técnicos que la soportan (30-40 palabras)
3. Contexto fundamental/macro relevante (30-40 palabras)
4. Consideración de riesgos (20-30 palabras)"""
        else:  # English
            return """You are an expert trading analyst specialized in Gold (XAU/USD).

Your task is to justify trading recommendations (BUY/SELL/WAIT) clearly and professionally.

IMPORTANT:
- Use direct, specific language
- Explain WHY this recommendation makes sense
- Mention key factors: technical, fundamental, macro context
- Be honest about risks and limitations
- 100-150 words (concise but complete)
- NO JSON format, only natural text

Suggested structure:
1. Main decision and why (30-40 words)
2. Technical factors supporting it (30-40 words)
3. Relevant fundamental/macro context (30-40 words)
4. Risk considerations (20-30 words)"""
    
    def _build_trade_justification_prompt(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        current_price: float,
        confidence: float,
        market_context: str,
        trading_mode: str,
        reasons: list[str],
        technical_summary: str,
        news_impact: str,
        language: str
    ) -> str:
        """
        Construye el prompt para justificar un trade
        
        Args:
            direction: Dirección del trade
            entry_price: Precio de entrada
            stop_loss: Stop loss
            take_profit: Take profit
            current_price: Precio actual
            confidence: Confianza (0-1)
            market_context: Contexto de mercado
            trading_mode: Modo de trading
            reasons: Lista de razones
            technical_summary: Resumen técnico
            news_impact: Impacto de noticias
            language: Idioma
        
        Returns:
            str: Prompt completo
        """
        if language == "es":
            prompt = f"""Justifica esta recomendación de trading para Gold (XAU/USD):

RECOMENDACIÓN:
- Dirección: {direction}
- Entrada: ${entry_price:.2f}
- Stop Loss: ${stop_loss:.2f}
- Take Profit: ${take_profit:.2f}
- Precio actual: ${current_price:.2f}
- Confianza: {confidence*100:.0f}%

CONTEXTO DE MERCADO:
- Sesgo macro: {market_context}
- Modo de trading: {trading_mode}
- Impacto de noticias: {news_impact}

ANÁLISIS TÉCNICO:
{technical_summary}

RAZONES PRINCIPALES:
{chr(10).join(f'- {r}' for r in reasons)}

INSTRUCCIONES:
Escribe un párrafo de 100-150 palabras explicando por qué esta recomendación tiene sentido.
Menciona los factores más relevantes (técnico, fundamental, contexto).
Sé honesto sobre limitaciones y riesgos.
Usa lenguaje directo y profesional."""
        
        else:  # English
            prompt = f"""Justify this trading recommendation for Gold (XAU/USD):

RECOMMENDATION:
- Direction: {direction}
- Entry: ${entry_price:.2f}
- Stop Loss: ${stop_loss:.2f}
- Take Profit: ${take_profit:.2f}
- Current price: ${current_price:.2f}
- Confidence: {confidence*100:.0f}%

MARKET CONTEXT:
- Macro bias: {market_context}
- Trading mode: {trading_mode}
- News impact: {news_impact}

TECHNICAL ANALYSIS:
{technical_summary}

MAIN REASONS:
{chr(10).join(f'- {r}' for r in reasons)}

INSTRUCTIONS:
Write a 100-150 word paragraph explaining why this recommendation makes sense.
Mention the most relevant factors (technical, fundamental, context).
Be honest about limitations and risks.
Use direct, professional language."""
        
        return prompt
    
    def _get_system_prompt(self, language: str) -> str:
        """
        Obtiene el system prompt según el idioma
        
        Args:
            language: Código de idioma (es, en)
        
        Returns:
            str: System prompt
        """
        if language == "es":
            return """Eres un analista experto de mercados financieros especializado en Gold (XAU/USD).

Tu tarea es generar resúmenes ejecutivos diarios para traders profesionales.

IMPORTANTE:
- Usa lenguaje claro y profesional
- Enfócate en probabilidades, no certezas
- Menciona factores clave: noticias, correlaciones, niveles técnicos
- Sé conciso pero informativo
- SIEMPRE responde en formato JSON con esta estructura exacta:

{
  "summary": "Resumen de 200-300 palabras...",
  "key_points": ["Punto 1", "Punto 2", "Punto 3"],
  "market_sentiment": "BULLISH|BEARISH|NEUTRAL",
  "recommended_action": "TRADE_ACTIVELY|TRADE_CAUTIOUSLY|OBSERVE",
  "confidence_level": 0.75
}

NO agregues texto fuera del JSON."""
        else:  # English
            return """You are an expert financial market analyst specialized in Gold (XAU/USD).

Your task is to generate daily executive summaries for professional traders.

IMPORTANT:
- Use clear, professional language
- Focus on probabilities, not certainties
- Mention key factors: news, correlations, technical levels
- Be concise but informative
- ALWAYS respond in JSON format with this exact structure:

{
  "summary": "200-300 word summary...",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "market_sentiment": "BULLISH|BEARISH|NEUTRAL",
  "recommended_action": "TRADE_ACTIVELY|TRADE_CAUTIOUSLY|OBSERVE",
  "confidence_level": 0.75
}

DO NOT add text outside the JSON."""
    
    def _build_daily_summary_prompt(
        self,
        context: MarketContext,
        yesterday_close: float,
        yesterday_change_percent: float,
        current_price: float,
        language: str,
        detail_level: str
    ) -> str:
        """
        Construye el prompt para generar el resumen diario
        
        Args:
            context: Contexto de mercado
            yesterday_close: Precio de cierre de ayer
            yesterday_change_percent: Cambio porcentual de ayer
            current_price: Precio actual
            language: Idioma del resumen
            detail_level: Nivel de detalle
        
        Returns:
            str: Prompt completo
        """
        if language == "es":
            detail_instruction = {
                "brief": "Sé muy conciso (150-200 palabras).",
                "standard": "Usa ~250 palabras.",
                "detailed": "Sé detallado (300-400 palabras)."
            }.get(detail_level, "Usa ~250 palabras.")
            
            # Formatear correlación
            correlation_text = f"{context.gold_dxy_correlation:.2f}" if context.gold_dxy_correlation is not None else "N/A"
            
            prompt = f"""Genera un resumen ejecutivo para Gold (XAU/USD) hoy.

DATOS DEL MERCADO:
- Ayer cerró en: ${yesterday_close:.2f} ({yesterday_change_percent:+.2f}%)
- Precio actual: ${current_price:.2f}
- Noticias de alto impacto hoy: {context.high_impact_news_count}
- Riesgo geopolítico: {context.geopolitical_risk_level}
- Sesgo macro (DXY-Bonds): {context.market_bias}
- Correlación Gold-DXY: {correlation_text}
- Modo de trading recomendado: {context.trading_mode}

INSTRUCCIONES:
{detail_instruction}

Incluye en tu análisis:
1. Resumen de movimiento de ayer y contexto
2. Factores clave hoy (noticias, geopolítica, correlaciones)
3. Sesgo direccional (alcista/bajista/neutral) con probabilidad
4. Recomendación operativa (tradear activamente/con cautela/observar)
5. Niveles clave a vigilar (aproximados según contexto)

Responde SOLO con el JSON (sin markdown, sin explicaciones extra)."""
        
        else:  # English
            detail_instruction = {
                "brief": "Be very concise (150-200 words).",
                "standard": "Use ~250 words.",
                "detailed": "Be detailed (300-400 words)."
            }.get(detail_level, "Use ~250 words.")
            
            # Format correlation
            correlation_text = f"{context.gold_dxy_correlation:.2f}" if context.gold_dxy_correlation is not None else "N/A"
            
            prompt = f"""Generate an executive summary for Gold (XAU/USD) today.

MARKET DATA:
- Yesterday closed at: ${yesterday_close:.2f} ({yesterday_change_percent:+.2f}%)
- Current price: ${current_price:.2f}
- High impact news today: {context.high_impact_news_count}
- Geopolitical risk: {context.geopolitical_risk_level}
- Macro bias (DXY-Bonds): {context.market_bias}
- Gold-DXY correlation: {correlation_text}
- Recommended trading mode: {context.trading_mode}

INSTRUCTIONS:
{detail_instruction}

Include in your analysis:
1. Summary of yesterday's move and context
2. Key factors today (news, geopolitics, correlations)
3. Directional bias (bullish/bearish/neutral) with probability
4. Trading recommendation (active/cautious/observe)
5. Key levels to watch (approximate based on context)

Respond ONLY with JSON (no markdown, no extra explanations)."""
        
        return prompt

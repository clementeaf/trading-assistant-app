"""
Tests unitarios para el servicio LLM
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from app.services.llm_service import LLMService
from app.config.settings import Settings
from app.models.daily_summary import MarketContext


@pytest.fixture
def settings():
    """Settings con API key configurada"""
    return Settings(
        openai_api_key="test-key-123",
        openai_model="gpt-4-turbo-preview",
        openai_max_tokens=500,
        openai_temperature=0.7
    )


@pytest.fixture
def settings_no_key():
    """Settings sin API key"""
    return Settings(openai_api_key=None)


@pytest.fixture
def market_context():
    """Contexto de mercado de ejemplo"""
    return MarketContext(
        high_impact_news_count=2,
        geopolitical_risk_level="MEDIUM",
        market_bias="RISK_OFF",
        trading_mode="CALM",
        gold_dxy_correlation=-0.78
    )


@pytest.fixture
def mock_llm_response():
    """Mock de respuesta de OpenAI"""
    return ChatCompletion(
        id="chatcmpl-123",
        model="gpt-4-turbo-preview",
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    content='{"summary": "Gold cerró ayer en $4510 con ligera alza...","key_points": ["NFP hoy a las 08:30", "DXY y bonos alineados risk-off", "Correlación Gold-DXY negativa fuerte"],"market_sentiment": "NEUTRAL","recommended_action": "TRADE_CAUTIOUSLY","confidence_level": 0.65}',
                ),
                finish_reason="stop"
            )
        ],
        usage=CompletionUsage(
            prompt_tokens=300,
            completion_tokens=150,
            total_tokens=450
        )
    )


class TestLLMServiceInit:
    """Tests de inicialización del servicio"""
    
    def test_init_with_api_key(self, settings):
        """Test que el servicio se inicializa correctamente con API key"""
        service = LLMService(settings)
        assert service.client is not None
        assert service.settings == settings
    
    def test_init_without_api_key(self, settings_no_key):
        """Test que el servicio se inicializa sin cliente si no hay API key"""
        service = LLMService(settings_no_key)
        assert service.client is None


class TestGenerateDailySummary:
    """Tests de generación de resumen diario"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_success(self, settings, market_context, mock_llm_response):
        """Test que genera resumen exitosamente"""
        service = LLMService(settings)
        
        # Mock del cliente OpenAI
        service.client = AsyncMock()
        service.client.chat.completions.create = AsyncMock(return_value=mock_llm_response)
        
        # Generar resumen
        summary = await service.generate_daily_summary(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="es",
            detail_level="standard"
        )
        
        # Validar resultado
        assert summary.summary.startswith("Gold cerró ayer")
        assert len(summary.key_points) == 3
        assert summary.market_sentiment == "NEUTRAL"
        assert summary.recommended_action == "TRADE_CAUTIOUSLY"
        assert summary.confidence_level == 0.65
        assert summary.context == market_context
        assert summary.tokens_used == 450
        assert summary.model_used == "gpt-4-turbo-preview"
    
    @pytest.mark.asyncio
    async def test_generate_summary_no_client(self, settings_no_key, market_context):
        """Test que falla si no hay cliente configurado"""
        service = LLMService(settings_no_key)
        
        with pytest.raises(ValueError, match="LLM service not configured"):
            await service.generate_daily_summary(
                context=market_context,
                yesterday_close=4510.0,
                yesterday_change_percent=0.5,
                current_price=4515.0
            )
    
    @pytest.mark.asyncio
    async def test_generate_summary_invalid_json(self, settings, market_context):
        """Test que maneja JSON inválido de LLM"""
        service = LLMService(settings)
        
        # Mock respuesta con JSON inválido
        invalid_response = ChatCompletion(
            id="chatcmpl-123",
            model="gpt-4-turbo-preview",
            object="chat.completion",
            created=1234567890,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="This is not JSON",
                    ),
                    finish_reason="stop"
                )
            ],
            usage=None
        )
        
        service.client = AsyncMock()
        service.client.chat.completions.create = AsyncMock(return_value=invalid_response)
        
        with pytest.raises(Exception, match="Invalid JSON response"):
            await service.generate_daily_summary(
                context=market_context,
                yesterday_close=4510.0,
                yesterday_change_percent=0.5,
                current_price=4515.0
            )
    
    @pytest.mark.asyncio
    async def test_generate_summary_english(self, settings, market_context):
        """Test generación en inglés"""
        service = LLMService(settings)
        
        english_response = ChatCompletion(
            id="chatcmpl-123",
            model="gpt-4-turbo-preview",
            object="chat.completion",
            created=1234567890,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content='{"summary": "Gold closed yesterday at $4510...","key_points": ["NFP today at 08:30", "DXY and bonds aligned risk-off", "Strong psychological support at 4500"],"market_sentiment": "BULLISH","recommended_action": "TRADE_ACTIVELY","confidence_level": 0.75}',
                    ),
                    finish_reason="stop"
                )
            ],
            usage=CompletionUsage(prompt_tokens=300, completion_tokens=150, total_tokens=450)
        )
        
        service.client = AsyncMock()
        service.client.chat.completions.create = AsyncMock(return_value=english_response)
        
        summary = await service.generate_daily_summary(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="en"
        )
        
        assert summary.summary.startswith("Gold closed")
        assert summary.market_sentiment == "BULLISH"


class TestPromptBuilding:
    """Tests de construcción de prompts"""
    
    def test_system_prompt_spanish(self, settings):
        """Test system prompt en español"""
        service = LLMService(settings)
        prompt = service._get_system_prompt("es")
        
        assert "analista experto" in prompt.lower()
        assert "gold" in prompt.lower()
        assert "json" in prompt.lower()
    
    def test_system_prompt_english(self, settings):
        """Test system prompt en inglés"""
        service = LLMService(settings)
        prompt = service._get_system_prompt("en")
        
        assert "expert" in prompt.lower()
        assert "gold" in prompt.lower()
        assert "json" in prompt.lower()
    
    def test_prompt_includes_context(self, settings, market_context):
        """Test que el prompt incluye todo el contexto"""
        service = LLMService(settings)
        prompt = service._build_daily_summary_prompt(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="es",
            detail_level="standard"
        )
        
        assert "4510.00" in prompt
        assert "+0.50%" in prompt
        assert "4515.00" in prompt
        assert str(market_context.high_impact_news_count) in prompt
        assert market_context.geopolitical_risk_level in prompt
        assert market_context.market_bias in prompt
        assert market_context.trading_mode in prompt
        assert "-0.78" in prompt  # Correlación
    
    def test_prompt_detail_levels(self, settings, market_context):
        """Test diferentes niveles de detalle"""
        service = LLMService(settings)
        
        # Brief
        prompt_brief = service._build_daily_summary_prompt(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="es",
            detail_level="brief"
        )
        assert "conciso" in prompt_brief.lower()
        
        # Standard
        prompt_standard = service._build_daily_summary_prompt(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="es",
            detail_level="standard"
        )
        assert "250" in prompt_standard
        
        # Detailed
        prompt_detailed = service._build_daily_summary_prompt(
            context=market_context,
            yesterday_close=4510.0,
            yesterday_change_percent=0.5,
            current_price=4515.0,
            language="es",
            detail_level="detailed"
        )
        assert "detallado" in prompt_detailed.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

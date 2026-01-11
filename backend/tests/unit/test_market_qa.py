"""
Tests unitarios para sistema Q&A de mercado
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm_service import LLMService
from app.config.settings import Settings


@pytest.fixture
def settings():
    """Configuración con OpenAI habilitado"""
    return Settings(
        openai_api_key="test-key-12345",
        openai_model="gpt-4o-mini"
    )


@pytest.fixture
def llm_service(settings):
    """Servicio LLM mockeado"""
    return LLMService(settings)


@pytest.fixture
def sample_context():
    """Contexto de mercado de muestra"""
    return {
        "current_price": 4510.0,
        "daily_change_percent": 0.5,
        "high_impact_news_count": 2,
        "market_bias": "RISK_OFF",
        "trading_mode": "CALM",
        "dxy_price": 99.14,
        "bond_yield": 4.18,
        "geopolitical_risk": "MEDIUM"
    }


class TestMarketQuestionAnswering:
    """Tests para Q&A de mercado"""
    
    @pytest.mark.asyncio
    async def test_answer_question_spanish(self, llm_service, sample_context):
        """Test responder pregunta en español"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "answer": "Gold está subiendo hoy principalmente por dos factores: (1) Debilidad del dólar (DXY en 99.14, bajando), lo cual hace más atractivo comprar Gold denominado en dólares. (2) Riesgo geopolítico medio, lo que impulsa demanda de activos refugio como el oro. Adicionalmente, hay 2 noticias de alto impacto hoy que están generando volatilidad en los mercados.",
            "confidence": 0.72,
            "sources_used": ["precio_actual", "dxy_price", "geopolitical_risk", "high_impact_news"],
            "related_topics": ["¿Cuál es la correlación entre DXY y Gold?", "¿Hasta dónde puede subir Gold hoy?", "¿Qué niveles técnicos son clave?"]
        }"""
        mock_response.usage.total_tokens = 420
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="¿Por qué está subiendo Gold hoy?",
                context=sample_context,
                language="es"
            )
        
        assert "answer" in result
        assert result["confidence"] == 0.72
        assert len(result["sources_used"]) == 4
        assert len(result["related_topics"]) == 3
        assert "Gold está subiendo" in result["answer"]
        assert result["tokens_used"] == 420
    
    @pytest.mark.asyncio
    async def test_answer_question_english(self, llm_service, sample_context):
        """Test responder pregunta en inglés"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "answer": "The DXY-Gold correlation is typically inverse, meaning when the dollar strengthens (DXY up), Gold tends to fall, and vice versa. Current DXY is at 99.14. This inverse relationship exists because Gold is priced in dollars - when the dollar weakens, Gold becomes cheaper for foreign buyers, increasing demand.",
            "confidence": 0.85,
            "sources_used": ["dxy_price", "market_theory"],
            "related_topics": ["What is the current DXY-Gold correlation coefficient?", "How strong is this correlation historically?"]
        }"""
        mock_response.usage.total_tokens = 380
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="What is the correlation between DXY and Gold?",
                context=sample_context,
                language="en"
            )
        
        assert "answer" in result
        assert result["confidence"] == 0.85
        assert "inverse" in result["answer"].lower()
        assert "DXY" in result["answer"]
    
    @pytest.mark.asyncio
    async def test_answer_with_minimal_context(self, llm_service):
        """Test responder con contexto mínimo"""
        minimal_context = {"current_price": 4500.0}
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "answer": "Con la información limitada disponible, solo puedo confirmar que el precio actual de Gold es aproximadamente $4500. Para dar una recomendación fundamentada, necesitaría más contexto sobre noticias, análisis técnico y macro.",
            "confidence": 0.3,
            "sources_used": ["precio_actual"],
            "related_topics": ["¿Qué noticias están afectando Gold hoy?", "¿Cuál es el análisis técnico actual?"]
        }"""
        mock_response.usage.total_tokens = 250
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="¿Debería comprar Gold ahora?",
                context=minimal_context,
                language="es"
            )
        
        assert result["confidence"] == 0.3
        assert "información limitada" in result["answer"].lower() or "información" in result["answer"].lower()
    
    @pytest.mark.asyncio
    async def test_answer_without_context(self, llm_service):
        """Test responder sin contexto"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "answer": "Gold generalmente reacciona positivamente a riesgo geopolítico porque actúa como activo refugio. Cuando hay incertidumbre política o conflictos internacionales, los inversores buscan proteger su capital en activos tangibles y seguros como el oro.",
            "confidence": 0.65,
            "sources_used": ["conocimiento_general"],
            "related_topics": ["¿Qué otros factores afectan a Gold?", "¿Cuál es el nivel actual de riesgo geopolítico?"]
        }"""
        mock_response.usage.total_tokens = 300
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="¿Cómo afecta el riesgo geopolítico a Gold?",
                context={},
                language="es"
            )
        
        assert result["confidence"] > 0
        assert "refugio" in result["answer"].lower() or "gold" in result["answer"].lower()
    
    @pytest.mark.asyncio
    async def test_llm_service_not_configured(self):
        """Test cuando LLM service no está configurado"""
        settings_no_key = Settings(openai_api_key=None)
        llm_service_no_key = LLMService(settings_no_key)
        
        with pytest.raises(ValueError, match="LLM service not configured"):
            await llm_service_no_key.answer_market_question(
                question="Test question",
                context={},
                language="es"
            )
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, llm_service, sample_context):
        """Test manejo de respuesta JSON inválida"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Esta no es una respuesta JSON válida"
        mock_response.usage.total_tokens = 200
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            with pytest.raises(Exception, match="Failed to parse"):
                await llm_service.answer_market_question(
                    question="Test",
                    context=sample_context,
                    language="es"
                )
    
    @pytest.mark.asyncio
    async def test_missing_answer_field(self, llm_service, sample_context):
        """Test manejo de respuesta sin campo 'answer'"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"confidence": 0.5}'  # Missing 'answer'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            with pytest.raises(ValueError, match="missing 'answer' field"):
                await llm_service.answer_market_question(
                    question="Test",
                    context=sample_context,
                    language="es"
                )
    
    @pytest.mark.asyncio
    async def test_llm_api_error(self, llm_service, sample_context):
        """Test manejo de error en API de OpenAI"""
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("OpenAI API error")
            
            with pytest.raises(Exception):
                await llm_service.answer_market_question(
                    question="Test",
                    context=sample_context,
                    language="es"
                )
    
    @pytest.mark.asyncio
    async def test_prompt_includes_context(self, llm_service, sample_context):
        """Test que el prompt incluye el contexto correctamente"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"answer": "Test answer", "confidence": 0.5, "sources_used": [], "related_topics": []}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.answer_market_question(
                question="Test question",
                context=sample_context,
                language="es"
            )
            
            # Verificar que se llamó al LLM
            assert mock_create.called
            call_args = mock_create.call_args
            
            # Verificar que el user prompt contiene datos de contexto
            user_message = call_args.kwargs["messages"][1]["content"]
            assert "4510" in user_message  # Precio actual
            assert "99.14" in user_message  # DXY
            assert "RISK_OFF" in user_message or "risk_off" in user_message.lower()
    
    @pytest.mark.asyncio
    async def test_system_prompt_spanish(self, llm_service, sample_context):
        """Test que el system prompt está en español"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"answer": "Test", "confidence": 0.5, "sources_used": [], "related_topics": []}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.answer_market_question(
                question="Test",
                context=sample_context,
                language="es"
            )
            
            call_args = mock_create.call_args
            system_message = call_args.kwargs["messages"][0]["content"]
            
            assert "asistente experto" in system_message.lower()
            assert "Gold" in system_message or "XAU/USD" in system_message
    
    @pytest.mark.asyncio
    async def test_system_prompt_english(self, llm_service, sample_context):
        """Test que el system prompt está en inglés"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"answer": "Test", "confidence": 0.5, "sources_used": [], "related_topics": []}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.answer_market_question(
                question="Test",
                context=sample_context,
                language="en"
            )
            
            call_args = mock_create.call_args
            system_message = call_args.kwargs["messages"][0]["content"]
            
            assert "expert" in system_message.lower()
            assert "analyst" in system_message.lower()
            assert "Gold" in system_message or "XAU/USD" in system_message
    
    @pytest.mark.asyncio
    async def test_confidence_level_validation(self, llm_service, sample_context):
        """Test validación de nivel de confianza"""
        # Confianza alta
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"answer": "High confidence answer", "confidence": 0.95, "sources_used": ["multiple_sources"], "related_topics": []}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="Test",
                context=sample_context,
                language="es"
            )
            
            assert result["confidence"] >= 0.0
            assert result["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_related_topics_format(self, llm_service, sample_context):
        """Test formato de temas relacionados"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "answer": "Test answer",
            "confidence": 0.7,
            "sources_used": ["test"],
            "related_topics": [
                "¿Qué es el DXY?",
                "¿Cómo se calcula la correlación?",
                "¿Qué otros factores afectan a Gold?"
            ]
        }"""
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.answer_market_question(
                question="Test",
                context=sample_context,
                language="es"
            )
            
            assert isinstance(result["related_topics"], list)
            assert len(result["related_topics"]) > 0
            assert all(isinstance(topic, str) for topic in result["related_topics"])

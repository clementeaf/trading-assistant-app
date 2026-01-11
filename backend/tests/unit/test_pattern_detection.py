"""
Tests unitarios para detección de patrones complejos
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm_service import LLMService
from app.config.settings import Settings


@pytest.fixture
def settings():
    """Configuración con OpenAI habilitado"""
    return Settings(
        openai_api_key="test-key-12345",
        openai_model="gpt-4o-mini",
        openai_temperature=0.4,
        openai_max_tokens=400
    )


@pytest.fixture
def llm_service(settings):
    """Servicio LLM mockeado"""
    return LLMService(settings)


@pytest.fixture
def sample_price_data():
    """Datos de precio de muestra para análisis"""
    base_price = 4500.0
    candles = []
    
    # Simular un patrón Head & Shoulders
    # Hombro izquierdo (sube a 4520, baja a 4500)
    for i in range(5):
        candles.append({
            "timestamp": f"2026-01-{i+1:02d} 10:00",
            "open": base_price + i * 4,
            "high": base_price + i * 4 + 5,
            "low": base_price + i * 4 - 2,
            "close": base_price + i * 4 + 3
        })
    
    # Cabeza (sube a 4550, baja a 4500)
    for i in range(5, 10):
        candles.append({
            "timestamp": f"2026-01-{i+1:02d} 10:00",
            "open": base_price + (i-5) * 10,
            "high": base_price + (i-5) * 10 + 8,
            "low": base_price + (i-5) * 10 - 3,
            "close": base_price + (i-5) * 10 + 5
        })
    
    # Hombro derecho (sube a 4525, baja a 4500)
    for i in range(10, 15):
        candles.append({
            "timestamp": f"2026-01-{i+1:02d} 10:00",
            "open": base_price + (14-i) * 3,
            "high": base_price + (14-i) * 3 + 4,
            "low": base_price + (14-i) * 3 - 2,
            "close": base_price + (14-i) * 3 + 2
        })
    
    return candles


class TestPatternDetection:
    """Tests para detección de patrones complejos"""
    
    @pytest.mark.asyncio
    async def test_detect_head_and_shoulders_spanish(self, llm_service, sample_price_data):
        """Test detección de patrón Head & Shoulders en español"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "pattern_type": "head_and_shoulders",
            "status": "forming",
            "bias": "bearish",
            "confidence": 0.75,
            "description": "Patrón H&S en formación con hombro izquierdo en 4520, cabeza en 4550, hombro derecho en 4525. Neckline en 4500.",
            "key_levels": {
                "neckline": 4500,
                "breakout": 4495,
                "target": 4450,
                "invalidation": 4560
            },
            "timeframe": "H4",
            "implications": "Si rompe neckline (4500), probable caída a 4450. Stop sobre 4560."
        }"""
        mock_response.usage.total_tokens = 350
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4505.0,
                language="es"
            )
        
        assert result["pattern_type"] == "head_and_shoulders"
        assert result["status"] == "forming"
        assert result["bias"] == "bearish"
        assert result["confidence"] == 0.75
        assert "H&S" in result["description"]
        assert result["key_levels"]["neckline"] == 4500
        assert result["key_levels"]["target"] == 4450
    
    @pytest.mark.asyncio
    async def test_detect_double_top_english(self, llm_service, sample_price_data):
        """Test detección de patrón Double Top en inglés"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "pattern_type": "double_top",
            "status": "confirmed",
            "bias": "bearish",
            "confidence": 0.82,
            "description": "Double Top pattern confirmed at 4550. Support broken at 4500.",
            "key_levels": {
                "resistance": 4550,
                "support": 4500,
                "breakout": 4495,
                "target": 4450
            },
            "timeframe": "H4",
            "implications": "Strong bearish reversal. Target 4450. Stop above 4560."
        }"""
        mock_response.usage.total_tokens = 320
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4490.0,
                language="en"
            )
        
        assert result["pattern_type"] == "double_top"
        assert result["status"] == "confirmed"
        assert result["confidence"] == 0.82
        assert "Double Top" in result["description"]
        assert result["key_levels"]["resistance"] == 4550
    
    @pytest.mark.asyncio
    async def test_detect_no_pattern(self, llm_service, sample_price_data):
        """Test cuando no se detecta ningún patrón"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "pattern_type": "none",
            "status": "forming",
            "bias": "neutral",
            "confidence": 0.0,
            "description": "No se detectó ningún patrón claro. Mercado en consolidación.",
            "key_levels": {},
            "timeframe": "H4",
            "implications": "Esperar confirmación de dirección antes de operar."
        }"""
        mock_response.usage.total_tokens = 280
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="Daily",
                current_price=4510.0,
                language="es"
            )
        
        assert result["pattern_type"] == "none"
        assert result["confidence"] == 0.0
        assert result["bias"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_detect_ascending_triangle(self, llm_service, sample_price_data):
        """Test detección de triángulo ascendente"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """{
            "pattern_type": "ascending_triangle",
            "status": "forming",
            "bias": "bullish",
            "confidence": 0.68,
            "description": "Triángulo ascendente formándose con resistencia en 4550 y soporte creciente.",
            "key_levels": {
                "resistance": 4550,
                "support_line": 4500,
                "breakout": 4555,
                "target": 4600
            },
            "timeframe": "H4",
            "implications": "Patrón de continuación alcista. Breakout sobre 4555 confirmaría subida a 4600."
        }"""
        mock_response.usage.total_tokens = 340
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4530.0,
                language="es"
            )
        
        assert result["pattern_type"] == "ascending_triangle"
        assert result["bias"] == "bullish"
        assert result["confidence"] == 0.68
        assert "Triángulo" in result["description"]
    
    @pytest.mark.asyncio
    async def test_llm_service_not_configured(self):
        """Test cuando LLM service no está configurado"""
        settings_no_key = Settings(openai_api_key=None)
        llm_service_no_key = LLMService(settings_no_key)
        
        with pytest.raises(ValueError, match="LLM service not configured"):
            await llm_service_no_key.detect_complex_patterns(
                price_data=[{"open": 4500, "high": 4510, "low": 4495, "close": 4505, "timestamp": "2026-01-11"}],
                timeframe="H4",
                current_price=4505.0
            )
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, llm_service, sample_price_data):
        """Test manejo de respuesta JSON inválida del LLM"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Esta no es una respuesta JSON válida"
        mock_response.usage.total_tokens = 200
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4505.0
            )
        
        # Debe retornar "none" en caso de error de parsing
        assert result["pattern_type"] == "none"
        assert result["confidence"] == 0.0
        assert "No se pudo detectar" in result["description"]
    
    @pytest.mark.asyncio
    async def test_llm_api_error(self, llm_service, sample_price_data):
        """Test manejo de error en API de OpenAI"""
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("OpenAI API error")
            
            result = await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4505.0
            )
        
        # Debe retornar "none" en caso de error
        assert result["pattern_type"] == "none"
        assert result["confidence"] == 0.0
        assert "Error en detección" in result["description"]
    
    @pytest.mark.asyncio
    async def test_prompt_includes_price_data(self, llm_service):
        """Test que el prompt incluye los datos de precio correctamente"""
        candles = [
            {"open": 4500, "high": 4510, "low": 4495, "close": 4505, "timestamp": "2026-01-11 10:00"},
            {"open": 4505, "high": 4515, "low": 4500, "close": 4512, "timestamp": "2026-01-11 14:00"}
        ]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"pattern_type": "none", "status": "forming", "bias": "neutral", "confidence": 0.0, "description": "Test", "key_levels": {}, "timeframe": "H4", "implications": "Test"}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.detect_complex_patterns(
                price_data=candles,
                timeframe="H4",
                current_price=4512.0,
                language="es"
            )
            
            # Verificar que se llamó al LLM
            assert mock_create.called
            call_args = mock_create.call_args
            
            # Verificar que el user prompt contiene datos de precio
            user_message = call_args.kwargs["messages"][1]["content"]
            assert "O:4500" in user_message or "open" in user_message.lower()
            assert "4512" in user_message  # Precio actual
            assert "H4" in user_message
    
    @pytest.mark.asyncio
    async def test_system_prompt_spanish(self, llm_service, sample_price_data):
        """Test que el system prompt está en español cuando se solicita"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"pattern_type": "none", "status": "forming", "bias": "neutral", "confidence": 0.0, "description": "Test", "key_levels": {}, "timeframe": "H4", "implications": "Test"}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4505.0,
                language="es"
            )
            
            call_args = mock_create.call_args
            system_message = call_args.kwargs["messages"][0]["content"]
            
            assert "analista técnico experto" in system_message.lower()
            assert "Head & Shoulders" in system_message
    
    @pytest.mark.asyncio
    async def test_system_prompt_english(self, llm_service, sample_price_data):
        """Test que el system prompt está en inglés cuando se solicita"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"pattern_type": "none", "status": "forming", "bias": "neutral", "confidence": 0.0, "description": "Test", "key_levels": {}, "timeframe": "H4", "implications": "Test"}'
        mock_response.usage.total_tokens = 100
        
        with patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await llm_service.detect_complex_patterns(
                price_data=sample_price_data,
                timeframe="H4",
                current_price=4505.0,
                language="en"
            )
            
            call_args = mock_create.call_args
            system_message = call_args.kwargs["messages"][0]["content"]
            
            assert "expert technical analyst" in system_message.lower()
            assert "Head & Shoulders" in system_message

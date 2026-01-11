"""
Tests de integración para endpoints de la API
"""
from fastapi.testclient import TestClient
import pytest

from app.main import app


class TestMarketBriefingEndpoints:
    """Tests para endpoints de market briefing"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_high_impact_news_endpoint(self, client):
        """Test del endpoint de noticias de alto impacto"""
        response = client.get("/api/market-briefing/high-impact-news")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "has_high_impact_news" in data
        assert "count" in data
        assert "events" in data
        assert "summary" in data
        assert "instrument" in data
        assert data["instrument"] == "XAUUSD"
        assert isinstance(data["has_high_impact_news"], bool)
        assert isinstance(data["count"], int)
        assert isinstance(data["events"], list)
        assert isinstance(data["summary"], str)
    
    def test_high_impact_news_with_currency_param(self, client):
        """Test del endpoint con parámetro de moneda"""
        response = client.get("/api/market-briefing/high-impact-news?currency=USD")
        
        assert response.status_code == 200
        data = response.json()
        assert data["instrument"] == "XAUUSD"
    
    def test_api_docs_available(self, client):
        """Test que la documentación está disponible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Test que el schema OpenAPI está disponible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_psychological_levels_endpoint(self, client):
        """Test del endpoint de niveles psicológicos"""
        response = client.get("/api/market-briefing/psychological-levels")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "instrument" in data
        assert "current_price" in data
        assert "analysis_datetime" in data
        assert "levels" in data
        assert "summary" in data
        
        # Verificar tipos
        assert isinstance(data["instrument"], str)
        assert isinstance(data["current_price"], (int, float))
        assert isinstance(data["levels"], list)
        assert isinstance(data["summary"], str)
        
        # Verificar que hay niveles
        assert len(data["levels"]) > 0
        
        # Verificar estructura de un nivel
        if len(data["levels"]) > 0:
            level = data["levels"][0]
            assert "level" in level
            assert "distance_from_current" in level
            assert "strength" in level
            assert "reaction_count" in level
            assert "type" in level
            assert "bounce_count" in level
            assert "is_round_hundred" in level
            assert "is_round_fifty" in level
    
    def test_psychological_levels_with_params(self, client):
        """Test del endpoint con parámetros personalizados"""
        response = client.get(
            "/api/market-briefing/psychological-levels"
            "?instrument=XAUUSD&lookback_days=15&max_distance_points=50"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["instrument"] == "XAUUSD"
        assert data["lookback_days"] == 15
        assert data["max_distance_points"] == 50.0
    
    def test_psychological_levels_invalid_lookback(self, client):
        """Test con lookback_days inválido"""
        # Menor que el mínimo (7)
        response = client.get("/api/market-briefing/psychological-levels?lookback_days=5")
        assert response.status_code == 422  # Validation error
        
        # Mayor que el máximo (90)
        response = client.get("/api/market-briefing/psychological-levels?lookback_days=100")
        assert response.status_code == 422
    
    def test_psychological_levels_invalid_distance(self, client):
        """Test con max_distance_points inválido"""
        # Menor que el mínimo (20)
        response = client.get("/api/market-briefing/psychological-levels?max_distance_points=10")
        assert response.status_code == 422
        
        # Mayor que el máximo (500)
        response = client.get("/api/market-briefing/psychological-levels?max_distance_points=600")
        assert response.status_code == 422
    
    def test_psychological_levels_has_strongest_levels(self, client):
        """Test que identifica niveles más fuertes"""
        response = client.get("/api/market-briefing/psychological-levels")
        
        assert response.status_code == 200
        data = response.json()
        
        # Debe tener al menos uno de estos (soporte o resistencia más fuerte)
        has_strongest = (
            data.get("strongest_support") is not None or 
            data.get("strongest_resistance") is not None
        )
        assert has_strongest
    
    def test_psychological_levels_has_nearest_levels(self, client):
        """Test que identifica niveles más cercanos"""
        response = client.get("/api/market-briefing/psychological-levels")
        
        assert response.status_code == 200
        data = response.json()
        
        # Debe tener al menos uno de estos (soporte o resistencia más cercano)
        has_nearest = (
            data.get("nearest_support") is not None or 
            data.get("nearest_resistance") is not None
        )
        assert has_nearest

    def test_trading_recommendation_has_new_fields(self, client):
        """Test que la recomendación incluye los nuevos campos"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        # Nuevos campos
        assert "disclaimer" in data
        assert "risk_reward_ratio" in data
        assert "confidence_breakdown" in data
        assert "invalidation_level" in data
        
        # Validar tipos
        assert isinstance(data["disclaimer"], str)
        assert len(data["disclaimer"]) > 0
        assert isinstance(data["risk_reward_ratio"], str)
        assert isinstance(data["confidence_breakdown"], dict)
        if data["invalidation_level"] is not None:
            assert isinstance(data["invalidation_level"], (int, float))

    def test_risk_reward_ratio_format(self, client):
        """Test formato del risk reward ratio"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        rr = data["risk_reward_ratio"]
        # Debe ser "1:X.XX" o "N/A"
        if rr != "N/A":
            assert rr.startswith("1:")
            parts = rr.split(":")
            assert len(parts) == 2
            try:
                float(parts[1])
            except ValueError:
                pytest.fail("Risk reward ratio second part should be a number")

    def test_confidence_breakdown_structure(self, client):
        """Test estructura del desglose de confianza"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        breakdown = data["confidence_breakdown"]
        assert "technical_analysis" in breakdown
        assert "market_context" in breakdown
        assert "news_impact" in breakdown
        assert "overall" in breakdown
        
        # Validar rangos 0-1
        assert 0 <= breakdown["technical_analysis"] <= 1
        assert 0 <= breakdown["market_context"] <= 1
        assert 0 <= breakdown["news_impact"] <= 1
        assert 0 <= breakdown["overall"] <= 1


class TestEventScheduleEndpoint:
    """Tests E2E para el endpoint de event-schedule"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_event_schedule_endpoint(self, client):
        """Test básico del endpoint de event-schedule"""
        response = client.get("/api/market-briefing/event-schedule")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert "total_events" in data
        assert "usd_events_count" in data
        assert "events" in data
        assert "summary" in data
        
        # Verificar tipos
        assert isinstance(data["total_events"], int)
        assert isinstance(data["usd_events_count"], int)
        assert isinstance(data["events"], list)
        assert isinstance(data["summary"], str)
    
    def test_event_schedule_with_currency(self, client):
        """Test con parámetro de moneda"""
        response = client.get("/api/market-briefing/event-schedule?currency=EUR")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["events"], list)
    
    def test_event_schedule_with_gold_impact(self, client):
        """Test con estimación de impacto en Gold"""
        response = client.get("/api/market-briefing/event-schedule?include_gold_impact=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Si hay eventos, verificar que tengan gold_impact
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "gold_impact" in event
            if event["gold_impact"] is not None:
                assert "probability" in event["gold_impact"]
                assert "direction" in event["gold_impact"]
                assert "magnitude_percent" in event["gold_impact"]
    
    def test_event_schedule_without_gold_impact(self, client):
        """Test sin estimación de impacto en Gold"""
        response = client.get("/api/market-briefing/event-schedule?include_gold_impact=false")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["events"], list)
    
    def test_event_schedule_timezones(self, client):
        """Test que los eventos incluyen múltiples zonas horarias"""
        response = client.get("/api/market-briefing/event-schedule")
        
        assert response.status_code == 200
        data = response.json()
        
        # Si hay eventos, verificar que tengan timezones
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "time" in event
            assert "timezones" in event
            
            if event["timezones"]:
                assert isinstance(event["timezones"], dict)


class TestYesterdayAnalysisEndpoint:
    """Tests E2E para el endpoint de yesterday-analysis"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_yesterday_analysis_endpoint(self, client):
        """Test básico del endpoint de yesterday-analysis"""
        response = client.get("/api/market-briefing/yesterday-analysis?instrument=XAUUSD")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert "instrument" in data
        assert "date" in data
        assert "close_price" in data
        assert "change_percent" in data
        assert "range_high" in data
        assert "range_low" in data
        assert "sessions" in data
        assert "summary" in data
        
        # Verificar tipos
        assert isinstance(data["instrument"], str)
        assert isinstance(data["close_price"], (int, float))
        assert isinstance(data["change_percent"], (int, float))
        assert isinstance(data["sessions"], list)
        assert isinstance(data["summary"], str)
    
    def test_yesterday_analysis_sessions(self, client):
        """Test que el análisis incluye sesiones de trading"""
        response = client.get("/api/market-briefing/yesterday-analysis?instrument=XAUUSD")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que hay al menos una sesión
        assert len(data["sessions"]) > 0
        
        session = data["sessions"][0]
        assert "session_name" in session
        assert "time_range" in session
        assert "price_action" in session
        
        # Verificar que incluye volatilidad y breaks psicológicos
        if "volatility" in session:
            assert isinstance(session["volatility"], str)
        if "psychological_breaks" in session:
            assert isinstance(session["psychological_breaks"], list)
    
    def test_yesterday_analysis_invalid_instrument(self, client):
        """Test con instrumento inválido"""
        response = client.get("/api/market-briefing/yesterday-analysis?instrument=INVALID123")
        assert response.status_code in [400, 422]


class TestDXYBondAlignmentEndpoint:
    """Tests E2E para el endpoint de dxy-bond-alignment"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_dxy_bond_alignment_endpoint(self, client):
        """Test básico del endpoint de dxy-bond-alignment"""
        response = client.get("/api/market-briefing/dxy-bond-alignment")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert "dxy_symbol" in data
        assert "bond_symbol" in data
        assert "dxy_change_percent" in data
        assert "bond_change_percent" in data
        assert "alignment" in data
        assert "market_bias" in data
        assert "explanation" in data
        
        # Verificar tipos
        assert isinstance(data["dxy_symbol"], str)
        assert isinstance(data["bond_symbol"], str)
        assert isinstance(data["alignment"], str)
        assert isinstance(data["market_bias"], str)
    
    def test_dxy_bond_alignment_with_gold_correlation(self, client):
        """Test con correlación Gold-DXY incluida"""
        response = client.get("/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que incluye correlación
        assert "gold_dxy_correlation" in data
        if data["gold_dxy_correlation"] is not None:
            corr = data["gold_dxy_correlation"]
            assert "coefficient" in corr
            assert "strength" in corr
            assert "p_value" in corr
            assert "is_significant" in corr
            
            # Verificar rangos
            assert -1 <= corr["coefficient"] <= 1
            assert 0 <= corr["p_value"] <= 1
    
    def test_dxy_bond_alignment_impact_projection(self, client):
        """Test que incluye proyección de impacto en Gold"""
        response = client.get("/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true")
        
        assert response.status_code == 200
        data = response.json()
        
        if data.get("gold_impact_projection") is not None:
            projection = data["gold_impact_projection"]
            assert "dxy_change_percent" in projection
            assert "expected_gold_change_percent" in projection
            assert "direction" in projection
            
            # Verificar que incluye rango de magnitud (Mejora 4 Fase 2.5)
            if "magnitude_range_percent" in projection:
                range_data = projection["magnitude_range_percent"]
                assert "min" in range_data
                assert "max" in range_data
    
    def test_dxy_bond_alignment_custom_bond(self, client):
        """Test con bono personalizado"""
        response = client.get("/api/market-briefing/dxy-bond-alignment?bond=US02Y")
        
        assert response.status_code == 200
        data = response.json()
        assert data["bond_symbol"] == "US02Y"
    
    def test_dxy_bond_alignment_invalid_bond(self, client):
        """Test con bono inválido"""
        response = client.get("/api/market-briefing/dxy-bond-alignment?bond=INVALID")
        assert response.status_code in [400, 422]


class TestTradingModeEndpoint:
    """Tests E2E para el endpoint de trading-mode"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_trading_mode_endpoint(self, client):
        """Test básico del endpoint de trading-mode"""
        response = client.get("/api/market-briefing/trading-mode")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert "mode" in data
        assert "confidence" in data
        assert "reasoning" in data
        assert "factors" in data
        
        # Verificar tipos
        assert isinstance(data["mode"], str)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["reasoning"], str)
        assert isinstance(data["factors"], dict)
        
        # Verificar rango de confianza
        assert 0 <= data["confidence"] <= 1
        
        # Verificar modo válido
        assert data["mode"] in ["CALM", "AGGRESSIVE", "OBSERVE"]
    
    def test_trading_mode_operational_levels(self, client):
        """Test que incluye niveles operativos (Mejora 2 Fase 2.5)"""
        response = client.get("/api/market-briefing/trading-mode")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que incluye niveles operativos
        assert "operational_levels" in data
        assert isinstance(data["operational_levels"], list)
        
        # Si hay niveles, verificar estructura
        if len(data["operational_levels"]) > 0:
            level = data["operational_levels"][0]
            assert "level" in level
            assert "type" in level
            assert "distance_points" in level
            assert "distance_percentage" in level
            assert "strength" in level
            assert "action" in level
            assert "explanation" in level
    
    def test_trading_mode_with_custom_params(self, client):
        """Test con parámetros personalizados"""
        response = client.get(
            "/api/market-briefing/trading-mode"
            "?instrument=XAUUSD&bond=US10Y&time_window_minutes=60"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["mode"], str)
    
    def test_trading_mode_time_window_validation(self, client):
        """Test validación de time_window_minutes"""
        # Menor que el mínimo
        response = client.get("/api/market-briefing/trading-mode?time_window_minutes=20")
        assert response.status_code == 422
        
        # Mayor que el máximo
        response = client.get("/api/market-briefing/trading-mode?time_window_minutes=400")
        assert response.status_code == 422


class TestTradingRecommendationEndpoint:
    """Tests E2E para el endpoint de trading-recommendation"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_trading_recommendation_endpoint(self, client):
        """Test básico del endpoint de trading-recommendation"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura básica
        assert "direction" in data
        assert "confidence" in data
        assert "entry_price" in data
        assert "stop_loss" in data
        assert "take_profit" in data
        assert "justification" in data
        
        # Verificar campos nuevos (Mejora 1 Fase 2.5)
        assert "disclaimer" in data
        assert "risk_reward_details" in data
        
        # Verificar tipos
        assert isinstance(data["direction"], str)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["disclaimer"], str)
        
        # Verificar dirección válida
        assert data["direction"] in ["BUY", "SELL", "WAIT"]
    
    def test_trading_recommendation_risk_reward_details(self, client):
        """Test estructura de risk_reward_details (Mejora 1 Fase 2.5)"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["risk_reward_details"] is not None:
            rr_details = data["risk_reward_details"]
            assert "risk_points" in rr_details
            assert "reward_points" in rr_details
            assert "risk_percent" in rr_details
            assert "reward_percent" in rr_details
            assert "min_ratio_met" in rr_details
            assert "explanation" in rr_details
            
            # Verificar tipos
            assert isinstance(rr_details["risk_points"], (int, float))
            assert isinstance(rr_details["reward_points"], (int, float))
            assert isinstance(rr_details["risk_percent"], (int, float))
            assert isinstance(rr_details["reward_percent"], (int, float))
            assert isinstance(rr_details["min_ratio_met"], bool)
            assert isinstance(rr_details["explanation"], str)
    
    def test_trading_recommendation_disclaimer_present(self, client):
        """Test que el disclaimer está presente y no vacío"""
        response = client.get("/api/market-briefing/trading-recommendation")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["disclaimer"] is not None
        assert len(data["disclaimer"]) > 0
        # Debe mencionar que no es consejo financiero
        assert any(word in data["disclaimer"].lower() for word in ["riesgo", "análisis", "probabilidad"])
    
    def test_trading_recommendation_with_params(self, client):
        """Test con parámetros personalizados"""
        response = client.get(
            "/api/market-briefing/trading-recommendation"
            "?instrument=XAUUSD&bond=US02Y&time_window_minutes=90"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["direction"], str)


class TestTechnicalAnalysisEndpoint:
    """Tests E2E para el endpoint de technical-analysis"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_technical_analysis_endpoint(self, client):
        """Test básico del endpoint de technical-analysis"""
        response = client.get("/api/market-briefing/technical-analysis")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura multi-timeframe
        assert "instrument" in data
        assert "analysis_datetime" in data
        assert "timeframes" in data
        
        # Verificar que hay al menos un timeframe
        assert isinstance(data["timeframes"], dict)
        assert len(data["timeframes"]) > 0
    
    def test_technical_analysis_timeframes(self, client):
        """Test que incluye análisis en múltiples temporalidades"""
        response = client.get("/api/market-briefing/technical-analysis")
        
        assert response.status_code == 200
        data = response.json()
        
        timeframes = data["timeframes"]
        
        # Verificar que al menos uno de los timeframes esperados está presente
        expected_tfs = ["daily", "h4", "h1", "m15"]
        assert any(tf in timeframes for tf in expected_tfs)
        
        # Verificar estructura de un timeframe
        if "daily" in timeframes:
            daily = timeframes["daily"]
            assert "trend" in daily
            assert "rsi" in daily or "indicators" in daily
    
    def test_technical_analysis_with_instrument(self, client):
        """Test con instrumento personalizado"""
        response = client.get("/api/market-briefing/technical-analysis?instrument=XAUUSD")
        
        assert response.status_code == 200
        data = response.json()
        assert data["instrument"] == "XAUUSD"
    
    def test_technical_analysis_invalid_instrument(self, client):
        """Test con instrumento inválido"""
        response = client.get("/api/market-briefing/technical-analysis?instrument=INVALID@#")
        assert response.status_code in [400, 422]


class TestHighImpactNewsGeopolitical:
    """Tests E2E para geopolitical risk en high-impact-news"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_high_impact_news_geopolitical_risk(self, client):
        """Test que incluye análisis de riesgo geopolítico (Fase 2)"""
        response = client.get("/api/market-briefing/high-impact-news")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que incluye geopolitical_risk
        if "geopolitical_risk" in data and data["geopolitical_risk"] is not None:
            risk = data["geopolitical_risk"]
            assert "level" in risk
            assert "score" in risk
            assert "explanation" in risk
            
            # Verificar nivel válido
            assert risk["level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            
            # Verificar rango de score
            assert 0 <= risk["score"] <= 1


class TestAPIHealth:
    """Tests E2E para health checks y disponibilidad general"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    def test_all_endpoints_respond(self, client):
        """Test que todos los endpoints principales responden"""
        endpoints = [
            "/api/market-briefing/high-impact-news",
            "/api/market-briefing/event-schedule",
            "/api/market-briefing/yesterday-analysis?instrument=XAUUSD",
            "/api/market-briefing/dxy-bond-alignment",
            "/api/market-briefing/trading-mode",
            "/api/market-briefing/trading-recommendation",
            "/api/market-briefing/technical-analysis",
            "/api/market-briefing/psychological-levels"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed with status {response.status_code}"
    
    def test_api_returns_json(self, client):
        """Test que todos los endpoints devuelven JSON"""
        endpoints = [
            "/api/market-briefing/high-impact-news",
            "/api/market-briefing/event-schedule",
            "/api/market-briefing/dxy-bond-alignment"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.headers["content-type"] == "application/json"
            # Verificar que es JSON válido
            data = response.json()
            assert isinstance(data, dict)


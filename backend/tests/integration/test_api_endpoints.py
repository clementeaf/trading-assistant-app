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


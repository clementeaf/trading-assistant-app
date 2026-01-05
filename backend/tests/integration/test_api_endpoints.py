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


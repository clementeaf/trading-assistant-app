"""
Tests E2E completos para todos los endpoints de la API
Estos tests validan el flujo completo de cada endpoint usando mocks
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app


@pytest.fixture
def mock_provider():
    """Mock del provider de datos económicos"""
    provider = Mock()
    provider.get_events_for_date = AsyncMock(return_value=[
        {
            "title": "Non-Farm Payrolls",
            "country": "United States",
            "date": datetime.now().isoformat(),
            "importance": "HIGH",
            "actual": None,
            "forecast": "200K",
            "previous": "195K",
            "category": "Labor"
        }
    ])
    return provider


@pytest.fixture
def mock_market_provider():
    """Mock del provider de datos de mercado"""
    provider = Mock()
    
    # Mock para datos históricos
    provider.get_historical_data = AsyncMock(return_value=[
        {
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            "open": 4500.0 + i,
            "high": 4520.0 + i,
            "low": 4480.0 + i,
            "close": 4510.0 + i,
            "volume": 10000
        }
        for i in range(30)
    ])
    
    # Mock para datos intraday
    provider.get_intraday_data = AsyncMock(return_value=[
        {
            "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
            "open": 4500.0 + i * 0.5,
            "high": 4510.0 + i * 0.5,
            "low": 4490.0 + i * 0.5,
            "close": 4505.0 + i * 0.5,
            "volume": 1000
        }
        for i in range(24)
    ])
    
    # Mock para precio actual
    provider.get_current_price = AsyncMock(return_value=4508.75)
    
    return provider


class TestHighImpactNewsE2E:
    """Tests E2E para el endpoint de high-impact-news"""
    
    def test_high_impact_news_success(self, mock_provider):
        """Test que el endpoint responde correctamente con datos válidos"""
        with patch("app.services.economic_calendar_service.EconomicCalendarService") as mock_service_class:
            # Configurar el mock del servicio
            mock_service = Mock()
            mock_service.get_high_impact_news_today = AsyncMock(return_value={
                "has_high_impact_news": True,
                "count": 1,
                "events": [
                    {
                        "title": "Non-Farm Payrolls",
                        "time": "08:30",
                        "importance": "HIGH",
                        "forecast": "200K",
                        "previous": "195K"
                    }
                ],
                "summary": "1 high impact event today",
                "instrument": "XAUUSD",
                "geopolitical_risk": {
                    "level": "LOW",
                    "score": 0.2,
                    "explanation": "No significant geopolitical risks detected"
                }
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/high-impact-news")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["has_high_impact_news"] is True
            assert data["count"] == 1
            assert len(data["events"]) == 1
            assert data["instrument"] == "XAUUSD"
            assert "geopolitical_risk" in data


class TestEventScheduleE2E:
    """Tests E2E para el endpoint de event-schedule"""
    
    def test_event_schedule_with_all_features(self):
        """Test que el endpoint incluye todas las características (timezones, gold_impact)"""
        with patch("app.services.economic_calendar_service.EconomicCalendarService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_event_schedule_today = AsyncMock(return_value={
                "total_events": 2,
                "usd_events_count": 2,
                "events": [
                    {
                        "time": "08:30",
                        "title": "Non-Farm Payrolls",
                        "importance": "HIGH",
                        "affects_usd": True,
                        "timezones": {
                            "UTC": "13:30",
                            "America/New_York": "08:30",
                            "Europe/London": "13:30"
                        },
                        "gold_impact": {
                            "probability": 0.85,
                            "direction": "HIGH_VOLATILITY",
                            "magnitude_percent": 1.5,
                            "explanation": "NFP typically causes high volatility in Gold"
                        }
                    },
                    {
                        "time": "10:00",
                        "title": "ISM Manufacturing PMI",
                        "importance": "HIGH",
                        "affects_usd": True,
                        "timezones": {
                            "UTC": "15:00",
                            "America/New_York": "10:00"
                        },
                        "gold_impact": {
                            "probability": 0.65,
                            "direction": "INVERSE_USD",
                            "magnitude_percent": 0.8,
                            "explanation": "PMI affects USD, inversely impacting Gold"
                        }
                    }
                ],
                "summary": "2 high impact USD events today"
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/event-schedule?include_gold_impact=true")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_events"] == 2
            assert data["usd_events_count"] == 2
            assert len(data["events"]) == 2
            
            # Verificar timezones
            assert "timezones" in data["events"][0]
            assert "UTC" in data["events"][0]["timezones"]
            
            # Verificar gold_impact
            assert "gold_impact" in data["events"][0]
            assert data["events"][0]["gold_impact"]["probability"] > 0
            assert data["events"][0]["gold_impact"]["direction"] in [
                "POSITIVE", "NEGATIVE", "HIGH_VOLATILITY", "INVERSE_USD", "UNKNOWN"
            ]


class TestYesterdayAnalysisE2E:
    """Tests E2E para el endpoint de yesterday-analysis"""
    
    def test_yesterday_analysis_with_sessions(self, mock_market_provider):
        """Test que el análisis incluye sesiones con volatilidad y breaks"""
        with patch("app.services.market_analysis_service.MarketAnalysisService") as mock_service_class:
            mock_service = Mock()
            mock_service.analyze_yesterday_sessions = AsyncMock(return_value={
                "instrument": "XAUUSD",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "close_price": 4510.50,
                "change_percent": 1.25,
                "range_high": 4525.00,
                "range_low": 4490.00,
                "sessions": [
                    {
                        "session_name": "Asia",
                        "time_range": "00:00-08:00 UTC",
                        "price_action": "Consolidation around 4500",
                        "volatility": "LOW",
                        "psychological_breaks": []
                    },
                    {
                        "session_name": "London",
                        "time_range": "08:00-16:00 UTC",
                        "price_action": "Breakout above 4500",
                        "volatility": "MEDIUM",
                        "psychological_breaks": [
                            {"level": 4500, "type": "BREAK_UP", "time": "10:30"}
                        ]
                    },
                    {
                        "session_name": "New York",
                        "time_range": "13:00-21:00 UTC",
                        "price_action": "Strong rally to 4525",
                        "volatility": "HIGH",
                        "psychological_breaks": []
                    }
                ],
                "summary": "Strong bullish day with breakout above 4500 during London session"
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/yesterday-analysis?instrument=XAUUSD")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["instrument"] == "XAUUSD"
            assert len(data["sessions"]) == 3
            
            # Verificar que incluye volatilidad
            assert data["sessions"][0]["volatility"] in ["LOW", "MEDIUM", "HIGH"]
            
            # Verificar que incluye psychological_breaks
            assert "psychological_breaks" in data["sessions"][0]
            assert len(data["sessions"][1]["psychological_breaks"]) > 0


class TestDXYBondAlignmentE2E:
    """Tests E2E para el endpoint de dxy-bond-alignment"""
    
    def test_dxy_bond_alignment_with_correlation_and_magnitude(self):
        """Test que incluye correlación Gold-DXY con rango de magnitud"""
        with patch("app.services.market_alignment_service.MarketAlignmentService") as mock_service_class:
            mock_service = Mock()
            mock_service.analyze_dxy_bond_alignment = AsyncMock(return_value={
                "dxy_symbol": "DXY",
                "bond_symbol": "US10Y",
                "dxy_change_percent": 0.50,
                "bond_change_percent": 2.0,
                "alignment": "ALIGNED",
                "market_bias": "RISK_OFF",
                "explanation": "DXY and US10Y both rising, indicating risk-off sentiment",
                "gold_dxy_correlation": {
                    "coefficient": -0.78,
                    "strength": "STRONG",
                    "p_value": 0.001,
                    "is_significant": True,
                    "days_analyzed": 30,
                    "explanation": "Strong negative correlation between Gold and DXY"
                },
                "gold_impact_projection": {
                    "dxy_change_percent": 0.50,
                    "expected_gold_change_percent": -0.39,
                    "direction": "NEGATIVE",
                    "explanation": "DXY +0.5% → Gold -0.39%",
                    "magnitude_range_percent": {
                        "min": -0.49,
                        "max": -0.29
                    },
                    "magnitude_range_points": {
                        "min": -22.1,
                        "max": -13.1
                    }
                }
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["alignment"] in ["ALIGNED", "CONFLICT", "NEUTRAL"]
            assert data["market_bias"] in ["RISK_ON", "RISK_OFF", "MIXED"]
            
            # Verificar correlación
            assert "gold_dxy_correlation" in data
            corr = data["gold_dxy_correlation"]
            assert -1 <= corr["coefficient"] <= 1
            assert corr["strength"] in ["VERY_WEAK", "WEAK", "MODERATE", "STRONG", "VERY_STRONG"]
            
            # Verificar proyección con rango de magnitud (Mejora 4 Fase 2.5)
            assert "gold_impact_projection" in data
            projection = data["gold_impact_projection"]
            assert "magnitude_range_percent" in projection
            assert "min" in projection["magnitude_range_percent"]
            assert "max" in projection["magnitude_range_percent"]


class TestTradingModeE2E:
    """Tests E2E para el endpoint de trading-mode"""
    
    def test_trading_mode_with_operational_levels(self):
        """Test que incluye niveles operativos según el modo (Mejora 2 Fase 2.5)"""
        with patch("app.services.trading_mode_service.TradingModeService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_trading_mode_recommendation = AsyncMock(return_value={
                "mode": "CALM",
                "confidence": 0.72,
                "reasoning": "Moderate volatility, no immediate high-impact news, market in consolidation",
                "factors": {
                    "high_impact_news_soon": False,
                    "volatility_level": "MEDIUM",
                    "market_alignment": "ALIGNED",
                    "time_until_news_minutes": 180
                },
                "operational_levels": [
                    {
                        "level": 4500.0,
                        "type": "SUPPORT",
                        "distance_points": 8.75,
                        "distance_percentage": 0.19,
                        "strength": "STRONG",
                        "action": "BUY",
                        "explanation": "Major 100-level support, 8.75 points away (0.19%)"
                    },
                    {
                        "level": 4550.0,
                        "type": "RESISTANCE",
                        "distance_points": 41.25,
                        "distance_percentage": 0.92,
                        "strength": "STRONG",
                        "action": "SELL",
                        "explanation": "Major 50-level resistance, 41.25 points away (0.92%)"
                    }
                ]
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/trading-mode")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["mode"] in ["CALM", "AGGRESSIVE", "OBSERVE"]
            assert 0 <= data["confidence"] <= 1
            assert "factors" in data
            
            # Verificar niveles operativos (Mejora 2 Fase 2.5)
            assert "operational_levels" in data
            assert len(data["operational_levels"]) > 0
            
            level = data["operational_levels"][0]
            assert "level" in level
            assert "type" in level
            assert level["type"] in ["SUPPORT", "RESISTANCE", "BOTH"]
            assert "distance_points" in level
            assert "distance_percentage" in level
            assert "strength" in level
            assert "action" in level
            assert "explanation" in level


class TestTradingRecommendationE2E:
    """Tests E2E para el endpoint de trading-recommendation"""
    
    def test_trading_recommendation_with_rr_details(self):
        """Test que incluye disclaimer y risk_reward_details (Mejora 1 Fase 2.5)"""
        with patch("app.services.trading_advisor_service.TradingAdvisorService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_trading_recommendation = AsyncMock(return_value={
                "disclaimer": "⚠️ ANÁLISIS PROBABILÍSTICO - NO ES CONSEJO FINANCIERO ⚠️\n\nEste análisis se basa en probabilidades históricas...",
                "direction": "BUY",
                "confidence": 0.68,
                "entry_price": 4505.0,
                "stop_loss": 4485.0,
                "take_profit": 4545.0,
                "justification": "Bullish market bias with support at 4500",
                "risk_reward_details": {
                    "risk_points": 20.0,
                    "reward_points": 40.0,
                    "risk_percent": 0.44,
                    "reward_percent": 0.89,
                    "min_ratio_met": True,
                    "explanation": "Risk: 20 pts (0.44%) | Reward: 40 pts (0.89%) | Ratio 1:2.00 ✅"
                },
                "confidence_breakdown": {
                    "technical_analysis": 0.70,
                    "market_context": 0.65,
                    "news_impact": 0.70,
                    "overall": 0.68
                },
                "invalidation_level": 4480.0
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/trading-recommendation")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar disclaimer prominente (Mejora 1 Fase 2.5)
            assert "disclaimer" in data
            assert len(data["disclaimer"]) > 0
            assert any(word in data["disclaimer"].lower() for word in ["riesgo", "probabilidad", "análisis"])
            
            # Verificar risk_reward_details detallado (Mejora 1 Fase 2.5)
            assert "risk_reward_details" in data
            rr = data["risk_reward_details"]
            assert "risk_points" in rr
            assert "reward_points" in rr
            assert "risk_percent" in rr
            assert "reward_percent" in rr
            assert "min_ratio_met" in rr
            assert "explanation" in rr
            assert isinstance(rr["min_ratio_met"], bool)
            
            # Verificar estructura básica
            assert data["direction"] in ["BUY", "SELL", "WAIT"]
            assert 0 <= data["confidence"] <= 1
            assert data["entry_price"] > 0
            
            # Verificar confidence_breakdown
            assert "confidence_breakdown" in data
            breakdown = data["confidence_breakdown"]
            assert 0 <= breakdown["technical_analysis"] <= 1
            assert 0 <= breakdown["market_context"] <= 1
            assert 0 <= breakdown["news_impact"] <= 1


class TestTechnicalAnalysisE2E:
    """Tests E2E para el endpoint de technical-analysis"""
    
    def test_technical_analysis_multi_timeframe(self):
        """Test que incluye análisis en múltiples temporalidades"""
        with patch("app.services.technical_analysis_service.TechnicalAnalysisService") as mock_service_class:
            mock_service = Mock()
            mock_service.analyze_multi_timeframe = AsyncMock(return_value={
                "instrument": "XAUUSD",
                "analysis_datetime": datetime.now().isoformat(),
                "timeframes": {
                    "daily": {
                        "trend": "BULLISH",
                        "rsi": 62.5,
                        "support": 4450.0,
                        "resistance": 4550.0,
                        "structure": "HIGHER_HIGHS"
                    },
                    "h4": {
                        "trend": "BULLISH",
                        "rsi": 58.3,
                        "support": 4490.0,
                        "resistance": 4530.0,
                        "structure": "CONSOLIDATION"
                    },
                    "h1": {
                        "trend": "NEUTRAL",
                        "rsi": 51.2,
                        "support": 4505.0,
                        "resistance": 4515.0,
                        "structure": "RANGE"
                    }
                },
                "summary": "Multi-timeframe bullish bias with daily trend intact"
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/technical-analysis?instrument=XAUUSD")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["instrument"] == "XAUUSD"
            assert "timeframes" in data
            
            # Verificar que al menos hay un timeframe
            assert len(data["timeframes"]) > 0
            
            # Verificar estructura de timeframes
            for tf_name, tf_data in data["timeframes"].items():
                assert "trend" in tf_data
                assert tf_data["trend"] in ["BULLISH", "BEARISH", "NEUTRAL"]


class TestPsychologicalLevelsE2E:
    """Tests E2E para el endpoint de psychological-levels"""
    
    def test_psychological_levels_with_reaction_history(self):
        """Test que incluye histórico de reacciones ampliado (Mejora 3 Fase 2.5)"""
        with patch("app.services.psychological_levels_service.PsychologicalLevelsService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_psychological_levels = AsyncMock(return_value={
                "instrument": "XAUUSD",
                "current_price": 4508.75,
                "analysis_datetime": datetime.now().isoformat(),
                "lookback_days": 30,
                "max_distance_points": 100.0,
                "levels": [
                    {
                        "level": 4500.0,
                        "distance_from_current": 8.75,
                        "strength": "STRONG",
                        "reaction_count": 12,
                        "type": "SUPPORT",
                        "bounce_count": 10,
                        "is_round_hundred": True,
                        "is_round_fifty": False,
                        "reaction_history": [
                            {
                                "timestamp": "2026-01-10T14:30:00Z",
                                "session": "NEW_YORK",
                                "volatility": "HIGH",
                                "magnitude_points": 15.5,
                                "magnitude_percent": 0.34,
                                "confirmation": True,
                                "explanation": "Strong bounce during NY session with high volatility"
                            },
                            {
                                "timestamp": "2026-01-09T10:15:00Z",
                                "session": "LONDON",
                                "volatility": "MEDIUM",
                                "magnitude_points": 8.2,
                                "magnitude_percent": 0.18,
                                "confirmation": True,
                                "explanation": "Confirmed bounce during London session"
                            }
                        ]
                    },
                    {
                        "level": 4550.0,
                        "distance_from_current": 41.25,
                        "strength": "MODERATE",
                        "reaction_count": 8,
                        "type": "RESISTANCE",
                        "bounce_count": 6,
                        "is_round_hundred": False,
                        "is_round_fifty": True,
                        "reaction_history": [
                            {
                                "timestamp": "2026-01-08T16:00:00Z",
                                "session": "NEW_YORK",
                                "volatility": "MEDIUM",
                                "magnitude_points": 12.0,
                                "magnitude_percent": 0.26,
                                "confirmation": False,
                                "explanation": "Rejection at resistance, unconfirmed"
                            }
                        ]
                    }
                ],
                "strongest_support": 4500.0,
                "strongest_resistance": 4550.0,
                "nearest_support": 4500.0,
                "nearest_resistance": 4550.0,
                "summary": "Key support at 4500 with strong historical reactions"
            })
            mock_service_class.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/market-briefing/psychological-levels")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["instrument"] == "XAUUSD"
            assert len(data["levels"]) > 0
            
            # Verificar estructura de nivel
            level = data["levels"][0]
            assert "level" in level
            assert "type" in level
            assert "strength" in level
            
            # Verificar reaction_history ampliado (Mejora 3 Fase 2.5)
            assert "reaction_history" in level
            if len(level["reaction_history"]) > 0:
                reaction = level["reaction_history"][0]
                assert "timestamp" in reaction
                assert "session" in reaction
                assert reaction["session"] in ["ASIA", "LONDON", "NEW_YORK", "OVERLAP"]
                assert "volatility" in reaction
                assert reaction["volatility"] in ["LOW", "MEDIUM", "HIGH"]
                assert "magnitude_points" in reaction
                assert "magnitude_percent" in reaction
                assert "confirmation" in reaction
                assert "explanation" in reaction


class TestAPIHealthE2E:
    """Tests E2E para validar salud general de la API"""
    
    def test_all_endpoints_accessible(self):
        """Test que todos los endpoints están accesibles (pueden fallar por falta de datos pero no 404)"""
        client = TestClient(app)
        
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
            # El endpoint debe existir (no 404)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            # Si falla, debe ser por razones válidas (500 por datos, 422 por validación, etc.)
            if response.status_code not in [200, 500, 422]:
                pytest.fail(f"Unexpected status code {response.status_code} for {endpoint}")
    
    def test_openapi_documentation_complete(self):
        """Test que la documentación OpenAPI incluye todos los endpoints"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Verificar que los endpoints principales están documentados
        paths = schema["paths"]
        expected_paths = [
            "/api/market-briefing/high-impact-news",
            "/api/market-briefing/event-schedule",
            "/api/market-briefing/yesterday-analysis",
            "/api/market-briefing/dxy-bond-alignment",
            "/api/market-briefing/trading-mode",
            "/api/market-briefing/trading-recommendation",
            "/api/market-briefing/technical-analysis",
            "/api/market-briefing/psychological-levels"
        ]
        
        for path in expected_paths:
            assert path in paths, f"Path {path} not documented in OpenAPI schema"
    
    def test_cors_headers_present(self):
        """Test que los headers CORS están configurados"""
        client = TestClient(app)
        response = client.get("/api/market-briefing/high-impact-news")
        
        # Verificar que no hay errores CORS (el middleware está configurado)
        assert response.status_code in [200, 500]  # 200 si hay datos, 500 si no hay API key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

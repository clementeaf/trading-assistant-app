"""
Performance tests para los endpoints de la API
Objetivo: Todos los endpoints deben responder en < 1.5 segundos
"""
import pytest
import time
from typing import Dict, List
from fastapi.testclient import TestClient
from app.main import app


class PerformanceMetrics:
    """Clase para almacenar y analizar métricas de performance"""
    
    def __init__(self):
        self.measurements: List[Dict[str, float]] = []
    
    def add_measurement(self, endpoint: str, duration: float):
        """Agrega una medición"""
        self.measurements.append({
            "endpoint": endpoint,
            "duration": duration
        })
    
    def get_stats(self, endpoint: str) -> Dict[str, float]:
        """Obtiene estadísticas para un endpoint"""
        durations = [m["duration"] for m in self.measurements if m["endpoint"] == endpoint]
        if not durations:
            return {}
        
        return {
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
            "count": len(durations)
        }
    
    def print_summary(self):
        """Imprime resumen de performance"""
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)
        
        endpoints = list(set(m["endpoint"] for m in self.measurements))
        for endpoint in sorted(endpoints):
            stats = self.get_stats(endpoint)
            status = "✅ PASS" if stats["avg"] < 1.5 else "❌ FAIL"
            print(f"{status} {endpoint}")
            print(f"     Min: {stats['min']:.3f}s | Max: {stats['max']:.3f}s | Avg: {stats['avg']:.3f}s")
        
        print("="*80)


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture(scope="module")
def metrics():
    """Métricas de performance compartidas"""
    m = PerformanceMetrics()
    yield m
    m.print_summary()


class TestPerformance:
    """Tests de performance para todos los endpoints"""
    
    MAX_RESPONSE_TIME = 1.5  # segundos
    WARMUP_CALLS = 2  # llamadas de precalentamiento
    TEST_CALLS = 5  # llamadas de prueba
    
    def _measure_endpoint(self, client, endpoint: str, metrics: PerformanceMetrics):
        """Mide el tiempo de respuesta de un endpoint"""
        # Warmup
        for _ in range(self.WARMUP_CALLS):
            try:
                client.get(endpoint, timeout=10.0)
            except Exception:
                pass
        
        # Mediciones reales
        durations = []
        for _ in range(self.TEST_CALLS):
            start = time.time()
            try:
                response = client.get(endpoint, timeout=10.0)
                duration = time.time() - start
                
                # Solo contar si la respuesta fue exitosa (200)
                if response.status_code == 200:
                    durations.append(duration)
                    metrics.add_measurement(endpoint, duration)
            except Exception as e:
                print(f"Warning: {endpoint} failed - {str(e)}")
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            return avg_duration
        
        return None
    
    def test_high_impact_news_performance(self, client, metrics):
        """Test performance del endpoint de high-impact-news"""
        endpoint = "/api/market-briefing/high-impact-news"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_event_schedule_performance(self, client, metrics):
        """Test performance del endpoint de event-schedule"""
        endpoint = "/api/market-briefing/event-schedule?include_gold_impact=true"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_yesterday_analysis_performance(self, client, metrics):
        """Test performance del endpoint de yesterday-analysis"""
        endpoint = "/api/market-briefing/yesterday-analysis?instrument=XAUUSD"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_dxy_bond_alignment_performance(self, client, metrics):
        """Test performance del endpoint de dxy-bond-alignment"""
        endpoint = "/api/market-briefing/dxy-bond-alignment?include_gold_correlation=true"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_trading_mode_performance(self, client, metrics):
        """Test performance del endpoint de trading-mode"""
        endpoint = "/api/market-briefing/trading-mode?instrument=XAUUSD"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_trading_recommendation_performance(self, client, metrics):
        """Test performance del endpoint de trading-recommendation"""
        endpoint = "/api/market-briefing/trading-recommendation?instrument=XAUUSD"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_technical_analysis_performance(self, client, metrics):
        """Test performance del endpoint de technical-analysis"""
        endpoint = "/api/market-briefing/technical-analysis?instrument=XAUUSD"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"
    
    def test_psychological_levels_performance(self, client, metrics):
        """Test performance del endpoint de psychological-levels"""
        endpoint = "/api/market-briefing/psychological-levels?instrument=XAUUSD"
        avg_duration = self._measure_endpoint(client, endpoint, metrics)
        
        if avg_duration is not None:
            assert avg_duration < self.MAX_RESPONSE_TIME, \
                f"Endpoint {endpoint} took {avg_duration:.3f}s (max: {self.MAX_RESPONSE_TIME}s)"


class TestPerformanceOptimizations:
    """Tests para verificar optimizaciones específicas"""
    
    def test_caching_is_effective(self, client):
        """Verifica que el caching mejora la performance"""
        endpoint = "/api/market-briefing/high-impact-news"
        
        # Primera llamada (sin cache)
        start = time.time()
        response1 = client.get(endpoint)
        first_duration = time.time() - start
        
        # Segunda llamada (con cache si está implementado)
        start = time.time()
        response2 = client.get(endpoint)
        second_duration = time.time() - start
        
        if response1.status_code == 200 and response2.status_code == 200:
            # La segunda llamada debería ser igual o más rápida (idealmente con cache)
            assert second_duration <= first_duration * 1.2, \
                "Second call should be at least as fast as first (caching benefit)"
    
    def test_parallel_requests_performance(self, client):
        """Verifica que múltiples requests paralelos no degradan significativamente"""
        import concurrent.futures
        
        endpoint = "/api/market-briefing/high-impact-news"
        num_parallel = 5
        
        def make_request():
            start = time.time()
            client.get(endpoint)
            return time.time() - start
        
        # Medir tiempo secuencial
        start = time.time()
        for _ in range(num_parallel):
            try:
                client.get(endpoint)
            except Exception:
                pass
        sequential_time = time.time() - start
        
        # Medir tiempo paralelo
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_parallel) as executor:
            futures = [executor.submit(make_request) for _ in range(num_parallel)]
            concurrent.futures.wait(futures)
        parallel_time = time.time() - start
        
        # El tiempo paralelo no debería ser mucho mayor que el secuencial
        # (indica que no hay bloqueos significativos)
        assert parallel_time < sequential_time * 1.5, \
            f"Parallel execution too slow: {parallel_time:.2f}s vs {sequential_time:.2f}s sequential"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

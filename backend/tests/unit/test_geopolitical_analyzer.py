"""
Tests para GeopoliticalAnalyzer
"""
import pytest
from datetime import datetime
from app.utils.geopolitical_analyzer import GeopoliticalAnalyzer
from app.models.geopolitical_risk import GeopoliticalRiskLevel
from app.models.economic_calendar import EconomicEvent, ImpactLevel


class TestGeopoliticalAnalyzer:
    """
    Tests para análisis de riesgo geopolítico
    """
    
    def _create_event(self, description: str, country: str = "US") -> EconomicEvent:
        """
        Crea un evento económico de prueba
        """
        return EconomicEvent(
            date=datetime.now(),
            importance=ImpactLevel.HIGH,
            currency="USD",
            description=description,
            country=country
        )
    
    def test_high_risk_with_war_keyword(self) -> None:
        """
        Detectar alto riesgo con keyword 'war'
        """
        events = [self._create_event("War impact on oil prices")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.level in [GeopoliticalRiskLevel.MEDIUM, GeopoliticalRiskLevel.HIGH]
        assert risk.score >= 0.3
        assert len(risk.factors) > 0
        assert any("war" in f.lower() for f in risk.factors)
    
    def test_high_risk_with_conflict_keyword(self) -> None:
        """
        Detectar alto riesgo con keyword 'conflict'
        """
        events = [self._create_event("Military conflict escalation")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.level in [GeopoliticalRiskLevel.MEDIUM, GeopoliticalRiskLevel.HIGH]
        assert risk.score >= 0.3
        assert any("conflict" in f.lower() for f in risk.factors)
    
    def test_medium_risk_with_tensions(self) -> None:
        """
        Detectar riesgo medio con keyword 'tensions'
        """
        events = [self._create_event("Rising tensions in trade")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.level in [GeopoliticalRiskLevel.LOW, GeopoliticalRiskLevel.MEDIUM]
        assert risk.score > 0.0
        assert any("tensions" in f.lower() for f in risk.factors)
    
    def test_low_risk_no_keywords(self) -> None:
        """
        Sin keywords = riesgo bajo
        """
        events = [self._create_event("GDP Growth Report")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.level == GeopoliticalRiskLevel.LOW
        assert risk.score <= 0.3
    
    def test_critical_region_boost_middle_east(self) -> None:
        """
        Boost por región crítica: Middle East
        """
        events = [self._create_event("War in Middle East", "Middle East")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.score >= 0.5  # war (0.3) + middle east (0.2)
        assert any("middle east" in f.lower() for f in risk.factors)
    
    def test_critical_region_boost_ukraine(self) -> None:
        """
        Boost por región crítica: Ukraine
        """
        events = [self._create_event("Conflict escalation", "Ukraine")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.score >= 0.5  # conflict (0.3) + ukraine (0.2)
        assert any("ukraine" in f.lower() or "conflict" in f.lower() for f in risk.factors)
    
    def test_multiple_keywords_cumulative(self) -> None:
        """
        Múltiples keywords suman score
        """
        events = [
            self._create_event("War and sanctions impact"),
            self._create_event("Military conflict escalates")
        ]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.score >= 0.6  # múltiples keywords de alto riesgo
        assert risk.level in [GeopoliticalRiskLevel.HIGH, GeopoliticalRiskLevel.CRITICAL]
    
    def test_score_bounded_between_0_and_1(self) -> None:
        """
        Score siempre entre 0.0 y 1.0
        """
        events = [
            self._create_event("War conflict sanctions invasion military attack"),
            self._create_event("Crisis in Middle East and Ukraine"),
            self._create_event("Terrorism threat in Iran")
        ]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert 0.0 <= risk.score <= 1.0
    
    def test_empty_events_list(self) -> None:
        """
        Lista vacía = riesgo bajo por defecto
        """
        risk = GeopoliticalAnalyzer.analyze_risk([])
        
        assert risk.level == GeopoliticalRiskLevel.LOW
        assert risk.score == 0.0
        assert len(risk.factors) == 0
    
    def test_factors_list_populated(self) -> None:
        """
        Factors list contiene keywords encontrados
        """
        events = [self._create_event("War and tensions in Middle East")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert len(risk.factors) > 0
        # Debe contener al menos uno de: war, tensions, middle east
        combined_factors = " ".join(risk.factors).lower()
        assert any(
            keyword in combined_factors 
            for keyword in ["war", "tensions", "middle east"]
        )
    
    def test_score_0_to_0_3_is_low(self) -> None:
        """
        Score 0-0.3 = bajo
        """
        events = [self._create_event("Normal GDP report")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        if risk.score <= 0.3:
            assert risk.level == GeopoliticalRiskLevel.LOW
    
    def test_score_0_3_to_0_6_is_medium(self) -> None:
        """
        Score 0.3-0.6 = medio
        """
        events = [self._create_event("Tensions and dispute")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        if 0.3 <= risk.score < 0.6:
            assert risk.level == GeopoliticalRiskLevel.MEDIUM
    
    def test_score_0_6_to_0_8_is_high(self) -> None:
        """
        Score 0.6-0.8 = alto
        """
        events = [self._create_event("War and conflict escalation")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        if 0.6 <= risk.score < 0.8:
            assert risk.level == GeopoliticalRiskLevel.HIGH
    
    def test_score_above_0_8_is_critical(self) -> None:
        """
        Score >0.8 = crítico
        """
        events = [
            self._create_event("War and military action in Middle East"),
            self._create_event("Conflict and sanctions in Ukraine")
        ]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        if risk.score >= 0.8:
            assert risk.level == GeopoliticalRiskLevel.CRITICAL
    
    def test_description_generation(self) -> None:
        """
        Descripción correcta generada
        """
        events = [self._create_event("War impact")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.description != ""
        assert "riesgo" in risk.description.lower() or "risk" in risk.description.lower()
    
    def test_additional_text_parameter(self) -> None:
        """
        Parámetro additional_text se analiza
        """
        risk = GeopoliticalAnalyzer.analyze_risk(
            [],
            additional_text="War and conflict in Middle East"
        )
        
        assert risk.score > 0.0
        assert risk.level != GeopoliticalRiskLevel.LOW
    
    def test_last_updated_timestamp(self) -> None:
        """
        last_updated contiene timestamp
        """
        events = [self._create_event("Normal report")]
        
        risk = GeopoliticalAnalyzer.analyze_risk(events)
        
        assert risk.last_updated is not None
        assert isinstance(risk.last_updated, datetime)

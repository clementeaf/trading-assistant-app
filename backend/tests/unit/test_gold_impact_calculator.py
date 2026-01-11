"""
Tests para GoldImpactCalculator
"""
import pytest
from app.utils.gold_impact_calculator import GoldImpactCalculator
from app.models.gold_impact import ImpactDirection, ImpactMagnitude


class TestGoldImpactCalculator:
    """
    Tests para cálculo de impacto en Gold
    """
    
    def test_detect_nfp_event(self) -> None:
        """
        Detectar evento NFP
        """
        event_type = GoldImpactCalculator._detect_event_type(
            "Non-Farm Payrolls",
            "US employment data"
        )
        assert event_type == "NFP"
        
        event_type = GoldImpactCalculator._detect_event_type("NFP", None)
        assert event_type == "NFP"
    
    def test_detect_cpi_event(self) -> None:
        """
        Detectar evento CPI
        """
        event_type = GoldImpactCalculator._detect_event_type(
            "Consumer Price Index",
            "Inflation data"
        )
        assert event_type == "CPI"
    
    def test_detect_fomc_event(self) -> None:
        """
        Detectar evento FOMC
        """
        event_type = GoldImpactCalculator._detect_event_type(
            "FOMC Meeting",
            "Federal Open Market Committee decision"
        )
        assert event_type == "FOMC"
    
    def test_detect_gdp_event(self) -> None:
        """
        Detectar evento GDP
        """
        event_type = GoldImpactCalculator._detect_event_type(
            "GDP Report",
            "Gross Domestic Product"
        )
        assert event_type == "GDP"
    
    def test_detect_unknown_event(self) -> None:
        """
        Evento desconocido
        """
        event_type = GoldImpactCalculator._detect_event_type(
            "Some Random Event",
            "Not a known economic indicator"
        )
        assert event_type == "UNKNOWN"
    
    def test_nfp_high_probability(self) -> None:
        """
        NFP tiene alta probabilidad de impacto
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Non-Farm Payrolls",
            importance="high"
        )
        
        assert impact.probability >= 0.9
        assert impact.event_type == "NFP"
    
    def test_cpi_high_probability(self) -> None:
        """
        CPI tiene alta probabilidad de impacto
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Consumer Price Index",
            importance="high"
        )
        
        assert impact.probability >= 0.85
        assert impact.event_type == "CPI"
    
    def test_fomc_high_probability(self) -> None:
        """
        FOMC tiene alta probabilidad de impacto
        """
        impact = GoldImpactCalculator.calculate_impact(
            "FOMC Meeting",
            importance="high"
        )
        
        assert impact.probability >= 0.9
        assert impact.event_type == "FOMC"
    
    def test_retail_sales_medium_probability(self) -> None:
        """
        Retail Sales tiene probabilidad media
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Retail Sales",
            importance="medium"
        )
        
        assert 0.5 <= impact.probability <= 0.7
        assert impact.event_type == "RETAIL_SALES"
    
    def test_housing_low_probability(self) -> None:
        """
        Housing tiene probabilidad baja
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Housing Starts",
            importance="low"
        )
        
        assert impact.probability <= 0.6
        assert impact.event_type == "HOUSING"
    
    def test_unknown_event_default_probability(self) -> None:
        """
        Evento desconocido tiene probabilidad default 0.5 + boost
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Unknown Event",
            importance="medium"
        )
        
        assert impact.probability == 0.55  # 0.5 base + 0.05 medium boost
        assert impact.event_type == "UNKNOWN"
    
    def test_importance_boost_high(self) -> None:
        """
        Importancia alta boost +0.1
        """
        probability_high = GoldImpactCalculator._calculate_probability(
            "PMI", "high"
        )
        probability_medium = GoldImpactCalculator._calculate_probability(
            "PMI", "medium"
        )
        
        assert probability_high > probability_medium
        assert probability_high - probability_medium == pytest.approx(0.05, abs=0.01)
    
    def test_probability_capped_at_1(self) -> None:
        """
        Probabilidad máxima 1.0
        """
        probability = GoldImpactCalculator._calculate_probability(
            "NFP", "high"
        )
        
        assert probability <= 1.0
    
    def test_nfp_direction_bearish(self) -> None:
        """
        NFP fuerte es bajista para Gold
        """
        direction, note = GoldImpactCalculator._estimate_direction(
            "NFP", "Non-Farm Payrolls"
        )
        
        assert direction == ImpactDirection.BEARISH
        assert "fuerte" in note.lower()
    
    def test_cpi_direction_bullish(self) -> None:
        """
        CPI alta es alcista para Gold
        """
        direction, note = GoldImpactCalculator._estimate_direction(
            "CPI", "Consumer Price Index"
        )
        
        assert direction == ImpactDirection.BULLISH
        assert "inflación" in note.lower()
    
    def test_fomc_direction_bearish(self) -> None:
        """
        FOMC hawkish es bajista para Gold
        """
        direction, note = GoldImpactCalculator._estimate_direction(
            "FOMC", "FOMC Meeting"
        )
        
        assert direction == ImpactDirection.BEARISH
        assert "hawkish" in note.lower() or "tasas" in note.lower()
    
    def test_unknown_direction_neutral(self) -> None:
        """
        Evento desconocido tiene dirección neutral
        """
        direction, note = GoldImpactCalculator._estimate_direction(
            "UNKNOWN", "Unknown Event"
        )
        
        assert direction == ImpactDirection.NEUTRAL
        assert note is not None
    
    def test_nfp_magnitude_high(self) -> None:
        """
        NFP tiene magnitud alta
        """
        magnitude, magnitude_range = GoldImpactCalculator._estimate_magnitude(
            "NFP", 2000.0
        )
        
        assert magnitude in [ImpactMagnitude.MEDIUM, ImpactMagnitude.HIGH]
        assert "50" in magnitude_range or "150" in magnitude_range
    
    def test_fomc_magnitude_very_high(self) -> None:
        """
        FOMC tiene magnitud muy alta
        """
        magnitude, magnitude_range = GoldImpactCalculator._estimate_magnitude(
            "FOMC", 2000.0
        )
        
        assert magnitude in [ImpactMagnitude.HIGH, ImpactMagnitude.VERY_HIGH]
        assert "100" in magnitude_range or "250" in magnitude_range
    
    def test_housing_magnitude_low(self) -> None:
        """
        Housing tiene magnitud baja
        """
        magnitude, magnitude_range = GoldImpactCalculator._estimate_magnitude(
            "HOUSING", 2000.0
        )
        
        assert magnitude in [ImpactMagnitude.VERY_LOW, ImpactMagnitude.LOW]
        assert "10" in magnitude_range or "40" in magnitude_range
    
    def test_confidence_nfp_high(self) -> None:
        """
        Confianza alta para NFP
        """
        confidence = GoldImpactCalculator._calculate_confidence("NFP", 0.95)
        assert confidence >= 0.85
    
    def test_confidence_unknown_low(self) -> None:
        """
        Confianza baja para evento desconocido
        """
        confidence = GoldImpactCalculator._calculate_confidence("UNKNOWN", 0.5)
        assert confidence <= 0.4
    
    def test_confidence_pmi_medium(self) -> None:
        """
        Confianza media para PMI
        """
        confidence = GoldImpactCalculator._calculate_confidence("PMI", 0.7)
        assert 0.5 <= confidence <= 0.8
    
    def test_calculate_impact_complete_nfp(self) -> None:
        """
        Cálculo completo de impacto para NFP
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Non-Farm Payrolls",
            "US employment data",
            importance="high",
            current_gold_price=2000.0
        )
        
        assert impact.probability >= 0.9
        assert impact.direction == ImpactDirection.BEARISH
        assert impact.direction_note is not None
        assert impact.magnitude in [ImpactMagnitude.MEDIUM, ImpactMagnitude.HIGH]
        assert impact.confidence >= 0.85
        assert impact.reasoning != ""
        assert impact.event_type == "NFP"
    
    def test_calculate_impact_complete_cpi(self) -> None:
        """
        Cálculo completo de impacto para CPI
        """
        impact = GoldImpactCalculator.calculate_impact(
            "Consumer Price Index",
            "Inflation report",
            importance="high",
            current_gold_price=2050.0
        )
        
        assert impact.probability >= 0.85
        assert impact.direction == ImpactDirection.BULLISH
        assert "inflación" in impact.direction_note.lower()
        assert impact.magnitude in [
            ImpactMagnitude.MEDIUM,
            ImpactMagnitude.HIGH
        ]
        assert impact.confidence >= 0.8
        assert "CPI" in impact.reasoning or "Precios" in impact.reasoning
    
    def test_reasoning_generation(self) -> None:
        """
        Generación de razonamiento textual
        """
        reasoning = GoldImpactCalculator._generate_reasoning(
            "NFP", 0.95, ImpactDirection.BEARISH, "50-150 puntos"
        )
        
        assert "alta" in reasoning.lower() or "95%" in reasoning
        assert "bajista" in reasoning.lower()
        assert "50-150" in reasoning
    
    def test_all_event_types_have_probabilities(self) -> None:
        """
        Todos los tipos de eventos tienen probabilidad definida
        """
        for event_type in GoldImpactCalculator.EVENT_PROBABILITIES.keys():
            probability = GoldImpactCalculator._calculate_probability(
                event_type, "medium"
            )
            assert 0.0 <= probability <= 1.0
    
    def test_all_event_types_have_magnitudes(self) -> None:
        """
        Todos los tipos de eventos tienen magnitud definida
        """
        for event_type in GoldImpactCalculator.EVENT_MAGNITUDES.keys():
            magnitude, magnitude_range = GoldImpactCalculator._estimate_magnitude(
                event_type, 2000.0
            )
            assert magnitude is not None
            assert "-" in magnitude_range
            assert "puntos" in magnitude_range

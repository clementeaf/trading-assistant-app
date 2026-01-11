"""
Tests unitarios para EventCategorizer
"""
import pytest
from app.utils.event_categorizer import EventCategorizer
from app.models.economic_calendar import EventType


class TestEventCategorizer:
    """Tests para categorización de eventos económicos"""
    
    def test_categorize_nfp(self):
        """Test categorización de Non-Farm Payrolls"""
        assert EventCategorizer.categorize("Non-Farm Payrolls") == EventType.NFP
        assert EventCategorizer.categorize("non farm payroll") == EventType.NFP
        assert EventCategorizer.categorize("Nonfarm Employment Change") == EventType.NFP
    
    def test_categorize_cpi(self):
        """Test categorización de CPI"""
        assert EventCategorizer.categorize("Consumer Price Index") == EventType.CPI
        assert EventCategorizer.categorize("CPI m/m") == EventType.CPI
        assert EventCategorizer.categorize("Inflation Rate") == EventType.CPI
    
    def test_categorize_fomc(self):
        """Test categorización de FOMC"""
        assert EventCategorizer.categorize("FOMC Statement") == EventType.FOMC
        assert EventCategorizer.categorize("Fed Interest Rate Decision") == EventType.FOMC
        assert EventCategorizer.categorize("Federal Open Market Committee") == EventType.FOMC
    
    def test_categorize_unemployment(self):
        """Test categorización de desempleo"""
        assert EventCategorizer.categorize("Unemployment Rate") == EventType.UNEMPLOYMENT
        assert EventCategorizer.categorize("Jobless Rate") == EventType.UNEMPLOYMENT
    
    def test_categorize_pce(self):
        """Test categorización de PCE"""
        assert EventCategorizer.categorize("PCE Price Index") == EventType.PCE
        assert EventCategorizer.categorize("Personal Consumption Expenditure") == EventType.PCE
        assert EventCategorizer.categorize("Core PCE") == EventType.PCE
    
    def test_categorize_gdp(self):
        """Test categorización de GDP"""
        assert EventCategorizer.categorize("GDP Growth Rate") == EventType.GDP
        assert EventCategorizer.categorize("Gross Domestic Product") == EventType.GDP
    
    def test_categorize_retail_sales(self):
        """Test categorización de ventas minoristas"""
        assert EventCategorizer.categorize("Retail Sales m/m") == EventType.RETAIL_SALES
        assert EventCategorizer.categorize("Consumer Spending") == EventType.RETAIL_SALES
    
    def test_categorize_ppi(self):
        """Test categorización de PPI"""
        assert EventCategorizer.categorize("Producer Price Index") == EventType.PPI
        assert EventCategorizer.categorize("PPI m/m") == EventType.PPI
    
    def test_categorize_pmi(self):
        """Test categorización de PMI"""
        assert EventCategorizer.categorize("Manufacturing PMI") == EventType.PMI
        assert EventCategorizer.categorize("Purchasing Managers Index") == EventType.PMI
    
    def test_categorize_ism_manufacturing(self):
        """Test categorización de ISM Manufacturing"""
        assert EventCategorizer.categorize("ISM Manufacturing PMI") == EventType.ISM_MANUFACTURING
        assert EventCategorizer.categorize("ISM Manufacturing Index") == EventType.ISM_MANUFACTURING
    
    def test_categorize_ism_services(self):
        """Test categorización de ISM Services"""
        assert EventCategorizer.categorize("ISM Services PMI") == EventType.ISM_SERVICES
        assert EventCategorizer.categorize("ISM Non-Manufacturing") == EventType.ISM_SERVICES
    
    def test_categorize_jolts(self):
        """Test categorización de JOLTS"""
        assert EventCategorizer.categorize("JOLTS Job Openings") == EventType.JOLTS
        assert EventCategorizer.categorize("Job Openings") == EventType.JOLTS
    
    def test_categorize_adp(self):
        """Test categorización de ADP"""
        assert EventCategorizer.categorize("ADP Employment Change") == EventType.ADP_EMPLOYMENT
        assert EventCategorizer.categorize("ADP Payroll") == EventType.ADP_EMPLOYMENT
    
    def test_categorize_jobless_claims(self):
        """Test categorización de Initial Claims"""
        assert EventCategorizer.categorize("Initial Jobless Claims") == EventType.JOBLESS_CLAIMS
        assert EventCategorizer.categorize("Unemployment Claims") == EventType.JOBLESS_CLAIMS
    
    def test_categorize_geopolitical(self):
        """Test categorización de eventos geopolíticos"""
        assert EventCategorizer.categorize("Geopolitical Tensions") == EventType.GEOPOLITICAL
        assert EventCategorizer.categorize("War in Middle East") == EventType.GEOPOLITICAL
        assert EventCategorizer.categorize("Presidential Election") == EventType.GEOPOLITICAL
    
    def test_categorize_fed_speech(self):
        """Test categorización de discursos Fed"""
        assert EventCategorizer.categorize("Fed Chair Powell Speaks") == EventType.FED_SPEECH
        assert EventCategorizer.categorize("Jerome Powell Speech") == EventType.FED_SPEECH
    
    def test_categorize_other(self):
        """Test categorización de eventos desconocidos"""
        assert EventCategorizer.categorize("Unknown Economic Event") == EventType.OTHER
        assert EventCategorizer.categorize("Random Data") == EventType.OTHER
    
    def test_categorize_empty_string(self):
        """Test categorización de string vacío"""
        assert EventCategorizer.categorize("") == EventType.OTHER
        assert EventCategorizer.categorize(None) == EventType.OTHER
    
    def test_get_tier_tier1(self):
        """Test tier 1 (máximo impacto)"""
        assert EventCategorizer.get_tier(EventType.FOMC) == 1
        assert EventCategorizer.get_tier(EventType.NFP) == 1
        assert EventCategorizer.get_tier(EventType.CPI) == 1
        assert EventCategorizer.get_tier(EventType.GEOPOLITICAL) == 1
    
    def test_get_tier_tier2(self):
        """Test tier 2 (alto impacto)"""
        assert EventCategorizer.get_tier(EventType.UNEMPLOYMENT) == 2
        assert EventCategorizer.get_tier(EventType.PCE) == 2
        assert EventCategorizer.get_tier(EventType.GDP) == 2
        assert EventCategorizer.get_tier(EventType.RETAIL_SALES) == 2
        assert EventCategorizer.get_tier(EventType.PPI) == 2
    
    def test_get_tier_tier3(self):
        """Test tier 3 (impacto medio-alto)"""
        assert EventCategorizer.get_tier(EventType.PMI) == 3
        assert EventCategorizer.get_tier(EventType.ISM_MANUFACTURING) == 3
        assert EventCategorizer.get_tier(EventType.ISM_SERVICES) == 3
        assert EventCategorizer.get_tier(EventType.JOLTS) == 3
        assert EventCategorizer.get_tier(EventType.ADP_EMPLOYMENT) == 3
    
    def test_get_tier_tier4(self):
        """Test tier 4 (impacto medio)"""
        assert EventCategorizer.get_tier(EventType.JOBLESS_CLAIMS) == 4
        assert EventCategorizer.get_tier(EventType.DURABLE_GOODS) == 4
        assert EventCategorizer.get_tier(EventType.HOUSING_STARTS) == 4
    
    def test_get_tier_other(self):
        """Test tier para eventos sin clasificar"""
        assert EventCategorizer.get_tier(EventType.OTHER) == 5
    
    def test_typical_time_nfp(self):
        """Test hora típica NFP"""
        time = EventCategorizer.get_typical_time_et(EventType.NFP)
        assert "8:30" in time
        assert "AM" in time
        assert "ET" in time
    
    def test_typical_time_fomc(self):
        """Test hora típica FOMC"""
        time = EventCategorizer.get_typical_time_et(EventType.FOMC)
        assert "2:00" in time
        assert "PM" in time
    
    def test_typical_time_cpi(self):
        """Test hora típica CPI"""
        time = EventCategorizer.get_typical_time_et(EventType.CPI)
        assert "8:30" in time
        assert "AM" in time
    
    def test_typical_time_ism(self):
        """Test hora típica ISM"""
        time = EventCategorizer.get_typical_time_et(EventType.ISM_MANUFACTURING)
        assert "10:00" in time
        assert "AM" in time
    
    def test_typical_time_unknown(self):
        """Test hora típica para eventos sin horario definido"""
        time = EventCategorizer.get_typical_time_et(EventType.OTHER)
        assert time == "Variable"
    
    def test_case_insensitive(self):
        """Test que la categorización es case-insensitive"""
        assert EventCategorizer.categorize("NON-FARM PAYROLLS") == EventType.NFP
        assert EventCategorizer.categorize("consumer price INDEX") == EventType.CPI
        assert EventCategorizer.categorize("Fomc STATEMENT") == EventType.FOMC

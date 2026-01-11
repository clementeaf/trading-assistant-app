"""
Tests unitarios para timezone_converter
"""
import pytest
from datetime import datetime

from app.utils.timezone_converter import TimezoneConverter


class TestTimezoneConverter:
    """Tests para TimezoneConverter"""
    
    def test_parse_time_string_valid(self):
        """Test parsear tiempo válido"""
        result = TimezoneConverter._parse_time_string("10:30")
        assert result.hour == 10
        assert result.minute == 30
    
    def test_parse_time_string_invalid_format(self):
        """Test parsear formato inválido"""
        with pytest.raises(ValueError, match="Invalid time format"):
            TimezoneConverter._parse_time_string("10-30")
    
    def test_parse_time_string_invalid_hour(self):
        """Test parsear hora inválida"""
        with pytest.raises(ValueError):
            TimezoneConverter._parse_time_string("25:30")
    
    def test_parse_time_string_invalid_minute(self):
        """Test parsear minuto inválido"""
        with pytest.raises(ValueError):
            TimezoneConverter._parse_time_string("10:70")
    
    def test_format_time(self):
        """Test formatear datetime a string"""
        dt = datetime(2026, 1, 11, 10, 30)
        result = TimezoneConverter._format_time(dt)
        assert result == "10:30"
    
    def test_convert_utc_to_et(self):
        """Test conversión UTC a Eastern Time"""
        # Usar fecha de referencia en enero (EST, no EDT)
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="ET",
            reference_date=ref_date
        )
        # EST es UTC-5
        assert result == "05:30"
    
    def test_convert_utc_to_pt(self):
        """Test conversión UTC a Pacific Time"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="PT",
            reference_date=ref_date
        )
        # PST es UTC-8
        assert result == "02:30"
    
    def test_convert_et_to_utc(self):
        """Test conversión inversa: ET a UTC"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "05:30",
            from_tz="ET",
            to_tz="UTC",
            reference_date=ref_date
        )
        assert result == "10:30"
    
    def test_convert_utc_to_gmt(self):
        """Test conversión UTC a GMT (deben ser iguales en invierno)"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="GMT",
            reference_date=ref_date
        )
        assert result == "10:30"
    
    def test_convert_utc_to_jst(self):
        """Test conversión UTC a Japan Standard Time"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="JST",
            reference_date=ref_date
        )
        # JST es UTC+9
        assert result == "19:30"
    
    def test_convert_invalid_timezone_raises_error(self):
        """Test zona horaria no soportada"""
        with pytest.raises(ValueError, match="Invalid timezone"):
            TimezoneConverter.convert_time(
                "10:30",
                from_tz="UTC",
                to_tz="INVALID"
            )
    
    def test_format_multi_timezone_default(self):
        """Test formato múltiples zonas con default (UTC, ET)"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.format_multi_timezone(
            "10:30",
            reference_date=ref_date
        )
        
        assert "UTC" in result
        assert "ET" in result
        assert result["UTC"] == "10:30"
        assert result["ET"] == "05:30"
    
    def test_format_multi_timezone_custom(self):
        """Test formato múltiples zonas custom"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.format_multi_timezone(
            "10:30",
            timezones=["UTC", "ET", "PT", "JST"],
            reference_date=ref_date
        )
        
        assert len(result) == 4
        assert result["UTC"] == "10:30"
        assert result["ET"] == "05:30"
        assert result["PT"] == "02:30"
        assert result["JST"] == "19:30"
    
    def test_format_multi_timezone_skips_invalid(self):
        """Test que zonas inválidas se saltan sin error"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.format_multi_timezone(
            "10:30",
            timezones=["UTC", "INVALID", "ET"],
            reference_date=ref_date
        )
        
        assert "UTC" in result
        assert "ET" in result
        assert "INVALID" not in result
    
    def test_format_time_display_single_zone(self):
        """Test formato display con una sola zona"""
        timezones_dict = {"UTC": "10:30"}
        result = TimezoneConverter.format_time_display(timezones_dict)
        assert result == "10:30 UTC"
    
    def test_format_time_display_multiple_zones(self):
        """Test formato display con múltiples zonas"""
        timezones_dict = {
            "UTC": "10:30",
            "ET": "05:30",
            "PT": "02:30"
        }
        result = TimezoneConverter.format_time_display(timezones_dict)
        assert result == "10:30 UTC (05:30 ET, 02:30 PT)"
    
    def test_format_time_display_empty(self):
        """Test formato display vacío"""
        result = TimezoneConverter.format_time_display({})
        assert result == ""
    
    def test_dst_summer_time(self):
        """Test conversión con DST activo (verano)"""
        # Julio: DST activo en US (EDT, PDT)
        ref_date = datetime(2026, 7, 15)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="ET",
            reference_date=ref_date
        )
        # EDT es UTC-4 (vs EST que es UTC-5)
        assert result == "06:30"
    
    def test_dst_winter_time(self):
        """Test conversión sin DST (invierno)"""
        # Enero: Sin DST en US (EST, PST)
        ref_date = datetime(2026, 1, 15)
        result = TimezoneConverter.convert_time(
            "10:30",
            from_tz="UTC",
            to_tz="ET",
            reference_date=ref_date
        )
        # EST es UTC-5
        assert result == "05:30"
    
    def test_midnight_conversion(self):
        """Test conversión de medianoche"""
        ref_date = datetime(2026, 1, 11)
        result = TimezoneConverter.convert_time(
            "00:00",
            from_tz="UTC",
            to_tz="ET",
            reference_date=ref_date
        )
        # 00:00 UTC = 19:00 ET del día anterior
        assert result == "19:00"

"""
Utilidades para convertir horarios entre diferentes zonas horarias
"""
from datetime import datetime, time
from typing import Optional
from zoneinfo import ZoneInfo


class TimezoneConverter:
    """Convierte horarios entre zonas horarias"""
    
    # Zonas horarias soportadas con sus identificadores IANA
    SUPPORTED_TIMEZONES = {
        "UTC": "UTC",
        "ET": "America/New_York",        # Eastern Time (US)
        "PT": "America/Los_Angeles",     # Pacific Time (US)
        "GMT": "Europe/London",          # Greenwich Mean Time
        "CET": "Europe/Paris",           # Central European Time
        "JST": "Asia/Tokyo",             # Japan Standard Time
        "AEST": "Australia/Sydney",      # Australian Eastern Standard Time
        "CST": "America/Chicago"         # Central Standard Time (US)
    }
    
    @classmethod
    def _parse_time_string(
        cls,
        time_str: str,
        reference_date: Optional[datetime] = None
    ) -> datetime:
        """
        Parsea string de tiempo "HH:MM" a datetime
        @param time_str - Tiempo en formato "HH:MM"
        @param reference_date - Fecha de referencia (default: hoy)
        @returns Datetime con el tiempo especificado
        """
        if not time_str or ":" not in time_str:
            raise ValueError(f"Invalid time format: '{time_str}'. Expected 'HH:MM'")
        
        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError(f"Invalid time values: hour={hour}, minute={minute}")
            
            # Usar fecha de referencia o hoy
            if reference_date is None:
                reference_date = datetime.now()
            
            return datetime.combine(
                reference_date.date(),
                time(hour=hour, minute=minute)
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"Error parsing time '{time_str}': {str(e)}")
    
    @classmethod
    def _format_time(cls, dt: datetime) -> str:
        """
        Formatea datetime a string "HH:MM"
        @param dt - Datetime a formatear
        @returns String en formato "HH:MM"
        """
        return dt.strftime("%H:%M")
    
    @classmethod
    def _get_timezone(cls, timezone_code: str) -> ZoneInfo:
        """
        Obtiene ZoneInfo para un código de zona
        @param timezone_code - Código de zona (ej: "UTC", "ET")
        @returns ZoneInfo object
        """
        tz_name = cls.SUPPORTED_TIMEZONES.get(timezone_code)
        if not tz_name:
            raise ValueError(
                f"Unsupported timezone: '{timezone_code}'. "
                f"Supported: {list(cls.SUPPORTED_TIMEZONES.keys())}"
            )
        
        return ZoneInfo(tz_name)
    
    @classmethod
    def convert_time(
        cls,
        time_str: str,
        from_tz: str = "UTC",
        to_tz: str = "America/New_York",
        reference_date: Optional[datetime] = None
    ) -> str:
        """
        Convierte hora de una zona horaria a otra
        @param time_str - Hora en formato "HH:MM"
        @param from_tz - Código de zona horaria origen (ej: "UTC")
        @param to_tz - Código de zona horaria destino (ej: "ET")
        @param reference_date - Fecha de referencia (default: hoy)
        @returns Hora convertida en formato "HH:MM"
        """
        # Parsear tiempo
        dt = cls._parse_time_string(time_str, reference_date)
        
        # Si to_tz está en formato de código, convertir a IANA name
        if to_tz in cls.SUPPORTED_TIMEZONES:
            to_tz_iana = cls.SUPPORTED_TIMEZONES[to_tz]
        else:
            to_tz_iana = to_tz
        
        # Si from_tz está en formato de código, convertir a IANA name
        if from_tz in cls.SUPPORTED_TIMEZONES:
            from_tz_iana = cls.SUPPORTED_TIMEZONES[from_tz]
        else:
            from_tz_iana = from_tz
        
        try:
            # Agregar timezone de origen
            dt_with_tz = dt.replace(tzinfo=ZoneInfo(from_tz_iana))
            
            # Convertir a timezone destino
            dt_converted = dt_with_tz.astimezone(ZoneInfo(to_tz_iana))
            
            # Formatear y retornar
            return cls._format_time(dt_converted)
        except Exception as e:
            # Si hay error con ZoneInfo, lanzar ValueError más claro
            raise ValueError(
                f"Error converting time: Invalid timezone '{to_tz}' or '{from_tz}'. "
                f"Supported timezones: {list(cls.SUPPORTED_TIMEZONES.keys())}"
            )
    
    @classmethod
    def format_multi_timezone(
        cls,
        utc_time: str,
        timezones: Optional[list[str]] = None,
        reference_date: Optional[datetime] = None
    ) -> dict[str, str]:
        """
        Formatea hora en múltiples zonas horarias
        @param utc_time - Hora UTC en formato "HH:MM"
        @param timezones - Lista de códigos de zonas (default: ["UTC", "ET"])
        @param reference_date - Fecha de referencia (default: hoy)
        @returns Dict con horas por zona: {"UTC": "10:30", "ET": "05:30"}
        """
        if timezones is None:
            timezones = ["UTC", "ET"]
        
        result: dict[str, str] = {}
        
        for tz_code in timezones:
            try:
                # UTC siempre es el mismo tiempo
                if tz_code == "UTC":
                    result[tz_code] = utc_time
                else:
                    # Convertir de UTC a la zona solicitada
                    converted = cls.convert_time(
                        utc_time,
                        from_tz="UTC",
                        to_tz=tz_code,
                        reference_date=reference_date
                    )
                    result[tz_code] = converted
            except ValueError:
                # Si la zona no es soportada, skip
                continue
        
        return result
    
    @classmethod
    def format_time_display(
        cls,
        timezones_dict: dict[str, str]
    ) -> str:
        """
        Formatea diccionario de zonas a string legible
        @param timezones_dict - Dict con zonas: {"UTC": "10:30", "ET": "05:30"}
        @returns String formateado: "10:30 UTC (05:30 ET)"
        """
        if not timezones_dict:
            return ""
        
        # Primera zona (usualmente UTC)
        first_tz = list(timezones_dict.keys())[0]
        first_time = timezones_dict[first_tz]
        result = f"{first_time} {first_tz}"
        
        # Resto de zonas entre paréntesis
        other_zones = []
        for tz_code, time_val in list(timezones_dict.items())[1:]:
            other_zones.append(f"{time_val} {tz_code}")
        
        if other_zones:
            result += f" ({', '.join(other_zones)})"
        
        return result

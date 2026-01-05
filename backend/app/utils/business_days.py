"""
Utilidades para trabajar con días hábiles (business days)
La Fed y los mercados financieros solo operan en días hábiles
"""
import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


class BusinessDays:
    """Utilidades para días hábiles (excluye fines de semana)"""
    
    @staticmethod
    def is_business_day(check_date: date) -> bool:
        """
        Verifica si una fecha es un día hábil (lunes a viernes)
        @param check_date - Fecha a verificar
        @returns True si es día hábil, False si es fin de semana
        """
        # 0 = Lunes, 6 = Domingo
        weekday = check_date.weekday()
        return weekday < 5  # Lunes (0) a Viernes (4)
    
    @staticmethod
    def get_last_business_day(target_date: date = None) -> date:
        """
        Obtiene el último día hábil antes de la fecha especificada
        @param target_date - Fecha de referencia (por defecto hoy)
        @returns Último día hábil
        """
        if target_date is None:
            target_date = date.today()
        
        current = target_date - timedelta(days=1)
        while not BusinessDays.is_business_day(current):
            current = current - timedelta(days=1)
        
        return current
    
    @staticmethod
    def get_previous_business_day(target_date: date) -> date:
        """
        Obtiene el día hábil anterior a la fecha especificada
        @param target_date - Fecha de referencia
        @returns Día hábil anterior
        """
        current = target_date - timedelta(days=1)
        while not BusinessDays.is_business_day(current):
            current = current - timedelta(days=1)
        
        return current
    
    @staticmethod
    def get_next_business_day(target_date: date) -> date:
        """
        Obtiene el siguiente día hábil después de la fecha especificada
        @param target_date - Fecha de referencia
        @returns Siguiente día hábil
        """
        current = target_date + timedelta(days=1)
        while not BusinessDays.is_business_day(current):
            current = current + timedelta(days=1)
        
        return current
    
    @staticmethod
    def get_business_days_in_range(start_date: date, end_date: date) -> list[date]:
        """
        Obtiene todos los días hábiles en un rango de fechas
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @returns Lista de días hábiles en el rango
        """
        business_days: list[date] = []
        current = start_date
        
        while current <= end_date:
            if BusinessDays.is_business_day(current):
                business_days.append(current)
            current = current + timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def adjust_to_business_day(target_date: date, direction: str = "backward") -> date:
        """
        Ajusta una fecha al día hábil más cercano
        @param target_date - Fecha a ajustar
        @param direction - "backward" (hacia atrás) o "forward" (hacia adelante)
        @returns Fecha ajustada a día hábil
        """
        if BusinessDays.is_business_day(target_date):
            return target_date
        
        if direction == "backward":
            return BusinessDays.get_previous_business_day(target_date)
        else:
            return BusinessDays.get_next_business_day(target_date)


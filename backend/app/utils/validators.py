"""
Validadores para parámetros de entrada
"""
import re
from typing import Optional


class CurrencyValidator:
    """Validador para códigos de moneda"""
    
    VALID_CURRENCIES = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "NZD", "SEK",
        "NOK", "DKK", "PLN", "HUF", "CZK", "RUB", "TRY", "ZAR", "BRL", "MXN",
        "INR", "KRW", "SGD", "HKD", "THB", "MYR", "IDR", "PHP"
    }
    
    CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
    
    @classmethod
    def validate_currency(cls, currency: Optional[str]) -> Optional[str]:
        """
        Valida un código de moneda
        @param currency - Código de moneda a validar
        @returns Código de moneda validado en mayúsculas o None
        @raises ValueError si el código no es válido
        """
        if currency is None:
            return None
        
        currency_upper = currency.upper().strip()
        
        if not cls.CURRENCY_PATTERN.match(currency_upper):
            raise ValueError(
                f"Invalid currency code format: {currency}. "
                f"Expected 3 uppercase letters (e.g., USD, EUR)"
            )
        
        if currency_upper not in cls.VALID_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: {currency_upper}. "
                f"Supported currencies: {', '.join(sorted(cls.VALID_CURRENCIES))}"
            )
        
        return currency_upper


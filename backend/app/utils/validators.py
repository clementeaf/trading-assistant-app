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


class InstrumentValidator:
    """Validador para símbolos de instrumentos financieros"""
    
    VALID_BONDS = {"US02Y", "US10Y", "US30Y"}
    BOND_PATTERN = re.compile(r"^US(02|10|30)Y$")
    INSTRUMENT_PATTERN = re.compile(r"^[A-Z0-9]{3,10}$")
    
    @classmethod
    def validate_instrument(cls, instrument: str) -> str:
        """
        Valida un símbolo de instrumento
        @param instrument - Símbolo del instrumento a validar
        @returns Símbolo validado en mayúsculas
        @raises ValueError si el símbolo no es válido
        """
        if not instrument:
            raise ValueError("Instrument symbol cannot be empty")
        
        instrument_upper = instrument.upper().strip()
        
        if not cls.INSTRUMENT_PATTERN.match(instrument_upper):
            raise ValueError(
                f"Invalid instrument symbol format: {instrument}. "
                f"Expected 3-10 alphanumeric characters (e.g., XAUUSD, EURUSD, NASDAQ)"
            )
        
        return instrument_upper
    
    @classmethod
    def validate_bond_symbol(cls, bond: str) -> str:
        """
        Valida un símbolo de bono
        @param bond - Símbolo del bono a validar
        @returns Símbolo validado en mayúsculas
        @raises ValueError si el símbolo no es válido
        """
        if not bond:
            raise ValueError("Bond symbol cannot be empty")
        
        bond_upper = bond.upper().strip()
        
        if not cls.BOND_PATTERN.match(bond_upper):
            raise ValueError(
                f"Invalid bond symbol: {bond}. "
                f"Expected one of: US02Y, US10Y, US30Y"
            )
        
        if bond_upper not in cls.VALID_BONDS:
            raise ValueError(
                f"Unsupported bond symbol: {bond_upper}. "
                f"Supported bonds: {', '.join(sorted(cls.VALID_BONDS))}"
            )
        
        return bond_upper


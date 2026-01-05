"""
Utilidades para analizar alineación entre instrumentos de mercado
"""
from app.models.market_alignment import (
    AlignmentStatus,
    InstrumentPrice,
    MarketAlignmentAnalysis,
    MarketBias
)


class AlignmentAnalyzer:
    """Analizador de alineación de mercado"""
    
    @classmethod
    def calculate_change_percent(cls, current: float, previous: float) -> float:
        """
        Calcula el cambio porcentual
        @param current - Precio actual
        @param previous - Precio anterior
        @returns Cambio porcentual
        """
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100
    
    @classmethod
    def get_direction(cls, change_percent: float) -> str:
        """
        Determina la dirección del cambio
        @param change_percent - Cambio porcentual
        @returns "sube" o "baja"
        """
        return "sube" if change_percent > 0 else "baja"
    
    @classmethod
    def determine_alignment(
        cls,
        dxy_change: float,
        bond_change: float
    ) -> tuple[AlignmentStatus, MarketBias]:
        """
        Determina si DXY y bonos están alineados o en conflicto
        @param dxy_change - Cambio porcentual del DXY
        @param bond_change - Cambio porcentual del bono
        @returns Tupla (AlignmentStatus, MarketBias)
        """
        # Ambos suben -> alineados, risk-off típico
        if dxy_change > 0 and bond_change > 0:
            return (AlignmentStatus.ALIGNED, MarketBias.RISK_OFF)
        
        # Ambos bajan -> alineados, risk-on típico
        if dxy_change < 0 and bond_change < 0:
            return (AlignmentStatus.ALIGNED, MarketBias.RISK_ON)
        
        # Uno sube y el otro baja -> conflicto
        return (AlignmentStatus.CONFLICT, MarketBias.MIXED)
    
    @classmethod
    def analyze_alignment(
        cls,
        dxy_current: float,
        dxy_previous: float,
        bond_current: float,
        bond_previous: float,
        bond_symbol: str = "US10Y"
    ) -> MarketAlignmentAnalysis:
        """
        Analiza la alineación entre DXY y un bono
        @param dxy_current - Precio actual del DXY
        @param dxy_previous - Precio anterior del DXY
        @param bond_current - Precio actual del bono
        @param bond_previous - Precio anterior del bono
        @param bond_symbol - Símbolo del bono (US10Y, US02Y, etc.)
        @returns Análisis de alineación
        """
        # Calcular cambios
        dxy_change = cls.calculate_change_percent(dxy_current, dxy_previous)
        bond_change = cls.calculate_change_percent(bond_current, bond_previous)
        
        # Determinar alineación
        alignment, market_bias = cls.determine_alignment(dxy_change, bond_change)
        
        # Crear objetos de precio
        dxy_price = InstrumentPrice(
            symbol="DXY",
            price=dxy_current,
            previous_price=dxy_previous,
            change_percent=round(dxy_change, 2),
            direction=cls.get_direction(dxy_change)
        )
        
        bond_price = InstrumentPrice(
            symbol=bond_symbol,
            price=bond_current,
            previous_price=bond_previous,
            change_percent=round(bond_change, 2),
            direction=cls.get_direction(bond_change)
        )
        
        # Generar resumen
        summary = cls._generate_summary(dxy_price, bond_price, alignment, market_bias)
        
        return MarketAlignmentAnalysis(
            dxy=dxy_price,
            bond=bond_price,
            alignment=alignment,
            market_bias=market_bias,
            summary=summary
        )
    
    @classmethod
    def _generate_summary(
        cls,
        dxy: InstrumentPrice,
        bond: InstrumentPrice,
        alignment: AlignmentStatus,
        market_bias: MarketBias
    ) -> str:
        """
        Genera un resumen textual del análisis
        @param dxy - Datos del DXY
        @param bond - Datos del bono
        @param alignment - Estado de alineación
        @param market_bias - Sesgo del mercado
        @returns Resumen textual
        """
        # Formatear cambios con signo correcto
        dxy_change_str = f"+{dxy.change_percent:.2f}%" if dxy.change_percent >= 0 else f"{dxy.change_percent:.2f}%"
        bond_change_str = f"+{bond.change_percent:.2f}%" if bond.change_percent >= 0 else f"{bond.change_percent:.2f}%"
        
        alignment_text = "Alineados" if alignment == AlignmentStatus.ALIGNED else "En conflicto"
        
        bias_text = {
            MarketBias.RISK_OFF: "sesgo más bien risk-off",
            MarketBias.RISK_ON: "sesgo más bien risk-on",
            MarketBias.MIXED: "señal mixta"
        }.get(market_bias, "señal mixta")
        
        return (
            f"DXY {dxy_change_str} y {bond.symbol} {bond_change_str} "
            f"→ {alignment_text}, {bias_text}."
        )


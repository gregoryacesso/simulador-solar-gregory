from pydantic import BaseModel

class Settings(BaseModel):
    # Parâmetros padrão
    default_tarifa_rs_kwh: float = 0.95
    default_hsp: float = 5.5
    performance_ratio: float = 0.80

    # ✅ Encargos reais (base Energisa SE pela sua fatura)
    perc_variavel_energia: float = 0.868  # 86,8% vira energia (kWh)
    perc_fixo_taxas: float = 0.132        # 13,2% taxas/encargos (fixo)

    # ✅ fallback manual (se trocar modo)
    custo_fixo_mensal_rs: float = 120.0

    # ✅ Limite de economia
    max_reducao: float = 0.85

    # ✅ SEUS PREÇOS (R$/kWp)
    preco_kwp_economico: float = 2300.0
    preco_kwp_padrao: float = 2470.0
    preco_kwp_premium: float = 3370.0

    # WhatsApp
    whatsapp_number_e164: str = "5579998451783"

settings = Settings()
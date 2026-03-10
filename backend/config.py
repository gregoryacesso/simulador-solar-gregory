from pydantic import BaseModel

class Settings(BaseModel):
    # Parâmetros padrão
    default_tarifa_rs_kwh: float = 0.95
    default_hsp: float = 5.5
    performance_ratio: float = 0.80

    # Base Energisa
    perc_variavel_energia: float = 0.868
    perc_fixo_taxas: float = 0.132

    # fallback manual
    custo_fixo_mensal_rs: float = 120.0

    # limite de economia
    max_reducao: float = 0.85

    # PREÇO ÚNICO POR KWP
    preco_kwp_unico: float = 2470.0

    # WhatsApp
    whatsapp_number_e164: str = "5579998451783"

settings = Settings()
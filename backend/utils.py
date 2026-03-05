import math
from datetime import date

def rs_to_kwh(mensal_rs: float, tarifa_rs_kwh: float) -> float:
    if tarifa_rs_kwh <= 0:
        raise ValueError("Tarifa deve ser > 0")
    return mensal_rs / tarifa_rs_kwh

def kwp_from_kwh_month(kwh_month: float, hsp: float, pr: float) -> float:
    # kWh/mês ≈ kWp * HSP * PR * 30
    if hsp <= 0 or pr <= 0:
        raise ValueError("HSP e PR devem ser > 0")
    kwp = kwh_month / (hsp * pr * 30.0)
    return max(0.1, kwp)

def arredonda_kwp(kwp: float) -> float:
    # Arredonda para 0,1 kWp
    return math.ceil(kwp * 10) / 10.0

def estimativa_producao_mensal_kwh(kwp: float, hsp: float, pr: float) -> float:
    return kwp * hsp * pr * 30.0

def estimativa_preco(kwp: float, preco_medio_rs_kwp: float) -> float:
    return kwp * preco_medio_rs_kwp

def estimativa_payback( valor_investimento: float, economia_mensal_rs: float) -> float | None:
    if economia_mensal_rs <= 0:
        return None
    return valor_investimento / economia_mensal_rs

def hoje_str() -> str:
    return date.today().strftime("%d/%m/%Y")

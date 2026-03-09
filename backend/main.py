from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
import uuid
import os
from typing import Literal

from config import settings
from utils import (
    rs_to_kwh,
    kwp_from_kwh_month,
    arredonda_kwp,
    estimativa_producao_mensal_kwh,
    estimativa_payback,
)
from pdf_gen import gerar_pdf
from leads import salvar_ou_atualizar_lead

APP_DIR = Path(__file__).parent
STORAGE_DIR = APP_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = APP_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpeg"

app = FastAPI(title="Simulador de Orçamento Solar - Gregory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PacoteNome = Literal["Econômico", "Padrão", "Premium"]
ModoTaxas = Literal["PERCENTUAL", "FIXO"]  # ✅ automático Energisa ou manual fixo


class SimulacaoIn(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    telefone: str = Field(min_length=8, max_length=30)
    cidade_uf: str = Field(default="Aracaju-SE", min_length=3, max_length=60)

    conta_media_rs: float = Field(gt=0)

    # ✅ modo de taxas
    modo_taxas: ModoTaxas = "PERCENTUAL"

    # ✅ usado apenas se modo_taxas == FIXO
    custo_fixo_mensal_rs: float = Field(default=settings.custo_fixo_mensal_rs, ge=0)

    # parâmetros
    tarifa_rs_kwh: float = Field(default=settings.default_tarifa_rs_kwh, gt=0)
    hsp: float = Field(default=settings.default_hsp, gt=0)
    pr: float = Field(default=settings.performance_ratio, gt=0)

    pacote_destacado: PacoteNome = "Padrão"


class SimulacaoOut(BaseModel):
    id: str

    kwp_sugerido: float
    producao_estimada_kwh_mes: float

    conta_total_rs: float
    modo_taxas: str
    custo_fixo_mensal_rs: float
    valor_variavel_rs: float
    kwh_estimado_mes: float

    economia_estimada_rs_mes: float

    investimento_economico_rs: float
    investimento_padrao_rs: float
    investimento_premium_rs: float

    payback_meses_economico: float | None
    payback_meses_padrao: float | None
    payback_meses_premium: float | None

    pacote_destacado: PacoteNome
    valor_pacote_destacado_rs: float

    pdf_url: str
    pdf_full_url: str
    whatsapp_url: str


def valor_pacote_destacado(pacote: str, inv_econ: float, inv_pad: float, inv_pre: float) -> float:
    if pacote == "Econômico":
        return inv_econ
    if pacote == "Premium":
        return inv_pre
    return inv_pad


def build_whatsapp_url(
    nome: str,
    cidade_uf: str,
    conta_total_rs: float,
    kwp: float,
    pacote_destacado: str,
    valor_pacote_rs: float,
    pdf_full_url: str,
) -> str:
    msg = (
        f"Olá! Me chamo {nome}.\n"
        f"Fiz uma simulação de energia solar.\n\n"
        f"Cidade: {cidade_uf}\n"
        f"Conta média: R$ {conta_total_rs:.2f}\n"
        f"Sistema sugerido: {kwp:.1f} kWp\n"
        f"Pacote escolhido: {pacote_destacado} (R$ {valor_pacote_rs:.2f})\n\n"
        f"PDF: {pdf_full_url}\n\n"
        f"Quero um orçamento final e agendar a visita técnica."
    )
    import urllib.parse
    return f"https://wa.me/{settings.whatsapp_number_e164}?text={urllib.parse.quote(msg)}"


@app.post("/api/simular", response_model=SimulacaoOut)
def simular(data: SimulacaoIn):
    lead_id = uuid.uuid4().hex[:10]

    # ✅ separa fixo/variável de acordo com modo
    if data.modo_taxas == "PERCENTUAL":
        custo_fixo_rs = data.conta_media_rs * settings.perc_fixo_taxas
        valor_variavel_rs = data.conta_media_rs * settings.perc_variavel_energia
    else:
        custo_fixo_rs = data.custo_fixo_mensal_rs
        valor_variavel_rs = max(0.0, data.conta_media_rs - custo_fixo_rs)

    kwh_mes = rs_to_kwh(valor_variavel_rs, data.tarifa_rs_kwh)

    # dimensionamento
    kwp = arredonda_kwp(kwp_from_kwh_month(kwh_mes, data.hsp, data.pr))

    # produção
    prod_kwh = estimativa_producao_mensal_kwh(kwp, data.hsp, data.pr)

    # economia
    economia_teorica_rs = data.tarifa_rs_kwh * prod_kwh
    teto_economia_rs = data.conta_media_rs * settings.max_reducao
    economia_rs = max(0.0, min(economia_teorica_rs, teto_economia_rs))

    # pacotes
    inv_econ = kwp * settings.preco_kwp_economico
    inv_pad = kwp * settings.preco_kwp_padrao
    inv_pre = kwp * settings.preco_kwp_premium

    pb_econ = estimativa_payback(inv_econ, economia_rs)
    pb_pad = estimativa_payback(inv_pad, economia_rs)
    pb_pre = estimativa_payback(inv_pre, economia_rs)

    pacote_destacado = data.pacote_destacado
    valor_destacado = valor_pacote_destacado(pacote_destacado, inv_econ, inv_pad, inv_pre)

    # ✅ salva lead como SIMULOU
    salvar_ou_atualizar_lead({
        "id": lead_id,
        "nome": data.nome,
        "telefone": data.telefone,
        "cidade": data.cidade_uf,
        "conta_total": f"{data.conta_media_rs:.2f}",
        "modo_taxas": data.modo_taxas,
        "custo_fixo": f"{custo_fixo_rs:.2f}",
        "valor_variavel": f"{valor_variavel_rs:.2f}",
        "kwh_estimado": f"{kwh_mes:.0f}",
        "kwp": f"{kwp:.1f}",
        "pacote": pacote_destacado,
        "valor_pacote": f"{valor_destacado:.2f}",
        "status": "SIMULOU",
    })

    # PDF
    pdf_name = f"orcamento_solar_{lead_id}.pdf"
    pdf_path = STORAGE_DIR / pdf_name

    condicao = "Entrada + 18x sem juros no cartão. Passe o cartão apenas quando o sistema estiver instalado."

    gerar_pdf(
        out_path=pdf_path,
        logo_path=LOGO_PATH if LOGO_PATH.exists() else None,
        empresa_nome="GREGORY",
        empresa_subtitulo="SEGURANÇA ELETRÔNICA & ENERGIA SOLAR",
        cnpj="23.368.243/0001-82",
        cidade_uf=data.cidade_uf,
        cliente_nome=data.nome,
        cliente_telefone=data.telefone,

        conta_total_rs=data.conta_media_rs,
        modo_taxas=data.modo_taxas,
        custo_fixo_mensal_rs=custo_fixo_rs,
        valor_variavel_rs=valor_variavel_rs,
        tarifa_rs_kwh=data.tarifa_rs_kwh,
        kwh_estimado_mes=kwh_mes,

        kwp_sugerido=kwp,
        prod_estimada_kwh_mes=prod_kwh,
        economia_estimada_rs_mes=economia_rs,

        investimento_economico_rs=inv_econ,
        investimento_padrao_rs=inv_pad,
        investimento_premium_rs=inv_pre,
        payback_meses_economico=pb_econ,
        payback_meses_padrao=pb_pad,
        payback_meses_premium=pb_pre,

        pacote_destacado=pacote_destacado,
        condicao_pagamento=condicao,
        validade_dias=10,
    )

    pdf_url = f"/api/pdf/{pdf_name}"
    base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    pdf_full_url = f"{base_url}{pdf_url}" if base_url else f"http://localhost:8000{pdf_url}"

    whatsapp_url = build_whatsapp_url(
        nome=data.nome,
        cidade_uf=data.cidade_uf,
        conta_total_rs=data.conta_media_rs,
        kwp=kwp,
        pacote_destacado=pacote_destacado,
        valor_pacote_rs=valor_destacado,
        pdf_full_url=pdf_full_url,
    )

    return SimulacaoOut(
        id=lead_id,
        kwp_sugerido=kwp,
        producao_estimada_kwh_mes=prod_kwh,

        conta_total_rs=data.conta_media_rs,
        modo_taxas=data.modo_taxas,
        custo_fixo_mensal_rs=custo_fixo_rs,
        valor_variavel_rs=valor_variavel_rs,
        kwh_estimado_mes=kwh_mes,

        economia_estimada_rs_mes=economia_rs,

        investimento_economico_rs=inv_econ,
        investimento_padrao_rs=inv_pad,
        investimento_premium_rs=inv_pre,

        payback_meses_economico=pb_econ,
        payback_meses_padrao=pb_pad,
        payback_meses_premium=pb_pre,

        pacote_destacado=pacote_destacado,
        valor_pacote_destacado_rs=valor_destacado,

        pdf_url=pdf_url,
        pdf_full_url=pdf_full_url,
        whatsapp_url=whatsapp_url,
    )


class LeadZapIn(BaseModel):
    id: str


@app.post("/api/lead-zap")
def marcou_whatsapp(dados: LeadZapIn):
    salvar_ou_atualizar_lead({"id": dados.id, "status": "CHAMOU_NO_ZAP"})
    return {"ok": True}


@app.get("/api/pdf/{pdf_name}")
def get_pdf(pdf_name: str):
    pdf_path = STORAGE_DIR / pdf_name
    if not pdf_path.exists():
        return {"error": "PDF não encontrado"}
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=pdf_name)


@app.get("/api/health")
def health():
    return {"ok": True}
from fastapi.responses import FileResponse
from pathlib import Path

STORAGE_DIR = Path("storage")
LEADS_FILE = STORAGE_DIR / "leads.csv"

@app.get("/leads")
def listar_leads():
    if not LEADS_FILE.exists():
        return {"mensagem": "Nenhum lead registrado ainda."}
    return FileResponse(
        LEADS_FILE,
        media_type="text/csv",
        filename="leads.csv"
    )
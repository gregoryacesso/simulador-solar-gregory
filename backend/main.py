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
from supabase_db import salvar_ou_atualizar_lead_db, listar_leads_db

APP_DIR = Path(__file__).parent
STORAGE_DIR = APP_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = APP_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpeg"

app = FastAPI(title="Simulador de Orçamento Solar - Gregory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ModoTaxas = Literal["PERCENTUAL", "FIXO"]


class SimulacaoIn(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    telefone: str = Field(min_length=8, max_length=30)
    cidade_uf: str = Field(default="Aracaju-SE", min_length=3, max_length=60)

    conta_media_rs: float = Field(gt=0)

    modo_taxas: ModoTaxas = "PERCENTUAL"
    custo_fixo_mensal_rs: float = Field(default=settings.custo_fixo_mensal_rs, ge=0)

    tarifa_rs_kwh: float = Field(default=settings.default_tarifa_rs_kwh, gt=0)
    hsp: float = Field(default=settings.default_hsp, gt=0)
    pr: float = Field(default=settings.performance_ratio, gt=0)


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

    investimento_total_rs: float
    payback_meses: float | None

    pdf_url: str
    pdf_full_url: str
    whatsapp_url: str


class LeadZapIn(BaseModel):
    id: str


def build_whatsapp_url(
    nome: str,
    cidade_uf: str,
    conta_total_rs: float,
    kwp: float,
    valor_total_rs: float,
    pdf_full_url: str,
) -> str:
    msg = (
        f"Olá! Me chamo {nome}.\n"
        f"Fiz uma simulação de energia solar.\n\n"
        f"Cidade: {cidade_uf}\n"
        f"Conta média: R$ {conta_total_rs:.2f}\n"
        f"Sistema sugerido: {kwp:.1f} kWp\n"
        f"Investimento estimado: R$ {valor_total_rs:.2f}\n\n"
        f"PDF: {pdf_full_url}\n\n"
        f"Quero um orçamento final e opções de pagamento/financiamento."
    )
    import urllib.parse
    return f"https://wa.me/{settings.whatsapp_number_e164}?text={urllib.parse.quote(msg)}"


@app.post("/api/simular", response_model=SimulacaoOut)
def simular(data: SimulacaoIn):
    lead_id = uuid.uuid4().hex[:10]

    if data.modo_taxas == "PERCENTUAL":
        custo_fixo_rs = data.conta_media_rs * settings.perc_fixo_taxas
        valor_variavel_rs = data.conta_media_rs * settings.perc_variavel_energia
    else:
        custo_fixo_rs = data.custo_fixo_mensal_rs
        valor_variavel_rs = max(0.0, data.conta_media_rs - custo_fixo_rs)

    kwh_mes = rs_to_kwh(valor_variavel_rs, data.tarifa_rs_kwh)

    kwp = arredonda_kwp(kwp_from_kwh_month(kwh_mes, data.hsp, data.pr))
    prod_kwh = estimativa_producao_mensal_kwh(kwp, data.hsp, data.pr)

    economia_teorica_rs = data.tarifa_rs_kwh * prod_kwh
    teto_economia_rs = data.conta_media_rs * settings.max_reducao
    economia_rs = max(0.0, min(economia_teorica_rs, teto_economia_rs))

    investimento_total_rs = kwp * settings.preco_kwp_unico
    payback_meses = estimativa_payback(investimento_total_rs, economia_rs)

    salvar_ou_atualizar_lead_db({
        "id": lead_id,
        "nome": data.nome,
        "telefone": data.telefone,
        "cidade": data.cidade_uf,
        "conta_total": data.conta_media_rs,
        "modo_taxas": data.modo_taxas,
        "custo_fixo": custo_fixo_rs,
        "valor_variavel": valor_variavel_rs,
        "kwh_estimado": round(kwh_mes),
        "kwp": kwp,
        "pacote": "VALOR_UNICO",
        "valor_pacote": investimento_total_rs,
        "status": "SIMULOU",
    })

    pdf_name = f"orcamento_solar_{lead_id}.pdf"
    pdf_path = STORAGE_DIR / pdf_name

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
        investimento_total_rs=investimento_total_rs,
        payback_meses=payback_meses,
        condicoes_pagamento=[
            "À vista",
            "Entrada + parcelamento no cartão",
            "Financiamento bancário sujeito à aprovação",
        ],
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
        valor_total_rs=investimento_total_rs,
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
        investimento_total_rs=investimento_total_rs,
        payback_meses=payback_meses,
        pdf_url=pdf_url,
        pdf_full_url=pdf_full_url,
        whatsapp_url=whatsapp_url,
    )


@app.post("/api/lead-zap")
def marcou_whatsapp(dados: LeadZapIn):
    leads = listar_leads_db()
    lead = next((x for x in leads if x.get("id") == dados.id), None)
    if lead:
        lead["status"] = "CHAMOU_NO_ZAP"
        salvar_ou_atualizar_lead_db(lead)
    return {"ok": True}


@app.get("/api/pdf/{pdf_name}")
def get_pdf(pdf_name: str):
    pdf_path = STORAGE_DIR / pdf_name
    if not pdf_path.exists():
        return {"error": "PDF não encontrado"}
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=pdf_name)


@app.get("/leads-json")
def listar_leads_json():
    return listar_leads_db()


@app.get("/api/health")
def health():
    return {"ok": True}
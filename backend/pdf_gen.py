from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from pathlib import Path
from datetime import date

def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def _try_set_alpha(c, a: float):
    try:
        c.setFillAlpha(a)
        c.setStrokeAlpha(a)
    except Exception:
        pass

def _marca_dagua(c, logo_path: Path | None):
    if not logo_path or not logo_path.exists():
        return
    w, h = A4
    c.saveState()
    _try_set_alpha(c, 0.06)
    try:
        img = ImageReader(str(logo_path))
        c.translate(w / 2, h / 2)
        c.rotate(25)
        c.drawImage(img, -9 * cm, -2.8 * cm, width=18 * cm, height=5.6 * cm, mask="auto")
    except Exception:
        pass
    c.restoreState()

def _rodape(c, empresa_nome, empresa_subtitulo, cnpj, cidade_uf, whatsapp):
    w, _ = A4
    y = 1.6 * cm
    c.saveState()
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.line(2 * cm, y + 0.7 * cm, w - 2 * cm, y + 0.7 * cm)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(2 * cm, y + 0.25 * cm, f"{empresa_nome} • {empresa_subtitulo}")
    c.drawString(2 * cm, y - 0.10 * cm, f"CNPJ: {cnpj} • {cidade_uf} • WhatsApp: {whatsapp}")
    c.restoreState()

def gerar_pdf(
    out_path: Path,
    logo_path: Path | None,
    empresa_nome: str,
    empresa_subtitulo: str,
    cnpj: str,
    cidade_uf: str,
    cliente_nome: str,
    cliente_telefone: str,
    conta_total_rs: float,
    modo_taxas: str,
    custo_fixo_mensal_rs: float,
    valor_variavel_rs: float,
    tarifa_rs_kwh: float,
    kwh_estimado_mes: float,
    kwp_sugerido: float,
    prod_estimada_kwh_mes: float,
    economia_estimada_rs_mes: float,
    investimento_total_rs: float,
    payback_meses: float | None,
    condicoes_pagamento: list[str],
    validade_dias: int = 10,
):
    w, h = A4
    c = canvas.Canvas(str(out_path), pagesize=A4)

    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    _marca_dagua(c, logo_path)

    top = h - 2.0 * cm
    c.setFillColor(colors.HexColor("#F3F7F6"))
    c.rect(0, h - 3.6 * cm, w, 3.6 * cm, fill=1, stroke=0)

    if logo_path and logo_path.exists():
        try:
            img = ImageReader(str(logo_path))
            c.drawImage(img, 2 * cm, top - 1.45 * cm, width=5.0 * cm, height=1.9 * cm, mask="auto")
        except Exception:
            pass

    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(7.4 * cm, top, empresa_nome)

    c.setFillColor(colors.HexColor("#374151"))
    c.setFont("Helvetica", 10.5)
    c.drawString(7.4 * cm, top - 0.55 * cm, empresa_subtitulo)
    c.drawString(7.4 * cm, top - 1.05 * cm, f"CNPJ: {cnpj} • {cidade_uf}")

    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.line(2 * cm, top - 1.75 * cm, w - 2 * cm, top - 1.75 * cm)

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, top - 2.9 * cm, "ORÇAMENTO ESTIMADO — ENERGIA SOLAR")

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, top - 3.9 * cm, f"Cliente: {cliente_nome}")
    c.drawString(2 * cm, top - 4.5 * cm, f"Telefone/WhatsApp: {cliente_telefone}")
    c.drawString(2 * cm, top - 5.1 * cm, f"Data: {date.today().strftime('%d/%m/%Y')}  |  Validade: {validade_dias} dias")

    box_top = top - 6.0 * cm
    box_h = 7.9 * cm
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.roundRect(2 * cm, box_top - box_h, w - 4 * cm, box_h, 14, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.drawString(2.6 * cm, box_top - 0.9 * cm, "Resumo da Simulação")

    modo_txt = "Automático (Energisa - percentuais)" if modo_taxas == "PERCENTUAL" else "Manual (valor fixo)"
    linhas = [
        ("Conta total informada:", brl(conta_total_rs)),
        ("Modo de taxas:", modo_txt),
        ("Taxas/encargos (fixo):", brl(custo_fixo_mensal_rs)),
        ("Parte variável (energia):", brl(valor_variavel_rs)),
        ("Tarifa considerada:", f"{brl(tarifa_rs_kwh)}/kWh"),
        ("Consumo estimado:", f"{int(round(kwh_estimado_mes))} kWh/mês"),
        ("Sistema sugerido:", f"{kwp_sugerido:.1f} kWp"),
        ("Produção estimada:", f"{int(round(prod_estimada_kwh_mes))} kWh/mês"),
        ("Economia estimada:", f"{brl(economia_estimada_rs_mes)}/mês"),
    ]

    yy = box_top - 1.7 * cm
    for label, val in linhas:
        c.setFont("Helvetica", 10.6)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(2.6 * cm, yy, label)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(colors.HexColor("#111827"))
        c.drawRightString(w - 2.6 * cm, yy, val)
        yy -= 0.55 * cm

    destaque_y = box_top - box_h - 1.3 * cm
    c.setFillColor(colors.HexColor("#E9FFF6"))
    c.setStrokeColor(colors.HexColor("#BFEEDC"))
    c.roundRect(2 * cm, destaque_y, w - 4 * cm, 1.1 * cm, 12, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2.5 * cm, destaque_y + 0.38 * cm, "Investimento estimado:")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(w - 2.5 * cm, destaque_y + 0.35 * cm, brl(investimento_total_rs))

    pay_y = destaque_y - 1.1 * cm
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, pay_y, "Formas de pagamento")

    c.setFont("Helvetica", 10.8)
    c.setFillColor(colors.HexColor("#374151"))
    y2 = pay_y - 0.7 * cm
    for item in condicoes_pagamento:
        c.drawString(2.3 * cm, y2, f"• {item}")
        y2 -= 0.55 * cm

    if payback_meses is not None:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor("#0A7A5A"))
        c.drawString(2 * cm, y2 - 0.15 * cm, f"Payback estimado: {payback_meses:.0f} meses")

    _rodape(
        c,
        empresa_nome=empresa_nome,
        empresa_subtitulo=empresa_subtitulo,
        cnpj=cnpj,
        cidade_uf=cidade_uf,
        whatsapp="(79) 99845-1783",
    )

    c.showPage()
    c.save()
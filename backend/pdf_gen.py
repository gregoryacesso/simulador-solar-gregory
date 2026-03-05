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

def _try_set_alpha(c: canvas.Canvas, a: float):
    try:
        c.setFillAlpha(a)
        c.setStrokeAlpha(a)
    except Exception:
        pass

def _marca_dagua(c: canvas.Canvas, logo_path: Path | None):
    if not logo_path or not logo_path.exists():
        return
    w, h = A4
    c.saveState()
    _try_set_alpha(c, 0.06)
    try:
        img = ImageReader(str(logo_path))
        c.translate(w / 2, h / 2)
        c.rotate(25)
        img_w = 18 * cm
        img_h = 5.2 * cm
        c.drawImage(img, -img_w / 2, -img_h / 2, width=img_w, height=img_h, mask="auto")
    except Exception:
        pass
    c.restoreState()

def _rodape(
    c: canvas.Canvas,
    empresa_nome: str,
    empresa_subtitulo: str,
    cnpj: str,
    cidade_uf: str,
    whatsapp: str,
):
    w, _ = A4
    y = 1.6 * cm

    c.saveState()
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.setLineWidth(1)
    c.line(2 * cm, y + 0.7 * cm, w - 2 * cm, y + 0.7 * cm)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(2 * cm, y + 0.25 * cm, f"{empresa_nome} • {empresa_subtitulo}")
    c.drawString(2 * cm, y - 0.10 * cm, f"CNPJ: {cnpj} • {cidade_uf} • WhatsApp: {whatsapp}")

    c.setFillColor(colors.HexColor("#9CA3AF"))
    c.setFont("Helvetica", 8)
    c.drawRightString(w - 2 * cm, y - 0.10 * cm, "Documento gerado automaticamente")
    c.restoreState()

def _pill_pacote(c: canvas.Canvas, y: float, texto: str):
    """Faixa 'Pacote destacado' fora do resumo (evita sobreposição)."""
    w, _ = A4
    c.saveState()
    c.setFillColor(colors.HexColor("#E9FFF6"))
    c.setStrokeColor(colors.HexColor("#BFEEDC"))
    c.setLineWidth(1)
    c.roundRect(2 * cm, y, w - 4 * cm, 0.95 * cm, 12, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.4 * cm, y + 0.30 * cm, texto)
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

    investimento_economico_rs: float,
    investimento_padrao_rs: float,
    investimento_premium_rs: float,
    payback_meses_economico: float | None,
    payback_meses_padrao: float | None,
    payback_meses_premium: float | None,

    pacote_destacado: str,
    condicao_pagamento: str,
    validade_dias: int = 10,
):
    w, h = A4
    c = canvas.Canvas(str(out_path), pagesize=A4)

    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # ✅ marca d'água
    _marca_dagua(c, logo_path)

    # Header
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

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(7.4 * cm, top - 1.05 * cm, f"CNPJ: {cnpj} • {cidade_uf}")

    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.setLineWidth(1)
    c.line(2 * cm, top - 1.75 * cm, w - 2 * cm, top - 1.75 * cm)

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, top - 2.9 * cm, "PROPOSTA / ORÇAMENTO ESTIMADO — ENERGIA SOLAR")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(2 * cm, top - 3.9 * cm, f"Cliente: {cliente_nome}")
    c.drawString(2 * cm, top - 4.5 * cm, f"Telefone/WhatsApp: {cliente_telefone}")

    c.setFillColor(colors.HexColor("#4B5563"))
    c.setFont("Helvetica", 10.5)
    c.drawString(2 * cm, top - 5.1 * cm, f"Data: {date.today().strftime('%d/%m/%Y')}  |  Validade: {validade_dias} dias")

    # ✅ Resumo (com altura confortável)
    box_y_top = top - 6.0 * cm
    box_h = 8.1 * cm  # um pouco maior pra dar respiro
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.roundRect(2 * cm, box_y_top - box_h, w - 4 * cm, box_h, 14, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.drawString(2.6 * cm, box_y_top - 0.9 * cm, "Resumo da Simulação")

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
        ("Economia estimada (limitada):", f"{brl(economia_estimada_rs_mes)}/mês"),
    ]

    yy = box_y_top - 1.7 * cm
    for label, val in linhas:
        c.setFont("Helvetica", 10.6)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(2.6 * cm, yy, label)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(colors.HexColor("#111827"))
        c.drawRightString(w - 2.6 * cm, yy, val)
        yy -= 0.55 * cm

    c.setFont("Helvetica", 9.5)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(2.6 * cm, yy - 0.12 * cm, "Obs: economia limitada a 85% da fatura (custo mínimo/fixo da concessionária).")

    # ✅ Pacote destacado AGORA FORA DO RESUMO (sem sobreposição)
    pill_y = (box_y_top - box_h) - 1.15 * cm
    _pill_pacote(c, pill_y, f"Pacote destacado: {pacote_destacado}")

    # ✅ seção pacotes começa depois do pill
    sec_y = pill_y - 1.3 * cm
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, sec_y, "Opções de investimento (3 pacotes)")

    table_y = sec_y - 0.8 * cm
    c.setFillColor(colors.HexColor("#0A7A5A"))
    c.roundRect(2 * cm, table_y, w - 4 * cm, 0.75 * cm, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(2.4 * cm, table_y + 0.24 * cm, "Pacote")
    c.drawString(7.6 * cm, table_y + 0.24 * cm, "Investimento (R$)")
    c.drawRightString(w - 2.4 * cm, table_y + 0.24 * cm, "Payback")

    def pb_txt(pb):
        return "-" if pb is None else f"{pb:.0f} meses"

    rows = [
        ("Econômico", investimento_economico_rs, pb_txt(payback_meses_economico)),
        ("Padrão", investimento_padrao_rs, pb_txt(payback_meses_padrao)),
        ("Premium", investimento_premium_rs, pb_txt(payback_meses_premium)),
    ]

    row_y = table_y - 0.85 * cm
    row_h = 0.85 * cm

    for i, (nome, inv, pb) in enumerate(rows):
        is_hi = (nome == pacote_destacado)

        c.setFillColor(colors.HexColor("#F8FAFC") if i % 2 == 0 else colors.white)
        c.roundRect(2 * cm, row_y, w - 4 * cm, row_h, 8, fill=1, stroke=0)

        if is_hi:
            c.setStrokeColor(colors.HexColor("#19B37A"))
            c.setLineWidth(1.2)
            c.roundRect(2 * cm, row_y, w - 4 * cm, row_h, 8, fill=0, stroke=1)

        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold" if is_hi else "Helvetica", 10.8)
        c.drawString(2.4 * cm, row_y + 0.28 * cm, ("★ " if is_hi else "") + nome)

        c.setFont("Helvetica-Bold", 10.8)
        c.drawString(7.6 * cm, row_y + 0.28 * cm, brl(inv))

        c.setFont("Helvetica", 10.8)
        c.drawRightString(w - 2.4 * cm, row_y + 0.28 * cm, pb)

        row_y -= (row_h + 0.18 * cm)

    # Pagamento
    pay_y = row_y - 0.2 * cm
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, pay_y, "Condição de pagamento")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#374151"))
    c.drawString(2 * cm, pay_y - 0.7 * cm, condicao_pagamento)

    # Rodapé
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
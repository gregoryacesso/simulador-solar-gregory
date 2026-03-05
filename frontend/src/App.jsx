import React, { useMemo, useState } from "react";
import logo from "./assets/logo.png";

const API_BASE = "http://localhost:8000";

function fmtBRL(v) {
  try {
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);
  } catch {
    return `R$ ${v}`;
  }
}
function fmtInt(v) {
  try {
    return new Intl.NumberFormat("pt-BR").format(Math.round(v));
  } catch {
    return String(Math.round(v));
  }
}

function Button({ variant = "primary", disabled, children, onClick }) {
  const styles = {
    primary: {
      bg: "linear-gradient(135deg, #0A7A5A 0%, #19B37A 55%, #F7C948 130%)",
      fg: "white",
      bd: "transparent",
      sh: "0 14px 32px rgba(10,122,90,.22)",
    },
    secondary: {
      bg: "rgba(255,255,255,0.85)",
      fg: "#111827",
      bd: "#E5E7EB",
      sh: "0 10px 24px rgba(0,0,0,.06)",
    },
  };
  const s = styles[variant] || styles.primary;
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      style={{
        padding: "12px 14px",
        borderRadius: 14,
        border: `1px solid ${s.bd}`,
        background: s.bg,
        color: s.fg,
        fontWeight: 950,
        cursor: disabled ? "not-allowed" : "pointer",
        boxShadow: s.sh,
      }}
    >
      {children}
    </button>
  );
}

function Field({ label, hint, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <label style={{ fontSize: 12, color: "#111827", fontWeight: 900 }}>{label}</label>
      {children}
      {hint ? <div style={{ fontSize: 12, color: "#6B7280" }}>{hint}</div> : null}
    </div>
  );
}

function Input(props) {
  return (
    <input
      {...props}
      style={{
        width: "100%",
        padding: "12px 12px",
        borderRadius: 14,
        border: "1px solid #E5E7EB",
        background: "rgba(255,255,255,0.92)",
        outline: "none",
        boxShadow: "0 1px 0 rgba(0,0,0,.02)",
        fontSize: 14,
      }}
    />
  );
}
function Select(props) {
  return (
    <select
      {...props}
      style={{
        width: "100%",
        padding: "12px 12px",
        borderRadius: 14,
        border: "1px solid #E5E7EB",
        background: "rgba(255,255,255,0.92)",
        outline: "none",
        boxShadow: "0 1px 0 rgba(0,0,0,.02)",
        fontSize: 14,
      }}
    />
  );
}

function Stat({ label, value, sub }) {
  return (
    <div
      style={{
        border: "1px solid rgba(229,231,235,.9)",
        borderRadius: 16,
        padding: 14,
        background: "rgba(255,255,255,0.85)",
        boxShadow: "0 12px 30px rgba(0,0,0,.04)",
      }}
    >
      <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 900 }}>{label}</div>
      <div style={{ fontSize: 18, color: "#111827", fontWeight: 1000, marginTop: 6 }}>{value}</div>
      {sub ? <div style={{ fontSize: 12, color: "#6B7280", marginTop: 4 }}>{sub}</div> : null}
    </div>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(2,6,23,.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 18,
        zIndex: 50,
      }}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          width: "min(640px, 100%)",
          background: "rgba(255,255,255,0.95)",
          borderRadius: 20,
          border: "1px solid rgba(255,255,255,0.6)",
          boxShadow: "0 25px 60px rgba(0,0,0,.35)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: 16,
            borderBottom: "1px solid #E5E7EB",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
          }}
        >
          <div style={{ fontSize: 16, fontWeight: 1000, color: "#111827" }}>{title}</div>
          <button
            onClick={onClose}
            style={{
              border: "1px solid #E5E7EB",
              background: "white",
              borderRadius: 12,
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 1000,
            }}
          >
            ✕
          </button>
        </div>
        <div style={{ padding: 16 }}>{children}</div>
      </div>
    </div>
  );
}

export default function App() {
  const [form, setForm] = useState({
    nome: "",
    telefone: "",
    cidade_uf: "Aracaju-SE",
    conta_media_rs: "",
    modo_taxas: "PERCENTUAL",
    custo_fixo_mensal_rs: "120",
    tarifa_rs_kwh: "0.95",
  });

  const [loading, setLoading] = useState(false);
  const [loadingPacote, setLoadingPacote] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [confirm, setConfirm] = useState(null);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const canSubmit = useMemo(() => {
    const okBasico =
      form.nome.trim().length >= 2 &&
      form.telefone.trim().length >= 8 &&
      Number(form.conta_media_rs) > 0 &&
      Number(form.tarifa_rs_kwh) > 0;

    if (!okBasico) return false;
    if (form.modo_taxas === "FIXO") return Number(form.custo_fixo_mensal_rs) >= 0;
    return true;
  }, [form]);

  async function simular(pacote_destacado = "Padrão") {
    const payload = {
      nome: form.nome.trim(),
      telefone: form.telefone.trim(),
      cidade_uf: form.cidade_uf.trim(),
      conta_media_rs: Number(form.conta_media_rs),
      modo_taxas: form.modo_taxas,
      custo_fixo_mensal_rs: Number(form.custo_fixo_mensal_rs),
      tarifa_rs_kwh: Number(form.tarifa_rs_kwh),
      pacote_destacado,
    };

    const r = await fetch(`${API_BASE}/api/simular`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await r.json();
    if (!r.ok || data.error) throw new Error(data.error || "Falha na simulação");
    return data;
  }

  async function gerarSimulacaoInicial() {
    setError("");
    setLoading(true);
    setResult(null);
    setConfirm(null);
    try {
      const data = await simular("Padrão");
      setResult(data);
    } catch (e) {
      setError(e?.message || "Erro");
    } finally {
      setLoading(false);
    }
  }

  const pacotes = useMemo(() => {
    if (!result) return [];
    return [
      {
        key: "economico",
        titulo: "Econômico",
        badge: "Custo-benefício",
        valor: result.investimento_economico_rs,
        payback: result.payback_meses_economico,
      },
      {
        key: "padrao",
        titulo: "Padrão",
        badge: "Mais vendido",
        destaque: true,
        valor: result.investimento_padrao_rs,
        payback: result.payback_meses_padrao,
      },
      {
        key: "premium",
        titulo: "Premium",
        badge: "Top performance",
        valor: result.investimento_premium_rs,
        payback: result.payback_meses_premium,
      },
    ];
  }, [result]);

  async function confirmarEAbrirWhatsApp() {
    if (!confirm) return;
    setLoadingPacote(true);
    setError("");

    try {
      const data = await simular(confirm.pacote);

      await fetch(`${API_BASE}/api/lead-zap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: data.id }),
      });

      setResult(data);
      window.open(data.whatsapp_url, "_blank");
      setConfirm(null);
    } catch (e) {
      setError(e?.message || "Erro ao confirmar pacote");
    } finally {
      setLoadingPacote(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(1200px 600px at 15% 10%, rgba(247,201,72,.38), transparent 60%), radial-gradient(900px 500px at 90% 5%, rgba(25,179,122,.22), transparent 55%), linear-gradient(180deg, #F8FAFC 0%, #F3F7F6 60%, #F8FAFC 100%)",
        padding: 22,
      }}
    >
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        {/* BANNER / HERO */}
        <div
          style={{
            borderRadius: 26,
            overflow: "hidden",
            position: "relative",
            border: "1px solid rgba(255,255,255,0.65)",
            boxShadow: "0 18px 46px rgba(0,0,0,.07)",
            backdropFilter: "blur(10px)",
            background:
              "linear-gradient(135deg, rgba(10,122,90,.14) 0%, rgba(25,179,122,.10) 45%, rgba(247,201,72,.18) 100%)",
          }}
        >
          {/* textura solar (SVG inline) */}
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 1200 260"
            preserveAspectRatio="none"
            style={{ position: "absolute", inset: 0, opacity: 0.28 }}
          >
            <defs>
              <radialGradient id="sun" cx="20%" cy="20%" r="60%">
                <stop offset="0%" stopColor="#F7C948" stopOpacity="0.95" />
                <stop offset="55%" stopColor="#F7C948" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#F7C948" stopOpacity="0" />
              </radialGradient>
              <linearGradient id="rays" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#19B37A" stopOpacity="0.0" />
                <stop offset="50%" stopColor="#19B37A" stopOpacity="0.35" />
                <stop offset="100%" stopColor="#19B37A" stopOpacity="0.0" />
              </linearGradient>
            </defs>
            <rect width="1200" height="260" fill="url(#sun)" />
            {Array.from({ length: 18 }).map((_, i) => (
              <rect
                key={i}
                x={i * 70}
                y="0"
                width="18"
                height="260"
                fill="url(#rays)"
                transform={`skewX(${(i % 2 === 0 ? -12 : 12)})`}
              />
            ))}
          </svg>

          <div
            style={{
              position: "relative",
              padding: 18,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 14,
              flexWrap: "wrap",
            }}
          >
            {/* LOGO + TITULO */}
            <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
              <div
                style={{
                  width: 190,
                  height: 56,
                  borderRadius: 16,
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid rgba(255,255,255,0.65)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 10,
                }}
              >
                <img
                  src={logo}
                  alt="Gregory"
                  style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <div style={{ fontSize: 20, fontWeight: 1000, color: "#0B1220" }}>
                  Simulador de Orçamento Solar
                </div>
                <div style={{ fontSize: 13, color: "#374151", fontWeight: 700 }}>
                  PDF na hora • Pacotes (Econômico/Padrão/Premium) • WhatsApp com 1 clique
                </div>
              </div>
            </div>

            {/* CTA */}
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Button variant="secondary" onClick={() => window.open("https://wa.me/5579998451783", "_blank")}>
                💬 WhatsApp
              </Button>
              <Button variant="primary" disabled={!canSubmit || loading} onClick={gerarSimulacaoInicial}>
                {loading ? "Calculando..." : "Gerar simulação + PDF"}
              </Button>
            </div>
          </div>
        </div>

        {/* CONTEÚDO */}
        <div style={{ display: "grid", gridTemplateColumns: "1.05fr .95fr", gap: 16, marginTop: 16 }}>
          {/* FORM */}
          <div
            style={{
              borderRadius: 22,
              padding: 18,
              background: "rgba(255,255,255,0.80)",
              border: "1px solid rgba(255,255,255,0.65)",
              boxShadow: "0 18px 44px rgba(0,0,0,.06)",
              backdropFilter: "blur(10px)",
            }}
          >
            <div style={{ fontSize: 16, fontWeight: 1000, color: "#111827" }}>Dados para simulação</div>
            <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Nome">
                <Input name="nome" value={form.nome} onChange={onChange} placeholder="Seu nome" />
              </Field>

              <Field label="Telefone/WhatsApp">
                <Input name="telefone" value={form.telefone} onChange={onChange} placeholder="(79) 9xxxx-xxxx" />
              </Field>

              <Field label="Cidade/UF">
                <Input name="cidade_uf" value={form.cidade_uf} onChange={onChange} />
              </Field>

              <Field label="Conta total (R$/mês)">
                <Input name="conta_media_rs" value={form.conta_media_rs} onChange={onChange} inputMode="decimal" placeholder="Ex: 500" />
              </Field>

              <Field
                label="Modo de taxas"
                hint="Automático usa percentuais baseados na fatura (mais real)."
              >
                <Select name="modo_taxas" value={form.modo_taxas} onChange={onChange}>
                  <option value="PERCENTUAL">Automático (Energisa)</option>
                  <option value="FIXO">Manual (valor fixo)</option>
                </Select>
              </Field>

              {form.modo_taxas === "FIXO" ? (
                <Field label="Valor fixo (taxas/encargos) R$" hint="Ex: CIP + custo mínimo.">
                  <Input name="custo_fixo_mensal_rs" value={form.custo_fixo_mensal_rs} onChange={onChange} inputMode="decimal" placeholder="Ex: 120" />
                </Field>
              ) : (
                <div
                  style={{
                    borderRadius: 16,
                    border: "1px dashed #D1FAE5",
                    background: "rgba(233,255,246,.75)",
                    padding: 12,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <div style={{ fontWeight: 1000, color: "#0A7A5A" }}>Percentuais atuais</div>
                  <div style={{ color: "#065F46", fontWeight: 900, fontSize: 13 }}>
                    86,8% energia • 13,2% taxas
                  </div>
                </div>
              )}

              <Field label="Tarifa (R$/kWh) — opcional" hint="Se não souber, deixe 0,95.">
                <Input name="tarifa_rs_kwh" value={form.tarifa_rs_kwh} onChange={onChange} inputMode="decimal" placeholder="Ex: 0.95" />
              </Field>
            </div>

            {error && (
              <div style={{ marginTop: 12, padding: 12, borderRadius: 16, background: "rgba(254,242,242,0.95)", border: "1px solid #FECACA" }}>
                <div style={{ fontWeight: 1000, color: "#991B1B" }}>Erro</div>
                <div style={{ color: "#7F1D1D", marginTop: 4 }}>{error}</div>
              </div>
            )}
          </div>

          {/* RESULTADO */}
          <div
            style={{
              borderRadius: 22,
              padding: 18,
              background: "rgba(255,255,255,0.80)",
              border: "1px solid rgba(255,255,255,0.65)",
              boxShadow: "0 18px 44px rgba(0,0,0,.06)",
              backdropFilter: "blur(10px)",
              minHeight: 220,
            }}
          >
            <div style={{ fontSize: 16, fontWeight: 1000, color: "#111827" }}>Resultado</div>
            <div style={{ fontSize: 13, color: "#6B7280", fontWeight: 650, marginTop: 6 }}>
              Estimativa + PDF + WhatsApp.
            </div>

            {!result ? (
              <div style={{ marginTop: 16, borderRadius: 18, border: "1px dashed #E5E7EB", padding: 16, color: "#6B7280", background: "rgba(255,255,255,0.65)" }}>
                Preencha os dados e clique em <b>Gerar simulação + PDF</b>.
              </div>
            ) : (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 }}>
                  <Stat label="Conta total" value={fmtBRL(result.conta_total_rs)} />
                  <Stat label="Taxas (fixo)" value={fmtBRL(result.custo_fixo_mensal_rs)} />
                  <Stat label="Parte variável" value={fmtBRL(result.valor_variavel_rs)} />
                  <Stat label="Consumo estimado" value={`${fmtInt(result.kwh_estimado_mes)} kWh/mês`} />
                  <Stat label="Sistema sugerido" value={`${Number(result.kwp_sugerido).toFixed(1)} kWp`} />
                  <Stat label="Economia estimada" value={`${fmtBRL(result.economia_estimada_rs_mes)}/mês`} sub="limitada a 85%" />
                </div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
                  <Button variant="secondary" onClick={() => window.open(`${API_BASE}${result.pdf_url}`, "_blank")}>
                    📄 Baixar PDF
                  </Button>
                  <Button variant="primary" onClick={() => window.open(result.whatsapp_url, "_blank")}>
                    💬 Abrir WhatsApp
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* PACOTES */}
        {result && (
          <div style={{ marginTop: 16 }}>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}>
              <div style={{ fontSize: 16, fontWeight: 1000, color: "#111827" }}>Pacotes</div>
              <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 800 }}>
                Clique no pacote → confirmar → WhatsApp
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, marginTop: 12 }}>
              {pacotes.map((p) => (
                <div
                  key={p.key}
                  style={{
                    borderRadius: 22,
                    padding: 16,
                    background: p.destaque
                      ? "linear-gradient(180deg, rgba(10,122,90,.10), rgba(255,255,255,.85))"
                      : "rgba(255,255,255,0.80)",
                    border: p.destaque ? "1px solid rgba(10,122,90,.25)" : "1px solid rgba(255,255,255,0.65)",
                    boxShadow: p.destaque ? "0 24px 50px rgba(10,122,90,.12)" : "0 18px 44px rgba(0,0,0,.06)",
                    backdropFilter: "blur(10px)",
                    position: "relative",
                  }}
                >
                  {p.destaque && (
                    <div style={{ position: "absolute", top: 12, right: 12, fontWeight: 900, fontSize: 12, color: "#0A7A5A" }}>
                      🔥 Mais vendido
                    </div>
                  )}

                  <div style={{ fontSize: 18, fontWeight: 1000, color: "#111827" }}>{p.titulo}</div>
                  <div style={{ color: "#6B7280", fontSize: 13, fontWeight: 700, marginTop: 6 }}>{p.badge}</div>

                  <div style={{ fontSize: 26, fontWeight: 1000, color: "#111827", marginTop: 10 }}>
                    {fmtBRL(p.valor)}
                  </div>

                  <div style={{ color: "#374151", fontSize: 13, fontWeight: 800, marginTop: 6 }}>
                    Payback: <b>{p.payback == null ? "-" : `${Math.round(p.payback)} meses`}</b>
                  </div>

                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
                    <Button variant="primary" onClick={() => setConfirm({ pacote: p.titulo, valor: p.valor })}>
                      Quero este pacote
                    </Button>
                    <Button variant="secondary" onClick={() => window.open(`${API_BASE}${result.pdf_url}`, "_blank")}>
                      Ver PDF
                    </Button>
                  </div>

                  <div style={{ marginTop: 10, color: "#6B7280", fontSize: 12, fontWeight: 650 }}>
                    * Valores estimados. Confirmação final após vistoria técnica.
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: 16, textAlign: "center", color: "#6B7280", fontSize: 12, fontWeight: 800 }}>
          © Gregory Segurança Eletrônica & Energia Solar — WhatsApp: (79) 99845-1783
        </div>
      </div>

      {/* Modal confirmação */}
      {confirm && (
        <Modal title="Confirmar e abrir WhatsApp" onClose={() => (!loadingPacote ? setConfirm(null) : null)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ color: "#111827", fontWeight: 900 }}>
              Você escolheu o pacote <span style={{ color: "#0A7A5A" }}>{confirm.pacote}</span>
            </div>

            <div style={{ color: "#111827", fontWeight: 1000, fontSize: 18 }}>{fmtBRL(confirm.valor)}</div>

            <div style={{ color: "#6B7280", fontWeight: 650, fontSize: 13 }}>
              Ao confirmar, geramos um PDF novo destacando este pacote e abrimos o WhatsApp com mensagem pronta.
            </div>

            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", flexWrap: "wrap", marginTop: 8 }}>
              <Button variant="secondary" disabled={loadingPacote} onClick={() => setConfirm(null)}>
                Cancelar
              </Button>
              <Button variant="primary" disabled={loadingPacote} onClick={confirmarEAbrirWhatsApp}>
                {loadingPacote ? "Gerando PDF..." : "Confirmar e abrir WhatsApp"}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
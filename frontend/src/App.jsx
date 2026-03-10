import React, { useEffect, useMemo, useState } from "react";
import logo from "./assets/logo.png";

const API_BASE = "https://simulador-solar-api.onrender.com";

function fmtBRL(v) {
  try {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(v);
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

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    function onResize() {
      setIsMobile(window.innerWidth <= 768);
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return isMobile;
}

function Button({ variant = "primary", disabled, children, onClick, fullWidth = false }) {
  const map = {
    primary: {
      bg: "linear-gradient(135deg, #0A7A5A 0%, #19B37A 60%, #F7C948 140%)",
      color: "#fff",
      border: "transparent",
      shadow: "0 16px 36px rgba(10,122,90,.24)",
    },
    secondary: {
      bg: "#fff",
      color: "#111827",
      border: "#E5E7EB",
      shadow: "0 10px 24px rgba(0,0,0,.05)",
    },
  };

  const s = map[variant] || map.primary;

  return (
    <button
      disabled={disabled}
      onClick={onClick}
      style={{
        width: fullWidth ? "100%" : "auto",
        padding: "14px 16px",
        borderRadius: 16,
        border: `1px solid ${s.border}`,
        background: s.bg,
        color: s.color,
        fontWeight: 900,
        fontSize: 14,
        cursor: disabled ? "not-allowed" : "pointer",
        boxShadow: s.shadow,
        opacity: disabled ? 0.7 : 1,
      }}
    >
      {children}
    </button>
  );
}

function Input(props) {
  return (
    <input
      {...props}
      style={{
        width: "100%",
        padding: "14px 13px",
        borderRadius: 16,
        border: "1px solid #E5E7EB",
        background: "#fff",
        fontSize: 15,
        outline: "none",
        boxSizing: "border-box",
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
        padding: "14px 13px",
        borderRadius: 16,
        border: "1px solid #E5E7EB",
        background: "#fff",
        fontSize: 15,
        outline: "none",
        boxSizing: "border-box",
      }}
    />
  );
}

function Field({ label, hint, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
      <label style={{ fontSize: 12, fontWeight: 900, color: "#111827" }}>{label}</label>
      {children}
      {hint ? <div style={{ fontSize: 12, color: "#6B7280", lineHeight: 1.35 }}>{hint}</div> : null}
    </div>
  );
}

function Card({ children, padding = 18 }) {
  return (
    <div
      style={{
        borderRadius: 24,
        padding,
        background: "rgba(255,255,255,0.88)",
        border: "1px solid rgba(255,255,255,0.7)",
        boxShadow: "0 18px 44px rgba(0,0,0,.06)",
      }}
    >
      {children}
    </div>
  );
}

function ProgressBar({ value }) {
  return (
    <div
      style={{
        height: 10,
        background: "#E5E7EB",
        borderRadius: 999,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${value}%`,
          background: "linear-gradient(90deg, #0A7A5A, #19B37A, #F7C948)",
          transition: "width .35s ease",
        }}
      />
    </div>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(2,6,23,.58)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        zIndex: 100,
      }}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          width: "min(640px, 100%)",
          background: "#fff",
          borderRadius: 22,
          border: "1px solid #E5E7EB",
          boxShadow: "0 30px 60px rgba(0,0,0,.35)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: 16,
            borderBottom: "1px solid #E5E7EB",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div style={{ fontWeight: 1000, fontSize: 16, color: "#111827" }}>{title}</div>
          <button
            onClick={onClose}
            style={{
              border: "1px solid #E5E7EB",
              background: "#fff",
              borderRadius: 12,
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 900,
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
  const isMobile = useIsMobile();

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
  const [loadingFollowup, setLoadingFollowup] = useState(false);
  const [warmingUp, setWarmingUp] = useState(true);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function warmUp() {
      try {
        await fetch(`${API_BASE}/api/health`);
      } catch (_) {
      } finally {
        if (active) setWarmingUp(false);
      }
    }
    warmUp();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let timer;
    if (loading || loadingFollowup) {
      setProgress(10);
      timer = setInterval(() => {
        setProgress((prev) => (prev >= 90 ? prev : prev + 8));
      }, 300);
    } else {
      setProgress(100);
      const t = setTimeout(() => setProgress(0), 350);
      return () => clearTimeout(t);
    }
    return () => clearInterval(timer);
  }, [loading, loadingFollowup]);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const canSubmit = useMemo(() => {
    const ok =
      form.nome.trim().length >= 2 &&
      form.telefone.trim().length >= 8 &&
      Number(form.conta_media_rs) > 0 &&
      Number(form.tarifa_rs_kwh) > 0;

    if (!ok) return false;
    if (form.modo_taxas === "FIXO") return Number(form.custo_fixo_mensal_rs) >= 0;
    return true;
  }, [form]);

  async function simular() {
    const payload = {
      nome: form.nome.trim(),
      telefone: form.telefone.trim(),
      cidade_uf: form.cidade_uf.trim(),
      conta_media_rs: Number(form.conta_media_rs),
      modo_taxas: form.modo_taxas,
      custo_fixo_mensal_rs: Number(form.custo_fixo_mensal_rs),
      tarifa_rs_kwh: Number(form.tarifa_rs_kwh),
    };

    const r = await fetch(`${API_BASE}/api/simular`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await r.json();
    if (!r.ok || data.error) throw new Error(data.error || "Falha na simulação");
    return data;
  }

  async function gerarSimulacao() {
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const data = await simular();
      setResult(data);
    } catch (e) {
      setError(e?.message || "Erro");
    } finally {
      setLoading(false);
    }
  }

  async function abrirWhatsApp() {
    if (!result) return;

    setLoadingFollowup(true);
    try {
      await fetch(`${API_BASE}/api/lead-zap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: result.id }),
      });

      window.open(result.whatsapp_url, "_blank");
    } catch (e) {
      setError(e?.message || "Erro ao abrir WhatsApp");
    } finally {
      setLoadingFollowup(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(1200px 600px at 15% 10%, rgba(247,201,72,.38), transparent 60%), radial-gradient(900px 500px at 90% 5%, rgba(25,179,122,.22), transparent 55%), linear-gradient(180deg, #F8FAFC 0%, #F3F7F6 60%, #F8FAFC 100%)",
        padding: isMobile ? 12 : 22,
      }}
    >
      <div style={{ maxWidth: 980, margin: "0 auto" }}>
        {(loading || loadingFollowup) && (
          <div style={{ marginBottom: 12 }}>
            <ProgressBar value={progress} />
          </div>
        )}

        <Card padding={isMobile ? 14 : 18}>
          <div
            style={{
              display: "flex",
              flexDirection: isMobile ? "column" : "row",
              justifyContent: "space-between",
              alignItems: isMobile ? "flex-start" : "center",
              gap: 14,
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: isMobile ? "column" : "row",
                alignItems: isMobile ? "flex-start" : "center",
                gap: 14,
              }}
            >
              <div
                style={{
                  width: isMobile ? 155 : 180,
                  height: isMobile ? 52 : 58,
                  borderRadius: 16,
                  background: "#fff",
                  border: "1px solid #E5E7EB",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 10,
                  boxShadow: "0 10px 24px rgba(0,0,0,.04)",
                }}
              >
                <img src={logo} alt="Gregory" style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} />
              </div>

              <div>
                <div style={{ fontSize: isMobile ? 20 : 25, fontWeight: 1000, color: "#0B1220", lineHeight: 1.15 }}>
                  Simulador de Orçamento Solar
                </div>
                <div style={{ fontSize: 13, color: "#4B5563", fontWeight: 700, marginTop: 6, lineHeight: 1.35 }}>
                  Resultado objetivo, PDF imediato e opções de pagamento.
                </div>
              </div>
            </div>
          </div>
        </Card>

        {warmingUp && (
          <div
            style={{
              marginTop: 12,
              padding: 12,
              borderRadius: 16,
              background: "#FFF7E6",
              border: "1px solid #FDE68A",
              color: "#92400E",
              fontWeight: 800,
              fontSize: 13,
            }}
          >
            Preparando o simulador... no primeiro acesso o servidor pode demorar um pouco.
          </div>
        )}

        {error && (
          <div
            style={{
              marginTop: 12,
              padding: 12,
              borderRadius: 16,
              background: "#FEF2F2",
              border: "1px solid #FECACA",
            }}
          >
            <div style={{ fontWeight: 1000, color: "#991B1B" }}>Erro</div>
            <div style={{ color: "#7F1D1D", marginTop: 4 }}>{error}</div>
          </div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr",
            gap: 16,
            marginTop: 16,
          }}
        >
          <Card padding={isMobile ? 14 : 18}>
            <div style={{ fontSize: 17, fontWeight: 1000, color: "#111827" }}>
              Dados da simulação
            </div>

            <div
              style={{
                marginTop: 14,
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                gap: 12,
              }}
            >
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

              <Field label="Modo de taxas" hint="Automático usa os percentuais da concessionária.">
                <Select name="modo_taxas" value={form.modo_taxas} onChange={onChange}>
                  <option value="PERCENTUAL">Automático (Energisa)</option>
                  <option value="FIXO">Manual (valor fixo)</option>
                </Select>
              </Field>

              {form.modo_taxas === "FIXO" ? (
                <Field label="Valor fixo (taxas/encargos) R$">
                  <Input
                    name="custo_fixo_mensal_rs"
                    value={form.custo_fixo_mensal_rs}
                    onChange={onChange}
                    inputMode="decimal"
                    placeholder="Ex: 120"
                  />
                </Field>
              ) : (
                <div
                  style={{
                    borderRadius: 18,
                    background: "#ECFDF5",
                    border: "1px dashed #A7F3D0",
                    padding: 14,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <div style={{ fontWeight: 1000, color: "#065F46" }}>Percentuais atuais</div>
                  <div style={{ fontSize: 13, color: "#047857", fontWeight: 800 }}>
                    86,8% energia • 13,2% taxas
                  </div>
                </div>
              )}

              <Field label="Tarifa (R$/kWh)" hint="Se não souber, deixe 0,95.">
                <Input
                  name="tarifa_rs_kwh"
                  value={form.tarifa_rs_kwh}
                  onChange={onChange}
                  inputMode="decimal"
                  placeholder="Ex: 0.95"
                />
              </Field>
            </div>
          </Card>

          {result && (
            <Card padding={isMobile ? 14 : 18}>
              <div style={{ fontSize: 17, fontWeight: 1000, color: "#111827" }}>
                Resultado da simulação
              </div>

              <div
                style={{
                  marginTop: 16,
                  display: "grid",
                  gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                  gap: 12,
                }}
              >
                <div style={{ background: "#fff", border: "1px solid #E5E7EB", borderRadius: 18, padding: 14 }}>
                  <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 900 }}>Sistema sugerido</div>
                  <div style={{ marginTop: 8, fontSize: 22, fontWeight: 1000, color: "#111827" }}>
                    {Number(result.kwp_sugerido).toFixed(1)} kWp
                  </div>
                </div>

                <div style={{ background: "#fff", border: "1px solid #E5E7EB", borderRadius: 18, padding: 14 }}>
                  <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 900 }}>Investimento estimado</div>
                  <div style={{ marginTop: 8, fontSize: 22, fontWeight: 1000, color: "#0A7A5A" }}>
                    {fmtBRL(result.investimento_total_rs)}
                  </div>
                </div>

                <div style={{ background: "#fff", border: "1px solid #E5E7EB", borderRadius: 18, padding: 14 }}>
                  <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 900 }}>Produção estimada</div>
                  <div style={{ marginTop: 8, fontSize: 18, fontWeight: 1000, color: "#111827" }}>
                    {fmtInt(result.producao_estimada_kwh_mes)} kWh/mês
                  </div>
                </div>

                <div style={{ background: "#fff", border: "1px solid #E5E7EB", borderRadius: 18, padding: 14 }}>
                  <div style={{ fontSize: 12, color: "#6B7280", fontWeight: 900 }}>Economia estimada</div>
                  <div style={{ marginTop: 8, fontSize: 18, fontWeight: 1000, color: "#111827" }}>
                    {fmtBRL(result.economia_estimada_rs_mes)}/mês
                  </div>
                </div>
              </div>

              <div
                style={{
                  marginTop: 16,
                  background: "#F8FAFC",
                  border: "1px solid #E5E7EB",
                  borderRadius: 18,
                  padding: 14,
                }}
              >
                <div style={{ fontWeight: 1000, color: "#111827" }}>Opções de pagamento</div>
                <div style={{ marginTop: 8, color: "#374151", lineHeight: 1.6, fontSize: 14 }}>
                  • À vista<br />
                  • Entrada + parcelamento no cartão<br />
                  • Financiamento bancário sujeito à aprovação
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: 10,
                  flexDirection: isMobile ? "column" : "row",
                  marginTop: 16,
                }}
              >
                <Button
                  variant="secondary"
                  fullWidth={isMobile}
                  onClick={() => window.open(`${API_BASE}${result.pdf_url}`, "_blank")}
                >
                  📄 Baixar PDF
                </Button>

                <Button
                  variant="primary"
                  fullWidth={isMobile}
                  onClick={abrirWhatsApp}
                  disabled={loadingFollowup}
                >
                  {loadingFollowup ? "Abrindo WhatsApp..." : "💬 Solicitar proposta"}
                </Button>
              </div>
            </Card>
          )}
        </div>

        <div style={{ height: isMobile ? 86 : 24 }} />

        {/* BOTÃO FIXO EMBAIXO */}
        <div
          style={{
            position: "fixed",
            left: 0,
            right: 0,
            bottom: 0,
            padding: isMobile ? "10px 12px calc(10px + env(safe-area-inset-bottom))" : "14px 22px",
            background: "rgba(255,255,255,0.96)",
            borderTop: "1px solid #E5E7EB",
            boxShadow: "0 -10px 24px rgba(0,0,0,.06)",
            zIndex: 90,
          }}
        >
          <div style={{ maxWidth: 980, margin: "0 auto" }}>
            <Button
              variant="primary"
              fullWidth={true}
              disabled={!canSubmit || loading}
              onClick={gerarSimulacao}
            >
              {loading ? "Gerando simulação..." : "Simular agora"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
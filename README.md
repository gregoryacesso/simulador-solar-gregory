# MVP - Simulador de Orçamento Solar (React + FastAPI + PDF)

Este MVP permite:
- Cliente informar conta média (R$/mês) + dados básicos
- API calcula estimativa (kWp, produção, economia, payback)
- Gera PDF automático com a sua logomarca
- Botão "Falar no WhatsApp" já abre conversa com mensagem + link do PDF

## Requisitos
- Windows 10/11
- Python 3.10+ instalado
- Node.js 18+ instalado

---

# 1) Backend (FastAPI)

## Instalar
Abra o terminal dentro da pasta `backend`:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Rodar
```bash
uvicorn main:app --reload --port 8000
```

Teste:
- http://localhost:8000/api/health

---

# 2) Frontend (React)

## Instalar
Abra outro terminal dentro da pasta `frontend`:

```bash
cd frontend
npm install
```

## Rodar
```bash
npm run dev
```

Abra:
- http://localhost:5173

---

# Observações
- Em produção, você deve hospedar o backend e usar um domínio. Depois, o botão WhatsApp vai enviar o link completo (https://...).
- O WhatsApp NÃO permite anexar PDF automaticamente apenas abrindo um link, então usamos link do PDF + mensagem pronta.

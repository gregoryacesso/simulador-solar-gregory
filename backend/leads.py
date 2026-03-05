from pathlib import Path
from datetime import datetime
import csv

BASE_DIR = Path(__file__).parent
LEADS_FILE = BASE_DIR / "leads.csv"

FIELDNAMES = [
    "id",
    "data",
    "nome",
    "telefone",
    "cidade",
    "conta_total",
    "modo_taxas",
    "custo_fixo",
    "valor_variavel",
    "kwh_estimado",
    "kwp",
    "pacote",
    "valor_pacote",
    "status",
]

def _garantir_arquivo():
    if not LEADS_FILE.exists():
        with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def salvar_ou_atualizar_lead(dados: dict):
    _garantir_arquivo()

    linhas = []
    atualizado = False

    with open(LEADS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") == str(dados.get("id")):
                if dados.get("status"):
                    row["status"] = dados["status"]

                for k in FIELDNAMES:
                    if k in ("id", "data"):
                        continue
                    v = dados.get(k)
                    if v is not None and str(v).strip() != "":
                        row[k] = str(v)

                atualizado = True
            linhas.append(row)

    if not atualizado:
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        nova = {k: "" for k in FIELDNAMES}
        nova["id"] = str(dados.get("id", ""))
        nova["data"] = now

        for k in FIELDNAMES:
            if k in ("id", "data"):
                continue
            if k in dados and dados[k] is not None:
                nova[k] = str(dados[k])

        if not nova["status"]:
            nova["status"] = "SIMULOU"

        linhas.append(nova)

    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(linhas)
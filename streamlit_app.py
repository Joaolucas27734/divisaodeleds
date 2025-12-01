import streamlit as st
import pandas as pd
import numpy as np
from urllib.parse import quote

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# ID e aba
SHEET_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
SHEET_NAME = "Total"

# Carregar planilha
@st.cache_data
def carregar_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
    df = pd.read_csv(url, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df

st.title("🔀 Divisão 50/50 por Classificação (Coluna G)")

df = carregar_sheet()

if "Responsável" not in df.columns:
    df["Responsável"] = ""

# Se a coluna G tiver outro nome, ajuste aqui:
COL_CLASSIFICACAO = df.columns[6]   # Coluna G → índice 6

st.write(f"✔ Coluna de classificação detectada: **{COL_CLASSIFICACAO}**")

# Divisão 50/50
responsaveis = []

for classificacao, grupo in df.groupby(COL_CLASSIFICACAO):
    grupo_embaralhado = grupo.sample(frac=1, random_state=42)  # embaralha
    metade = len(grupo_embaralhado) // 2

    nomes = ["Vendedor A"] * metade + ["Vendedor B"] * (len(grupo_embaralhado) - metade)
    grupo_embaralhado["Responsável"] = nomes

    responsaveis.append(grupo_embaralhado)

df_final = pd.concat(responsaveis).sort_index()

st.success("✅ Divisão 50/50 realizada com sucesso!")

st.dataframe(df_final.head(50), use_container_width=True)

# Download
csv = df_final.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV dividido", csv, "divisao_50_50.csv", "text/csv")

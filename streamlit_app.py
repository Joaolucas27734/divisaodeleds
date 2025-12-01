import streamlit as st
import pandas as pd
import numpy as np
from urllib.parse import quote

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# Planilha alvo
SHEET_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
SHEET_NAME = "Total"

# Carregar planilha Google Sheets
@st.cache_data
def carregar_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
    df = pd.read_csv(url, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df

st.title("📊 Divisão 50/50 por Classificação + Filtro por Data")

df = carregar_sheet()

# Detectar coluna de data automaticamente
col_data = None
possiveis_datas = ["DATA", "Data", "data", "DATA DA COMPRA", "Data compra", "Data da Compra"]

for col in df.columns:
    if col in possiveis_datas:
        col_data = col
        break

if col_data is None:
    st.error("❌ Não encontrei coluna de data. Informe o nome da coluna para continuar.")
else:
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

# Filtro de data
min_date = df[col_data].min()
max_date = df[col_data].max()

periodo = st.date_input("📅 Filtrar período", value=(min_date, max_date))

df_filtrado = df[(df[col_data] >= pd.to_datetime(periodo[0])) &
                 (df[col_data] <= pd.to_datetime(periodo[1]))]

# Detectar classificação (coluna G = índice 6)
col_classificacao = df.columns[6]

st.write(f"✔ Classificação detectada: **{col_classificacao}**")

# Separar 50/50 por classificação
vendedor_a_list = []
vendedor_b_list = []

for classificacao, grupo in df_filtrado.groupby(col_classificacao):
    grupo_embaralhado = grupo.sample(frac=1, random_state=42)

    metade = len(grupo_embaralhado) // 2

    vendedor_a_list.append(grupo_embaralhado.iloc[:metade])
    vendedor_b_list.append(grupo_embaralhado.iloc[metade:])

df_vendedor_a = pd.concat(vendedor_a_list).sort_values(col_data)
df_vendedor_b = pd.concat(vendedor_b_list).sort_values(col_data)

# ======================
#        ABAS
# ======================

aba_geral, aba_a, aba_b = st.tabs(["📄 Geral", "🟦 Vendedor A", "🟥 Vendedor B"])

with aba_geral:
    st.subheader("📄 Geral (após filtro de data)")
    st.dataframe(df_filtrado, use_container_width=True)
    st.download_button("📥 Baixar Geral", df_filtrado.to_csv(index=False).encode(),
                       "geral.csv", "text/csv")

with aba_a:
    st.subheader("🟦 Carteira Vendedor A (50%)")
    st.dataframe(df_vendedor_a, use_container_width=True)
    st.download_button("📥 Baixar Vendedor A", df_vendedor_a.to_csv(index=False).encode(),
                       "vendedor_a.csv", "text/csv")

with aba_b:
    st.subheader("🟥 Carteira Vendedor B (50%)")
    st.dataframe(df_vendedor_b, use_container_width=True)
    st.download_button("📥 Baixar Vendedor B", df_vendedor_b.to_csv(index=False).encode(),
                       "vendedor_b.csv", "text/csv")

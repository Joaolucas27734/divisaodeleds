import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# ============================
# CONFIG DA PLANILHA
# ============================
SHEET_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
SHEET_NAME = "Total"

# ============================
# CARREGAR PLANILHA
# ============================
@st.cache_data
def carregar_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
    df = pd.read_csv(url, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df

st.title("📊 Divisão 50/50 + Classificações por Aba")

df = carregar_sheet()

# ============================
# DATA = COLUNA A
# ============================
col_data = df.columns[0]
df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

min_date = df[col_data].min().date()
max_date = df[col_data].max().date()

st.write(f"📅 Período: **{min_date.strftime('%d/%m/%Y')} → {max_date.strftime('%d/%m/%Y')}**")

periodo = st.date_input(
    "Filtrar período",
    value=(min_date, max_date),
    format="DD/MM/YYYY"
)

df_filtrado = df[
    (df[col_data] >= pd.to_datetime(periodo[0])) &
    (df[col_data] <= pd.to_datetime(periodo[1]))
]

df_filtrado["Data (BR)"] = df_filtrado[col_data].dt.strftime("%d/%m/%Y")

# ============================
# CLASSIFICAÇÃO = COLUNA G
# ============================
col_classificacao = df.columns[6]
classificacoes_unicas = sorted(df_filtrado[col_classificacao].dropna().unique())

# ============================
# DIVISÃO 50/50
# ============================
vendedor_a_list = []
vendedor_b_list = []

for classificacao, grupo in df_filtrado.groupby(col_classificacao):
    grupo_embaralhado = grupo.sample(frac=1, random_state=42)
    metade = len(grupo_embaralhado) // 2

    vendedor_a_list.append(grupo_embaralhado.iloc[:metade])
    vendedor_b_list.append(grupo_embaralhado.iloc[metade:])

df_vendedor_a = pd.concat(vendedor_a_list).sort_values(col_data) if vendedor_a_list else pd.DataFrame()
df_vendedor_b = pd.concat(vendedor_b_list).sort_values(col_data) if vendedor_b_list else pd.DataFrame()

# ============================
# ABAS PRINCIPAIS
# ============================
aba_geral, aba_a, aba_b = st.tabs(["📄 Geral", "🟦 Vendedor A", "🟥 Vendedor B"])

# ----------------------------
# 🔵 ABA GERAL COM SUB-ABAS
# ----------------------------
with aba_geral:
    st.subheader("📄 Geral")

    sub_tabs = st.tabs(classificacoes_unicas)

    for i, classificacao in enumerate(classificacoes_unicas):
        with sub_tabs[i]:
            df_temp = df_filtrado[df_filtrado[col_classificacao] == classificacao]
            st.write(f"### {classificacao} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)

# ----------------------------
# 🟦 ABA VENDEDOR A
# ----------------------------
with aba_a:
    st.subheader("🟦 Vendedor A — 50% dos leads")

    sub_tabs_a = st.tabs(classificacoes_unicas)

    for i, classificacao in enumerate(classificacoes_unicas):
        with sub_tabs_a[i]:
            df_temp = df_vendedor_a[df_vendedor_a[col_classificacao] == classificacao]
            st.write(f"### {classificacao} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)

# ----------------------------
# 🟥 ABA VENDEDOR B
# ----------------------------
with aba_b:
    st.subheader("🟥 Vendedor B — 50% dos leads")

    sub_tabs_b = st.tabs(classificacoes_unicas)

    for i, classificacao in enumerate(classificacoes_unicas):
        with sub_tabs_b[i]:
            df_temp = df_vendedor_b[df_vendedor_b[col_classificacao] == classificacao]
            st.write(f"### {classificacao} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)

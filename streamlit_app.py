import streamlit as st
import pandas as pd
import unicodedata
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


st.title("📊 Divisão 50/50 + Classificações (Apenas 10 Primeiras Colunas)")

df = carregar_sheet()

# ============================
# PEGAR SOMENTE AS 10 PRIMEIRAS COLUNAS
# ============================
df = df.iloc[:, :8]

# ============================
# LIMPEZA DA CLASSIFICAÇÃO (COLUNA G = índice 6)
# ============================
def limpar_texto(x):
    if pd.isna(x) or str(x).strip() == "":
        return "Sem classificação"

    x = str(x)
    x = x.replace("\u200f", "").replace("\u200e", "")  # remove invisíveis
    x = x.strip()
    x = " ".join(x.split())

    # Normaliza acentos
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))

    return x.capitalize()

col_classificacao = df.columns[6]  # coluna G

df[col_classificacao] = df[col_classificacao].apply(limpar_texto)
classificacoes_unicas = sorted(df[col_classificacao].unique())

# ============================
# DATA (COLUNA A) — NÃO EXCLUI LEADS
# ============================
col_data = df.columns[0]
df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
df["Data (BR)"] = df[col_data].dt.strftime("%d/%m/%Y").fillna("Sem data")

# Filtro apenas VISUAL
min_date = df[col_data].min()
max_date = df[col_data].max()

st.write(f"📅 Período (visual): **{min_date.strftime('%d/%m/%Y')} → {max_date.strftime('%d/%m/%Y')}**")

periodo = st.date_input(
    "Período apenas para exibição",
    value=(min_date.date(), max_date.date()),
    format="DD/MM/YYYY"
)

df_visual = df[
    (df[col_data] >= pd.to_datetime(periodo[0])) &
    (df[col_data] <= pd.to_datetime(periodo[1]))
].copy()

# ============================
# DIVISÃO 50/50 (TODOS OS LEADS)
# ============================
vendedor_a_list = []
vendedor_b_list = []

for classificacao, grupo in df.groupby(col_classificacao):
    grupo_embaralhado = grupo.sample(frac=1, random_state=42)
    metade = len(grupo_embaralhado) // 2

    vendedor_a_list.append(grupo_embaralhado.iloc[:metade])
    vendedor_b_list.append(grupo_embaralhado.iloc[metade:])

df_vendedor_a = pd.concat(vendedor_a_list).sort_values(col_data)
df_vendedor_b = pd.concat(vendedor_b_list).sort_values(col_data)

# ============================
# ABAS PRINCIPAIS
# ============================
aba_geral, aba_a, aba_b = st.tabs([
    "🗂️ Geral",
    "🟦 Vendedor A",
    "🟥 Vendedor B"
])

# -------------------------------------------------------
# 🗂️ ABA GERAL (UNIFICADA)
# -------------------------------------------------------
with aba_geral:
    st.subheader("🗂️ Geral — Visual + Classificações")

    sub_tabs_geral = st.tabs(["📚 Geralzona", "📄 Por Classificação"])

    # ---- Geralzona ----
    with sub_tabs_geral[0]:
        st.write("### 📚 Geralzona — Todos os Leads Filtrados (Visual)")
        st.write(f"Total exibido: **{len(df_visual)}**")
        st.dataframe(df_visual, use_container_width=True)

    # ---- Por Classificação ----
    with sub_tabs_geral[1]:
        st.write("### 📄 Geral por Classificação")

        sub_class_tabs = st.tabs(classificacoes_unicas)

        for i, classificacao in enumerate(classificacoes_unicas):
            with sub_class_tabs[i]:
                df_temp = df[df[col_classificacao] == classificacao]
                st.write(f"### {classificacao} — {len(df_temp)} registros")
                st.dataframe(df_temp, use_container_width=True)

# -------------------------------------------------------
# 🟦 VENDEDOR A
# -------------------------------------------------------
with aba_a:
    st.subheader("🟦 Vendedor A — 50% dos Leads")

    classificacoes_a = ["GERAL"] + classificacoes_unicas
    sub_tabs_a = st.tabs(classificacoes_a)

    for i, classificacao in enumerate(classificacoes_a):
        with sub_tabs_a[i]:

            if classificacao == "GERAL":
                df_temp = df_vendedor_a
                st.write(f"### Geral — {len(df_temp)} registros")
            else:
                df_temp = df_vendedor_a[df_vendedor_a[col_classificacao] == classificacao]
                st.write(f"### {classificacao} — {len(df_temp)} registros")

            st.dataframe(df_temp, use_container_width=True)

# -------------------------------------------------------
# 🟥 VENDEDOR B
# -------------------------------------------------------
with aba_b:
    st.subheader("🟥 Vendedor B — 50% dos Leads")

    classificacoes_b = ["GERAL"] + classificacoes_unicas
    sub_tabs_b = st.tabs(classificacoes_b)

    for i, classificacao in enumerate(classificacoes_b):
        with sub_tabs_b[i]:

            if classificacao == "GERAL":
                df_temp = df_vendedor_b
                st.write(f"### Geral — {len(df_temp)} registros")
            else:
                df_temp = df_vendedor_b[df_vendedor_b[col_classificacao] == classificacao]
                st.write(f"### {classificacao} — {len(df_temp)} registros")

            st.dataframe(df_temp, use_container_width=True)

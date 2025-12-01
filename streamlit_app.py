import streamlit as st
import pandas as pd
import unicodedata
from urllib.parse import quote
from datetime import datetime, timedelta

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# =====================================================
# CARREGAR PLANILHA
# =====================================================
SHEET_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
SHEET_NAME = "Total"

@st.cache_data
def carregar_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
    df = pd.read_csv(url, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df

df = carregar_sheet()
df = df.iloc[:, :7]  # usa 7 colunas

# =====================================================
# LIMPAR CLASSIFICAÇÃO
# =====================================================
def limpar_texto(x):
    if pd.isna(x) or str(x).strip() == "":
        return "Sem classificação"
    x = str(x).replace("\u200f","").replace("\u200e","").strip()
    x = " ".join(x.split())
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))
    return x.capitalize()

col_classificacao = df.columns[6]
df[col_classificacao] = df[col_classificacao].apply(limpar_texto)
classificacoes = sorted(df[col_classificacao].unique())

# =====================================================
# TRATAR DATA
# =====================================================
col_data = df.columns[0]

def tentar_converter(x):
    if pd.isna(x):
        return pd.NaT
    x = str(x).strip()
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return pd.to_datetime(x, format=fmt)
        except:
            pass
    return pd.NaT

df["Data_Convertida"] = df[col_data].apply(tentar_converter)
df["Data (BR)"] = df["Data_Convertida"].dt.strftime("%d/%m/%Y").fillna("Sem data")

# =====================================================
# PÁGINAS
# =====================================================
st.sidebar.title("📑 Navegação")
pagina = st.sidebar.radio("Escolha a página:", ["Geral", "Vendedor A", "Vendedor B"])

# =====================================================
# SELETOR DE DATA (STREAMLIT PURO)
# =====================================================
st.sidebar.subheader("📅 Filtro de Data")

hoje = datetime.today().date()

preset = st.sidebar.selectbox(
    "Período:",
    [
        "Últimos 30 dias",
        "Últimos 7 dias",
        "Últimos 14 dias",
        "Ontem",
        "Hoje",
        "Este mês",
        "Mês passado",
        "Personalizado"
    ]
)

def calcular_periodo():
    if preset == "Hoje":
        return hoje, hoje
    if preset == "Ontem":
        return hoje - timedelta(days=1), hoje - timedelta(days=1)
    if preset == "Últimos 7 dias":
        return hoje - timedelta(days=7), hoje
    if preset == "Últimos 14 dias":
        return hoje - timedelta(days=14), hoje
    if preset == "Últimos 30 dias":
        return hoje - timedelta(days=30), hoje
    if preset == "Este mês":
        return hoje.replace(day=1), hoje
    if preset == "Mês passado":
        fim = hoje.replace(day=1) - timedelta(days=1)
        inicio = fim.replace(day=1)
        return inicio, fim
    return None

if preset != "Personalizado":
    inicio, fim = calcular_periodo()
else:
    inicio, fim = st.sidebar.date_input(
        "Escolha o intervalo:",
        value=(hoje - timedelta(days=30), hoje),
        format="DD/MM/YYYY"
    )

df_visual = df[
    (df["Data_Convertida"] >= pd.to_datetime(inicio)) &
    (df["Data_Convertida"] <= pd.to_datetime(fim))
]

# =====================================================
# DIVISÃO 50/50
# =====================================================
vendedor_a_list = []
vendedor_b_list = []

for classif, grupo in df.groupby(col_classificacao):
    grupo = grupo.sample(frac=1, random_state=42)
    metade = len(grupo) // 2
    vendedor_a_list.append(grupo.iloc[:metade])
    vendedor_b_list.append(grupo.iloc[metade:])

df_a = pd.concat(vendedor_a_list)
df_b = pd.concat(vendedor_b_list)

# =====================================================
# PÁGINA: GERAL
# =====================================================
if pagina == "Geral":
    st.title("📁 Página Geral")
    aba1, aba2 = st.tabs(["📚 Geralzona", "📄 Por Classificação"])

    with aba1:
        st.subheader("📚 Geralzona (Filtrada)")
        st.write(f"Total: **{len(df_visual)}**")
        st.dataframe(df_visual, use_container_width=True)

    with aba2:
        abas = st.tabs(classificacoes)
        for i, classif in enumerate(classificacoes):
            dft = df_visual[df_visual[col_classificacao] == classif]
            with abas[i]:
                st.write(f"### {classif} — {len(dft)}")
                st.dataframe(dft, use_container_width=True)

# =====================================================
# PÁGINA: VENDEDOR A
# =====================================================
elif pagina == "Vendedor A":
    st.title("🟦 Vendedor A — 50%")
    abas = st.tabs(["GERAL"] + classificacoes)

    for i, classif in enumerate(["GERAL"] + classificacoes):
        if classif == "GERAL":
            dft = df_a
        else:
            dft = df_a[df_a[col_classificacao] == classif]
        with abas[i]:
            st.write(f"### {classif} — {len(dft)}")
            st.dataframe(dft, use_container_width=True)

# =====================================================
# PÁGINA: VENDEDOR B
# =====================================================
elif pagina == "Vendedor B":
    st.title("🟥 Vendedor B — 50%")
    abas = st.tabs(["GERAL"] + classificacoes)

    for i, classif in enumerate(["GERAL"] + classificacoes):
        if classif == "GERAL":
            dft = df_b
        else:
            dft = df_b[df_b[col_classificacao] == classif]
        with abas[i]:
            st.write(f"### {classif} — {len(dft)}")
            st.dataframe(dft, use_container_width=True)

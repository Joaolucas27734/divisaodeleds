import streamlit as st
import pandas as pd
import unicodedata
from urllib.parse import quote

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# =====================================================
# CONFIG / LOAD SHEET
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
df = df.iloc[:, :7]  # usar somente 7 colunas


# =====================================================
# LIMPEZA DA CLASSIFICAÇÃO (coluna G = índice 6)
# =====================================================
def limpar_texto(x):
    if pd.isna(x) or str(x).strip() == "":
        return "Sem classificação"
    x = str(x)
    x = x.replace("\u200f", "").replace("\u200e", "")  
    x = x.strip()
    x = " ".join(x.split())
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))
    return x.capitalize()

col_classificacao = df.columns[6]
df[col_classificacao] = df[col_classificacao].apply(limpar_texto)
classificacoes = sorted(df[col_classificacao].unique())

# =====================================================
# DATA VISUAL (coluna A)
# =====================================================
col_data = df.columns[0]
df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
df["Data (BR)"] = df[col_data].dt.strftime("%d/%m/%Y").fillna("Sem data")

min_date = df[col_data].min()
max_date = df[col_data].max()

st.sidebar.title("📑 Menu de Navegação")
pagina = st.sidebar.radio(
    "Escolha a página:",
    ["Geral", "Vendedor A", "Vendedor B"]
)

# Filtro visual
periodo = st.sidebar.date_input(
    "Filtro de período (VISUAL):",
    value=(min_date.date(), max_date.date()),
    format="DD/MM/YYYY"
)

df_visual = df[
    (df[col_data] >= pd.to_datetime(periodo[0])) &
    (df[col_data] <= pd.to_datetime(periodo[1]))
].copy()

# =====================================================
# DIVISÃO 50/50 (todos os leads)
# =====================================================
vendedor_a_list, vendedor_b_list = [], []

for c, grupo in df.groupby(col_classificacao):
    grupo = grupo.sample(frac=1, random_state=42)
    metade = len(grupo) // 2
    vendedor_a_list.append(grupo.iloc[:metade])
    vendedor_b_list.append(grupo.iloc[metade:])

df_a = pd.concat(vendedor_a_list).sort_values(col_data)
df_b = pd.concat(vendedor_b_list).sort_values(col_data)

# =====================================================
# PÁGINA: GERAL
# =====================================================
if pagina == "Geral":
    st.title("🗂️ Página Geral")

    tabs = st.tabs(["📚 Geralzona", "📄 Por Classificação"])

    # GERALZONA
    with tabs[0]:
        st.subheader("📚 Geralzona (VISUAL)")
        st.write(f"Total exibido: **{len(df_visual)}**")
        st.dataframe(df_visual, use_container_width=True)

    # POR CLASSIFICAÇÃO
    with tabs[1]:
        st.subheader("📄 Por Classificação")

        sub_tabs = st.tabs(classificacoes)

        for i, classif in enumerate(classificacoes):
            with sub_tabs[i]:
                df_temp = df[df[col_classificacao] == classif]
                st.write(f"### {classif} — {len(df_temp)} registros")
                st.dataframe(df_temp, use_container_width=True)


# =====================================================
# PÁGINA: VENDEDOR A
# =====================================================
elif pagina == "Vendedor A":
    st.title("🟦 Vendedor A")

    classifs_a = ["GERAL"] + classificacoes
    tabs = st.tabs(classifs_a)

    for i, classif in enumerate(classifs_a):
        with tabs[i]:
            if classif == "GERAL":
                df_temp = df_a
            else:
                df_temp = df_a[df_a[col_classificacao] == classif]

            st.write(f"### {classif} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)


# =====================================================
# PÁGINA: VENDEDOR B
# =====================================================
elif pagina == "Vendedor B":
    st.title("🟥 Vendedor B")

    classifs_b = ["GERAL"] + classificacoes
    tabs = st.tabs(classifs_b)

    for i, classif in enumerate(classifs_b):
        with tabs[i]:
            if classif == "GERAL":
                df_temp = df_b
            else:
                df_temp = df_b[df_b[col_classificacao] == classif]

            st.write(f"### {classif} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)

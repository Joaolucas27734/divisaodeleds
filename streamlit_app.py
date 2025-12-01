import streamlit as st
import pandas as pd
import unicodedata
from urllib.parse import quote

st.set_page_config(page_title="Divisão 50/50", layout="wide")

# =====================================================
# CONFIG / CARREGAR PLANILHA
# =====================================================
SHEET_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
SHEET_NAME = "Total"

@st.cache_data
def carregar_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
    df = pd.read_csv(url, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df

# Carrega planilha e limita a 7 colunas
df = carregar_sheet()
df = df.iloc[:, :7]  # usa só as 7 primeiras colunas

# =====================================================
# LIMPAR CLASSIFICAÇÃO (COLUNA G = índice 6)
# =====================================================
def limpar_texto(x):
    if pd.isna(x) or str(x).strip() == "":
        return "Sem classificação"

    x = str(x)
    x = x.replace("\u200f", "").replace("\u200e", "")  # invisíveis
    x = x.strip()
    x = " ".join(x.split())  # espaços duplos -> simples

    # Normaliza acentos
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))

    return x.capitalize()

col_classificacao = df.columns[6]
df[col_classificacao] = df[col_classificacao].apply(limpar_texto)
classificacoes = sorted(df[col_classificacao].unique())

# =====================================================
# TRATAR DATA (COLUNA A) SÓ PRA ORDENAR / EXIBIR
# =====================================================
col_data = df.columns[0]

def tentar_converter_data(x):
    if pd.isna(x):
        return pd.NaT
    x = str(x).strip()
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]
    for fmt in formatos:
        try:
            return pd.to_datetime(x, format=fmt)
        except Exception:
            continue
    return pd.NaT

df["Data_Convertida"] = df[col_data].apply(tentar_converter_data)
df["Data (BR)"] = df["Data_Convertida"].dt.strftime("%d/%m/%Y").fillna("Sem data")

# =====================================================
# MENU LATERAL (PÁGINAS)
# =====================================================
st.sidebar.title("📑 Navegação")

pagina = st.sidebar.radio(
    "Escolha a página:",
    ["Geral", "Vendedor A", "Vendedor B"]
)

# =====================================================
# DIVISÃO 50/50 (POR CLASSIFICAÇÃO, USANDO TODOS OS LEADS)
# =====================================================
vendedor_a_list = []
vendedor_b_list = []

for classif, grupo in df.groupby(col_classificacao):
    grupo = grupo.sample(frac=1, random_state=42)  # embaralha
    metade = len(grupo) // 2
    vendedor_a_list.append(grupo.iloc[:metade])
    vendedor_b_list.append(grupo.iloc[metade:])

df_a = pd.concat(vendedor_a_list).sort_values("Data_Convertida")
df_b = pd.concat(vendedor_b_list).sort_values("Data_Convertida")

# =====================================================
# PÁGINA: GERAL
# =====================================================
if pagina == "Geral":
    st.title("📁 Página Geral")

    aba1, aba2 = st.tabs(["📚 Geralzona", "📄 Por Classificação"])

    # --------------- Geralzona ----------------------
    with aba1:
        st.subheader("📚 Geralzona (Todos os registros)")
        st.write(f"Total exibido: **{len(df)}**")
        st.dataframe(df, use_container_width=True)

    # --------------- Por Classificação --------------
    with aba2:
        st.subheader("📄 Geral por Classificação")
        abas_class = st.tabs(classificacoes)

        for i, classif in enumerate(classificacoes):
            with abas_class[i]:
                df_temp = df[df[col_classificacao] == classif]
                st.write(f"### {classif} — {len(df_temp)} registros")
                st.dataframe(df_temp, use_container_width=True)

# =====================================================
# PÁGINA: VENDEDOR A
# =====================================================
elif pagina == "Vendedor A":
    st.title("🟦 Vendedor A — 50% dos Leads")
    abas = st.tabs(["GERAL"] + classificacoes)

    for i, classif in enumerate(["GERAL"] + classificacoes):
        with abas[i]:
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
    st.title("🟥 Vendedor B — 50% dos Leads")
    abas = st.tabs(["GERAL"] + classificacoes)

    for i, classif in enumerate(["GERAL"] + classificacoes):
        with abas[i]:
            if classif == "GERAL":
                df_temp = df_b
            else:
                df_temp = df_b[df_b[col_classificacao] == classif]

            st.write(f"### {classif} — {len(df_temp)} registros")
            st.dataframe(df_temp, use_container_width=True)

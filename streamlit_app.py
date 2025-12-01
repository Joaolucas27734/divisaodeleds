# streamlit_app.py
import streamlit as st
import pandas as pd
import time
from urllib.parse import quote

# ------------------------------
# ⚙️ Configuração da página
# ------------------------------
st.set_page_config(page_title="Conexão com Planilha 2", page_icon="📊", layout="wide")

# ------------------------------
# 🔗 ID da Planilha 2
# ------------------------------
SHEET2_ID = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"
DEFAULT_SHEET2_SHEETNAME = "Total"

# ==============================
# 🧩 Função utilitária
# ==============================
@st.cache_data(ttl=120)
def carregar_csv(url: str) -> pd.DataFrame:
    """Carrega CSV remoto de forma simples."""
    df = pd.read_csv(
        url,
        sep=",",
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8",
        na_values=["", "NA", "NaN", None],
    )
    df.columns = [str(c).strip() for c in df.columns]
    return df

# ==============================
# 🧭 Sidebar / Controles
# ==============================
st.sidebar.title("⚙️ Controles")

sheet2_sheetname = st.sidebar.text_input(
    "📄 Nome da aba (Planilha 2)",
    value=DEFAULT_SHEET2_SHEETNAME,
    help="Tem que ser exatamente como aparece na guia do Google Sheets",
)

# Gera a URL baseada na aba digitada
SHEET_URL_2 = f"https://docs.google.com/spreadsheets/d/{SHEET2_ID}/gviz/tq?tqx=out:csv&sheet={quote(sheet2_sheetname)}"

# Botão de atualizar
if st.sidebar.button("🔄 Atualizar dados agora"):
    st.cache_data.clear()
    time.sleep(0.3)
    st.rerun()

st.sidebar.success(f"✅ Dados atualizados às {time.strftime('%H:%M:%S')}")

# ==============================
# 📥 Carregamento da Planilha 2
# ==============================
st.title("Planilha 2 — Conexão e Prévia")

with st.spinner("Carregando Planilha 2…"):
    try:
        df2 = carregar_csv(SHEET_URL_2)
        st.success(f"Planilha carregada com sucesso! (aba: {sheet2_sheetname})")

        st.caption("Prévia (primeiras 50 linhas):")
        st.dataframe(df2.head(50), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar Planilha 2: {e}")
        df2 = pd.DataFrame()

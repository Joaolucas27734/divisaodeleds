import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURAÇÕES DO DASHBOARD
# --------------------------------------------------

st.set_page_config(page_title="Dashboard de Separação de LEDs", layout="wide")
st.title("🔦 Dashboard de Separação dos LEDs (Google Sheets)")

# --------------------------------------------------
# LER PLANILHA DO GOOGLE SHEETS
# --------------------------------------------------

# ID da sua planilha (já peguei da URL que você enviou)
sheet_id = "1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc"

# Nome da aba — se tiver outra, só trocar aqui
sheet_name = "Página1"   # mude para o nome exato da aba

# Link para exportar a aba em CSV (compatível com pandas)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Ler a planilha
df = pd.read_csv(url)

st.subheader("📄 Dados carregados da Planilha")
st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# SEÇÃO DE TOTALIZAÇÃO
# --------------------------------------------------

if "Classificação A" in df.columns and "Classificação B" in df.columns:
    st.subheader("📈 Totais")

    col1, col2, col3 = st.columns(3)

    total_A = df["Classificação A"].sum()
    total_B = df["Classificação B"].sum()
    total_geral = total_A + total_B

    col1.metric("Total Classificação A", int(total_A))
    col2.metric("Total Classificação B", int(total_B))
    col3.metric("Total Geral", int(total_geral))
else:
    st.error("As colunas 'Classificação A' e 'Classificação B' não foram encontradas na planilha.")

# --------------------------------------------------
# EXPORTAR OS DADOS
# --------------------------------------------------

st.subheader("📤 Exportar Dados Processados")

csv_data = df.to_csv(index=False)

st.download_button(
    label="Baixar CSV",
    data=csv_data,
    file_name="dados_leds.csv",
    mime="text/csv"
)

st.write("---")
st.caption("Dashboard conectado ao Google Sheets — totalmente automático.")

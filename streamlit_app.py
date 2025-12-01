import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Separação de LEDs", layout="wide")

st.title("🔦 Dashboard de Separação dos LEDs")

# Criar dataframe inicial
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Divisão": [f"Divisão {i+1}" for i in range(6)],
        "Classificação A": [0]*6,
        "Classificação B": [0]*6
    })

st.subheader("📊 Tabela de Controle")

st.session_state.df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
)

st.subheader("📈 Totais")
col1, col2, col3 = st.columns(3)

col1.metric("Total Classificação A", int(st.session_state.df["Classificação A"].sum()))
col2.metric("Total Classificação B", int(st.session_state.df["Classificação B"].sum()))
col3.metric("Total Geral", int(st.session_state.df["Classificação A"].sum() + st.session_state.df["Classificação B"].sum()))

st.subheader("📤 Exportar Dados")
if st.button("Baixar CSV"):
    st.download_button(
        label="Clique para baixar",
        data=st.session_state.df.to_csv(index=False),
        file_name="dashboard_leds.csv",
        mime="text/csv"
    )

st.write("---")
st.caption("Desenvolvido para organização da separação de LEDs.")

import streamlit as st

st.set_page_config(page_title="Planilha", layout="wide")

st.title("📄 Planilha conectada")

sheet_url = "https://docs.google.com/spreadsheets/d/1UD2_Q9oua4OCqYls-Is4zVKwTc9LjucLjPUgmVmyLBc/edit?usp=sharing"

st.components.v1.iframe(sheet_url, height=800)

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="TB4 Data Visualization",
    layout="wide"
)

st.title("TB4 — Data Visualization")
st.write("Dashboard interactivo de energía y sostenibilidad.")

st.info("Primera versión del dashboard. Aquí se cargarán los datos integrados.")
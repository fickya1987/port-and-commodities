import streamlit as st
import pandas as pd
import os
import openai
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Upload Data File
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Format file tidak didukung. Silakan unggah file CSV atau Excel.")
        return None
    
    # Konversi kolom numerik otomatis
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
    return df

# App Title
st.title("Visualisasi dan Analisis Data Komoditas Pelabuhan")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Unggah File CSV atau Excel", type=["csv", "xlsx"])
if uploaded_file:
    data = load_data(uploaded_file)
else:
    st.warning("Harap unggah file data terlebih dahulu.")
    st.stop()

# Sidebar Menu
st.sidebar.header("Pengaturan Visualisasi")

# Pilihan Pelabuhan, JenisKomoditi, dan Kategori
pelabuhan_filter = st.sidebar.multiselect(
    "Filter Pelabuhan",
    options=data['Pelabuhan'].unique(),
    default=data['Pelabuhan'].unique()
)
jenis_komoditi_filter = st.sidebar.multiselect(
    "Filter Jenis Komoditi",
    options=data['JenisKomoditi'].unique(),
    default=data['JenisKomoditi'].unique()
)
kategori_filter = st.sidebar.multiselect(
    "Filter Kategori",
    options=data['Kategori'].unique(),
    default=data['Kategori'].unique()
)

# Filter Data
filtered_data = data[
    (data['Pelabuhan'].isin(pelabuhan_filter)) &
    (data['JenisKomoditi'].isin(jenis_komoditi_filter)) &
    (data['Kategori'].isin(kategori_filter))
]

# Dropdown pilihan untuk jenis visualisasi
chart_type = st.sidebar.selectbox(
    "Pilih Jenis Visualisasi", 
    [
        "Bar Chart", "Line Chart", "Pie Chart", "Treemap", "Bubble Chart", "Heatmap", "Sunburst Chart", "Radar Chart"
    ]
)

# Pilih kolom data untuk visualisasi
y_axis = st.sidebar.selectbox(
    "Pilih Kolom Y-Axis", 
    [
        "DomestikBongkar2023", "DomestikMuat2023", "Impor2023", "Ekspor2023",
        "DomestikBongkar2022", "DomestikMuat2022", "Impor2022", "Ekspor2022",
        "DomestikBongkar2021", "DomestikMuat2021", "Impor2021", "Ekspor2021",
        "DomestikBongkar2020", "DomestikMuat2020", "Impor2020", "Ekspor2020"
    ]
)

# Konversi nilai kolom y_axis ke numerik
filtered_data[y_axis] = pd.to_numeric(filtered_data[y_axis], errors='coerce')
filtered_data = filtered_data.dropna(subset=[y_axis])

# Menampilkan data
if st.checkbox("Lihat Data Komoditas"):
    st.write(filtered_data)

# Visualisasi Data
st.header("Visualisasi Data")
if chart_type == "Bar Chart":
    fig = px.bar(
        filtered_data, 
        x="Komoditi", 
        y=y_axis, 
        color="Pelabuhan", 
        barmode="group", 
        title="Bar Chart Berdasarkan Pelabuhan dan Kategori",
        text_auto=True
    )
elif chart_type == "Radar Chart":
    categories = ["DomestikBongkar2023", "DomestikMuat2023", "Impor2023", "Ekspor2023"]
    radar_data = filtered_data.groupby('Pelabuhan')[categories].sum().reset_index()
    
    fig = go.Figure()
    for _, row in radar_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=row[categories].values,
            theta=categories,
            fill='toself',
            name=row['Pelabuhan']
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Radar Chart Berdasarkan Kategori Data untuk Setiap Pelabuhan"
    )
elif chart_type == "Treemap":
    fig = px.treemap(
        filtered_data, 
        path=["Pelabuhan", "Kategori", "JenisKomoditi", "Komoditi"], 
        values=y_axis, 
        title="Treemap Berdasarkan Pelabuhan, Kategori, dan Jenis Komoditi"
    )
elif chart_type == "Bubble Chart":
    fig = px.scatter(
        filtered_data, 
        x="Komoditi", 
        y=y_axis, 
        size=y_axis, 
        color="Pelabuhan", 
        hover_data=["Kategori"],
        title="Bubble Chart Berdasarkan Pelabuhan dan Kategori"
    )
elif chart_type == "Sunburst Chart":
    fig = px.sunburst(
        filtered_data, 
        path=["Pelabuhan", "Kategori", "JenisKomoditi", "Komoditi"], 
        values=y_axis, 
        title="Sunburst Chart Berdasarkan Pelabuhan dan Kategori"
    )
else:
    st.warning("Pilih tipe chart yang valid")

# Tampilkan visualisasi
st.plotly_chart(fig, use_container_width=True)



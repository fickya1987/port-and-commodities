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
    
    # Bersihkan header kolom
    df.columns = df.columns.str.strip()
    
    # Bersihkan dan konversi kolom numerik
    for col in df.columns:
        if df[col].dtype == 'object':  # Konversi hanya kolom object
            try:
                df[col] = pd.to_numeric(df[col].str.replace(',', '').str.strip(), errors='coerce')
            except Exception as e:
                print(f"Kolom '{col}' tidak dapat dikonversi: {e}")
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
    options=data['Pelabuhan'].dropna().unique(),
    default=data['Pelabuhan'].dropna().unique()
)
jenis_komoditi_filter = st.sidebar.multiselect(
    "Filter Jenis Komoditi",
    options=data['JenisKomoditi'].dropna().unique(),
    default=data['JenisKomoditi'].dropna().unique()
)
kategori_filter = st.sidebar.multiselect(
    "Filter Kategori",
    options=data['Kategori'].dropna().unique(),
    default=data['Kategori'].dropna().unique()
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
    radar_data = filtered_data.groupby('Pelabuhan')[categories].mean().reset_index()

    fig = go.Figure()
    for _, row in radar_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=row[categories].values,
            theta=categories,
            fill='toself',
            name=row['Pelabuhan']
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, radar_data[categories].max().max()])),
        title="Radar Chart Berdasarkan Kategori Data untuk Setiap Pelabuhan"
    )
elif chart_type == "Heatmap":
    heatmap_data = filtered_data.pivot_table(index="Pelabuhan", columns="Kategori", values=y_axis, aggfunc='sum', fill_value=0)
    fig = px.imshow(heatmap_data, title="Heatmap Berdasarkan Pelabuhan dan Kategori")
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
if 'fig' in locals():
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Visualisasi tidak dapat ditampilkan. Silakan periksa pengaturan Anda.")


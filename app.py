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
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Format file tidak didukung. Silakan unggah file CSV atau Excel.")
        return None

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
        "Bar Chart", "Line Chart", "Pie Chart", "Treemap", "Bubble Chart", "Heatmap", "Sunburst Chart", "Scatter Matrix", "Density Contour"
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
elif chart_type == "Line Chart":
    fig = px.line(
        filtered_data, 
        x="Komoditi", 
        y=y_axis, 
        color="Pelabuhan", 
        markers=True, 
        title="Line Chart Berdasarkan Pelabuhan"
    )
elif chart_type == "Pie Chart":
    fig = px.pie(
        filtered_data, 
        names="Pelabuhan", 
        values=y_axis, 
        title="Distribusi Data Berdasarkan Pelabuhan"
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
elif chart_type == "Heatmap":
    pivot_data = filtered_data.pivot_table(index="Pelabuhan", columns="Kategori", values=y_axis, aggfunc='sum', fill_value=0)
    fig = px.imshow(pivot_data, title="Heatmap Berdasarkan Pelabuhan dan Kategori")
elif chart_type == "Sunburst Chart":
    fig = px.sunburst(
        filtered_data, 
        path=["Pelabuhan", "Kategori", "JenisKomoditi", "Komoditi"], 
        values=y_axis, 
        title="Sunburst Chart Berdasarkan Pelabuhan dan Kategori"
    )
elif chart_type == "Scatter Matrix":
    fig = px.scatter_matrix(
        filtered_data, 
        dimensions=["DomestikBongkar2023", "DomestikMuat2023", "Ekspor2023", "Impor2023"],
        color="Pelabuhan",
        title="Scatter Matrix untuk Kolom Terpilih"
    )
elif chart_type == "Density Contour":
    fig = px.density_contour(
        filtered_data, 
        x="Komoditi", 
        y=y_axis, 
        title="Density Contour Berdasarkan Komoditi dan Y-Axis"
    )
else:
    st.warning("Pilih tipe chart yang valid")

# Tampilkan visualisasi
st.plotly_chart(fig, use_container_width=True)

# Fitur Analisis dengan GPT-4o
st.header("Analisis Data Menggunakan GPT-4o")
user_query = st.text_area("Masukkan Pertanyaan Berdasarkan Data Anda")

def ask_gpt4o(question, context):
    """Fungsi untuk memanggil GPT-4o API"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Anda adalah asisten data scientist yang menganalisis data komoditas pelabuhan."},
            {"role": "user", "content": f"Data: {context}\nPertanyaan: {question}"}
        ],
        max_tokens=2048,
        temperature=1.0
    )
    return response["choices"][0]["message"]["content"]

if st.button("Analisa dengan GPT-4o"):
    if user_query:
        # Convert data to string context
        data_context = filtered_data.head(100).to_string()
        with st.spinner("Menganalisis dengan GPT-4o..."):
            result = ask_gpt4o(user_query, data_context)
        st.subheader("Hasil Analisis:")
        st.write(result)
    else:
        st.warning("Silakan masukkan pertanyaan terlebih dahulu")

st.sidebar.info("Dibuat oleh AI dengan GPT-4o untuk analisis data interaktif.")



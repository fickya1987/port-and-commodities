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

# Dropdown pilihan untuk jenis visualisasi
chart_type = st.sidebar.selectbox(
    "Pilih Jenis Visualisasi", 
    [
        "Line Chart", "Bar Chart", "Scatter Plot", "Pie Chart", "Heatmap",
        "Histogram", "Box Plot", "Area Chart", "Treemap", "Bubble Chart"
    ]
)

# Pilih kolom data untuk visualisasi
x_axis = st.sidebar.selectbox("Pilih Kolom X-Axis", data.columns)
y_axis = st.sidebar.selectbox("Pilih Kolom Y-Axis", data.columns)

# Menampilkan data
if st.checkbox("Lihat Data Komoditas"):
    st.write(data)

# Visualisasi Data
st.header("Visualisasi Data")
if chart_type == "Line Chart":
    fig = px.line(data, x=x_axis, y=y_axis, title="Line Chart")
elif chart_type == "Bar Chart":
    fig = px.bar(data, x=x_axis, y=y_axis, title="Bar Chart")
elif chart_type == "Scatter Plot":
    fig = px.scatter(data, x=x_axis, y=y_axis, title="Scatter Plot")
elif chart_type == "Pie Chart":
    fig = px.pie(data, names=x_axis, values=y_axis, title="Pie Chart")
elif chart_type == "Heatmap":
    pivot_data = data.pivot_table(index=x_axis, columns=y_axis, aggfunc='size', fill_value=0)
    fig = px.imshow(pivot_data, title="Heatmap")
elif chart_type == "Histogram":
    fig = px.histogram(data, x=x_axis, title="Histogram")
elif chart_type == "Box Plot":
    fig = px.box(data, x=x_axis, y=y_axis, title="Box Plot")
elif chart_type == "Area Chart":
    fig = px.area(data, x=x_axis, y=y_axis, title="Area Chart")
elif chart_type == "Treemap":
    fig = px.treemap(data, path=[x_axis], values=y_axis, title="Treemap")
elif chart_type == "Bubble Chart":
    fig = px.scatter(data, x=x_axis, y=y_axis, size=y_axis, color=x_axis, title="Bubble Chart")
else:
    st.warning("Pilih tipe chart yang valid")

# Tampilkan visualisasi
st.plotly_chart(fig)

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
        ]
    )
    return response["choices"][0]["message"]["content"]

if st.button("Analisa dengan GPT-4o"):
    if user_query:
        # Convert data to string context
        data_context = data.head(100).to_string()
        with st.spinner("Menganalisis dengan GPT-4o..."):
            result = ask_gpt4o(user_query, data_context)
        st.subheader("Hasil Analisis:")
        st.write(result)
    else:
        st.warning("Silakan masukkan pertanyaan terlebih dahulu")

st.sidebar.info("Dibuat oleh AI dengan GPT-4o untuk analisis data interaktif.")

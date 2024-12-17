import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit page config
st.set_page_config(page_title="Pelabuhan Komoditas Dashboard", layout="wide")
st.title("Visualisasi dan Analisis Komoditas Pelabuhan")

# File uploader
uploaded_file = st.file_uploader("Unggah file CSV atau Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("Data berhasil diunggah!")
    
    # Quick preview
    st.subheader("Tampilan Data")
    st.dataframe(df.head())

    # Ensure numeric columns
    numeric_columns = [
        "DomestikBongkar2023", "DomestikMuat2023", "Impor2023", "Ekspor2023",
        "DomestikBongkar2022", "DomestikMuat2022", "Impor2022", "Ekspor2022",
        "DomestikBongkar2021", "DomestikMuat2021", "Impor2021", "Ekspor2021",
        "DomestikBongkar2020", "DomestikMuat2020", "Impor2020", "Ekspor2020"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Dropdown filter options
    selected_port = st.multiselect("Pilih Pelabuhan", df["Pelabuhan"].unique(), default=df["Pelabuhan"].unique())
    selected_category = st.multiselect("Pilih Kategori", df["Kategori"].unique(), default=df["Kategori"].unique())
    selected_type = st.multiselect("Pilih Jenis Komoditi", df["JenisKomoditi"].unique(), default=df["JenisKomoditi"].unique())
    
    # Filter data
    filtered_data = df[(df["Pelabuhan"].isin(selected_port)) &
                       (df["Kategori"].isin(selected_category)) &
                       (df["JenisKomoditi"].isin(selected_type))]
    
    st.subheader("Data Terfilter")
    st.dataframe(filtered_data)

    # Chart Visualizations
    st.subheader("Visualisasi Data")

    # 1. Bar Chart - Domestik vs Ekspor/Impor
    st.plotly_chart(px.bar(filtered_data, x="Pelabuhan", y=["DomestikBongkar2023", "Ekspor2023", "Impor2023"],
                           color="Kategori", barmode="group", title="Perbandingan Domestik, Ekspor, dan Impor"))

    # 2. Pie Chart - Jenis Komoditi
    st.plotly_chart(px.pie(filtered_data, names="JenisKomoditi", title="Distribusi Jenis Komoditi"))

    # 3. Line Chart - Tren Domestik dari Tahun 2020-2023
    st.plotly_chart(px.line(filtered_data, x="Pelabuhan", y=["DomestikBongkar2020", "DomestikBongkar2021", 
                                                             "DomestikBongkar2022", "DomestikBongkar2023"],
                            color="Pelabuhan", title="Tren Domestik Bongkar"))

    # 4. Scatter Plot - Ekspor vs Impor
    st.plotly_chart(px.scatter(filtered_data, x="Ekspor2023", y="Impor2023", color="Kategori",
                               size="DomestikMuat2023", title="Ekspor vs Impor"))

    # 5. Heatmap - Korelasi Tahun ke Tahun
    st.plotly_chart(px.imshow(filtered_data.corr(), title="Korelasi Antar Kolom"))

    # 6. Histogram - Distribusi Domestik Muat
    st.plotly_chart(px.histogram(filtered_data, x="DomestikMuat2023", color="Pelabuhan", title="Distribusi Domestik Muat"))

    # 7. Area Chart - Kategori per Pelabuhan
    st.plotly_chart(px.area(filtered_data, x="Pelabuhan", y="DomestikBongkar2023", color="Kategori",
                            title="Domestik Bongkar per Kategori"))

    # 8. Boxplot - Distribusi Impor
    st.plotly_chart(px.box(filtered_data, x="Pelabuhan", y="Impor2023", color="JenisKomoditi",
                           title="Distribusi Impor"))

    # 9. Treemap - Hierarki Jenis Komoditi
    st.plotly_chart(px.treemap(filtered_data, path=["Pelabuhan", "JenisKomoditi"], values="DomestikMuat2023",
                               title="Treemap Jenis Komoditi"))

    # 10. Sunburst - Kategori dan Jenis Komoditi
    st.plotly_chart(px.sunburst(filtered_data, path=["Kategori", "JenisKomoditi"], values="Ekspor2023",
                                title="Kategori dan Jenis Komoditi"))

    # GPT-4o Integration
    st.subheader("Analisis Data dengan GPT-4o")
    user_query = st.text_area("Masukkan Pertanyaan Berdasarkan Data")

    if st.button("Kirim ke GPT-4o"):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah asisten data analyst yang menganalisa file CSV/Excel."},
                    {"role": "user", "content": f"Berikut data saya: {filtered_data.head(20).to_string()} \nPertanyaan saya: {user_query}"}
                ],
                max_tokens=2048,
                temperature=1.0
            )
            st.write(response["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

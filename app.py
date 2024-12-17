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

    # Exclude specific numeric columns from dropdown but still include in charts
    excluded_columns = [
        "DomestikBongkar2023", "DomestikMuat2023", "Impor2023", "Ekspor2023",
        "DomestikBongkar2022", "DomestikMuat2022", "Impor2022", "Ekspor2022",
        "DomestikBongkar2021", "DomestikMuat2021", "Impor2021", "Ekspor2021",
        "DomestikBongkar2020", "DomestikMuat2020", "Impor2020", "Ekspor2020"
    ]
    selectable_columns = [col for col in df.columns if col not in excluded_columns]

    # Convert all non-numeric columns to string
    for col in df.select_dtypes(exclude=['number']).columns:
        df[col] = df[col].astype(str)

    # Ensure numeric columns dynamically
    non_numeric_columns = df[selectable_columns].select_dtypes(exclude=['number']).columns.tolist()
    numeric_columns = df[selectable_columns].select_dtypes(include=['number']).columns.tolist()

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Dropdown for choosing columns dynamically
    selected_chart = st.selectbox(
        "Pilih Jenis Chart",
        [
            "Bar Chart", "Line Chart", "Scatter Plot"
        ]
    )

    # Filters
    st.subheader("Filter Data")
    selected_pelabuhan = st.multiselect("Pilih Pelabuhan", df['Pelabuhan'].unique(), default=df['Pelabuhan'].unique())
    selected_jenis = st.multiselect("Pilih Jenis Komoditas", df['JenisKomoditi'].unique(), default=df['JenisKomoditi'].unique())
    selected_kategori = st.multiselect("Pilih Kategori", df['Kategori'].unique(), default=df['Kategori'].unique())

    filtered_data = df[(df['Pelabuhan'].isin(selected_pelabuhan)) &
                       (df['JenisKomoditi'].isin(selected_jenis)) &
                       (df['Kategori'].isin(selected_kategori))]

    st.subheader("Data Terfilter")
    st.dataframe(filtered_data)

    # Prepare long-format data for comparison
    columns_to_melt = [
        "DomestikBongkar2023", "DomestikMuat2023", "Impor2023", "Ekspor2023",
        "DomestikBongkar2022", "DomestikMuat2022", "Impor2022", "Ekspor2022",
        "DomestikBongkar2021", "DomestikMuat2021", "Impor2021", "Ekspor2021",
        "DomestikBongkar2020", "DomestikMuat2020", "Impor2020", "Ekspor2020"
    ]

    melted_data = filtered_data.melt(id_vars=['Pelabuhan', 'JenisKomoditi', 'Kategori'], 
                                     value_vars=columns_to_melt, 
                                     var_name='Tahun', value_name='Jumlah')

    # Clean year column
    melted_data['Tahun'] = melted_data['Tahun'].str.extract('(\\d{4})')

    # Chart visualizations
    st.subheader("Visualisasi Data")
    if selected_chart == "Bar Chart":
        st.plotly_chart(
            px.bar(melted_data, x="Tahun", y="Jumlah", color="Pelabuhan", 
                   facet_col="JenisKomoditi", title="Perbandingan Data Ekspor/Impor dari 2020-2023")
        )
    elif selected_chart == "Line Chart":
        st.plotly_chart(
            px.line(melted_data, x="Tahun", y="Jumlah", color="Pelabuhan", 
                    line_group="JenisKomoditi", title="Tren Data Ekspor/Impor dari 2020-2023")
        )
    elif selected_chart == "Scatter Plot":
        st.plotly_chart(
            px.scatter(melted_data, x="Tahun", y="Jumlah", color="Pelabuhan", 
                       size="Jumlah", facet_col="Kategori", title="Distribusi Data Ekspor/Impor per Tahun")
        )

    # GPT-4o Integration
    st.subheader("Analisis Data dengan GPT-4o")
    st.write("### AI Data Analysis")
    analysis_type = st.radio("Pilih jenis analisis:", ["Analisis Berdasarkan Data", "Pencarian Detail GPT-4o"])
    analysis_query = st.text_area("Deskripsi analisis atau detail pencarian:")
    if st.button("Generate AI Analysis") and analysis_query:
        try:
            if analysis_type == "Analisis Berdasarkan Data":
                prompt = (
                    f"Berdasarkan dataset berikut, lakukan analisis mendalam tentang '{analysis_query}'.Gunakan bahasa Indonesia.Fokuskan analisis pada tren ekspor dan peluang untuk Indonesia:\n"
                    + filtered_data.to_csv(index=False)
                )
            else:
                prompt = (
                    f"Cari informasi lengkap tentang '{analysis_query}' yang relevan dengan data ekspor Indonesia. Tambahkan referensi sumber terpercaya."
                )

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah analis data berpengalaman. Gunakan bahasa Indonesia"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048,
                temperature=1.0
            )
            result = response['choices'][0]['message']['content']
            st.write("#### Hasil Analisis AI:")
            st.write(result)
        except Exception as e:
            st.error(f"Error generating analysis: {e}")

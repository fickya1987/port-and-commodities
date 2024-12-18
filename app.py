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
    try:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file, skip_blank_lines=True)
        else:
            df = pd.read_excel(uploaded_file)

        # Bersihkan header kolom
        df.columns = df.columns.str.strip()

        # Bersihkan data: Hapus baris kosong atau kolom yang berisi None
        df = df.dropna(how="all")  # Hapus baris kosong sepenuhnya
        df = df.dropna(axis=1, how="all")  # Hapus kolom kosong sepenuhnya

        # Ubah kolom object ke numerik jika mungkin
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col].str.replace(',', '').str.strip(), errors='ignore')

        st.success("Data berhasil diunggah!")
        st.dataframe(df.head())  # Tampilkan data hasil pembersihan
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
else:
    st.warning("Tidak ada file yang diunggah. Silakan unggah file CSV atau Excel.")



    # Clean column names
    df.columns = df.columns.str.strip()

    # Ensure numeric columns are cleaned and converted
    for col in df.columns:
        if df[col].dtype == 'object':  # Only convert object columns
            df[col] = pd.to_numeric(df[col].str.replace(',', '').str.strip(), errors='coerce')

    # Separate numeric and non-numeric columns
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    non_numeric_columns = df.select_dtypes(exclude='number').columns.tolist()

    # Quick preview
    st.subheader("Tampilan Data")
    st.dataframe(df.head())

    # Dropdown for choosing columns dynamically
    selected_x = st.selectbox("Pilih Kolom X", options=non_numeric_columns + numeric_columns)
    selected_y = st.selectbox("Pilih Kolom Y", options=numeric_columns)

    selected_chart = st.selectbox(
        "Pilih Jenis Chart",
        [
            "Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot", "Heatmap",
            "Histogram", "Area Chart", "Boxplot", "Treemap", "Sunburst"
        ]
    )

    # Filters
    st.subheader("Filter Data")
    filters = {}
    for col in non_numeric_columns:
        unique_vals = df[col].unique()
        selected_vals = st.multiselect(f"Pilih {col}", unique_vals, default=unique_vals)
        filters[col] = selected_vals

    filtered_data = df.copy()
    for col, vals in filters.items():
        filtered_data = filtered_data[filtered_data[col].isin(vals)]

    st.subheader("Data Terfilter")
    st.dataframe(filtered_data.head())

    # Chart visualizations
    st.subheader("Visualisasi Data")
    if selected_chart == "Bar Chart":
        st.plotly_chart(px.bar(filtered_data, x=selected_x, y=selected_y, barmode="group"))
    elif selected_chart == "Pie Chart":
        st.plotly_chart(px.pie(filtered_data, names=selected_x, values=selected_y))
    elif selected_chart == "Line Chart":
        st.plotly_chart(px.line(filtered_data, x=selected_x, y=selected_y))
    elif selected_chart == "Scatter Plot":
        st.plotly_chart(px.scatter(filtered_data, x=selected_x, y=selected_y, size=selected_y))
    elif selected_chart == "Heatmap":
        st.plotly_chart(px.imshow(filtered_data[numeric_columns].corr()))
    elif selected_chart == "Histogram":
        st.plotly_chart(px.histogram(filtered_data, x=selected_x))
    elif selected_chart == "Area Chart":
        st.plotly_chart(px.area(filtered_data, x=selected_x, y=selected_y))
    elif selected_chart == "Boxplot":
        st.plotly_chart(px.box(filtered_data, x=selected_x, y=selected_y))
    elif selected_chart == "Treemap":
        st.plotly_chart(px.treemap(filtered_data, path=[selected_x], values=selected_y))
    elif selected_chart == "Sunburst":
        st.plotly_chart(px.sunburst(filtered_data, path=[selected_x], values=selected_y))

    # GPT-4o Integration
    st.subheader("Analisis Data dengan GPT-4o")
    analysis_query = st.text_area("Deskripsi analisis atau detail pencarian:")
    if st.button("Generate AI Analysis") and analysis_query:
        try:
            prompt = f"Lakukan analisis mendalam tentang '{analysis_query}' berdasarkan data berikut:\n{filtered_data.to_csv(index=False)}"

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah analis data berpengalaman. Gunakan bahasa Indonesia."},
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

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

        # Bersihkan data: Hapus baris kosong atau kolom kosong
        df = df.dropna(how="all")  # Hapus baris kosong sepenuhnya
        df = df.dropna(axis=1, how="all")  # Hapus kolom kosong sepenuhnya

        # Ubah kolom object ke numerik jika memungkinkan
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col].str.replace(',', '').str.strip(), errors='ignore')

        # Pisahkan kolom numerik dan non-numerik
        numeric_columns = df.select_dtypes(include='number').columns.tolist()
        non_numeric_columns = df.select_dtypes(exclude='number').columns.tolist()

        # Tampilan Data
        st.subheader("Tampilan Data")
        st.dataframe(df.head())

        # Dropdown untuk memilih kolom
        selected_x = st.selectbox("Pilih Kolom X", options=non_numeric_columns + numeric_columns)
        selected_y = st.selectbox("Pilih Kolom Y", options=numeric_columns)

        # Pilihan Jenis Chart
        selected_chart = st.selectbox(
            "Pilih Jenis Chart",
            ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot", "Heatmap", 
             "Histogram", "Area Chart", "Boxplot", "Treemap", "Sunburst"]
        )

        # Filter Data
        st.subheader("Filter Data")
        filters = {}
        for col in non_numeric_columns:
            unique_vals = df[col].dropna().unique()
            selected_vals = st.multiselect(f"Pilih {col}", unique_vals, default=unique_vals)
            filters[col] = selected_vals

        # Terapkan filter
        filtered_data = df.copy()
        for col, vals in filters.items():
            filtered_data = filtered_data[filtered_data[col].isin(vals)]

        # Tampilkan Data Terfilter
        st.subheader("Data Terfilter")
        st.dataframe(filtered_data.head())

        # Visualisasi Data
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


  # GPT-4o Integration for Analysis
        st.subheader("Analisis Data dengan Pelindo AI")
        analysis_query = st.text_area("Deskripsi analisis atau detail pencarian:")
        if st.button("Pelindo AI") and analysis_query:
            try:
                # Analisis berdasarkan data
                prompt_data = f"Lakukan analisis mendalam tentang '{analysis_query}' berdasarkan data berikut:\n{filtered_data.to_csv(index=False)}"
                response_data = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Anda adalah analis data berpengalaman. Gunakan bahasa Indonesia."},
                        {"role": "user", "content": prompt_data}
                    ],
                    max_tokens=2048,
                    temperature=1.0
                )
                result_data = response_data['choices'][0]['message']['content']

                # Pencarian global GPT-4o
                prompt_search = f"Lakukan pencarian mendalam tentang '{analysis_query}' menggunakan pengetahuan global Anda."
                response_search = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Anda adalah mesin pencari pintar. Gunakan bahasa Indonesia."},
                        {"role": "user", "content": prompt_search}
                    ],
                    max_tokens=2048,
                    temperature=1.0
                )
                result_search = response_search['choices'][0]['message']['content']

                # Tampilkan hasil analisis
                st.write("#### Hasil Analisis Berdasarkan Data:")
                st.write(result_data)

                st.write("#### Hasil Pencarian GPT-4o:")
                st.write(result_search)
            except Exception as e:
                st.error(f"Error generating analysis: {e}")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
else:
    st.warning("Tidak ada file yang diunggah. Silakan unggah file CSV atau Excel.")

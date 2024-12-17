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

    # Columns to exclude from selection
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
    selected_x = st.selectbox("Pilih Kolom X", options=selectable_columns)
    selected_y = st.selectbox("Pilih Kolom Y", options=selectable_columns)
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
        st.plotly_chart(
            px.bar(filtered_data, x=selected_x, y=selected_y, color=non_numeric_columns[0], barmode="group")
        )
    elif selected_chart == "Pie Chart":
        st.plotly_chart(px.pie(filtered_data, names=selected_x, title=f"Distribusi {selected_x}"))
    elif selected_chart == "Line Chart":
        st.plotly_chart(px.line(filtered_data, x=selected_x, y=selected_y, color=non_numeric_columns[0]))
    elif selected_chart == "Scatter Plot":
        st.plotly_chart(px.scatter(filtered_data, x=selected_x, y=selected_y, color=non_numeric_columns[0]))
    elif selected_chart == "Heatmap":
        st.plotly_chart(px.imshow(filtered_data.corr()))
    elif selected_chart == "Histogram":
        st.plotly_chart(px.histogram(filtered_data, x=selected_x, color=non_numeric_columns[0]))
    elif selected_chart == "Area Chart":
        st.plotly_chart(px.area(filtered_data, x=selected_x, y=selected_y, color=non_numeric_columns[0]))
    elif selected_chart == "Boxplot":
        st.plotly_chart(px.box(filtered_data, x=selected_x, y=selected_y, color=non_numeric_columns[0]))
    elif selected_chart == "Treemap":
        st.plotly_chart(px.treemap(filtered_data, path=[selected_x], values=selected_y))
    elif selected_chart == "Sunburst":
        st.plotly_chart(px.sunburst(filtered_data, path=[selected_x], values=selected_y))

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

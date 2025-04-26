# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 🚨 set_page_config must be first Streamlit command
st.set_page_config(page_title="Bank Assets and Liabilities Dashboard", layout="wide")

# App title
st.title("📊 Bank Assets and Liabilities Dashboard")

# Sidebar for uploading files
st.sidebar.header("Upload CSV Files")

assets_file = st.sidebar.file_uploader("Upload Assets CSV", type=["csv"])
liabilities_file = st.sidebar.file_uploader("Upload Liabilities CSV", type=["csv"])

# Load data
if assets_file and liabilities_file:
    assets_df = pd.read_csv(assets_file)
    liabilities_df = pd.read_csv(liabilities_file)

    # Sidebar filters
    st.sidebar.header("Visualization Settings")
    dataset_choice = st.sidebar.radio("Select Dataset", ("Assets", "Liabilities"))

    # Set data based on choice
    if dataset_choice == "Assets":
        df = assets_df
    else:
        df = liabilities_df

    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    all_columns = df.columns.tolist()

    # Filter options
    st.sidebar.subheader("Filter Data")
    selected_columns = st.sidebar.multiselect("Select columns to display", all_columns, default=all_columns)

    # Tabs for better navigation
    tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📈 Charts", "🔎 Data Exploration"])

    with tab1:
        st.subheader(f"{dataset_choice} - Data Table")
        st.dataframe(df[selected_columns])

    with tab2:
        st.subheader(f"{dataset_choice} - Visualizations")

        if numeric_columns:
            selected_col = st.selectbox("Select a numeric column to visualize", numeric_columns)

            # Line Chart
            st.plotly_chart(px.line(df, y=selected_col, title=f"Line Chart of {selected_col}"))

            # Histogram
            st.plotly_chart(px.histogram(df, x=selected_col, nbins=30, title=f"Histogram of {selected_col}"))

            # Box Plot
            st.plotly_chart(px.box(df, y=selected_col, title=f"Box Plot of {selected_col}"))
        else:
            st.warning("No numeric columns found for visualization.")

    with tab3:
        st.subheader(f"{dataset_choice} - Basic Data Exploration")

        st.write("**Summary Statistics**")
        st.dataframe(df.describe())

        st.write("**Missing Values**")
        missing = df.isnull().sum()
        st.dataframe(missing[missing > 0])

else:
    st.info("⬅️ Please upload both Assets and Liabilities CSV files to start.")

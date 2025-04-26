# streamlit_app.py

import streamlit as st
import pandas as pd
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

    # ---- TRY to detect date column
    possible_date_cols = [col for col in assets_df.columns if 'date' in col.lower() or 'month' in col.lower()]
    date_col = None
    if possible_date_cols:
        date_col = possible_date_cols[0]  # assume first one
        assets_df[date_col] = pd.to_datetime(assets_df[date_col])
        liabilities_df[date_col] = pd.to_datetime(liabilities_df[date_col])

    # Sidebar filters
    st.sidebar.header("Visualization Settings")
    dataset_choice = st.sidebar.radio("Select Dataset", ("Assets", "Liabilities", "Comparison"))

    # Date filtering
    if date_col:
        st.sidebar.subheader("Filter by Date")
        min_date = assets_df[date_col].min()
        max_date = assets_df[date_col].max()
        start_date, end_date = st.sidebar.date_input("Select date range", [min_date, max_date])

        # Filter assets and liabilities based on selected date
        assets_df = assets_df[(assets_df[date_col] >= pd.to_datetime(start_date)) & (assets_df[date_col] <= pd.to_datetime(end_date))]
        liabilities_df = liabilities_df[(liabilities_df[date_col] >= pd.to_datetime(start_date)) & (liabilities_df[date_col] <= pd.to_datetime(end_date))]

    if dataset_choice == "Assets":
        df = assets_df
    elif dataset_choice == "Liabilities":
        df = liabilities_df
    else:
        df = None  # for Comparison view

    # Tabs
    if dataset_choice != "Comparison":
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        all_columns = df.columns.tolist()

        selected_columns = st.sidebar.multiselect("Select columns to display", all_columns, default=all_columns)

        tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📈 Charts", "🔎 Data Exploration"])

        with tab1:
            st.subheader(f"{dataset_choice} - Data Table")
            st.dataframe(df[selected_columns])

        with tab2:
            st.subheader(f"{dataset_choice} - Visualizations")

            if numeric_columns:
                selected_col = st.selectbox("Select a numeric column to visualize", numeric_columns)

                # Line Chart
                st.plotly_chart(px.line(df, x=date_col, y=selected_col, title=f"Line Chart of {selected_col}"))

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
        st.subheader("📊 Assets vs Liabilities Comparison")

        # Ask user which two columns to compare
        st.info("Select columns to compare from Assets and Liabilities data.")

        col1 = st.selectbox("Select Assets column", assets_df.select_dtypes(include=["float64", "int64"]

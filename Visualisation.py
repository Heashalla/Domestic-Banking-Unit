# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page config
st.set_page_config(page_title="Sri Lanka Bank Dashboard", layout="wide")

# App Title
st.title("🏦 Sri Lanka Banks: Assets and Liabilities Dashboard")

# 🚀 Directly Load CSV Files (no upload)
assets_df = pd.read_csv("assets_data_cleaned.csv")
liabilities_df = pd.read_csv("liabilties_data_cleaned.csv")

# Sidebar for user choice
st.sidebar.header("Options")
dataset_choice = st.sidebar.radio("Select Dataset", ("Assets", "Liabilities"))

# Choose dataset based on user choice
if dataset_choice == "Assets":
    df = assets_df
else:
    df = liabilities_df

# KPIs Section
st.subheader("🔑 Key Performance Indicators")

col1, col2 = st.columns(2)

with col1:
    total_value = df.select_dtypes(include=["float64", "int64"]).sum().sum()
    st.metric(f"Total {dataset_choice}", f"{total_value:,.0f}")

with col2:
    st.metric("Number of Records", f"{len(df):,}")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📈 Charts", "🔎 Data Exploration"])

# Tab 1: Data Table
with tab1:
    st.subheader(f"{dataset_choice} - Data Table")
    st.dataframe(df)

# Tab 2: Charts
with tab2:
    st.subheader(f"{dataset_choice} - Visualizations")
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    if numeric_columns:
        selected_col = st.selectbox("Select a numeric column to visualize", numeric_columns)

        st.plotly_chart(px.line(df, y=selected_col, title=f"Line Chart of {selected_col}"))
        st.plotly_chart(px.histogram(df, x=selected_col, nbins=30, title=f"Histogram of {selected_col}"))
        st.plotly_chart(px.box(df, y=selected_col, title=f"Box Plot of {selected_col}"))
    else:
        st.warning("No numeric columns available for visualization.")

# Tab 3: Data Exploration
with tab3:
    st.subheader(f"{dataset_choice} - Data Exploration")
    st.write("**Summary Statistics**")
    st.dataframe(df.describe())

    st.write("**Missing Values**")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.dataframe(missing)
    else:
        st.success("No missing values found.")

# Footer
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

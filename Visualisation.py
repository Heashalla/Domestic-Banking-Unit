# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Bank Assets and Liabilities Dashboard", layout="wide")

# App title
st.title("🏦 Sri Lanka Banks: Assets and Liabilities Dashboard")

# Load data (no uploads, loading directly)
assets_df = pd.read_csv("assets_data_cleaned.csv")
liabilities_df = pd.read_csv("liabilties_data_cleaned.csv")

# Sidebar options
st.sidebar.header("Options")
view_option = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

# Dataset selection
if view_option == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"

# KPI Section
st.subheader(f"🔑 {dataset_title} - Key Performance Indicators")

col1, col2 = st.columns(2)

with col1:
    total_sum = df.select_dtypes(include=["float64", "int64"]).sum().sum()
    st.metric(f"Total {dataset_title}", f"{total_sum:,.0f}")

with col2:
    avg_value = df.select_dtypes(include=["float64", "int64"]).mean().mean()
    st.metric(f"Average {dataset_title} Value", f"{avg_value:,.2f}")

# Tabs for content
tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📈 Charts", "🔎 Insights"])

with tab1:
    st.subheader(f"{dataset_title} Data Table")
    st.dataframe(df)

with tab2:
    st.subheader(f"{dataset_title} Charts")

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("Select a numeric column to visualize", numeric_cols)

        # Line Chart
        st.plotly_chart(px.line(df, y=selected_col, title=f"{dataset_title} - {selected_col} Over Time"))

        # Histogram
        st.plotly_chart(px.histogram(df, x=selected_col, nbins=30, title=f"{dataset_title} - {selected_col} Distribution"))

        # Box Plot
        st.plotly_chart(px.box(df, y=selected_col, title=f"{dataset_title} - {selected_col} Spread"))
    else:
        st.warning("No numeric columns found for visualization.")

with tab3:
    st.subheader(f"{dataset_title} Insights")

    if df.select_dtypes(include=["float64", "int64"]).shape[1] > 0:
        # Show Top 5 and Bottom 5 values
        st.write("### 🔝 Top 5 Records (by Total Sum)")
        df["Total"] = df.select_dtypes(include=["float64", "int64"]).sum(axis=1)
        top5 = df.nlargest(5, "Total")
        st.dataframe(top5)

        st.write("### 🔻 Bottom 5 Records (by Total Sum)")
        bottom5 = df.nsmallest(5, "Total")
        st.dataframe(bottom5)

        # Correlation Heatmap
        st.write("### 📈 Correlation Heatmap")
        corr = df.select_dtypes(include=["float64", "int64"]).corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
        st.pyplot(fig)

        # Trend overview
        st.write("### 📈 Overall Trend Overview")
        df["Index"] = df.index
        trend_col = df.select_dtypes(include=["float64", "int64"]).columns[0]  # First numeric column
        trend_fig = px.line(df, x="Index", y=trend_col, title=f"{dataset_title} - {trend_col} Trend")
        st.plotly_chart(trend_fig)

        # Clean up temp columns
        df.drop(columns=["Total", "Index"], inplace=True)
    else:
        st.info("No numeric data available for insights.")

# Footer
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

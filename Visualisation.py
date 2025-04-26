# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 🚀 Page setup
st.set_page_config(page_title="Bank Assets and Liabilities Dashboard", layout="wide")
st.title("🏦 Sri Lanka Banks: Assets & Liabilities Dashboard")

# 📥 Load data
assets_df = pd.read_csv("assets_data_cleaned.csv")
liabilities_df = pd.read_csv("liabilties_data_cleaned.csv")

# 📦 Filter column (date filter)
filter_col = "End of Period"  # Make sure it matches exactly!

# 🔘 Sidebar
st.sidebar.header("Controls")
dataset_choice = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

# 🎯 Select dataset
if dataset_choice == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"

# 📅 Filter by Year and Month separately
if filter_col in df.columns:
    df[filter_col] = pd.to_datetime(df[filter_col], errors='coerce')
    df = df.dropna(subset=[filter_col])

    # Extract Year and Month
    df['Year'] = df[filter_col].dt.year
    df['Month'] = df[filter_col].dt.month_name()

    # Sidebar filter options
    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique(), reverse=True))
    available_months = df[df['Year'] == selected_year]['Month'].unique()
    selected_month = st.sidebar.selectbox("Select Month", sorted(available_months))

    # Apply filtering
    df = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

# 📊 KPI Section
st.subheader(f"🔑 {dataset_title} Key Stats ({selected_month} {selected_year})")
col1, col2 = st.columns(2)
with col1:
    total_val = df.select_dtypes(include="number").sum().sum()
    st.metric("Total Value", f"{total_val:,.0f}")
with col2:
    avg_val = df.select_dtypes(include="number").mean().mean()
    st.metric("Average per Metric", f"{avg_val:,.2f}")

# 📈 Charts Section
st.subheader(f"📊 Visual Analysis of {dataset_title}")

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if numeric_cols:
    selected_col = st.selectbox(f"Choose a {dataset_title} metric to visualize:", numeric_cols)

    # Line Chart
    st.plotly_chart(px.line(df, x=filter_col, y=selected_col,
                            title=f"{selected_col} Over Time",
                            template="plotly_dark",
                            markers=True))

    # Box Plot
    st.plotly_chart(px.box(df, y=selected_col,
                           title=f"{selected_col} Value Spread",
                           template="ggplot2"))
else:
    st.warning("No numeric columns found for visualization.")

# 📊 Insights Section
st.subheader(f"🔍 Correlation & Distribution Insights")

if numeric_cols:
    insight_col = st.selectbox("Choose a metric for deeper insights", numeric_cols, key="insight_col")

    # Correlation Heatmap
    st.write("### 🔵 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Optional Pie Chart
    st.write("### 🥧 Pie Chart (Proportional View)")
    pie_df = df[[insight_col]].copy()
    pie_df["Label"] = pie_df.index.astype(str)
    st.plotly_chart(px.pie(pie_df, names="Label", values=insight_col,
                           title=f"{insight_col} Distribution",
                           template="seaborn"))

else:
    st.info("No numeric columns available to show insights.")

# 📎 Footer
st.markdown("---")
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 🚀 Page setup
st.set_page_config(page_title="Sri Lanka Banks Dashboard", layout="wide")
st.title("🏦 Sri Lanka Banks: Domestic Banking Insights")
st.markdown("_Tracking assets, loans, and financial strength from 1995 to 2025._")

# 📥 Load data
@st.cache_data
def load_data():
    assets = pd.read_csv("assets_data_cleaned.csv")
    liabilities = pd.read_csv("liabilties_data_cleaned.csv")
    assets["End of Period"] = pd.to_datetime(assets["End of Period"], errors="coerce")
    liabilities["End of Period"] = pd.to_datetime(liabilities["End of Period"], errors="coerce")
    return assets, liabilities

assets_df, liabilities_df = load_data()

# 📦 Sidebar controls
st.sidebar.header("🔧 Controls")
dataset_choice = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

if dataset_choice == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"

filter_col = "End of Period"

# 🗓️ Sidebar - Year and Month Filters
if filter_col in df.columns:
    df = df.dropna(subset=[filter_col])
    df['Year'] = df[filter_col].dt.year
    df['Month'] = df[filter_col].dt.month_name()

    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique(), reverse=True))
    available_months = df[df['Year'] == selected_year]['Month'].unique()
    selected_month = st.sidebar.selectbox("Select Month", sorted(available_months))

    df = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

# 📊 Smart KPI Section
st.subheader(f"🔑 {dataset_title} Overview ({selected_month} {selected_year})")

# Metrics calculations
total_assets = df.select_dtypes(include="number").sum().sum()
average_asset = df.select_dtypes(include="number").mean().mean()

# Growth Calculation
previous_month_df = df.copy()
previous_month_df['Month'] = pd.Categorical(previous_month_df['Month'],
    categories=list(calendar.month_name)[1:], ordered=True)

previous_months = previous_month_df.sort_values('Month')['Month'].unique()
current_index = list(previous_months).tolist().index(selected_month)
if current_index > 0:
    previous_month_name = previous_months[current_index-1]
    previous_data = df[df['Month'] == previous_month_name]
    if not previous_data.empty:
        previous_total = previous_data.select_dtypes(include="number").sum().sum()
        growth_rate = ((total_assets - previous_total) / previous_total) * 100
    else:
        growth_rate = 0
else:
    growth_rate = 0

# Biggest Contributor
biggest_contributor = df.select_dtypes(include="number").sum().idxmax()

# Display KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value", f"Rs. {total_assets:,.0f}")
col2.metric("Average Value", f"Rs. {average_asset:,.0f}")
col3.metric("Monthly Growth Rate", f"{growth_rate:.2f}%")
col4.metric("Top Category", biggest_contributor)

# 📈 Charts Section
st.subheader(f"📈 {dataset_title} Trend Visualizations")

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if numeric_cols:
    selected_col = st.selectbox(f"Select a {dataset_title} metric to visualize:", numeric_cols)

    fig_line = px.line(df, x=filter_col, y=selected_col,
                       title=f"{selected_col} Trend Over Time",
                       template="plotly_dark", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    fig_area = px.area(df, x=filter_col, y=selected_col,
                       title=f"{selected_col} Area Representation",
                       template="simple_white")
    st.plotly_chart(fig_area, use_container_width=True)

else:
    st.warning("No numeric columns available to visualize.")

# 🔍 Insights Section
st.subheader(f"🔎 Correlation & Distribution Insights")

if numeric_cols:
    # Correlation heatmap
    st.write("### 🔵 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Pie Chart
    st.write("### 🥧 Pie Chart View")
    pie_df = df[[selected_col]].copy()
    pie_df["Label"] = pie_df.index.astype(str)
    st.plotly_chart(px.pie(pie_df, names="Label", values=selected_col,
                           title=f"{selected_col} Distribution",
                           template="seaborn"))
else:
    st.info("No numeric columns to display.")

# 📎 Footer
st.markdown("---")
st.caption("Developed by [Your Name] | 5DATA004W Data Science Project Lifecycle | University of Westminster")

# Dynamically change background color using Streamlit's markdown
def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background color based on dataset choice
if dataset_choice == "Assets":
    set_background("#E3F2FD")  # Light blue
else:
    set_background("#ECEFF1")  # Light grey

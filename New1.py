# 🚀 Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import calendar

# 🚀 Page Config
st.set_page_config(page_title="Sri Lanka Banks Dashboard", layout="wide")

# 🇱🇰 Background Styling
def sri_lanka_flag_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #8D1B1B 0%, #FFD700 25%, #007847 50%, #FF8200 75%, #8D1B1B 100%);
            background-size: 400% 400%;
            animation: gradientAnimation 15s ease infinite;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #c49a6c 0%, #FFD700 50%, #c49a6c 100%);
            border: 2px solid #8D1B1B;
            border-radius: 15px;
            padding: 15px;
            margin: 10px;
            color: black;
            font-weight: bold;
        }
        [data-testid="stSidebar"] section {
            margin-top: 20px;
        }
        @keyframes gradientAnimation {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        </style>
        """,
        unsafe_allow_html=True
    )

sri_lanka_flag_background()

# 📥 Load Data
@st.cache_data
def load_data():
    assets = pd.read_csv("assets_data_cleaned.csv")
    liabilities = pd.read_csv("liabilties_data_cleaned.csv")
    assets["End of Period"] = pd.to_datetime(assets["End of Period"], errors="coerce")
    liabilities["End of Period"] = pd.to_datetime(liabilities["End of Period"], errors="coerce")
    return assets, liabilities

assets_df, liabilities_df = load_data()

# 🏦 Title and Description
st.title("🏦 🇱🇰 Sri Lanka Banks: Domestic Banking Insights")
st.markdown("_Tracking assets, loans, and financial strength from 1995 to 2025._")

# 📦 Sidebar Controls
st.sidebar.header("🔧 Controls")
dataset_choice = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

if dataset_choice == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"

filter_col = "End of Period"

if filter_col in df.columns:
    df = df.dropna(subset=[filter_col])
    df['Year'] = df[filter_col].dt.year
    df['Month'] = df[filter_col].dt.month_name()

    selected_year = st.sidebar.selectbox("Select Year 📅", sorted(df['Year'].unique(), reverse=True))
    available_months = df[df['Year'] == selected_year]['Month'].unique()
    selected_month = st.sidebar.selectbox("Select Month 📆", sorted(available_months))

    df = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]

# 🔑 KPI Section
st.subheader(f"🔑 {dataset_title} Overview ({selected_month} {selected_year})")

total_value = df.select_dtypes(include="number").sum().sum()
average_value = df.select_dtypes(include="number").mean().mean()
biggest_contributor = df.select_dtypes(include="number").sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Total Value", f"Rs. {total_value:,.0f}")
col2.metric("Average per Metric", f"Rs. {average_value:,.0f}")
col3.metric("Top Contributor", biggest_contributor)

# 📈 Charts Section
st.subheader(f"📈 Visual Analysis of {dataset_title}")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if numeric_cols:
    selected_metrics = st.multiselect(
        f"Choose up to 2 {dataset_title} metrics to visualize:", 
        numeric_cols, 
        max_selections=2
    )

    if selected_metrics:
        fig = px.line(df, x=filter_col, y=selected_metrics,
                      title=" ➡️ ".join(selected_metrics) + " Trend",
                      markers=True,
                      template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one metric to display the chart.")

else:
    st.warning("No numeric columns available to visualize.")

# 🔍 Insights Section
st.subheader(f"🔎 Correlation & Distribution Insights")

if numeric_cols:
    st.write("### 🔵 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
else:
    st.info("No numeric data available for insights.")

# 📎 Footer
st.markdown("---")
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

# 🇱🇰 Floating Sri Lanka Flag
st.markdown(
    """
    <style>
    .floating-flag {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: auto;
        opacity: 0.9;
        z-index: 9999;
    }
    </style>
    <a href="https://en.wikipedia.org/wiki/Flag_of_Sri_Lanka" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/320px-Flag_of_Sri_Lanka.svg.png" class="floating-flag">
    </a>
    """,
    unsafe_allow_html=True
)

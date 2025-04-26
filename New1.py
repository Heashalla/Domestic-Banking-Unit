# streamlit_app.py

# 🚀 Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import calendar

# 🚀 FIRST: Page setup (must be FIRST Streamlit command!)
st.set_page_config(page_title="Sri Lanka Banks Dashboard", layout="wide")

# 🇱🇰 THEN: Set Sri Lanka Flag Colors as Background
def sri_lanka_flag_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                135deg,
                #8D1B1B 0%,
                #FFD700 25%,
                #007847 50%,
                #FF8200 75%,
                #8D1B1B 100%
            );
            background-size: 400% 400%;
            animation: gradientAnimation 15s ease infinite;
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

# 🎨 Apply Background
sri_lanka_flag_background()

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

# 🧠 Identify shared filter column
filter_col = "End of Period"  # Adjust this if your actual column name is slightly different

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

# 📆 Filter by End of Period
if filter_col in df.columns:
    df[filter_col] = pd.to_datetime(df[filter_col], errors='coerce')
    df = df.dropna(subset=[filter_col])
    unique_dates = sorted(df[filter_col].dt.to_period('M').astype(str).unique())
    selected_date = st.sidebar.selectbox("Filter by End of Period", unique_dates)
    df = df[df[filter_col].dt.to_period('M').astype(str) == selected_date]

# 📊 KPI Section
st.subheader(f"🔑 {dataset_title} Key Stats ({selected_date})")
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

    chart1, chart2 = st.columns(2)

    with chart1:
        st.plotly_chart(px.line(df, x=filter_col, y=selected_col,
                                title=f"{selected_col} - Trend Line",
                                template="plotly_dark",
                                markers=True))

    with chart2:
        st.plotly_chart(px.area(df, x=filter_col, y=selected_col,
                                title=f"{selected_col} - Area Chart",
                                template="plotly"))

    if df[selected_col].nunique() > 1:
        st.plotly_chart(px.box(df, y=selected_col,
                               title=f"{selected_col} - Value Spread",
                               template="ggplot2"))
else:
    st.warning("No numeric columns found for visualization.")

# 📊 Insights Section
st.subheader(f"🔍 Explore & Compare Insights")

if numeric_cols:
    insight_col = st.selectbox("Choose a metric for deeper insights", numeric_cols, key="insight_col")

    # Top/Bottom 5
    df["Total"] = df[numeric_cols].sum(axis=1)
    st.write("### 🔝 Top 5 Records (by Total across columns)")
    st.dataframe(df.nlargest(5, "Total")[["Total", insight_col]])

    st.write("### 🔻 Bottom 5 Records (by Total across columns)")
    st.dataframe(df.nsmallest(5, "Total")[["Total", insight_col]])

    # Correlation Heatmap
    st.write("### 🔵 Correlation Map")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Optional Pie Chart if values add up to meaningful whole
    if df[insight_col].sum() > 0:
        st.write("### 🥧 Pie Chart Representation")
        pie_df = df[[insight_col]].copy()
        pie_df["Label"] = pie_df.index.astype(str)
        st.plotly_chart(px.pie(pie_df, names="Label", values=insight_col, title=f"{insight_col} Distribution"))

    df.drop(columns=["Total"], inplace=True)

else:
    st.info("No numeric data available for insights.")

# Footer
st.markdown("---")
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

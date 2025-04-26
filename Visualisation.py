# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 🚀 Page settings
st.set_page_config(page_title="Sri Lanka Bank Dashboard", layout="wide")

# 📄 Load datasets
assets_df = pd.read_csv("assets_data_cleaned.csv")
liabilities_df = pd.read_csv("liabilties_data_cleaned.csv")

# 📦 Predefined column lists for dropdowns
assets_columns = [
    'Cash on Hand',
    'Due from Central Bank',
    'Due from Domestic Banks',
    'Cash Items in Process of Collection',
    'Foreign Currency on Hand and Balances Due from Banks',
    'Treasury Bills',
    'Treasury Bonds',
    'Govt. of Sri Lanka Securities (a)',
    'Other Investments (c)',
    'Local',
    'Imports',
    'Exports',
    'Overdrafts',
    'Loans and Advances',
    'Total Loans and Advances (b)',
    'Fixed Assets and Other Assets',
    'Total Assets or Liabilities',
    'Percentage of Liquid Assets to Demand Deposits (e)',
    'Percentage of Loans & Advances to Total Deposits'
]

liabilities_columns = [
    'Paid-up Capital, Reserve Fund and Undistributed Profits',
    'Domestic',
    'Foreign',
    'Govt. of Sri Lanka',
    'Resident Constituents',
    'Non Resident Constituents',
    'Govt. of Sri Lanka',
    'Resident Constituents',
    'Non Resident Constituents',
    'Demand',
    'Time and Savings',
    'Total',
    'Domestic InterBank (h)',
    'Foreign',
    'Other Liabilities'
]

# 🎯 Sidebar controls
st.sidebar.header("Options")
view_option = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

# 🎯 Dataset selector
if view_option == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
    valid_cols = [col for col in assets_columns if col in df.columns]
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"
    valid_cols = [col for col in liabilities_columns if col in df.columns]

# 📊 KPIs
st.title(f"🏦 Sri Lanka Bank: {dataset_title} Dashboard")
st.subheader("🔑 Key Performance Indicators")
col1, col2 = st.columns(2)
with col1:
    total_sum = df.select_dtypes(include=["float64", "int64"]).sum().sum()
    st.metric(f"Total {dataset_title}", f"{total_sum:,.0f}")
with col2:
    avg_val = df.select_dtypes(include=["float64", "int64"]).mean().mean()
    st.metric(f"Average {dataset_title} Value", f"{avg_val:,.2f}")

# 📚 TABS
tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📈 Charts", "🔎 Insights"])

# TAB 1: Table
with tab1:
    st.subheader(f"{dataset_title} Data Table")
    st.dataframe(df)

# TAB 2: Charts
with tab2:
    st.subheader(f"{dataset_title} Charts")

    if valid_cols:
        selected_col = st.selectbox(f"Select a {dataset_title} item to visualize", valid_cols)

        # Line Chart
        st.plotly_chart(px.line(df, y=selected_col, title=f"{dataset_title} - {selected_col} Over Time"))

        # Histogram
        st.plotly_chart(px.histogram(df, x=selected_col, nbins=30, title=f"{dataset_title} - {selected_col} Distribution"))

        # Box Plot
        st.plotly_chart(px.box(df, y=selected_col, title=f"{dataset_title} - {selected_col} Spread"))
    else:
        st.warning("No matching columns found in dataset.")

# TAB 3: Insights
with tab3:
    st.subheader(f"{dataset_title} Insights")

    numeric_df = df.select_dtypes(include=["float64", "int64"])

    if not numeric_df.empty:
        # Top 5 and Bottom 5
        st.markdown("### 🔝 Top 5 Records (by Total Sum)")
        df["Total"] = numeric_df.sum(axis=1)
        top5 = df.nlargest(5, "Total")
        st.dataframe(top5)

        st.markdown("### 🔻 Bottom 5 Records (by Total Sum)")
        bottom5 = df.nsmallest(5, "Total")
        st.dataframe(bottom5)

        # Correlation heatmap
        st.markdown("### 📊 Correlation Heatmap")
        corr = numeric_df.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
        st.pyplot(fig)

        # Trend overview
        st.markdown("### 📈 Overall Trend of First Numeric Column")
        df["Index"] = df.index
        first_col = numeric_df.columns[0]
        trend_fig = px.line(df, x="Index", y=first_col, title=f"{dataset_title} - {first_col} Trend")
        st.plotly_chart(trend_fig)

        df.drop(columns=["Total", "Index"], inplace=True)
    else:
        st.info("No numeric columns available to display insights.")

# 📌 Footer
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

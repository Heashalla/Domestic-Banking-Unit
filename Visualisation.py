# 1. Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# 2. Set Streamlit page config
st.set_page_config(page_title="Sri Lanka Bank Dashboard", layout="wide")

# 3. App title
st.title("🏦 Sri Lanka Banks: Assets vs Liabilities Dashboard")

# 🚀 4. Load assets and liabilities CSVs (DIRECT LOAD — no upload)
assets_df = pd.read_csv("assets_data_cleaned.csv")
liabilities_df = pd.read_csv("liabilties_data_cleaned.csv")

# 5. Prepare the combined data
if "Date" in assets_df.columns and "Date" in liabilities_df.columns:
    # Make sure Date columns are datetime
    assets_df["Date"] = pd.to_datetime(assets_df["Date"])
    liabilities_df["Date"] = pd.to_datetime(liabilities_df["Date"])
    
    # Sum numeric values
    assets_df["Total Assets"] = assets_df.select_dtypes(include=["float64", "int64"]).sum(axis=1)
    liabilities_df["Total Liabilities"] = liabilities_df.select_dtypes(include=["float64", "int64"]).sum(axis=1)
    
    # Merge only needed columns
    combined_df = pd.merge(
        assets_df[["Date", "Total Assets"]],
        liabilities_df[["Date", "Total Liabilities"]],
        on="Date",
        how="inner"
    )
    # Create a new column for Asset-to-Liability Ratio
    combined_df["Assets/Liabilities Ratio"] = combined_df["Total Assets"] / combined_df["Total Liabilities"]
else:
    st.error("Date column missing in one or both files. Cannot create combined analysis.")

# Sidebar options
st.sidebar.header("Options")
view_option = st.sidebar.radio("Select View", ["Assets", "Liabilities", "Combined Analysis"])

# KPI Section
st.subheader("🔑 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    total_assets = assets_df.select_dtypes(include=["float64", "int64"]).sum().sum()
    st.metric("Total Assets", f"{total_assets:,.0f}")

with col2:
    total_liabilities = liabilities_df.select_dtypes(include=["float64", "int64"]).sum().sum()
    st.metric("Total Liabilities", f"{total_liabilities:,.0f}")

with col3:
    ratio = total_assets / total_liabilities if total_liabilities != 0 else 0
    st.metric("Assets to Liabilities Ratio", f"{ratio:.2f}")

# Tabs for content
tab1, tab2, tab3 = st.tabs(["📊 Data Table", "📈 Charts", "🔍 Insights"])

with tab1:
    st.subheader(f"{view_option} Data Table")
    if view_option == "Assets":
        st.dataframe(assets_df)
    elif view_option == "Liabilities":
        st.dataframe(liabilities_df)
    else:
        st.dataframe(combined_df)

with tab2:
    st.subheader(f"{view_option} Charts")

    if view_option == "Assets":
        numeric_cols = assets_df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        selected_col = st.selectbox("Select a column to visualize", numeric_cols)
        st.plotly_chart(px.line(assets_df, x=assets_df.index, y=selected_col, title=f"Assets - {selected_col} Trend"))

    elif view_option == "Liabilities":
        numeric_cols = liabilities_df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        selected_col = st.selectbox("Select a column to visualize", numeric_cols)
        st.plotly_chart(px.line(liabilities_df, x=liabilities_df.index, y=selected_col, title=f"Liabilities - {selected_col} Trend"))

    else:
        if "Date" in combined_df.columns:
            combined_df["Date"] = pd.to_datetime(combined_df["Date"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=combined_df["Date"], y=assets_df.select_dtypes(include=["float64", "int64"]).sum(axis=1),
                                     mode="lines", name="Assets"))
            fig.add_trace(go.Scatter(x=combined_df["Date"], y=liabilities_df.select_dtypes(include=["float64", "int64"]).sum(axis=1),
                                     mode="lines", name="Liabilities"))
            fig.update_layout(title="Assets vs Liabilities Over Time")
            st.plotly_chart(fig)
        else:
            st.warning("No Date column available for time series chart.")

with tab3:
    st.subheader(f"{view_option} Insights")

    if view_option == "Combined Analysis":
        st.markdown("### Correlation Heatmap (Assets + Liabilities)")
        corr = combined_df.corr()
        fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        st.markdown("### Assets vs Liabilities Distribution")
        fig2 = go.Figure(data=[
            go.Bar(name="Assets", x=assets_df.columns, y=assets_df.sum()),
            go.Bar(name="Liabilities", x=liabilities_df.columns, y=liabilities_df.sum())
        ])
        fig2.update_layout(barmode='group')
        st.plotly_chart(fig2)

    else:
        st.info("Select 'Combined Analysis' to view advanced insights.")

# Footer
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

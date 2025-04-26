# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="Sri Lanka Financial Dashboard", layout="wide")

# Load datasets
assets = pd.read_csv("assets_data_cleaned.csv")
liabilities = pd.read_csv("liabilties_data_cleaned.csv")

# Clean column names
assets.columns = assets.columns.str.strip()
liabilities.columns = liabilities.columns.str.strip()

# Rename 'End of Period' to 'Year'
assets.rename(columns={'End of Period': 'Year'}, inplace=True)
liabilities.rename(columns={'End of Period': 'Year'}, inplace=True)

# Preprocessing
assets['Type'] = 'Asset'
liabilities['Type'] = 'Liability'

# Combine datasets
combined = pd.concat([assets, liabilities], ignore_index=True)

# Sidebar filters
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Select Year", combined['Year'].unique())

# Filtered data
filtered_data = combined[combined['Year'] == selected_year]

# KPIs
total_assets = assets[assets['Year'] == selected_year]['Value'].sum()
total_liabilities = liabilities[liabilities['Year'] == selected_year]['Value'].sum()
net_worth = total_assets - total_liabilities

# Display KPIs
st.title("Sri Lanka Financial Dashboard")
col1, col2, col3 = st.columns(3)

col1.metric("Total Assets", f"LKR {total_assets:,.2f}")
col2.metric("Total Liabilities", f"LKR {total_liabilities:,.2f}")
col3.metric("Net Worth", f"LKR {net_worth:,.2f}")

# Advanced Analysis: Asset to Liability Ratio
try:
    ratio = total_assets / total_liabilities
except ZeroDivisionError:
    ratio = 0
st.subheader(f"Asset to Liability Ratio in {selected_year}: {ratio:.2f}")

# Trend Analysis (across years)
st.subheader("Trend Over Time")
trend_data = combined.groupby(['Year', 'Type'])['Value'].sum().reset_index()
fig_trend = px.line(trend_data, x='Year', y='Value', color='Type', markers=True)
st.plotly_chart(fig_trend, use_container_width=True)

# Breakdown by Category (if available)
if 'Category' in combined.columns:
    st.subheader("Category-wise Breakdown")
    col4, col5 = st.columns(2)

    asset_cat = assets[assets['Year'] == selected_year]
    liability_cat = liabilities[liabilities['Year'] == selected_year]

    fig_asset_cat = px.pie(asset_cat, names='Category', values='Value', title='Assets by Category')
    fig_liability_cat = px.pie(liability_cat, names='Category', values='Value', title='Liabilities by Category')

    col4.plotly_chart(fig_asset_cat, use_container_width=True)
    col5.plotly_chart(fig_liability_cat, use_container_width=True)

# Raw Data View
with st.expander("See Raw Data"):
    st.dataframe(filtered_data)

# Footer
st.markdown("---")
st.caption("Developed for 5DATA004W - University of Westminster")

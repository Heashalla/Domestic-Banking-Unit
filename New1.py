import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Sri Lankan Financial Data Dashboard",
    page_icon="🇱🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title and description
st.title("🇱🇰 Sri Lankan Financial Data Analysis Dashboard")

st.markdown("""
This dashboard provides comprehensive analysis of Sri Lankan financial assets and liabilities data from 1995 to 2023.
Explore various financial indicators, compare trends, and discover insights through interactive visualizations.
""")

# Load and process data
try:
    assets_df = pd.read_csv('attached_assets/assets_data_cleaned.csv')
    liabilities_df = pd.read_csv('attached_assets/liabilties_data_cleaned.csv')
    
    # Convert 'End of Period' to datetime
    assets_df['End of Period'] = pd.to_datetime(assets_df['End of Period'])
    liabilities_df['End of Period'] = pd.to_datetime(liabilities_df['End of Period'])
    
    # Store the processed data in session state for other pages
    st.session_state['assets_df'] = assets_df
    st.session_state['liabilities_df'] = liabilities_df
    
    # Display basic information about the datasets
    st.subheader("Data Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Assets Data Timespan", 
                 f"{assets_df['End of Period'].min().strftime('%b %Y')} - {assets_df['End of Period'].max().strftime('%b %Y')}")
        st.metric("Number of Asset Records", f"{len(assets_df)}")
    
    with col2:
        st.metric("Liabilities Data Timespan", 
                 f"{liabilities_df['End of Period'].min().strftime('%b %Y')} - {liabilities_df['End of Period'].max().strftime('%b %Y')}")
        st.metric("Number of Liability Records", f"{len(liabilities_df)}")
    
    # Sample data preview
    with st.expander("Preview Assets Data"):
        st.dataframe(assets_df.head())
    
    with st.expander("Preview Liabilities Data"):
        st.dataframe(liabilities_df.head())
    
    # Quick summary visualization
    st.subheader("Quick Summary")
    st.markdown("Explore key financial indicators over time using the visualizations below.")
    
    # Date range selector for summary
    min_date = min(assets_df['End of Period'].min(), liabilities_df['End of Period'].min())
    max_date = max(assets_df['End of Period'].max(), liabilities_df['End of Period'].max())
    
    summary_start_date, summary_end_date = st.select_slider(
        "Select Date Range for Summary",
        options=sorted(set(assets_df['End of Period'].tolist() + liabilities_df['End of Period'].tolist())),
        value=(min_date, max_date)
    )
    
    # Filter data based on selected date range
    filtered_assets = assets_df[(assets_df['End of Period'] >= summary_start_date) & 
                              (assets_df['End of Period'] <= summary_end_date)]
    filtered_liabilities = liabilities_df[(liabilities_df['End of Period'] >= summary_start_date) & 
                                       (liabilities_df['End of Period'] <= summary_end_date)]
    
    # Display summary charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Total Assets Over Time
        if 'Total Assets' in filtered_assets.columns:
            fig = px.line(filtered_assets, x='End of Period', y='Total Assets', 
                         title='Total Assets Over Time',
                         labels={'End of Period': 'Date', 'Total Assets': 'Value'},
                         template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Create sum of key asset columns as proxy for total assets
            key_asset_columns = [col for col in filtered_assets.columns if 'Cash' in col or 'Investments' in col or 'Loans' in col]
            if key_asset_columns:
                filtered_assets['Assets Sum'] = filtered_assets[key_asset_columns].sum(axis=1)
                fig = px.line(filtered_assets, x='End of Period', y='Assets Sum', 
                             title='Sum of Key Assets Over Time',
                             labels={'End of Period': 'Date', 'Assets Sum': 'Value'},
                             template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No asset summary columns found for visualization")
                
    with col2:
        # Total Liabilities Over Time
        if 'Total All Deposits_Total' in filtered_liabilities.columns:
            fig = px.line(filtered_liabilities, x='End of Period', y='Total All Deposits_Total', 
                         title='Total Deposits Over Time',
                         labels={'End of Period': 'Date', 'Total All Deposits_Total': 'Value'},
                         template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Create sum of key liability columns
            key_liability_columns = [col for col in filtered_liabilities.columns if 'Deposits' in col or 'Borrowings' in col]
            if key_liability_columns:
                filtered_liabilities['Liabilities Sum'] = filtered_liabilities[key_liability_columns].sum(axis=1)
                fig = px.line(filtered_liabilities, x='End of Period', y='Liabilities Sum', 
                             title='Sum of Key Liabilities Over Time',
                             labels={'End of Period': 'Date', 'Liabilities Sum': 'Value'},
                             template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No liability summary columns found for visualization")
    
    # Navigation guide
    st.subheader("Navigation Guide")
    st.markdown("""
    Use the sidebar to navigate to different analysis pages:
    
    - **Assets Analysis**: Detailed exploration of financial assets over time
    - **Liabilities Analysis**: Comprehensive analysis of financial liabilities
    - **Comparative Analysis**: Compare assets and liabilities trends
    - **Financial Ratios**: Key financial ratios and indicators
    - **About**: Information about this dashboard and data sources
    """)
    
except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")
    st.info("Please make sure the CSV files are correctly placed in the 'attached_assets' folder.")
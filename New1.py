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
# Function to convert dataframe to csv for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
# Application title and description
st.title("🇱🇰 Sri Lankan Financial Data Analysis Dashboard")
st.markdown("""
This dashboard provides comprehensive analysis of Sri Lankan financial assets and liabilities data from 1995 to 2023.
Explore various financial indicators, compare trends, and discover insights through interactive visualizations.
""")
# Create sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Analysis Page",
    ["Home", "Assets Analysis", "Liabilities Analysis", "Comparative Analysis", "Financial Ratios", "About"]
)
# Load and process data
try:
    # Display loading status
    with st.spinner("Loading data..."):
        try:
            assets_df = pd.read_csv('attached_assets/assets_data_cleaned.csv')
            liabilities_df = pd.read_csv('attached_assets/liabilties_data_cleaned.csv')
        except FileNotFoundError:
            # Debug info to help locate files
            import os
            st.error(f"Error: CSV files not found. Current working directory: {os.getcwd()}")
            st.info("Please ensure the CSV files are in the 'attached_assets' folder with correct names: 'assets_data_cleaned.csv' and 'liabilties_data_cleaned.csv'")
            
            # Try to show available files to help debugging
            if os.path.exists("attached_assets"):
                st.write("Files in attached_assets folder:", os.listdir("attached_assets"))
            else:
                st.warning("The 'attached_assets' folder does not exist in the current directory.")
            
            st.stop()
    
    # Convert 'End of Period' to datetime
    assets_df['End of Period'] = pd.to_datetime(assets_df['End of Period'])
    liabilities_df['End of Period'] = pd.to_datetime(liabilities_df['End of Period'])
    
    # Define helper functions
    
    # Define asset categories
    def get_asset_categories(df):
        return {
            'Cash and Balances': [col for col in df.columns if any(x in col for x in ['Cash', 'Due from', 'Foreign Currency'])],
            'Investments': [col for col in df.columns if 'Investments' in col],
            'Loans and Advances': [col for col in df.columns if 'Loans and Advances' in col],
            'Other Assets': [col for col in df.columns if any(x in col for x in ['Bills of Exchange', 'Accrued Interest', 'Other Assets'])]
        }
    
    # Define liability categories
    def get_liability_categories(df):
        return {
            'Capital': [col for col in df.columns if 'Capital' in col or 'Reserves' in col],
            'Demand Deposits': [col for col in df.columns if 'Demand Deposits' in col],
            'Time and Savings Deposits': [col for col in df.columns if 'Time and Savings Deposits' in col],
            'Borrowings': [col for col in df.columns if 'Borrowings' in col],
            'Other Liabilities': [col for col in df.columns if any(x in col for x in ['Bills Payable', 'Accrued Interest', 'Other Liabilities'])]
        }
    
    # Add category totals to dataframes
    def add_category_totals(df, categories):
        for category, columns in categories.items():
            numeric_cols = [col for col in columns if df[col].dtype in [np.float64, np.int64, float, int]]
            if numeric_cols:
                df[f'Total {category}'] = df[numeric_cols].sum(axis=1)
        return df
    
    # Calculate growth rates
    def calculate_growth_rates(df, columns, periods=12):
        for col in columns:
            df[f'{col} Growth Rate'] = df[col].pct_change(periods=periods) * 100
        return df
    
    # Additional processing
    asset_categories = get_asset_categories(assets_df)
    liability_categories = get_liability_categories(liabilities_df)
    
    assets_df = add_category_totals(assets_df, asset_categories)
    liabilities_df = add_category_totals(liabilities_df, liability_categories)
    
    # Define date range for filtering (used across all pages)
    min_date = min(assets_df['End of Period'].min(), liabilities_df['End of Period'].min())
    max_date = max(assets_df['End of Period'].max(), liabilities_df['End of Period'].max())
    
    # Add date filter to sidebar (used across all pages)
    st.sidebar.markdown("---")
    st.sidebar.header("Filter Options")
    
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data based on selected date range
    filtered_assets = assets_df[(assets_df['End of Period'] >= pd.Timestamp(start_date)) & 
                             (assets_df['End of Period'] <= pd.Timestamp(end_date))]
    filtered_liabilities = liabilities_df[(liabilities_df['End of Period'] >= pd.Timestamp(start_date)) & 
                                       (liabilities_df['End of Period'] <= pd.Timestamp(end_date))]
    
    # Display filter info
    st.sidebar.markdown(f"**Selected Period:** {start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}")
    
    # HOME PAGE
    if page == "Home":
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
            st.dataframe(filtered_assets.head())
        
        with st.expander("Preview Liabilities Data"):
            st.dataframe(filtered_liabilities.head())
        
        # Quick summary visualization
        st.subheader("Quick Summary")
        st.markdown("Explore key financial indicators over time using the visualizations below.")
        
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
                asset_totals = [col for col in filtered_assets.columns if col.startswith('Total ') and col != 'Total Assets']
                if asset_totals:
                    filtered_assets['Assets Sum'] = filtered_assets[asset_totals].sum(axis=1)
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
                liability_totals = [col for col in filtered_liabilities.columns if col.startswith('Total ')]
                if liability_totals:
                    filtered_liabilities['Liabilities Sum'] = filtered_liabilities[liability_totals].sum(axis=1)
                    fig = px.line(filtered_liabilities, x='End of Period', y='Liabilities Sum', 
                                 title='Sum of Key Liabilities Over Time',
                                 labels={'End of Period': 'Date', 'Liabilities Sum': 'Value'},
                                 template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No liability summary columns found for visualization")
        
        st.markdown("""
        ### Dashboard Features
        
        - **Interactive Visualizations**: Explore trends with dynamic charts
        - **Time Period Selection**: Focus on specific date ranges
        - **Comparative Analysis**: Compare assets and liabilities
        - **Financial Ratio Analysis**: Evaluate financial health metrics
        - **Data Download**: Export filtered data and analysis results
        
        Use the sidebar to navigate between analysis pages and apply filters.
        """)
    
    # ASSETS ANALYSIS PAGE
    elif page == "Assets Analysis":
        st.header("💰 Assets Analysis")
        st.markdown("Explore and analyze Sri Lankan financial assets over time")
        
        # Add analysis type selection to sidebar
        analysis_type = st.sidebar.selectbox(
            "Select Assets Analysis Type",
            ["Overview", "Asset Breakdown", "Time Series Analysis", "Asset Growth"]
        )
        
        if analysis_type == "Overview":
            st.subheader("Assets Overview")
            
            # Show summary statistics
            st.markdown("### Summary Statistics")
            
            # Identify numeric columns for statistics
            numeric_cols = filtered_assets.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                # Select columns for summary
                selected_cols = st.multiselect(
                    "Select columns for summary statistics",
                    options=numeric_cols,
                    default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
                )
                
                if selected_cols:
                    summary_stats = filtered_assets[selected_cols].describe()
                    st.dataframe(summary_stats)
                    
                    # Download option
                    st.download_button(
                        label="Download Summary Statistics",
                        data=convert_df_to_csv(summary_stats.reset_index()),
                        file_name="asset_summary_statistics.csv",
                        mime="text/csv"
                    )
            
            # Show filtered data 
            st.markdown("### Filtered Data")
            st.dataframe(filtered_assets)
            
            # Download option
            st.download_button(
                label="Download Filtered Data",
                data=convert_df_to_csv(filtered_assets),
                file_name="filtered_assets_data.csv",
                mime="text/csv"
            )
        
        elif analysis_type == "Asset Breakdown":
            st.subheader("Asset Breakdown Analysis")
            
            # Select date for pie chart
            selected_date = st.select_slider(
                "Select Date for Asset Breakdown",
                options=sorted(filtered_assets['End of Period'].unique()),
                value=filtered_assets['End of Period'].max()
            )
            
            date_df = filtered_assets[filtered_assets['End of Period'] == selected_date]
            
            if date_df.empty:
                st.warning(f"No data available for {selected_date.strftime('%b %Y')}.")
            else:
                # Create pie chart of asset categories
                category_totals = []
                category_names = []
                
                for category in asset_categories:
                    if f'Total {category}' in date_df.columns:
                        category_names.append(category)
                        category_totals.append(date_df[f'Total {category}'].iloc[0])
                
                if category_names:
                    pie_data = pd.DataFrame({
                        'Category': category_names,
                        'Value': category_totals
                    })
                    
                    fig = px.pie(
                        pie_data, 
                        values='Value', 
                        names='Category',
                        title=f'Asset Composition as of {selected_date.strftime("%b %Y")}',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create bar chart for detailed breakdown within categories
                    st.markdown("### Detailed Breakdown by Category")
                    
                    selected_category = st.selectbox(
                        "Select Category for Detailed Breakdown",
                        list(asset_categories.keys())
                    )
                    
                    category_columns = asset_categories[selected_category]
                    numeric_cols = [col for col in category_columns if date_df[col].dtype in [np.float64, np.int64, float, int]]
                    
                    if numeric_cols:
                        detailed_data = pd.DataFrame({
                            'Item': numeric_cols,
                            'Value': [date_df[col].iloc[0] for col in numeric_cols]
                        })
                        
                        # Sort by value
                        detailed_data = detailed_data.sort_values('Value', ascending=False)
                        
                        fig = px.bar(
                            detailed_data,
                            x='Item',
                            y='Value',
                            title=f'Detailed Breakdown of {selected_category} as of {selected_date.strftime("%b %Y")}',
                            template='plotly_white'
                        )
                        
                        fig.update_layout(xaxis_tickangle=-45)
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No numeric data available for {selected_category}")
                else:
                    st.info("Could not calculate category totals from available data")
        
        elif analysis_type == "Time Series Analysis":
            st.subheader("Asset Time Series Analysis")
            
            # Flatten the categories for selection
            all_asset_columns = []
            for category, columns in asset_categories.items():
                for col in columns:
                    if filtered_assets[col].dtype in [np.float64, np.int64, float, int]:
                        all_asset_columns.append(col)
            
            # Add total for each category for selection
            category_totals = [f'Total {category}' for category in asset_categories if f'Total {category}' in filtered_assets.columns]
            all_asset_columns.extend(category_totals)
            
            # Allow user to select metrics to visualize
            selected_metrics = st.multiselect(
                "Select Metrics to Visualize",
                options=sorted(all_asset_columns),
                default=category_totals[:3] if len(category_totals) >= 3 else category_totals
            )
            
            if selected_metrics:
                # Create time series chart
                fig = go.Figure()
                
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_assets['End of Period'],
                        y=filtered_assets[metric],
                        name=metric
                    ))
                
                fig.update_layout(
                    title="Asset Metrics Over Time",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analyze trends with rolling averages
                st.markdown("### Trend Analysis with Moving Averages")
                
                window_size = st.slider("Select Window Size for Moving Average", 1, 12, 3)
                
                # Calculate moving averages
                for metric in selected_metrics:
                    filtered_assets[f'{metric} MA'] = filtered_assets[metric].rolling(window=window_size).mean()
                
                # Create chart with moving averages
                fig = go.Figure()
                
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_assets['End of Period'],
                        y=filtered_assets[metric],
                        name=metric,
                        line=dict(dash='dot')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=filtered_assets['End of Period'],
                        y=filtered_assets[f'{metric} MA'],
                        name=f'{metric} {window_size}-Month MA',
                        line=dict(width=3)
                    ))
                
                fig.update_layout(
                    title=f"Asset Trends with {window_size}-Month Moving Averages",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select at least one metric to visualize")
        
        elif analysis_type == "Asset Growth":
            st.subheader("Asset Growth Analysis")
            
            # Get category totals
            category_totals = [f'Total {category}' for category in asset_categories if f'Total {category}' in filtered_assets.columns]
            
            # Allow user to select growth rate period
            growth_period = st.select_slider(
                "Select Growth Rate Period",
                options=[1, 3, 6, 12],
                value=12,
                format_func=lambda x: f"{x} Month{'s' if x > 1 else ''}"
            )
            
            # Calculate growth rates for each metric
            for metric in category_totals:
                filtered_assets[f'{metric} Growth Rate'] = filtered_assets[metric].pct_change(periods=growth_period) * 100
            
            growth_rate_columns = [f'{metric} Growth Rate' for metric in category_totals]
            
            # Select metrics for visualization
            selected_growth_metrics = st.multiselect(
                "Select Growth Metrics to Visualize",
                options=growth_rate_columns,
                default=growth_rate_columns[:3] if len(growth_rate_columns) >= 3 else growth_rate_columns
            )
            
            if selected_growth_metrics:
                # Create line chart for growth rates
                fig = go.Figure()
                
                for metric in selected_growth_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_assets['End of Period'][growth_period:],  # Skip initial NaN values
                        y=filtered_assets[metric][growth_period:],
                        name=metric.replace(' Growth Rate', '')
                    ))
                
                fig.update_layout(
                    title=f"{growth_period}-Month Growth Rates of Asset Categories",
                    xaxis_title="Date",
                    yaxis_title="Growth Rate (%)",
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Add zero line for reference
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics for growth rates
                st.markdown("### Growth Rate Statistics")
                
                growth_stats = filtered_assets[selected_growth_metrics].describe()
                st.dataframe(growth_stats)
                
                # Download option
                st.download_button(
                    label="Download Growth Rate Statistics",
                    data=convert_df_to_csv(growth_stats.reset_index()),
                    file_name="asset_growth_statistics.csv",
                    mime="text/csv"
                )
            else:
                st.info("Please select at least one growth metric to visualize")
    
    # LIABILITIES ANALYSIS PAGE - Similar structure to Assets Analysis
    elif page == "Liabilities Analysis":
        st.header("💼 Liabilities Analysis")
        st.markdown("Explore and analyze Sri Lankan financial liabilities over time")
        
        # Add analysis type selection to sidebar
        analysis_type = st.sidebar.selectbox(
            "Select Liabilities Analysis Type",
            ["Overview", "Liability Breakdown", "Time Series Analysis", "Liability Growth"]
        )
        
        if analysis_type == "Overview":
            st.subheader("Liabilities Overview")
            
            # Show summary statistics
            st.markdown("### Summary Statistics")
            
            # Identify numeric columns for statistics
            numeric_cols = filtered_liabilities.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                # Select columns for summary
                selected_cols = st.multiselect(
                    "Select columns for summary statistics",
                    options=numeric_cols,
                    default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
                )
                
                if selected_cols:
                    summary_stats = filtered_liabilities[selected_cols].describe()
                    st.dataframe(summary_stats)
                    
                    # Download option
                    st.download_button(
                        label="Download Summary Statistics",
                        data=convert_df_to_csv(summary_stats.reset_index()),
                        file_name="liability_summary_statistics.csv",
                        mime="text/csv"
                    )
            
            # Show filtered data 
            st.markdown("### Filtered Data")
            st.dataframe(filtered_liabilities)
            
            # Download option
            st.download_button(
                label="Download Filtered Data",
                data=convert_df_to_csv(filtered_liabilities),
                file_name="filtered_liabilities_data.csv",
                mime="text/csv"
            )
        
        elif analysis_type == "Liability Breakdown":
            st.subheader("Liability Breakdown Analysis")
            
            # Rest of liability breakdown analysis code
            # Similar to Asset Breakdown but using liability categories
            
            # Select date for pie chart
            selected_date = st.select_slider(
                "Select Date for Liability Breakdown",
                options=sorted(filtered_liabilities['End of Period'].unique()),
                value=filtered_liabilities['End of Period'].max()
            )
            
            date_df = filtered_liabilities[filtered_liabilities['End of Period'] == selected_date]
            
            if date_df.empty:
                st.warning(f"No data available for {selected_date.strftime('%b %Y')}.")
            else:
                # Create pie chart of liability categories
                category_totals = []
                category_names = []
                
                for category in liability_categories:
                    if f'Total {category}' in date_df.columns:
                        category_names.append(category)
                        category_totals.append(date_df[f'Total {category}'].iloc[0])
                
                if category_names:
                    pie_data = pd.DataFrame({
                        'Category': category_names,
                        'Value': category_totals
                    })
                    
                    fig = px.pie(
                        pie_data, 
                        values='Value', 
                        names='Category',
                        title=f'Liability Composition as of {selected_date.strftime("%b %Y")}',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed breakdown by category
                    # Similar to the asset breakdown section
                    st.markdown("### Detailed Breakdown by Category")
                    
                    selected_category = st.selectbox(
                        "Select Category for Detailed Breakdown",
                        list(liability_categories.keys())
                    )
                    
                    category_columns = liability_categories[selected_category]
                    numeric_cols = [col for col in category_columns if date_df[col].dtype in [np.float64, np.int64, float, int]]
                    
                    if numeric_cols:
                        detailed_data = pd.DataFrame({
                            'Item': numeric_cols,
                            'Value': [date_df[col].iloc[0] for col in numeric_cols]
                        })
                        
                        # Sort by value
                        detailed_data = detailed_data.sort_values('Value', ascending=False)
                        
                        fig = px.bar(
                            detailed_data,
                            x='Item',
                            y='Value',
                            title=f'Detailed Breakdown of {selected_category} as of {selected_date.strftime("%b %Y")}',
                            template='plotly_white'
                        )
                        
                        fig.update_layout(xaxis_tickangle=-45)
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No numeric data available for {selected_category}")
                else:
                    st.info("Could not calculate category totals from available data")
                    
        elif analysis_type == "Time Series Analysis":
            # Similar to Asset Time Series Analysis but for liabilities
            st.subheader("Liability Time Series Analysis")
            
            # Get all liability columns
            all_liability_columns = []
            for category, columns in liability_categories.items():
                for col in columns:
                    if filtered_liabilities[col].dtype in [np.float64, np.int64, float, int]:
                        all_liability_columns.append(col)
            
            # Add category totals
            category_totals = [f'Total {category}' for category in liability_categories if f'Total {category}' in filtered_liabilities.columns]
            all_liability_columns.extend(category_totals)
            
            # Select metrics to visualize
            selected_metrics = st.multiselect(
                "Select Metrics to Visualize",
                options=sorted(all_liability_columns),
                default=category_totals[:3] if len(category_totals) >= 3 else category_totals
            )
            
            if selected_metrics:
                # Create time series chart
                fig = go.Figure()
                
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_liabilities['End of Period'],
                        y=filtered_liabilities[metric],
                        name=metric
                    ))
                
                fig.update_layout(
                    title="Liability Metrics Over Time",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Moving averages - similar to assets analysis
                st.markdown("### Trend Analysis with Moving Averages")
                
                window_size = st.slider("Select Window Size for Moving Average", 1, 12, 3)
                
                # Calculate moving averages
                for metric in selected_metrics:
                    filtered_liabilities[f'{metric} MA'] = filtered_liabilities[metric].rolling(window=window_size).mean()
                
                # Create chart with moving averages
                fig = go.Figure()
                
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_liabilities['End of Period'],
                        y=filtered_liabilities[metric],
                        name=metric,
                        line=dict(dash='dot')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=filtered_liabilities['End of Period'],
                        y=filtered_liabilities[f'{metric} MA'],
                        name=f'{metric} {window_size}-Month MA',
                        line=dict(width=3)
                    ))
                
                fig.update_layout(
                    title=f"Liability Trends with {window_size}-Month Moving Averages",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select at least one metric to visualize")
                
        elif analysis_type == "Liability Growth":
            # Similar to Asset Growth analysis
            st.subheader("Liability Growth Analysis")
            
            # Get category totals
            category_totals = [f'Total {category}' for category in liability_categories if f'Total {category}' in filtered_liabilities.columns]
            
            # Growth rate period selection
            growth_period = st.select_slider(
                "Select Growth Rate Period",
                options=[1, 3, 6, 12],
                value=12,
                format_func=lambda x: f"{x} Month{'s' if x > 1 else ''}"
            )
            
            # Calculate growth rates
            for metric in category_totals:
                filtered_liabilities[f'{metric} Growth Rate'] = filtered_liabilities[metric].pct_change(periods=growth_period) * 100
            
            growth_rate_columns = [f'{metric} Growth Rate' for metric in category_totals]
            
            # Select metrics for visualization
            selected_growth_metrics = st.multiselect(
                "Select Growth Metrics to Visualize",
                options=growth_rate_columns,
                default=growth_rate_columns[:3] if len(growth_rate_columns) >= 3 else growth_rate_columns
            )
            
            if selected_growth_metrics:
                # Create line chart for growth rates
                fig = go.Figure()
                
                for metric in selected_growth_metrics:
                    fig.add_trace(go.Scatter(
                        x=filtered_liabilities['End of Period'][growth_period:],
                        y=filtered_liabilities[metric][growth_period:],
                        name=metric.replace(' Growth Rate', '')
                    ))
                
                fig.update_layout(
                    title=f"{growth_period}-Month Growth Rates of Liability Categories",
                    xaxis_title="Date",
                    yaxis_title="Growth Rate (%)",
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Add zero line for reference
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics
                st.markdown("### Growth Rate Statistics")
                
                growth_stats = filtered_liabilities[selected_growth_metrics].describe()
                st.dataframe(growth_stats)
                
                # Download option
                st.download_button(
                    label="Download Growth Rate Statistics",
                    data=convert_df_to_csv(growth_stats.reset_index()),
                    file_name="liability_growth_statistics.csv",
                    mime="text/csv"
                )
            else:
                st.info("Please select at least one growth metric to visualize")
    
    # COMPARATIVE ANALYSIS PAGE
    elif page == "Comparative Analysis":
        st.header("⚖️ Comparative Analysis")
        st.markdown("Compare assets and liabilities to gain deeper insights into Sri Lanka's financial position")
        
        # Analysis type selection
        analysis_type = st.sidebar.selectbox(
            "Select Comparative Analysis Type",
            ["Asset vs Liability Trends", "Asset-Liability Ratio", "Category Composition", "Correlation Analysis"]
        )
        
        # Find common dates between assets and liabilities
        common_dates = sorted(list(set(filtered_assets['End of Period']) & set(filtered_liabilities['End of Period'])))
        
        if not common_dates:
            st.warning("No common dates found between assets and liabilities datasets for the selected period.")
            st.stop()
        
        # Filter data to common dates
        assets_common = filtered_assets[filtered_assets['End of Period'].isin(common_dates)]
        liabilities_common = filtered_liabilities[filtered_liabilities['End of Period'].isin(common_dates)]
        
        if analysis_type == "Asset vs Liability Trends":
            st.subheader("Asset vs Liability Trends Over Time")
            
            # Get key asset and liability columns
            asset_key_columns = []
            for col in assets_common.columns:
                if any(x in col for x in ['Total Assets', 'Cash', 'Investments', 'Loans and Advances']) or col.startswith('Total '):
                    if assets_common[col].dtype in [np.float64, np.int64, float, int]:
                        asset_key_columns.append(col)
            
            liability_key_columns = []
            for col in liabilities_common.columns:
                if any(x in col for x in ['Total All Deposits', 'Paid-up Capital', 'Borrowings']) or col.startswith('Total '):
                    if liabilities_common[col].dtype in [np.float64, np.int64, float, int]:
                        liability_key_columns.append(col)
            
            # Allow user to select metrics to compare
            st.markdown("### Select Metrics to Compare")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_asset_metric = st.selectbox(
                    "Select Asset Metric",
                    asset_key_columns
                )
            
            with col2:
                selected_liability_metric = st.selectbox(
                    "Select Liability Metric",
                    liability_key_columns
                )
            
            # Merge the data
            assets_selected = assets_common[['End of Period', selected_asset_metric]]
            liabilities_selected = liabilities_common[['End of Period', selected_liability_metric]]
            merged_df = pd.merge(assets_selected, liabilities_selected, on='End of Period')
            
            # Create comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=merged_df['End of Period'],
                y=merged_df[selected_asset_metric],
                name=selected_asset_metric,
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=merged_df['End of Period'],
                y=merged_df[selected_liability_metric],
                name=selected_liability_metric,
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title=f"Comparison of {selected_asset_metric} vs {selected_liability_metric}",
                xaxis_title="Date",
                yaxis_title="Value",
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display summary statistics
            st.markdown("### Summary Statistics")
            
            summary_df = pd.DataFrame({
                'Metric': [selected_asset_metric, selected_liability_metric],
                'Mean': [merged_df[selected_asset_metric].mean(), merged_df[selected_liability_metric].mean()],
                'Median': [merged_df[selected_asset_metric].median(), merged_df[selected_liability_metric].median()],
                'Min': [merged_df[selected_asset_metric].min(), merged_df[selected_liability_metric].min()],
                'Max': [merged_df[selected_asset_metric].max(), merged_df[selected_liability_metric].max()],
                'Std Dev': [merged_df[selected_asset_metric].std(), merged_df[selected_liability_metric].std()]
            })
            
            st.dataframe(summary_df)
            
            # Percentage difference chart
            st.markdown("### Percentage Difference Chart")
            
            # Calculate percentage difference
            merged_df['Percentage Difference'] = ((merged_df[selected_asset_metric] - 
                                                merged_df[selected_liability_metric]) / 
                                               merged_df[selected_liability_metric]) * 100
            
            fig = px.line(
                merged_df,
                x='End of Period',
                y='Percentage Difference',
                title=f"Percentage Difference Between {selected_asset_metric} and {selected_liability_metric}",
                labels={'End of Period': 'Date', 'Percentage Difference': 'Percentage Difference (%)'},
                template="plotly_white"
            )
            
            # Add reference line at 0
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Asset-Liability Ratio":
            st.subheader("Asset-Liability Ratio Analysis")
            
            # Calculate key ratios
            
            # 1. Assets to Liabilities Ratio
            st.markdown("### Assets to Liabilities Ratio")
            
            # Get total assets and liabilities
            asset_totals = [col for col in assets_common.columns if col.startswith('Total ')]
            liability_totals = [col for col in liabilities_common.columns if col.startswith('Total ')]
            
            # Allow user to select specific metrics for ratio calculation
            col1, col2 = st.columns(2)
            
            with col1:
                selected_asset = st.selectbox(
                    "Select Asset Metric for Ratio",
                    asset_totals if asset_totals else [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            with col2:
                selected_liability = st.selectbox(
                    "Select Liability Metric for Ratio",
                    liability_totals if liability_totals else [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            # Merge data and calculate ratio
            assets_selected = assets_common[['End of Period', selected_asset]]
            liabilities_selected = liabilities_common[['End of Period', selected_liability]]
            ratio_df = pd.merge(assets_selected, liabilities_selected, on='End of Period')
            
            ratio_df['Assets to Liabilities Ratio'] = ratio_df[selected_asset] / ratio_df[selected_liability]
            
            # Create ratio chart
            fig = px.line(
                ratio_df,
                x='End of Period',
                y='Assets to Liabilities Ratio',
                title=f"Ratio of {selected_asset} to {selected_liability}",
                labels={'End of Period': 'Date', 'Assets to Liabilities Ratio': 'Ratio'},
                template="plotly_white"
            )
            
            # Add reference line at 1.0
            fig.add_hline(y=1, line_dash="dash", line_color="red")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics for the ratio
            stats = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    ratio_df['Assets to Liabilities Ratio'].mean(),
                    ratio_df['Assets to Liabilities Ratio'].median(),
                    ratio_df['Assets to Liabilities Ratio'].min(),
                    ratio_df['Assets to Liabilities Ratio'].max(),
                    ratio_df['Assets to Liabilities Ratio'].std()
                ]
            })
            
            st.dataframe(stats)
            
            # Interpretation
            st.markdown("""
            **Interpretation:** 
            - Ratio > 1: Assets exceed liabilities, indicating positive net worth.
            - Ratio = 1: Assets equal liabilities, indicating zero net worth.
            - Ratio < 1: Liabilities exceed assets, potentially indicating financial distress.
            """)
        
        elif analysis_type == "Category Composition":
            st.subheader("Category Composition Analysis")
            
            # Get asset and liability categories
            asset_categories_totals = [col for col in assets_common.columns if col.startswith('Total ') and col != 'Total Assets']
            liability_categories_totals = [col for col in liabilities_common.columns if col.startswith('Total ') and col != 'Total Liabilities']
            
            # Select date for comparison
            selected_date = st.select_slider(
                "Select Date for Composition Analysis",
                options=common_dates,
                value=common_dates[-1]
            )
            
            assets_date = assets_common[assets_common['End of Period'] == selected_date]
            liabilities_date = liabilities_common[liabilities_common['End of Period'] == selected_date]
            
            if assets_date.empty or liabilities_date.empty:
                st.warning(f"No data available for {selected_date.strftime('%b %Y')}.")
            else:
                # Create side-by-side pie charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Asset composition
                    if asset_categories_totals:
                        asset_pie_data = pd.DataFrame({
                            'Category': [cat.replace('Total ', '') for cat in asset_categories_totals],
                            'Value': [assets_date[col].iloc[0] for col in asset_categories_totals]
                        })
                        
                        fig = px.pie(
                            asset_pie_data, 
                            values='Value', 
                            names='Category',
                            title=f'Asset Composition as of {selected_date.strftime("%b %Y")}',
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No asset categories available for visualization")
                
                with col2:
                    # Liability composition
                    if liability_categories_totals:
                        liability_pie_data = pd.DataFrame({
                            'Category': [cat.replace('Total ', '') for cat in liability_categories_totals],
                            'Value': [liabilities_date[col].iloc[0] for col in liability_categories_totals]
                        })
                        
                        fig = px.pie(
                            liability_pie_data, 
                            values='Value', 
                            names='Category',
                            title=f'Liability Composition as of {selected_date.strftime("%b %Y")}',
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No liability categories available for visualization")
                
                # Compare composition over time
                st.markdown("### Composition Change Over Time")
                
                # Select start and end dates for comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    start_compare_date = st.selectbox(
                        "Select Start Date",
                        options=common_dates,
                        index=0
                    )
                
                with col2:
                    end_compare_date = st.selectbox(
                        "Select End Date",
                        options=common_dates,
                        index=len(common_dates) - 1
                    )
                
                # Create function to compute composition change
                def get_composition_change(df, date1, date2, categories):
                    date1_data = df[df['End of Period'] == date1]
                    date2_data = df[df['End of Period'] == date2]
                    
                    changes = []
                    for category in categories:
                        cat_name = category.replace('Total ', '')
                        value1 = date1_data[category].iloc[0] if not date1_data.empty else 0
                        value2 = date2_data[category].iloc[0] if not date2_data.empty else 0
                        
                        changes.append({
                            'Category': cat_name,
                            'Start Value': value1,
                            'End Value': value2,
                            'Absolute Change': value2 - value1,
                            'Percent Change': ((value2 - value1) / value1 * 100) if value1 != 0 else float('inf')
                        })
                    
                    return pd.DataFrame(changes)
                
                # Calculate and display changes for assets and liabilities
                if asset_categories_totals:
                    st.markdown("#### Asset Composition Change")
                    asset_changes = get_composition_change(assets_common, start_compare_date, end_compare_date, asset_categories_totals)
                    st.dataframe(asset_changes)
                
                if liability_categories_totals:
                    st.markdown("#### Liability Composition Change")
                    liability_changes = get_composition_change(liabilities_common, start_compare_date, end_compare_date, liability_categories_totals)
                    st.dataframe(liability_changes)
        
        elif analysis_type == "Correlation Analysis":
            st.subheader("Correlation Analysis")
            
            # Select asset and liability metrics for correlation
            asset_numeric_cols = [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            liability_numeric_cols = [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            
            st.markdown("### Select Metrics for Correlation Analysis")
            
            # Select metrics for correlation
            col1, col2 = st.columns(2)
            
            with col1:
                selected_asset_cols = st.multiselect(
                    "Select Asset Metrics",
                    options=asset_numeric_cols,
                    default=asset_numeric_cols[:2] if len(asset_numeric_cols) >= 2 else asset_numeric_cols
                )
            
            with col2:
                selected_liability_cols = st.multiselect(
                    "Select Liability Metrics",
                    options=liability_numeric_cols,
                    default=liability_numeric_cols[:2] if len(liability_numeric_cols) >= 2 else liability_numeric_cols
                )
            
            if selected_asset_cols and selected_liability_cols:
                # Prepare data for correlation analysis
                assets_selected = assets_common[['End of Period'] + selected_asset_cols]
                liabilities_selected = liabilities_common[['End of Period'] + selected_liability_cols]
                merged_df = pd.merge(assets_selected, liabilities_selected, on='End of Period')
                
                # Calculate correlation matrix
                correlation_cols = selected_asset_cols + selected_liability_cols
                corr_matrix = merged_df[correlation_cols].corr()
                
                # Display correlation matrix
                st.markdown("### Correlation Matrix")
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    labels=dict(x="Variables", y="Variables", color="Correlation"),
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    color_continuous_scale='RdBu_r'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Highlight strong correlations
                st.markdown("### Strong Correlations")
                
                strong_corr = []
                for i in range(len(correlation_cols)):
                    for j in range(i+1, len(correlation_cols)):
                        var1 = correlation_cols[i]
                        var2 = correlation_cols[j]
                        corr_val = corr_matrix.iloc[i, j]
                        
                        if abs(corr_val) > 0.7:  # Threshold for strong correlation
                            strong_corr.append({
                                'Variable 1': var1,
                                'Variable 2': var2,
                                'Correlation': corr_val,
                                'Strength': 'Strong Positive' if corr_val > 0 else 'Strong Negative'
                            })
                
                if strong_corr:
                    st.dataframe(pd.DataFrame(strong_corr))
                else:
                    st.info("No strong correlations found between the selected variables.")
                
                # Scatter plot for selected pair
                st.markdown("### Scatter Plot for Selected Pair")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    x_var = st.selectbox("Select X Variable", correlation_cols)
                
                with col2:
                    y_var = st.selectbox("Select Y Variable", correlation_cols, index=1 if len(correlation_cols) > 1 else 0)
                
                fig = px.scatter(
                    merged_df,
                    x=x_var,
                    y=y_var,
                    trendline="ols",
                    title=f"Scatter Plot: {x_var} vs {y_var}",
                    labels={x_var: x_var, y_var: y_var},
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate correlation value
                corr_val = merged_df[x_var].corr(merged_df[y_var])
                st.metric("Correlation Coefficient", f"{corr_val:.4f}")
            else:
                st.info("Please select at least one metric from each category for correlation analysis.")
    
    # FINANCIAL RATIOS PAGE
    elif page == "Financial Ratios":
        st.header("📈 Financial Ratios Analysis")
        st.markdown("Explore key financial ratios to understand Sri Lanka's financial health")
        
        # Ratio type selection
        ratio_type = st.sidebar.selectbox(
            "Select Ratio Type",
            ["Asset-Liability Ratios", "Liquidity Ratios", "Efficiency Ratios", "Growth Rates", "Custom Ratio"]
        )
        
        # Find common dates between assets and liabilities
        common_dates = sorted(list(set(filtered_assets['End of Period']) & set(filtered_liabilities['End of Period'])))
        
        if not common_dates:
            st.warning("No common dates found between assets and liabilities datasets for the selected period.")
            st.stop()
        
        # Filter data to common dates
        assets_common = filtered_assets[filtered_assets['End of Period'].isin(common_dates)]
        liabilities_common = filtered_liabilities[filtered_liabilities['End of Period'].isin(common_dates)]
        
        # Merge data
        merged_df = pd.merge(assets_common, liabilities_common, on='End of Period', suffixes=('_asset', '_liability'))
        
        if ratio_type == "Asset-Liability Ratios":
            st.subheader("Asset-Liability Ratios")
            
            # Get total assets and liabilities
            asset_totals = [col for col in assets_common.columns if col.startswith('Total ')]
            liability_totals = [col for col in liabilities_common.columns if col.startswith('Total ')]
            
            # Allow user to select specific metrics for ratio calculation
            col1, col2 = st.columns(2)
            
            with col1:
                selected_asset = st.selectbox(
                    "Select Asset Metric",
                    asset_totals if asset_totals else [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            with col2:
                selected_liability = st.selectbox(
                    "Select Liability Metric",
                    liability_totals if liability_totals else [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            # Calculate ratio
            assets_selected = assets_common[['End of Period', selected_asset]]
            liabilities_selected = liabilities_common[['End of Period', selected_liability]]
            ratio_df = pd.merge(assets_selected, liabilities_selected, on='End of Period')
            
            ratio_df['Assets to Liabilities Ratio'] = ratio_df[selected_asset] / ratio_df[selected_liability]
            
            # Create ratio chart
            fig = px.line(
                ratio_df,
                x='End of Period',
                y='Assets to Liabilities Ratio',
                title=f"Ratio of {selected_asset} to {selected_liability}",
                labels={'End of Period': 'Date', 'Assets to Liabilities Ratio': 'Ratio'},
                template="plotly_white"
            )
            
            # Add reference line at 1.0
            fig.add_hline(y=1, line_dash="dash", line_color="red")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics for the ratio
            stats = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    ratio_df['Assets to Liabilities Ratio'].mean(),
                    ratio_df['Assets to Liabilities Ratio'].median(),
                    ratio_df['Assets to Liabilities Ratio'].min(),
                    ratio_df['Assets to Liabilities Ratio'].max(),
                    ratio_df['Assets to Liabilities Ratio'].std()
                ]
            })
            
            st.dataframe(stats)
            
            # Interpretation
            st.markdown("""
            **Interpretation:** 
            - Ratio > 1: Assets exceed liabilities, indicating positive net worth.
            - Ratio = 1: Assets equal liabilities, indicating zero net worth.
            - Ratio < 1: Liabilities exceed assets, potentially indicating financial distress.
            """)
        
        # Other ratio types would be implemented similarly
        elif ratio_type == "Liquidity Ratios":
            st.subheader("Liquidity Ratios")
            
            # Calculate liquidity ratios
            
            # 1. Cash to Deposit Ratio
            st.markdown("### Cash to Deposit Ratio")
            
            # Get cash and deposit columns
            cash_cols = [col for col in assets_common.columns if any(x in col for x in ['Cash', 'Due from', 'Foreign Currency'])]
            deposit_cols = [col for col in liabilities_common.columns if 'Deposits' in col]
            
            # Allow users to select specific columns for ratio
            col1, col2 = st.columns(2)
            
            with col1:
                selected_cash = st.selectbox(
                    "Select Cash Metric",
                    cash_cols if cash_cols else [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            with col2:
                selected_deposit = st.selectbox(
                    "Select Deposit Metric",
                    deposit_cols if deposit_cols else [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            # Calculate ratio
            cash_selected = assets_common[['End of Period', selected_cash]]
            deposit_selected = liabilities_common[['End of Period', selected_deposit]]
            liquidity_df = pd.merge(cash_selected, deposit_selected, on='End of Period')
            
            liquidity_df['Cash to Deposit Ratio'] = liquidity_df[selected_cash] / liquidity_df[selected_deposit]
            
            # Create ratio chart
            fig = px.line(
                liquidity_df,
                x='End of Period',
                y='Cash to Deposit Ratio',
                title=f"Cash to Deposit Ratio ({selected_cash} to {selected_deposit})",
                labels={'End of Period': 'Date', 'Cash to Deposit Ratio': 'Ratio'},
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics for the ratio
            stats = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    liquidity_df['Cash to Deposit Ratio'].mean(),
                    liquidity_df['Cash to Deposit Ratio'].median(),
                    liquidity_df['Cash to Deposit Ratio'].min(),
                    liquidity_df['Cash to Deposit Ratio'].max(),
                    liquidity_df['Cash to Deposit Ratio'].std()
                ]
            })
            
            st.dataframe(stats)
            
            # Interpretation
            st.markdown("""
            **Interpretation:** 
            - Higher Ratio: Indicates better ability to meet immediate withdrawal demands.
            - Lower Ratio: May indicate higher utilization of deposits for lending.
            """)
            
        elif ratio_type == "Efficiency Ratios":
            st.subheader("Efficiency Ratios")
            
            # Loan to Deposit Ratio
            st.markdown("### Loan to Deposit Ratio")
            
            # Get loan and deposit columns
            loan_cols = [col for col in assets_common.columns if 'Loans and Advances' in col]
            deposit_cols = [col for col in liabilities_common.columns if 'Deposits' in col]
            
            # Allow users to select specific columns for ratio
            col1, col2 = st.columns(2)
            
            with col1:
                selected_loan = st.selectbox(
                    "Select Loan Metric",
                    loan_cols if loan_cols else [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            with col2:
                selected_deposit = st.selectbox(
                    "Select Deposit Metric",
                    deposit_cols if deposit_cols else [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int]]
                )
            
            # Calculate ratio
            loan_selected = assets_common[['End of Period', selected_loan]]
            deposit_selected = liabilities_common[['End of Period', selected_deposit]]
            efficiency_df = pd.merge(loan_selected, deposit_selected, on='End of Period')
            
            efficiency_df['Loan to Deposit Ratio'] = efficiency_df[selected_loan] / efficiency_df[selected_deposit]
            
            # Create ratio chart
            fig = px.line(
                efficiency_df,
                x='End of Period',
                y='Loan to Deposit Ratio',
                title=f"Loan to Deposit Ratio ({selected_loan} to {selected_deposit})",
                labels={'End of Period': 'Date', 'Loan to Deposit Ratio': 'Ratio'},
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics for the ratio
            stats = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                'Value': [
                    efficiency_df['Loan to Deposit Ratio'].mean(),
                    efficiency_df['Loan to Deposit Ratio'].median(),
                    efficiency_df['Loan to Deposit Ratio'].min(),
                    efficiency_df['Loan to Deposit Ratio'].max(),
                    efficiency_df['Loan to Deposit Ratio'].std()
                ]
            })
            
            st.dataframe(stats)
            
            # Interpretation
            st.markdown("""
            **Interpretation:**
            - High Ratio: Bank is lending more relative to deposits, potentially higher returns but also higher risk.
            - Low Ratio: Bank is more conservative in lending, potentially lower returns but also lower risk.
            - Optimal range typically varies by country and economic conditions.
            """)
            
        elif ratio_type == "Growth Rates":
            st.subheader("Growth Rate Analysis")
            
            # Allow user to select growth rate period
            growth_period = st.select_slider(
                "Select Growth Rate Period",
                options=[1, 3, 6, 12],
                value=12,
                format_func=lambda x: f"{x} Month{'s' if x > 1 else ''}"
            )
            
            # Select asset and liability metrics for growth analysis
            asset_numeric_cols = [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            liability_numeric_cols = [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            
            # Allow user to select metrics
            selected_metrics = st.multiselect(
                "Select Metrics for Growth Analysis",
                options=['Assets: ' + col for col in asset_numeric_cols] + ['Liabilities: ' + col for col in liability_numeric_cols],
                default=['Assets: ' + asset_numeric_cols[0], 'Liabilities: ' + liability_numeric_cols[0]] if asset_numeric_cols and liability_numeric_cols else []
            )
            
            if selected_metrics:
                # Prepare data for growth rate calculation
                growth_df = pd.DataFrame({'End of Period': common_dates})
                
                for metric in selected_metrics:
                    parts = metric.split(': ')
                    if len(parts) == 2:
                        category, col_name = parts
                        
                        if category == 'Assets':
                            series = assets_common.set_index('End of Period')[col_name]
                        else:  # Liabilities
                            series = liabilities_common.set_index('End of Period')[col_name]
                        
                        # Match indices
                        series = series.reindex(growth_df['End of Period'])
                        
                        # Calculate growth rate
                        growth_df[metric] = series.pct_change(periods=growth_period) * 100
                
                # Create line chart for growth rates
                fig = go.Figure()
                
                for metric in selected_metrics:
                    fig.add_trace(go.Scatter(
                        x=growth_df['End of Period'][growth_period:],  # Skip initial NaN values
                        y=growth_df[metric][growth_period:],
                        name=metric
                    ))
                
                fig.update_layout(
                    title=f"{growth_period}-Month Growth Rates",
                    xaxis_title="Date",
                    yaxis_title="Growth Rate (%)",
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Add zero line for reference
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics for growth rates
                st.markdown("### Growth Rate Statistics")
                
                growth_stats = growth_df[selected_metrics].describe()
                st.dataframe(growth_stats)
                
                # Download option
                st.download_button(
                    label="Download Growth Rate Statistics",
                    data=convert_df_to_csv(growth_stats.reset_index()),
                    file_name="growth_rate_statistics.csv",
                    mime="text/csv"
                )
            else:
                st.info("Please select at least one metric for growth rate analysis")
                
        elif ratio_type == "Custom Ratio":
            st.subheader("Custom Ratio Calculator")
            
            # Select columns for numerator and denominator
            st.markdown("### Select Metrics for Custom Ratio")
            
            asset_numeric_cols = [col for col in assets_common.columns if assets_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            liability_numeric_cols = [col for col in liabilities_common.columns if liabilities_common[col].dtype in [np.float64, np.int64, float, int] and col != 'End of Period']
            
            all_metrics = ['Assets: ' + col for col in asset_numeric_cols] + ['Liabilities: ' + col for col in liability_numeric_cols]
            
            col1, col2 = st.columns(2)
            
            with col1:
                numerator = st.selectbox(
                    "Select Numerator",
                    options=all_metrics,
                    index=0 if all_metrics else None
                )
            
            with col2:
                denominator = st.selectbox(
                    "Select Denominator",
                    options=all_metrics,
                    index=1 if len(all_metrics) > 1 else 0 if all_metrics else None
                )
                
            # Custom ratio name
            ratio_name = st.text_input("Enter Custom Ratio Name", f"Custom Ratio: {numerator} / {denominator}" if numerator and denominator else "Custom Ratio")
            
            if numerator and denominator:
                # Extract the actual column names and data sources
                num_parts = numerator.split(': ')
                denom_parts = denominator.split(': ')
                
                if len(num_parts) == 2 and len(denom_parts) == 2:
                    num_category, num_col = num_parts
                    denom_category, denom_col = denom_parts
                    
                    # Create dataframe for custom ratio
                    custom_df = pd.DataFrame({'End of Period': common_dates})
                    
                    # Add numerator
                    if num_category == 'Assets':
                        num_series = assets_common.set_index('End of Period')[num_col]
                    else:  # Liabilities
                        num_series = liabilities_common.set_index('End of Period')[num_col]
                    
                    # Add denominator
                    if denom_category == 'Assets':
                        denom_series = assets_common.set_index('End of Period')[denom_col]
                    else:  # Liabilities
                        denom_series = liabilities_common.set_index('End of Period')[denom_col]
                    
                    # Match indices and calculate ratio
                    num_series = num_series.reindex(custom_df['End of Period'])
                    denom_series = denom_series.reindex(custom_df['End of Period'])
                    
                    custom_df[ratio_name] = num_series / denom_series
                    
                    # Create ratio chart
                    fig = px.line(
                        custom_df,
                        x='End of Period',
                        y=ratio_name,
                        title=f"Custom Ratio: {num_col} / {denom_col}",
                        labels={'End of Period': 'Date', ratio_name: 'Ratio'},
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistics for the custom ratio
                    stats = pd.DataFrame({
                        'Statistic': ['Mean', 'Median', 'Min', 'Max', 'Std Dev'],
                        'Value': [
                            custom_df[ratio_name].mean(),
                            custom_df[ratio_name].median(),
                            custom_df[ratio_name].min(),
                            custom_df[ratio_name].max(),
                            custom_df[ratio_name].std()
                        ]
                    })
                    
                    st.dataframe(stats)
                    
                    # Download data
                    st.download_button(
                        label="Download Custom Ratio Data",
                        data=convert_df_to_csv(custom_df),
                        file_name="custom_ratio_data.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Invalid metric format. Please select valid metrics.")
            else:
                st.info("Please select both numerator and denominator metrics.")
    
    # ABOUT PAGE
    elif page == "About":
        st.header("ℹ️ About This Dashboard")
        
        # Dashboard overview
        st.markdown("""
        ## Sri Lankan Financial Data Analysis Dashboard
        
        This interactive dashboard provides comprehensive analysis and visualization of Sri Lankan financial assets and liabilities data from 1995 to 2023. The dashboard enables users to explore trends, compare metrics, analyze financial ratios, and gain insights into Sri Lanka's financial health over time.
        
        ### Data Source
        
        The data used in this dashboard comes from the Central Bank of Sri Lanka and includes detailed information about various assets and liabilities maintained by financial institutions in Sri Lanka. The datasets include:
        
        1. **Assets Data**: Contains information about cash holdings, investments, loans and advances, and other financial assets.
        2. **Liabilities Data**: Contains information about capital, deposits, borrowings, and other financial liabilities.
        
        ### Dashboard Features
        
        This dashboard offers the following key features:
        
        - **Interactive Time Series Visualizations**: Explore financial trends over customizable time periods
        - **Comprehensive Asset Analysis**: Detailed breakdown and visualization of different asset categories
        - **Detailed Liability Analysis**: In-depth examination of deposit composition and liability trends
        - **Comparative Analysis**: Direct comparison between assets and liabilities to understand financial position
        - **Financial Ratio Analysis**: Calculate and visualize key financial ratios to assess financial health
        - **Customizable Visualizations**: Ability to select specific metrics and visualization types
        - **Data Download**: Download filtered data and analysis results for further research
        
        ### Dashboard Components
        
        The dashboard is organized into several sections for focused analysis:
        
        1. **Home Page**: Overview of the data and quick summary visualizations
        2. **Assets Analysis**: Detailed exploration of financial assets over time
        3. **Liabilities Analysis**: Comprehensive analysis of financial liabilities
        4. **Comparative Analysis**: Compare assets and liabilities trends
        5. **Financial Ratios**: Key financial ratios and indicators
        6. **About**: Information about the dashboard and data sources
        """)
        
        # Data information
        st.subheader("Dataset Details")
        
        # Display dataset information if available
        if 'assets_df' in locals() and 'liabilities_df' in locals():
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Assets Dataset")
                st.markdown(f"**Time Period**: {assets_df['End of Period'].min().strftime('%b %Y')} - {assets_df['End of Period'].max().strftime('%b %Y')}")
                st.markdown(f"**Number of Records**: {len(assets_df)}")
                st.markdown(f"**Number of Variables**: {len(assets_df.columns)}")
                
                # Display column categories
                st.markdown("**Asset Categories**:")
                asset_categories = {
                    "Cash and Balances": [col for col in assets_df.columns if any(x in col for x in ['Cash', 'Due from', 'Foreign Currency'])],
                    "Investments": [col for col in assets_df.columns if 'Investments' in col],
                    "Loans and Advances": [col for col in assets_df.columns if 'Loans and Advances' in col],
                    "Other Assets": [col for col in assets_df.columns if any(x in col for x in ['Bills of Exchange', 'Accrued Interest', 'Other Assets'])]
                }
                
                for category, columns in asset_categories.items():
                    if columns:
                        with st.expander(f"{category} ({len(columns)} variables)"):
                            st.write(", ".join(columns))
            
            with col2:
                st.markdown("### Liabilities Dataset")
                st.markdown(f"**Time Period**: {liabilities_df['End of Period'].min().strftime('%b %Y')} - {liabilities_df['End of Period'].max().strftime('%b %Y')}")
                st.markdown(f"**Number of Records**: {len(liabilities_df)}")
                st.markdown(f"**Number of Variables**: {len(liabilities_df.columns)}")
                
                # Display column categories
                st.markdown("**Liability Categories**:")
                liability_categories = {
                    "Capital": [col for col in liabilities_df.columns if 'Capital' in col or 'Reserves' in col],
                    "Demand Deposits": [col for col in liabilities_df.columns if 'Demand Deposits' in col],
                    "Time and Savings Deposits": [col for col in liabilities_df.columns if 'Time and Savings Deposits' in col],
                    "Borrowings": [col for col in liabilities_df.columns if 'Borrowings' in col],
                    "Other Liabilities": [col for col in liabilities_df.columns if any(x in col for x in ['Bills Payable', 'Accrued Interest', 'Other Liabilities'])]
                }
                
                for category, columns in liability_categories.items():
                    if columns:
                        with st.expander(f"{category} ({len(columns)} variables)"):
                            st.write(", ".join(columns))
        else:
            st.warning("Data not loaded. Please return to the home page.")
        
        # Interpretation guidelines
        st.subheader("Key Financial Indicators Interpretation")
                
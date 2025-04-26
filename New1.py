import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import data_processor as dp

# Set page configuration
st.set_page_config(
    page_title="Liabilities Analysis - Sri Lankan Financial Data Dashboard",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("📊 Liabilities Analysis")
st.markdown("Explore and analyze financial liabilities data for Sri Lanka")

# Check if data is loaded in session state
if 'liabilities_df' not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

# Get data from session state
liabilities_df = st.session_state['liabilities_df']

# Create sidebar for filtering options
st.sidebar.header("Filter Options")

# Date range filter
min_date = liabilities_df['End of Period'].min()
max_date = liabilities_df['End of Period'].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter data by date range
filtered_df = liabilities_df[(liabilities_df['End of Period'] >= pd.Timestamp(start_date)) & 
                            (liabilities_df['End of Period'] <= pd.Timestamp(end_date))]

# Display filter info
st.sidebar.markdown(f"**Selected Period:** {start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}")
st.sidebar.markdown(f"**Number of Records:** {len(filtered_df)}")

# Liability categories selection
liability_categories = dp.get_liability_categories()
selected_categories = st.sidebar.multiselect(
    "Select Liability Categories",
    list(liability_categories.keys()),
    default=list(liability_categories.keys())
)

# Visualization type selection
viz_type = st.sidebar.selectbox(
    "Select Visualization Type",
    ["Time Series", "Bar Chart", "Area Chart", "Scatter Plot", "Heatmap", "Box Plot"]
)

# Get numeric columns for visualization
numeric_cols = [col for col in filtered_df.columns if filtered_df[col].dtype in [np.float64, np.int64, float, int]]

# Remove 'End of Period' if present in numeric_cols
if 'End of Period' in numeric_cols:
    numeric_cols.remove('End of Period')

# List to store visualization metrics
viz_metrics = []

# Fill viz_metrics based on selected categories
for category in selected_categories:
    for pattern in liability_categories[category]:
        matching_cols = [col for col in numeric_cols if pattern in col]
        viz_metrics.extend(matching_cols)

# Make sure we have unique metrics
viz_metrics = list(set(viz_metrics))

# Allow user to select specific metrics for detailed visualization
selected_metrics = st.multiselect(
    "Select Specific Metrics to Visualize",
    viz_metrics,
    default=viz_metrics[:5] if len(viz_metrics) > 5 else viz_metrics
)

# Main content
st.subheader("Liabilities Trend Analysis")

# Display the selected metrics visualization based on the selected visualization type
if selected_metrics:
    if viz_type == "Time Series":
        fig = px.line(
            filtered_df, 
            x='End of Period', 
            y=selected_metrics,
            title="Liabilities Trends Over Time",
            labels={'End of Period': 'Date', 'value': 'Amount'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Bar Chart":
        # For bar chart, we'll show the average value over the selected period
        avg_data = filtered_df[selected_metrics].mean().reset_index()
        avg_data.columns = ['Metric', 'Average Value']
        
        fig = px.bar(
            avg_data,
            x='Metric',
            y='Average Value',
            title="Average Liability Values in Selected Period",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Area Chart":
        fig = px.area(
            filtered_df,
            x='End of Period',
            y=selected_metrics,
            title="Cumulative Liabilities Over Time",
            labels={'End of Period': 'Date', 'value': 'Amount'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Scatter Plot":
        # Choose two metrics for scatter plot
        if len(selected_metrics) >= 2:
            x_metric = st.selectbox("Select X-Axis Metric", selected_metrics)
            y_metric = st.selectbox("Select Y-Axis Metric", [m for m in selected_metrics if m != x_metric])
            
            fig = px.scatter(
                filtered_df,
                x=x_metric,
                y=y_metric,
                title=f"Relationship Between {x_metric} and {y_metric}",
                labels={x_metric: x_metric, y_metric: y_metric},
                template="plotly_white",
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least two metrics for scatter plot visualization.")
            
    elif viz_type == "Heatmap":
        # Create correlation matrix
        corr_matrix = filtered_df[selected_metrics].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            title="Correlation Matrix of Selected Liability Metrics",
            template="plotly_white",
            color_continuous_scale="RdBu_r"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Box Plot":
        # Melt the dataframe to have metrics as a categorical variable
        melted_df = pd.melt(
            filtered_df, 
            id_vars=['End of Period'],
            value_vars=selected_metrics,
            var_name='Metric',
            value_name='Value'
        )
        
        fig = px.box(
            melted_df,
            x='Metric',
            y='Value',
            title="Distribution of Liability Values",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select at least one metric to visualize.")

# Deposit composition analysis
if any('Deposits' in metric for metric in viz_metrics):
    st.subheader("Deposit Composition Analysis")
    
    # Extract all deposit columns
    deposit_cols = [col for col in viz_metrics if 'Deposits' in col]
    
    # Allow user to select specific deposit types
    selected_deposit_types = st.multiselect(
        "Select Deposit Types to Analyze",
        deposit_cols,
        default=deposit_cols[:5] if len(deposit_cols) > 5 else deposit_cols
    )
    
    if selected_deposit_types:
        # Create deposit composition over time
        fig = px.area(
            filtered_df,
            x='End of Period',
            y=selected_deposit_types,
            title="Deposit Composition Over Time",
            labels={'End of Period': 'Date', 'value': 'Amount'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show the percentage composition for the most recent date
        latest_date = filtered_df['End of Period'].max()
        latest_data = filtered_df[filtered_df['End of Period'] == latest_date][selected_deposit_types]
        
        if not latest_data.empty:
            # Calculate percentages
            latest_data_pct = latest_data.div(latest_data.sum(axis=1), axis=0) * 100
            
            # Create pie chart
            fig = px.pie(
                names=selected_deposit_types,
                values=latest_data_pct.iloc[0],
                title=f"Deposit Composition as of {latest_date.strftime('%b %Y')}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one deposit type for composition analysis.")

# Growth rate analysis
st.subheader("Growth Rate Analysis")

# Get available periods for growth rate calculation
growth_periods = [3, 6, 12, 24]
selected_growth_period = st.selectbox(
    "Select Period for Growth Rate Calculation",
    growth_periods,
    index=2  # Default to 12-period (annual) growth
)

if selected_metrics:
    # Calculate growth rates
    growth_df = dp.get_growth_rates(filtered_df, selected_metrics, selected_growth_period)
    
    # Get growth rate columns
    growth_cols = [f"{metric}_Growth" for metric in selected_metrics if f"{metric}_Growth" in growth_df.columns]
    
    if growth_cols:
        # Plot growth rates
        fig = px.line(
            growth_df,
            x='End of Period',
            y=growth_cols,
            title=f"{selected_growth_period}-Period Growth Rates",
            labels={'End of Period': 'Date', 'value': 'Growth Rate (%)'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display average growth rates
        avg_growth = growth_df[growth_cols].mean().reset_index()
        avg_growth.columns = ['Metric', 'Average Growth Rate (%)']
        
        # Clean up metric names
        avg_growth['Metric'] = avg_growth['Metric'].str.replace('_Growth', '')
        
        st.subheader("Average Growth Rates")
        st.dataframe(avg_growth)
    else:
        st.info("Could not calculate growth rates with the selected parameters.")
else:
    st.warning("Please select at least one metric for growth rate analysis.")

# Statistical summary
st.subheader("Statistical Summary")

if selected_metrics:
    # Calculate summary statistics
    stats_df = dp.get_summary_statistics(filtered_df, selected_metrics)
    
    if not stats_df.empty:
        st.dataframe(stats_df)
    else:
        st.info("Could not calculate statistics for the selected metrics.")
else:
    st.warning("Please select at least one metric for statistical summary.")

# Download the filtered data
st.subheader("Download Filtered Data")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')

csv = convert_df_to_csv(filtered_df[['End of Period'] + selected_metrics] if selected_metrics else filtered_df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='sri_lanka_liabilities_data.csv',
    mime='text/csv',
)

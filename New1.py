# 🚀 Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import calendar

# 🚀 Page Config (must be first Streamlit command)
st.set_page_config(page_title="Sri Lanka Banks Dashboard", layout="wide")

# 🇱🇰 Sri Lanka Flag Animated Background + Sidebar Styling
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

        [data-testid="stSidebar"] {
    background: linear-gradient(
        135deg,
        #c49a6c 0%,   
        #FFD700 50%,  
        #c49a6c 100%
    );
    border: 2px solid #8D1B1B;
    border-radius: 20px; /* slightly more rounded */
    padding: 20px;
    margin: 60px 10px 10px 10px; /* top margin added */
    color: black;
    font-weight: bold;
    height: auto; /* let the sidebar height grow naturally */
    position: relative; /* not sticky */
}

        [data-testid="stSidebar"] .css-ng1t4o {
            color: black;
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

# Adjust sidebar height dynamically
st.markdown(
    """
    <script>
    function setSidebarHeight() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.minHeight = (window.innerHeight - 20) + 'px';
        }
    }
    window.addEventListener('load', setSidebarHeight);
    window.addEventListener('resize', setSidebarHeight);
    </script>
    """,
    unsafe_allow_html=True,
)

# 🏦 Title and Description
st.title("🏦 🇱🇰 Sri Lanka Banks: Domestic Banking Insights")
st.markdown("_Tracking assets, loans, and financial strength from 1995 to 2025._")

# 📥 Load Data
@st.cache_data
def load_data():
    assets = pd.read_csv("assets_data_cleaned.csv")
    liabilities = pd.read_csv("liabilties_data_cleaned.csv")
    assets["End of Period"] = pd.to_datetime(assets["End of Period"], errors="coerce")
    liabilities["End of Period"] = pd.to_datetime(liabilities["End of Period"], errors="coerce")
    return assets, liabilities

assets_df, liabilities_df = load_data()

# 📦 Sidebar Controls
st.sidebar.header("🔧 Controls")
dataset_choice = st.sidebar.radio("Select Dataset", ["Assets", "Liabilities"])

# 🎯 Dataset selection
if dataset_choice == "Assets":
    df = assets_df.copy()
    dataset_title = "Assets"
else:
    df = liabilities_df.copy()
    dataset_title = "Liabilities"

filter_col = "End of Period"

# 📆 Sidebar Filter: Select Year Only
if filter_col in df.columns:
    df = df.dropna(subset=[filter_col])
    df['Year'] = df[filter_col].dt.year
    df['Month'] = df[filter_col].dt.month
    df['Month Name'] = df[filter_col].dt.month_name()

    selected_year = st.sidebar.selectbox("Select Year 📅", sorted(df['Year'].unique(), reverse=True))
    df = df[df['Year'] == selected_year]

# 🔑 KPI Section
st.subheader(f"🔑 {dataset_title} Overview ({selected_year})")

# KPI Calculations
total_value = df.select_dtypes(include="number").sum().sum()
average_value = df.select_dtypes(include="number").mean().mean()
biggest_contributor = df.select_dtypes(include="number").sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Total Value", f"Rs. {total_value:,.0f}")
col2.metric("Average per Metric", f"Rs. {average_value:,.0f}")
col3.metric("Top Contributor", biggest_contributor)

# 📈 Charts Section
st.subheader(f"📈 Visual Analysis of {dataset_title} ({selected_year})")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if numeric_cols:
    selected_cols = st.multiselect(
        f"Select one or more {dataset_title} metrics to visualize:", 
        numeric_cols, 
        default=[numeric_cols[0]]
    )

    if selected_cols:
        fig = px.line(
            df.sort_values(by="Month"),
            x="Month Name",
            y=selected_cols,
            markers=True,
            title=f"{', '.join(selected_cols)} Over Months - {selected_year}",
            template="plotly_dark",
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Value", legend_title="Metric")
        fig.update_xaxes(categoryorder='array', categoryarray=list(calendar.month_name)[1:])  # Correct month order
        st.plotly_chart(fig, use_container_width=True)

        # Box plot for distribution of selected metric
        if len(selected_cols) == 1:
            st.plotly_chart(
                px.box(
                    df,
                    y=selected_cols[0],
                    title=f"{selected_cols[0]} Value Distribution ({selected_year})",
                    template="ggplot2"
                ),
                use_container_width=True
            )

else:
    st.warning("No numeric columns available to visualize.")

# 🔍 Insights Section
st.subheader(f"🔎 Correlation Insights ({selected_year})")

# 🔍 Insights Section
st.subheader(f"🔎 Correlation Insights ({selected_year})")

if numeric_cols:
    corr_matrix = df[numeric_cols].corr()

    # Create 4 columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("### 🔵 Heatmap (Seaborn)")
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax, cbar=False)
        st.pyplot(fig)

    with col2:
        st.write("### 🔵 Heatmap (Plotly)")
        fig2 = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu",
            origin="lower",
            title="",
            aspect="auto",
        )
        fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.write("### 🔵 Diverging Correlation Bars")
        corr_unstacked = corr_matrix.iloc[:, 0].sort_values()
        fig3 = px.bar(
            corr_unstacked,
            orientation='h',
            color=corr_unstacked,
            color_continuous_scale='RdBu',
            title="",
        )
        fig3.update_layout(xaxis_title="Correlation with " + corr_unstacked.index[0])
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.write("### 🔵 Correlation Network")
        import networkx as nx

        G = nx.Graph()
        threshold = 0.5  # Only strong correlations

        for i in corr_matrix.columns:
            for j in corr_matrix.columns:
                if i != j and abs(corr_matrix.loc[i, j]) > threshold:
                    G.add_edge(i, j, weight=corr_matrix.loc[i, j])

        fig4 = plt.figure(figsize=(4, 4))
        pos = nx.spring_layout(G, seed=42)
        edges = G.edges()
        weights = [G[u][v]['weight'] for u,v in edges]

        nx.draw(G, pos, with_labels=True, edge_color=weights, edge_cmap=plt.cm.RdBu, node_color='skyblue', node_size=700, font_size=8)
        st.pyplot(fig4)

else:
    st.info("No numeric data available for correlation analysis.")

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

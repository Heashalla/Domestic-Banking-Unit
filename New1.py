# 🚀 Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import calendar
from io import BytesIO
from PIL import Image  # For handling images

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
                #8D1B1B 20%,
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
        #c49a6c 20%,
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
st.sidebar.markdown("<h2 style='color: #8D1B1B; font-weight: bold; margin-bottom: 1.5rem;'>⚙️ Dashboard Settings</h2>", unsafe_allow_html=True)

# Add a logo or thematic image at the top (replace with your URL)
logo_url = "YOUR_LOGO_URL_HERE"  # Replace with your image URL or leave empty
if logo_url != "YOUR_LOGO_URL_HERE":
    try:
        st.sidebar.image(logo_url, width=100)
        st.sidebar.markdown("---")
    except Exception as e:
        st.sidebar.warning(f"Error loading logo: {e}")
        st.sidebar.markdown("---")

st.sidebar.markdown("<h4 style='color: #FFD700;'>📊 Data Selection</h4>", unsafe_allow_html=True)
dataset_choice = st.sidebar.radio("Choose Data View:", ["Assets", "Liabilities"])

st.sidebar.markdown("<h4 style='color: #FFD700; margin-top: 1.5rem;'>💾 Export Options</h4>", unsafe_allow_html=True)
export_format = st.sidebar.radio("Select Format:", ["CSV", "Excel"])

def download_df(dataframe, file_format):
    if file_format == "CSV":
        csv_buffer = dataframe.to_csv(index=False).encode('utf-8')
        return csv_buffer, "text/csv", f"{dataset_choice.lower()}_{selected_year}.csv"
    elif file_format == "Excel":
        excel_buffer = BytesIO()
        dataframe.to_excel(excel_buffer, index=False, sheet_name=dataset_choice)
        excel_buffer.seek(0)
        return excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"{dataset_choice.lower()}_{selected_year}.xlsx"
    return None, None, None

if st.sidebar.button("📤 Download Selected Data"):
    buffer, mime_type, filename = download_df(df, export_format)
    if buffer:
        st.download_button(
            label=f"✅ Download as {export_format}",
            data=buffer,
            file_name=filename,
            mime=mime_type,
            key=f"export_button_{export_format}"
        )
    else:
        st.sidebar.warning("⚠️ Error during export.")

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #FFD700;'>🗓️ Filter by Time</h4>", unsafe_allow_html=True)

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

    selected_year = st.sidebar.selectbox("Choose Year:", sorted(df['Year'].unique(), reverse=True))
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

if numeric_cols:
    corr_matrix = df[numeric_cols].corr()

    # 🔵 Plotly Heatmap
    st.write("### 🔵 Correlation Heatmap (Plotly)")
    fig2 = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu",
        origin="lower",
        title="",
        aspect="auto",
    )
    fig2.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        coloraxis_colorbar=dict(title="Correlation")
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 🔵 Diverging Correlation Bars
    st.write("### 🔵 Diverging Correlation Bars")
    reference_var = numeric_cols[0]
    corr_unstacked = corr_matrix[reference_var].sort_values()

    fig3 = px.bar(
        corr_unstacked,
        orientation='h',
        color=corr_unstacked,
        color_continuous_scale='RdBu',
        title=f"Correlation with {reference_var}",
    )
    fig3.update_layout(
        xaxis_title="Correlation Strength",
        yaxis_title="Variable",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("No numeric data available for correlation analysis.")


# 📎 Footer
st.markdown("---")
st.caption("Developed for Data Science Project Lifecycle Coursework 5DATA004W | University of Westminster")

# Add a thematic image at the bottom of the sidebar (replace with your URL)
footer_image_url = "YOUR_FOOTER_IMAGE_URL_HERE"  # Replace with your image URL or leave empty
if footer_image_url != "YOUR_FOOTER_IMAGE_URL_HERE":
    try:
        st.sidebar.image(footer_image_url, width=50)
    except Exception as e:
        st.sidebar.warning(f"Error loading footer image: {e}")

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
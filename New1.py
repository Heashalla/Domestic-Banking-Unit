# 🚀 Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import calendar
from io import BytesIO
from PIL import Image  # For handling images

# Page Config (must be first Streamlit command)
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
            background: linear-gradient(135deg, #f0f0f0 20%, #e0e0e0 80%); /* Light grey gradient */
            border: 1px solid #8D1B1B;
            border-radius: 10px;
            padding: 20px;
            margin: 60px 10px 10px 10px;
            color: #333; /* Dark grey default text */
            font-family: "Arial", sans-serif; /* Modern sans-serif default */
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: #8D1B1B !important; /* Red for main headings */
            font-family: "Times New Roman", serif !important;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        [data-testid="stSidebar"] label {
            color: #555; /* Slightly lighter grey for labels */
        }

        [data-testid="stSidebar"] button {
            color: white;
            background-color: #8D1B1B;
            border: none;
            border-radius: 5px;
            padding: 0.5em 1em;
            cursor: pointer;
            font-family: "Arial", sans-serif;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #a02a2a;
        }

        .sidebar-section {
            margin-bottom: 1.5em; /* Add spacing between sections */
            padding-bottom: 0.5em;
            border-bottom: 1px solid #eee; /* Subtle separator */
        }
        .sidebar-section:last-child {
            border-bottom: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply Background
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
with st.sidebar:
    st.markdown("<h2 style='color: #8D1B1B; font-family: Times New Roman, serif; font-weight: bold;'>⚙️ Controls</h2>", unsafe_allow_html=True)

    # Add a logo or thematic image at the top (replace with your URL)
    logo_url = "YOUR_LOGO_URL_HERE"  # Replace with your image URL or leave empty
    if logo_url != "YOUR_LOGO_URL_HERE":
        try:
            st.image(logo_url, width=100)
        except Exception as e:
            st.warning(f"Error loading logo: {e}")

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #8D1B1B; font-family: Times New Roman, serif;'>📊 Data Selection</h4>", unsafe_allow_html=True)
    dataset_choice = st.radio("Choose Data View:", ["Assets", "Liabilities"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #8D1B1B; font-family: Times New Roman, serif;'>🗓️ Filter by Time</h4>", unsafe_allow_html=True)
    filter_col = "End of Period"
    if filter_col in (assets_df.columns if dataset_choice == "Assets" else liabilities_df.columns):
        df_for_years = assets_df if dataset_choice == "Assets" else liabilities_df
        df_for_years = df_for_years.dropna(subset=[filter_col])
        df_for_years['Year'] = df_for_years[filter_col].dt.year
        selected_year = st.selectbox("Choose Year:", sorted(df_for_years['Year'].unique(), reverse=True))
    else:
        selected_year = None
        st.info("Year selection not available for this dataset.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #8D1B1B; font-family: Times New Roman, serif;'>💾 Export Options</h4>", unsafe_allow_html=True)
    export_format = st.radio("Select Format:", ["CSV", "Excel"])

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

    if st.button("📤 Download Selected Data"):
        if selected_year is not None:
            df_to_export = assets_df[assets_df['End of Period'].dt.year == selected_year] if dataset_choice == "Assets" else liabilities_df[liabilities_df['End of Period'].dt.year == selected_year]
            buffer, mime_type, filename = download_df(df_to_export, export_format)
            if buffer:
                st.download_button(
                    label=f"✅ Download as {export_format}",
                    data=buffer,
                    file_name=filename,
                    mime=mime_type,
                    key=f"export_button_{export_format}"
                )
            else:
                st.warning("⚠️ Error during export.")
        else:
            st.warning("Please select a year to export data.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Add a thematic image at the bottom (replace with your URL)
    footer_image_url = "YOUR_FOOTER_IMAGE_URL_HERE"  # Replace with your image URL or leave empty
    if footer_image_url != "YOUR_FOOTER_IMAGE_URL_HERE":
        try:
            st.image(footer_image_url, width=50)
        except Exception as e:
            st.warning(f"Error loading footer image: {e}")

# Main content area
if selected_year is not None:
    df = assets_df[assets_df['Year'] == selected_year].copy() if dataset_choice == "Assets" else liabilities_df[liabilities_df['Year'] == selected_year].copy()
    dataset_title = dataset_choice

    # KPI Section
    st.subheader(f"🔑 {dataset_title} Overview ({selected_year})")

    # KPI Calculations
    numeric_cols = df.select_dtypes(include="number").columns
    total_value = df[numeric_cols].sum().sum() if not numeric_cols.empty else 0
    average_value = df[numeric_cols].mean().mean() if not numeric_cols.empty else 0
    biggest_contributor = df[numeric_cols].sum().idxmax() if not numeric_cols.empty else "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Value", f"Rs. {total_value:,.0f}")
    col2.metric("Average per Metric", f"Rs. {average_value:,.0f}")
    col3.metric("Top Contributor", biggest_contributor)

    # Charts Section
    st.subheader(f"📈 Visual Analysis of {dataset_title} ({selected_year})")

    numeric_cols_for_viz = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols_for_viz and 'End of Period' in df.columns:
        df['Month'] = df['End of Period'].dt.month
        df['Month Name'] = df['End of Period'].dt.month_name()
        selected_cols = st.multiselect(
            f"Select one or more {dataset_title} metrics to visualize:",
            numeric_cols_for_viz,
            default=[numeric_cols_for_viz[0]] if numeric_cols_for_viz else []
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
    elif not numeric_cols_for_viz:
        st.warning("No numeric columns available to visualize.")
    elif 'End of Period' not in df.columns:
        st.warning("Date information not available for time-based visualization.")

    # 🔍 Insights Section
    st.subheader(f"🔎 Correlation Insights ({selected_year})")

    numeric_cols_corr = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols_corr:
        corr_matrix = df[numeric_cols_corr].corr()

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
        if numeric_cols_corr:
            reference_var = numeric_cols_corr[0]
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

else:
    st.info("Please select a year in the sidebar to view the dashboard.")

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
import streamlit as st
st.write("Hi")
st.write("Hello")

# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 🚨 set_page_config MUST come FIRST before any other Streamlit command
st.set_page_config(page_title="Bank Assets and Liabilities Dashboard", layout="wide")

st.title("📊 Bank Assets and Liabilities Visualization")

# Upload files
st.sidebar.header("Upload your CSV files")
assets_file = st.sidebar.file_uploader("Upload Assets CSV", type=["csv"])
liabilities_file = st.sidebar.file_uploader("Upload Liabilities CSV", type=["csv"])

# Load data
if assets_file is not None and liabilities_file is not None:
    assets_df = pd.read_csv(assets_file)
    liabilities_df = pd.read_csv(liabilities_file)

    st.header("Assets Data")
    st.dataframe(assets_df)

    st.header("Liabilities Data")
    st.dataframe(liabilities_df)

    st.sidebar.header("Select Visualization Options")

    # Choose which dataset to visualize
    dataset_choice = st.sidebar.selectbox("Choose dataset", ("Assets", "Liabilities"))

    if dataset_choice == "Assets":
        df = assets_df
    else:
        df = liabilities_df

    # Select column for plotting
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if numeric_columns:
        selected_col = st.sidebar.selectbox("Select a column to plot", numeric_columns)

        # Line Chart
        st.subheader(f"Line Chart of {selected_col}")
        st.line_chart(df[selected_col])

        # Histogram
        st.subheader(f"Histogram of {selected_col}")
        fig, ax = plt.subplots()
        sns.histplot(df[selected_col], kde=True, ax=ax)
        st.pyplot(fig)

        # Boxplot
        st.subheader(f"Boxplot of {selected_col}")
        fig2, ax2 = plt.subplots()
        sns.boxplot(x=df[selected_col], ax=ax2)
        st.pyplot(fig2)
    else:
        st.warning("No numeric columns found for plotting.")

else:
    st.info("Please upload both Assets and Liabilities CSV files to begin.")

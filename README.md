# Sri Lanka Commercial Bank Assets and Liabilities Dashboard
An interactive Streamlit dashboard that visualizes monthly data on Domestic Banking Units (DBU) of Sri Lanka’s commercial banks, sourced from the Central Bank of Sri Lanka. This tool helps policymakers, researchers, and the public explore financial indicators such as deposits, loans, and total credit from 1995 to the present.

## Dataset
Source: Central Bank of Sri Lanka – Monetary Sector Statistics

Link: CBStat Monetary Sector Tables

Type: Time-series (monthly) data from 1995 onwards

Focus: Domestic Banking Units (DBUs) only

Format: Pre-hosted and auto-loaded into the app

## Project Aim
To turn raw financial data into an easy-to-use, interactive dashboard that visualizes banking trends over time and enables data filtering, analysis, and download for offline use.

## Features
Functional Requirements

Auto-loading Dataset – No manual uploads required.
Time Filter – Select year range using a slider (1995 to present).
Indicator Selection – Choose between assets or liabilities and select specific variables (e.g., deposits, loans).
Interactive Charts – Line, bar, box, pie, and diverging bar charts with full-screen, hover, and zoom capabilities.
Data Export – Download filtered datasets in CSV or Excel formats.

Non-Functional Requirements

Usability – Clean UI with dropdowns and sliders, suitable for all users.
Accessibility – Web-deployed with high contrast visuals, screen reader support.
Maintainability – Version-controlled via this GitHub repository.
Deployability – Hosted on Streamlit Cloud for public access.

## Deployment
The app is deployed via Streamlit Cloud and can be accessed here:

Live Dashboard Link (Insert link once deployed)

## Development Methodology
This project followed the CRISP-DM process:

Understanding the Problem – Focused on analyzing domestic bank trends in Sri Lanka.

Data Preparation – Cleaned and reshaped time-series data using Python and Excel.

Modeling – Built with Streamlit to visualize and interact with financial indicators.

Evaluation – Tested for usability, performance, and filter accuracy.

Deployment – Released through Streamlit and version-controlled with GitHub.

## Technologies Used
Python (Pandas, Plotly, Streamlit)

Excel (for initial data cleaning)

GitHub (version control and documentation)

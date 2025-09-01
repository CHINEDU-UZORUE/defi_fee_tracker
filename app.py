import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
from datetime import datetime
from pathlib import Path

# Set page config
st.set_page_config(page_title="Solana DeFi Tracker", layout="wide")

# Set up paths
streamlit_data_dir = os.path.normpath('../data/streamlit')

# Helper function to format currency
def format_currency(amount):
    if amount is None or amount == 0:
        return "$0"
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.2f}K"
    else:
        return f"${amount:.2f}"

# Load metadata to get the latest data files
metadata_filepath = os.path.join(streamlit_data_dir, 'latest_data_metadata.joblib')
if os.path.exists(metadata_filepath):
    metadata = joblib.load(metadata_filepath)
    last_updated = metadata['last_updated']
    data_files = metadata['data_files']
else:
    st.error("Metadata file not found. Please run the data processing script first.")
    st.stop()

# Load datasets
try:
    tab1_overview = joblib.load(os.path.join(streamlit_data_dir, data_files['tab1_overview']))
    tab2_financial = joblib.load(os.path.join(streamlit_data_dir, data_files['tab2_financial']))
    tab3_distribution = joblib.load(os.path.join(streamlit_data_dir, data_files['tab3_distribution']))
    category_analysis = joblib.load(os.path.join(streamlit_data_dir, data_files['category_analysis']))
    financial_rankings = joblib.load(os.path.join(streamlit_data_dir, data_files['financial_rankings']))
    summary_stats = joblib.load(os.path.join(streamlit_data_dir, data_files['summary_stats']))
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Title and header
st.title("Solana DeFi Tracker")
st.markdown(f"**Last Updated:** {last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Protocols Overview", "Fees and Revenue", "Calculated Metrics", "Tokens"])

# Tab 1: Protocols Overview
with tab1:
    st.header("Protocols Overview")
    
    # KPI Cards
    if 'overview' in summary_stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Protocols", summary_stats['overview']['total_protocols'])
        with col2:
            st.metric("Total TVL", format_currency(summary_stats['overview']['total_tvl']))
        with col3:
            st.metric("Total Market Cap", format_currency(summary_stats['overview']['total_market_cap']))
        with col4:
            st.metric("Top Category", summary_stats['overview']['top_category'])
    
    # Protocols Table
    if not tab1_overview.empty:
        st.subheader("Protocol Details")
        st.dataframe(
            tab1_overview[['Protocol', 'Category', 'TVL_USD', 'Market_Cap_USD', 'Price_USD', 'TVL_Change_1d', 'Price_Change_24h', 'MCap_TVL_Ratio']]
            .style.format({
                'TVL_USD': format_currency,
                'Market_Cap_USD': format_currency,
                'Price_USD': "${:.2f}",
                'TVL_Change_1d': "{:.2%}",
                'Price_Change_24h': "{:.2%}",
                'MCap_TVL_Ratio': "{:.2f}"
            })
        )
        
        # Charts
        st.subheader("Top Protocols by TVL")
        top_10_tvl = tab1_overview.nlargest(10, 'TVL_USD')
        fig_tvl = px.bar(
            top_10_tvl,
            x='Protocol',
            y='TVL_USD',
            color='Category',
            title="Top 10 Protocols by TVL",
            labels={'TVL_USD': 'Total Value Locked (USD)'},
            text_auto='.2s'
        )
        fig_tvl.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_tvl.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_tvl, use_container_width=True)
        
        st.subheader("TVL Distribution by Category")
        fig_category = px.pie(
            category_analysis,
            values='Total_TVL',
            names='Category',
            title="TVL Distribution by Category"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.warning("No protocol overview data available.")

# Tab 2: Fees and Revenue
with tab2:
    st.header("Fees and Revenue")
    
    # KPI Cards
    if 'financial' in summary_stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Protocols with Revenue", summary_stats['financial']['protocols_with_revenue'])
        with col2:
            st.metric("Total Daily Revenue", format_currency(summary_stats['financial']['total_daily_revenue']))
        with col3:
            st.metric("Protocols with Fees", summary_stats['financial']['protocols_with_fees'])
        with col4:
            st.metric("Total Daily Fees", format_currency(summary_stats['financial']['total_daily_fees']))
    
    # Tables and Charts
    if not tab2_financial.empty:
        st.subheader("Top 10 Protocols by Fees")
        top_fees = financial_rankings.get('top_fees', pd.DataFrame())
        if not top_fees.empty:
            st.dataframe(
                top_fees.style.format({
                    'Fees_24h': format_currency,
                    'Fees_7d': format_currency,
                    'Fees_30d': format_currency
                })
            )
            fig_fees = px.bar(
                top_fees,
                x='Protocol',
                y='Fees_24h',
                color='Category',
                title="Top 10 Protocols by 24h Fees",
                labels={'Fees_24h': 'Fees (USD)'},
                text_auto='.2s'
            )
            fig_fees.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_fees.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_fees, use_container_width=True)
        
        st.subheader("Top 10 Protocols by Revenue")
        top_revenue = financial_rankings.get('top_revenue', pd.DataFrame())
        if not top_revenue.empty:
            st.dataframe(
                top_revenue.style.format({
                    'Revenue_24h': format_currency,
                    'Revenue_7d': format_currency,
                    'Revenue_30d': format_currency
                })
            )
            fig_revenue = px.bar(
                top_revenue,
                x='Protocol',
                y='Revenue_24h',
                color='Category',
                title="Top 10 Protocols by 24h Revenue",
                labels={'Revenue_24h': 'Revenue (USD)'},
                text_auto='.2s'
            )
            fig_revenue.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_revenue.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.warning("No financial data available.")

# Tab 3: Calculated Metrics
with tab3:
    st.header("Calculated Metrics")
    
    # KPI Cards
    if 'financial' in summary_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg P/F Ratio", f"{summary_stats['financial']['avg_pf_ratio']:.2f}" if not pd.isna(summary_stats['financial']['avg_pf_ratio']) else "N/A")
        with col2:
            st.metric("Avg P/R Ratio", f"{summary_stats['financial']['avg_pr_ratio']:.2f}" if not pd.isna(summary_stats['financial']['avg_pr_ratio']) else "N/A")
        with col3:
            st.metric("Highest Revenue Protocol", summary_stats['financial']['highest_revenue_protocol'])
    
    # Table
    if not tab2_financial.empty:
        st.subheader("Protocol Metrics")
        st.dataframe(
            tab2_financial[['Protocol', 'Category', 'PF_Ratio', 'PR_Ratio', 'MCap_TVL_Ratio']]
            .style.format({
                'PF_Ratio': "{:.2f}",
                'PR_Ratio': "{:.2f}",
                'MCap_TVL_Ratio': "{:.2f}"
            })
        )
        
        # Charts
        st.subheader("P/F vs P/R Ratio")
        fig_metrics = px.scatter(
            tab2_financial[tab2_financial['PF_Ratio'].notna() & tab2_financial['PR_Ratio'].notna()],
            x='PF_Ratio',
            y='PR_Ratio',
            color='Category',
            size='MCap_TVL_Ratio',
            hover_data=['Protocol'],
            title="P/F Ratio vs P/R Ratio",
            labels={'PF_Ratio': 'Price-to-Fees Ratio', 'PR_Ratio': 'Price-to-Revenue Ratio'}
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
        
        st.subheader("MCap/TVL Ratio Distribution")
        fig_mcap_tvl = px.histogram(
            tab2_financial[tab2_financial['MCap_TVL_Ratio'].notna()],
            x='MCap_TVL_Ratio',
            nbins=30,
            title="Distribution of MCap/TVL Ratios",
            labels={'MCap_TVL_Ratio': 'Market Cap to TVL Ratio'}
        )
        st.plotly_chart(fig_mcap_tvl, use_container_width=True)
    else:
        st.warning("No calculated metrics data available.")

# Tab 4: Tokens
with tab4:
    st.header("Token Distribution Analysis")
    
    # KPI Cards
    if 'distribution' in summary_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tokens Analyzed", summary_stats['distribution']['tokens_analyzed'])
        with col2:
            st.metric("Avg Gini Coefficient", f"{summary_stats['distribution']['avg_gini_coefficient']:.3f}")
        with col3:
            st.metric("Avg Top 10 Holders Share", f"{summary_stats['distribution']['avg_top_10_share']:.2f}%")
    
    # Table
    if not tab3_distribution.empty:
        st.subheader("Token Distribution Metrics")
        st.dataframe(
            tab3_distribution[['token_name', 'token_symbol', 'total_accounts_analyzed', 'top_1_holder_share', 'top_5_holders_share', 'top_10_holders_share', 'gini_coefficient']]
            .style.format({
                'top_1_holder_share': "{:.2f}%",
                'top_5_holders_share': "{:.2f}%",
                'top_10_holders_share': "{:.2f}%",
                'gini_coefficient': "{:.3f}"
            })
        )
        
        # Charts
        st.subheader("Top 10 Tokens by Gini Coefficient")
        top_gini = tab3_distribution.nlargest(10, 'gini_coefficient')
        fig_gini = px.bar(
            top_gini,
            x='token_name',
            y='gini_coefficient',
            title="Top 10 Tokens by Gini Coefficient",
            labels={'gini_coefficient': 'Gini Coefficient'},
            text_auto='.3f'
        )
        fig_gini.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_gini.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_gini, use_container_width=True)
        
        st.subheader("Concentration Levels")
        fig_concentration = px.pie(
            concentration_dist,
            values='Token_Count',
            names='Concentration_Level',
            title="Token Concentration Levels"
        )
        st.plotly_chart(fig_concentration, use_container_width=True)
    else:
        st.warning("No token distribution data available.")

st.markdown("---")
st.markdown("**Note**: Data is sourced from processed Solana DeFi datasets. Ensure the data processing script has been run to generate the latest data files.")
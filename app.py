import streamlit as st
import pandas as pd
import os
import joblib
import plotly.io as pio
from config.settings import SOLANA_PROTOCOLS

st.title("Solana DeFi Protocol Dashboard")

# Tabs for different views
tabs = st.tabs(["Overview", "Top 100 Holders", "P/F Ratios"])

# Overview tab
with tabs[0]:
    st.header("Protocol Overview")
    consolidated_files = [f for f in os.listdir('../data/processed') if f.startswith('consolidated_metrics_') and f.endswith('.joblib')]
    if consolidated_files:
        consolidated_file = max(consolidated_files, key=lambda x: x)
        df_consolidated = joblib.load(f"../data/processed/{consolidated_file}")
        st.dataframe(df_consolidated[['protocol', 'price_usd', 'market_cap', 'tvl', 'fees_24h', 'revenue_24h', 'total_holders_helius', 'top_100_holders_share']])
    else:
        st.warning("No consolidated metrics data available. Run 02_data_collection.ipynb to generate data.")

# Top 100 Holders tab
with tabs[1]:
    st.header("Top 100 Holders by Protocol")
    protocol_options = [info['name'] for key, info in SOLANA_PROTOCOLS.items() if info.get('mint_address')]
    selected_protocol = st.selectbox("Select Protocol", protocol_options)
    
    # Load top 100 holders
    protocol_key = [key for key, info in SOLANA_PROTOCOLS.items() if info['name'] == selected_protocol][0]
    holder_files = [f for f in os.listdir('../data/processed') if f.startswith(f'top_100_holders_{protocol_key}_') and f.endswith('.joblib')]
    if holder_files:
        latest_file = max(holder_files, key=lambda x: x)
        df_top_100 = joblib.load(f"../data/processed/{latest_file}")
        st.write(f"Top 100 Holders for {selected_protocol}")
        st.dataframe(df_top_100.style.format({
            'balance': '{:,.2f}',
            'share_percent': '{:.2f}%'
        }))
        
        # Display pie chart (static PNG)
        vis_dir = '../data/processed/visualizations'
        pie_files = [f for f in os.listdir(vis_dir) if f.startswith(f'holder_distribution_{protocol_key}_') and f.endswith('.png')]
        if pie_files:
            latest_pie = max(pie_files, key=lambda x: x)
            st.image(f"{vis_dir}/{latest_pie}", caption=f"Holder Distribution: {selected_protocol}")
        else:
            st.warning(f"No holder distribution chart for {selected_protocol}")
    else:
        st.warning(f"No holder data available for {selected_protocol}. Verify mint address in config/settings.py.")

# P/F Ratios tab
with tabs[2]:
    st.header("Price-to-Fees and Price-to-Revenue Ratios")
    results_files = [f for f in os.listdir('../data/processed') if f.startswith('analysis_results_') and f.endswith('.joblib')]
    if results_files:
        results_file = max(results_files, key=lambda x: x)
        df_results = joblib.load(f"../data/processed/{results_file}")
        st.dataframe(df_results[['protocol', 'pf_ratio', 'pr_ratio', 'top_100_share', 'gini_coefficient']].style.format({
            'pf_ratio': '{:.2f}',
            'pr_ratio': '{:.2f}',
            'top_100_share': '{:.2f}%',
            'gini_coefficient': '{:.3f}'
        }))
        
        # Display interactive P/F and P/R ratios bar chart
        vis_dir = '../data/processed/visualizations'
        pf_pr_files = [f for f in os.listdir(vis_dir) if f.startswith('pf_pr_ratios_') and f.endswith('.html')]
        if pf_pr_files:
            latest_pf_pr = max(pf_pr_files, key=lambda x: x)
            fig = pio.read_json(f"{vis_dir}/{latest_pf_pr}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No P/F and P/R ratios chart available. Run 03_analysis.ipynb to generate charts.")
        
        # Display interactive Gini coefficient bar chart
        gini_files = [f for f in os.listdir(vis_dir) if f.startswith('gini_coefficient_') and f.endswith('.html')]
        if gini_files:
            latest_gini = max(gini_files, key=lambda x: x)
            fig = pio.read_json(f"{vis_dir}/{latest_gini}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No Gini coefficient chart available. Run 03_analysis.ipynb to generate charts.")
    else:
        st.warning("No analysis results available. Run 03_analysis.ipynb to generate analysis data.")
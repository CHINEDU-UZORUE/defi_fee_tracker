import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="Solana DeFi Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful KPI cards
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #4a5568;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #2d8659;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #d53f8c;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #3182ce;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_currency(amount):
    if amount is None or pd.isna(amount) or amount == 0:
        return "$0"
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.2f}K"
    else:
        return f"${amount:.2f}"

def create_metric_card(title, value, card_type="default"):
    """Create a colorful metric card"""
    card_class = f"metric-card-{card_type}" if card_type != "default" else "metric-card"
    return f"""
    <div class="{card_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# Data directory
data_dir = 'data/streamlit'
metadata_file = os.path.join(data_dir, 'latest_data_metadata.joblib')

if not os.path.exists(metadata_file):
    st.error("Data not found. Run the data collection and analysis notebooks first.")
    st.stop()

metadata = joblib.load(metadata_file)
data_files = metadata['data_files']

# Load all datasets
datasets = {}
for key, filename in data_files.items():
    filepath = os.path.join(data_dir, filename)
    datasets[key] = joblib.load(filepath) if os.path.exists(filepath) else (pd.DataFrame() if key not in ['financial_rankings', 'raw_token_holders'] else {})

tab1_overview = datasets['tab1_overview']
tab2_revenue = datasets['tab2_revenue']
tab2_fees = datasets['tab2_fees']
tab3_metrics = datasets['tab3_metrics']
tab4_distribution = datasets['tab4_distribution']
category_analysis = datasets['category_analysis']
financial_rankings = datasets['financial_rankings']
summary_stats = datasets['summary_stats']
raw_token_holders = datasets.get('raw_token_holders', {})

# App header
st.title("🚀 Solana DeFi Fees & Revenue Tracker")
st.markdown(f"**Last Updated:** {metadata['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")

# Sidebar with filters
st.sidebar.header("🔍 Filters & Controls")

# Manual refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Category filter for Tab 1
available_categories = []
if not tab1_overview.empty and 'Category' in tab1_overview.columns:
    available_categories = sorted(tab1_overview['Category'].dropna().unique().tolist())

selected_categories = st.sidebar.multiselect(
    "📊 Filter by Category (Overview)",
    options=available_categories,
    default=available_categories[:5] if len(available_categories) > 5 else available_categories
)

# TVL range filter
if not tab1_overview.empty and 'TVL_USD' in tab1_overview.columns:
    min_tvl = float(tab1_overview['TVL_USD'].min())
    max_tvl = float(tab1_overview['TVL_USD'].max())
    
    tvl_range = st.sidebar.slider(
        "💰 TVL Range (USD)",
        min_value=min_tvl,
        max_value=max_tvl,
        value=(min_tvl, max_tvl),
        format="$%.0f"
    )

# Top N protocols filter
top_n_options = ["All", 5, 10, 20, 50, 100]
top_n = st.sidebar.selectbox(
    "🔝 Show Top N Protocols",
    top_n_options,
    index=0
)

# Apply filters function
def apply_filters(df, categories=None, tvl_range=None, top_n=None):
    """Apply sidebar filters to dataframe with safe checks"""
    if df is None or df.empty:
        return df

    filtered_df = df.copy()

    # Category filter
    if categories and 'Category' in filtered_df.columns:
        try:
            filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
        except Exception:
            pass

    # TVL range filter
    if tvl_range and 'TVL_USD' in filtered_df.columns:
        try:
            min_val, max_val = tvl_range
            filtered_df = filtered_df[
                (filtered_df['TVL_USD'] >= min_val) &
                (filtered_df['TVL_USD'] <= max_val)
            ]
        except Exception:
            pass

    # Top N filter
    if top_n and top_n != "All" and 'TVL_USD' in filtered_df.columns:
        try:
            n = int(top_n)
            if n > 0 and len(filtered_df) > 0:
                filtered_df = filtered_df.nlargest(n, 'TVL_USD')
        except Exception:
            pass

    return filtered_df

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Revenue & Fees", "📈 Metrics", "🎯 Token Distribution"])

# Tab 1: Overview
with tab1:
    st.header("📊 Protocols Overview")
    
    # Apply filters
    filtered_overview = apply_filters(
        tab1_overview,
        selected_categories,
        tvl_range if not tab1_overview.empty else None,
        top_n
    )
    
    # KPIs
    if 'overview' in summary_stats:
        kpis = summary_stats['overview']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card(
                "Total Protocols",
                str(len(filtered_overview) if not filtered_overview.empty else kpis.get('total_protocols', 0)),
                "blue"
            ), unsafe_allow_html=True)
        
        with col2:
            total_tvl = filtered_overview['TVL_USD'].sum() if not filtered_overview.empty else kpis.get('total_tvl', 0)
            st.markdown(create_metric_card(
                "Total TVL",
                format_currency(total_tvl),
                "green"
            ), unsafe_allow_html=True)
        
        with col3:
            total_mcap = filtered_overview['Market_Cap_USD'].sum() if not filtered_overview.empty else kpis.get('total_market_cap', 0)
            st.markdown(create_metric_card(
                "Total Market Cap",
                format_currency(total_mcap),
                "orange"
            ), unsafe_allow_html=True)
        
        with col4:
            top_category = filtered_overview.groupby('Category')['TVL_USD'].sum().idxmax() if not filtered_overview.empty else kpis.get('top_category', 'N/A')
            st.markdown(create_metric_card(
                "Top Category",
                str(top_category),
                "default"
            ), unsafe_allow_html=True)
    
    if not filtered_overview.empty:
        # Protocol table
        st.subheader("📋 Protocol Details")
        display_cols = [col for col in ['Protocol', 'Category', 'TVL_USD', 'Market_Cap_USD', 'Price_USD']
                       if col in filtered_overview.columns]
        
        display_df = filtered_overview[display_cols].reset_index(drop=True)
        display_df.index = display_df.index + 1
        
        format_dict = {
            'TVL_USD': lambda x: format_currency(x),
            'Market_Cap_USD': lambda x: format_currency(x),
            'Price_USD': lambda x: f"${x:.2f}" if pd.notna(x) else "$0.00"
        }
        format_dict = {k: v for k, v in format_dict.items() if k in display_cols}
        
        st.dataframe(display_df.style.format(format_dict), use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Protocols by TVL")
            top_10_filtered = filtered_overview.nlargest(10, 'TVL_USD')
            fig = px.bar(top_10_filtered, x='Protocol', y='TVL_USD', color='Category',
                        title="Top Protocols by TVL")
            fig.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not category_analysis.empty:
                filtered_categories = category_analysis[
                    category_analysis['Category'].isin(selected_categories)
                ] if selected_categories else category_analysis
                
                st.subheader("🥧 TVL by Category")
                fig = px.pie(filtered_categories, values='Total_TVL', names='Category',
                           title="TVL Distribution")
                st.plotly_chart(fig, use_container_width=True)

# Tab 2: Revenue & Fees
with tab2:
    st.header("💰 Revenue & Fees")
    
    # KPIs
    if 'financial' in summary_stats:
        kpis = summary_stats['financial']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            protocols_with_rev = len(tab2_revenue[tab2_revenue['Revenue_24h'] > 0]) if not tab2_revenue.empty else kpis.get('protocols_with_revenue', 0)
            st.markdown(create_metric_card(
                "Protocols w/ Revenue",
                str(protocols_with_rev),
                "blue"
            ), unsafe_allow_html=True)
        
        with col2:
            daily_revenue = tab2_revenue['Revenue_24h'].sum() if not tab2_revenue.empty else kpis.get('total_daily_revenue', 0)
            st.markdown(create_metric_card(
                "Daily Revenue",
                format_currency(daily_revenue),
                "green"
            ), unsafe_allow_html=True)
        
        with col3:
            protocols_with_fees = len(tab2_fees[tab2_fees['Fees_24h'] > 0]) if not tab2_fees.empty else kpis.get('protocols_with_fees', 0)
            st.markdown(create_metric_card(
                "Protocols w/ Fees",
                str(protocols_with_fees),
                "orange"
            ), unsafe_allow_html=True)
        
        with col4:
            daily_fees = tab2_fees['Fees_24h'].sum() if not tab2_fees.empty else kpis.get('total_daily_fees', 0)
            st.markdown(create_metric_card(
                "Daily Fees",
                format_currency(daily_fees),
                "default"
            ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Revenue
    with col1:
        st.subheader("💵 Top Revenue Earners")
        top_revenue = financial_rankings.get('top_revenue', pd.DataFrame())
        if not top_revenue.empty and 'Revenue_24h' in top_revenue.columns:
            display_revenue = top_revenue[['Protocol', 'Revenue_24h']].head(10).reset_index(drop=True)
            display_revenue.index = display_revenue.index + 1
            
            st.dataframe(display_revenue.style.format({'Revenue_24h': lambda x: format_currency(x)}))
            
            fig = px.bar(top_revenue.head(10), x='Protocol', y='Revenue_24h',
                        title="24h Revenue", color_discrete_sequence=['#11998e'])
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full revenue table
        if not tab2_revenue.empty:
            st.subheader("📋 All Revenue Data")
            display_revenue = tab2_revenue[['Protocol', 'Revenue_24h', 'Revenue_7d', 'Revenue_30d']].reset_index(drop=True)
            display_revenue.index = display_revenue.index + 1
            format_dict = {
                'Revenue_24h': lambda x: format_currency(x),
                'Revenue_7d': lambda x: format_currency(x),
                'Revenue_30d': lambda x: format_currency(x)
            }
            st.dataframe(display_revenue.style.format(format_dict), use_container_width=True)
    
    # Fees
    with col2:
        st.subheader("💸 Top Fee Generators")
        top_fees = financial_rankings.get('top_fees', pd.DataFrame())
        if not top_fees.empty and 'Fees_24h' in top_fees.columns:
            display_fees = top_fees[['Protocol', 'Fees_24h']].head(10).reset_index(drop=True)
            display_fees.index = display_fees.index + 1
            
            st.dataframe(display_fees.style.format({'Fees_24h': lambda x: format_currency(x)}))
            
            fig = px.bar(top_fees.head(10), x='Protocol', y='Fees_24h',
                        title="24h Fees", color_discrete_sequence=['#f5576c'])
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full fees table
        if not tab2_fees.empty:
            st.subheader("📋 All Fees Data")
            display_fees = tab2_fees[['Protocol', 'Fees_24h', 'Fees_7d', 'Fees_30d']].reset_index(drop=True)
            display_fees.index = display_fees.index + 1
            format_dict = {
                'Fees_24h': lambda x: format_currency(x),
                'Fees_7d': lambda x: format_currency(x),
                'Fees_30d': lambda x: format_currency(x)
            }
            st.dataframe(display_fees.style.format(format_dict), use_container_width=True)

# Tab 3: Metrics
with tab3:
    st.header("📈 Financial Metrics")
    
    # Sidebar filters for metrics
    st.sidebar.subheader("📈 Metrics Filters")
    
    if not tab3_metrics.empty:
        max_pf_ratio = st.sidebar.slider(
            "Max P/F Ratio",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0
        )
        max_pr_ratio = st.sidebar.slider(
            "Max P/R Ratio",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0
        )
        
        filtered_metrics = tab3_metrics[
            (tab3_metrics['PF_Ratio'] <= max_pf_ratio) &
            (tab3_metrics['PR_Ratio'] <= max_pr_ratio)
        ]
    else:
        filtered_metrics = tab3_metrics
    
    # KPIs
    if 'financial' in summary_stats and not filtered_metrics.empty:
        col1, col2, col3 = st.columns(3)
        
        avg_pf = filtered_metrics['PF_Ratio'].median()
        avg_pr = filtered_metrics['PR_Ratio'].median()
        top_revenue_protocol = filtered_metrics.loc[filtered_metrics['Revenue_24h'].idxmax(), 'Protocol'] if filtered_metrics['Revenue_24h'].max() > 0 else 'N/A'
        
        with col1:
            st.markdown(create_metric_card(
                "Median P/F Ratio",
                f"{avg_pf:.2f}" if avg_pf and not pd.isna(avg_pf) else "N/A",
                "blue"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card(
                "Median P/R Ratio",
                f"{avg_pr:.2f}" if avg_pr and not pd.isna(avg_pr) else "N/A",
                "green"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card(
                "Top Revenue Protocol",
                str(top_revenue_protocol),
                "orange"
            ), unsafe_allow_html=True)
    
    if not filtered_metrics.empty:
        # Ratios scatter plot
        if 'PF_Ratio' in filtered_metrics.columns and 'PR_Ratio' in filtered_metrics.columns:
            st.subheader("📊 P/F vs P/R Ratios")
            valid_data = filtered_metrics[
                filtered_metrics['PF_Ratio'].notna() &
                filtered_metrics['PR_Ratio'].notna() &
                (filtered_metrics['PF_Ratio'] > 0) &
                (filtered_metrics['PR_Ratio'] > 0)
            ]
            
            if not valid_data.empty:
                fig = px.scatter(valid_data, x='PF_Ratio', y='PR_Ratio',
                               hover_data=['Protocol'],
                               title="Price-to-Fees vs Price-to-Revenue Ratios")
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        # Financial metrics table
        st.subheader("📋 Financial Metrics Table")
        metrics_cols = ['Protocol', 'Revenue_24h', 'Fees_24h', 'Market_Cap_USD', 'PF_Ratio', 'PR_Ratio']
        metrics_cols = [col for col in metrics_cols if col in filtered_metrics.columns]
        
        if metrics_cols:
            display_metrics = filtered_metrics[metrics_cols].reset_index(drop=True)
            display_metrics.index = display_metrics.index + 1
            
            format_dict = {
                'Revenue_24h': lambda x: format_currency(x),
                'Fees_24h': lambda x: format_currency(x),
                'Market_Cap_USD': lambda x: format_currency(x),
                'PF_Ratio': lambda x: f"{x:.2f}" if pd.notna(x) else "N/A",
                'PR_Ratio': lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
            }
            format_dict = {k: v for k, v in format_dict.items() if k in metrics_cols}
            
            st.dataframe(display_metrics.style.format(format_dict), use_container_width=True)

# Tab 4: Token Distribution
with tab4:
    st.header("🎯 Token Distribution Analysis")
    
    # Sidebar filters for token distribution
    st.sidebar.subheader("🎯 Distribution Filters")
    
    if not tab4_distribution.empty:
        concentration_filter = st.sidebar.selectbox(
            "📊 Concentration Level",
            options=["All", "Low (0-25%)", "Medium (25-50%)", "High (50-75%)", "Very High (75-100%)"],
            index=0
        )
        
        if 'gini_coefficient' in tab4_distribution.columns:
            min_gini = float(tab4_distribution['gini_coefficient'].min())
            max_gini = float(tab4_distribution['gini_coefficient'].max())
            
            gini_range = st.sidebar.slider(
                "Gini Coefficient Range",
                min_value=min_gini,
                max_value=max_gini,
                value=(min_gini, max_gini),
                step=0.01
            )
    
    # Apply distribution filters
    filtered_distribution = tab4_distribution.copy()
    if not filtered_distribution.empty:
        if concentration_filter != "All":
            filtered_distribution['concentration_level'] = pd.cut(
                filtered_distribution['top_10_holders_share'],
                bins=[0, 25, 50, 75, 100],
                labels=['Low (0-25%)', 'Medium (25-50%)', 'High (50-75%)', 'Very High (75-100%)']
            )
            filtered_distribution = filtered_distribution[
                filtered_distribution['concentration_level'] == concentration_filter
            ]
        
        if 'gini_coefficient' in filtered_distribution.columns:
            filtered_distribution = filtered_distribution[
                (filtered_distribution['gini_coefficient'] >= gini_range[0]) &
                (filtered_distribution['gini_coefficient'] <= gini_range[1])
            ]
    
    # KPIs
    if 'distribution' in summary_stats:
        kpis = summary_stats['distribution']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tokens_count = len(filtered_distribution) if not filtered_distribution.empty else kpis.get('tokens_analyzed', 0)
            st.markdown(create_metric_card(
                "Tokens Analyzed",
                str(tokens_count),
                "blue"
            ), unsafe_allow_html=True)
        
        with col2:
            avg_gini = filtered_distribution['gini_coefficient'].mean() if not filtered_distribution.empty else kpis.get('avg_gini_coefficient')
            st.markdown(create_metric_card(
                "Avg Gini Coefficient",
                f"{avg_gini:.3f}" if avg_gini else "N/A",
                "green"
            ), unsafe_allow_html=True)
        
        with col3:
            avg_top10 = filtered_distribution['top_10_holders_share'].mean() if not filtered_distribution.empty else kpis.get('avg_top_10_share')
            st.markdown(create_metric_card(
                "Avg Top 10 Share",
                f"{avg_top10:.1f}%" if avg_top10 else "N/A",
                "orange"
            ), unsafe_allow_html=True)
    
    if not filtered_distribution.empty:
        # Distribution table
        st.subheader("📊 Token Concentration Metrics")
        display_cols = [col for col in ['token_name', 'token_symbol', 'token_price_usd','top_10_holders_share', 'gini_coefficient']
                       if col in filtered_distribution.columns]
        
        display_dist = filtered_distribution[display_cols].reset_index(drop=True)
        display_dist.index = display_dist.index + 1
        
        format_dict = {
            'top_10_holders_share': lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A",
            'gini_coefficient': lambda x: f"{x:.3f}" if pd.notna(x) else "N/A",
            'token_price_usd': lambda x: f"${x:.2f}" if pd.notna(x) else "$0.00"
        }
        format_dict = {k: v for k, v in format_dict.items() if k in display_cols}
        
        st.dataframe(display_dist.style.format(format_dict), use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'gini_coefficient' in filtered_distribution.columns:
                st.subheader("🔴 Most Concentrated Tokens")
                top_gini = filtered_distribution.nlargest(10, 'gini_coefficient')
                fig = px.bar(top_gini, x='token_name', y='gini_coefficient',
                           title="Highest Gini Coefficients",
                           color_discrete_sequence=['#f5576c'])
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'top_10_holders_share' in filtered_distribution.columns:
                st.subheader("📈 Concentration Distribution")
                df_temp = filtered_distribution.copy()
                df_temp['concentration_level'] = pd.cut(
                    df_temp['top_10_holders_share'],
                    bins=[0, 25, 50, 75, 100],
                    labels=['Low (0-25%)', 'Medium (25-50%)', 'High (50-75%)', 'Very High (75-100%)']
                )
                conc_dist = df_temp['concentration_level'].value_counts().reset_index()
                conc_dist.columns = ['Level', 'Count']
                
                fig = px.pie(conc_dist, values='Count', names='Level',
                           title="Token Concentration Levels",
                           color_discrete_sequence=['#4facfe', '#11998e', '#f093fb', '#f5576c'])
                st.plotly_chart(fig, use_container_width=True)
    
        # Token filter for holders
    if raw_token_holders:
        st.subheader("🔍 View Top Holders for a Token")
        available_tokens = sorted(raw_token_holders.keys())
        selected_token = st.selectbox("Select Token", options=available_tokens)
        
        if selected_token:
            holders_df = raw_token_holders[selected_token].head(10)
            if not holders_df.empty:
                # Ensure 'account_address' exists
                if 'account_address' not in holders_df.columns:
                    holders_df['account_address'] = holders_df.index.astype(str)
                
                # Table
                st.subheader(f"Top 10 Holders for {selected_token}")
                display_holders = holders_df[['rank', 'account_address', 'ui_amount']].reset_index(drop=True)
                display_holders.index = display_holders.index + 1
                format_dict = {
                    'ui_amount': lambda x: f"{x:,.2f}" if pd.notna(x) else "0.00"
                }
                st.dataframe(display_holders.style.format(format_dict), use_container_width=True)
                
                # Pie chart
                total_supply = holders_df['ui_amount'].sum()
                if total_supply > 0:
                    holders_df['share_percent'] = (holders_df['ui_amount'] / total_supply) * 100
                    fig_pie = px.pie(
                        holders_df,
                        values='share_percent',
                        names='account_address',
                        title=f"Top 10 Holder Shares for {selected_token}"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Data Sources:**")
    st.markdown("- DefiLlama API")
    st.markdown("- CoinGecko API")
    st.markdown("- Helius Solana RPC")

with col2:
    st.markdown("**🔄 Refresh Schedule:**")
    st.markdown("- Auto-refresh: Every 24 hours")
    st.markdown("- Manual refresh: Use sidebar button")
    st.markdown("- Data collection: Via APIs")

with col3:
    st.markdown("**📈 Current Stats:**")
    if not tab1_overview.empty:
        st.markdown(f"- Protocols: {len(tab1_overview):,}")
    if 'financial' in summary_stats:
        st.markdown(f"- Daily Fees: {format_currency(summary_stats['financial'].get('total_daily_fees', 0))}")
    if 'overview' in summary_stats:
        st.markdown(f"- Total TVL: {format_currency(summary_stats['overview'].get('total_tvl', 0))}")
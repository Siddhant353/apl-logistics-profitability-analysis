# ============================================================
# APL LOGISTICS — Profitability & Margin Intelligence Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="APL Logistics — Profitability Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# STYLING
# ------------------------------------------------------------
st.markdown("""
<style>
    /* KPI cards — dark */
    .kpi-card {
        background: #1a2332;
        border: 1px solid #2a3a52;
        border-left: 4px solid #3498db;
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .kpi-card.profit { border-left-color: #2ecc71; }
    .kpi-card.loss   { border-left-color: #e74c3c; }
    .kpi-label {
        font-size: 0.78rem;
        color: #7a8699;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #e4e8ef;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #7a8699;
        margin-top: 0.2rem;
    }

    /* Headline */
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #e4e8ef;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        font-size: 1rem;
        color: #7a8699;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    /* Section headers */
    .section-head {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e4e8ef;
        margin: 0.5rem 0 0.2rem 0;
    }
    .section-desc {
        font-size: 0.9rem;
        color: #7a8699;
        margin-bottom: 1rem;
    }

    /* Insight box */
    .insight-box {
        background: #161d2b;
        border: 1px solid #2a3a52;
        border-left: 4px solid #3498db;
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
    }
    .insight-box h4 {
        color: #e4e8ef;
        margin-top: 0;
        font-size: 1rem;
    }
    .insight-box p { color: #c2cad6; margin: 0.4rem 0; }
    .insight-box b { color: #e4e8ef; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------
@st.cache_data
def load_data():
    """Load cleaned APL Logistics dataset.
    Tries the relative project path first, then a local fallback."""
    candidate_paths = [
        Path("Data_processed/apl_cleaned.csv.gz"),
        Path("../Data_processed/apl_cleaned.csv.gz"),
        Path("Data_processed/apl_cleaned.csv"),
        Path("../Data_processed/apl_cleaned.csv"),
        Path("apl_cleaned.csv.gz"),
        Path("apl_cleaned.csv"),
    ]
    for p in candidate_paths:
        if p.exists():
            return pd.read_csv(p)
    st.error(
        "Could not find the cleaned dataset. Expected "
        "apl_cleaned.csv.gz in the Data_processed folder."
    )
    st.stop()

df = load_data()

# Fix discount band ordering globally
band_order = ['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25-30%']
if 'Discount_Band' in df.columns:
    df['Discount_Band'] = pd.Categorical(
        df['Discount_Band'], categories=band_order, ordered=True
    )

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.markdown(
    '<div class="main-title">APL Logistics — Profitability & Margin Intelligence</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="main-subtitle">Which customers, products, and regions '
    'truly generate value — beyond top-line revenue.</div>',
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------
st.sidebar.header("Filters")

# Customer segment
segments = ['All'] + sorted(df['Customer Segment'].dropna().unique().tolist())
sel_segment = st.sidebar.selectbox("Customer Segment", segments)

# Market
markets = ['All'] + sorted(df['Market'].dropna().unique().tolist())
sel_market = st.sidebar.selectbox("Market", markets)

# Category
categories = ['All'] + sorted(df['Category Name'].dropna().unique().tolist())
sel_category = st.sidebar.selectbox("Product Category", categories)

# Apply filters
fdf = df.copy()
if sel_segment != 'All':
    fdf = fdf[fdf['Customer Segment'] == sel_segment]
if sel_market != 'All':
    fdf = fdf[fdf['Market'] == sel_market]
if sel_category != 'All':
    fdf = fdf[fdf['Category Name'] == sel_category]

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**Filtered orders:** {len(fdf):,}  \n"
    f"**of** {len(df):,} total"
)

if len(fdf) == 0:
    st.warning("No orders match the selected filters. Adjust your selection.")
    st.stop()

# ------------------------------------------------------------
# EXECUTIVE KPI CARDS
# ------------------------------------------------------------
total_revenue = fdf['Revenue'].sum()
total_profit = fdf['Profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
total_orders = len(fdf)
total_customers = fdf['Customer Id'].nunique()
loss_orders = int(fdf['Is_Loss_Making_Order'].sum())
loss_rate = (loss_orders / total_orders * 100) if total_orders else 0
avg_discount = fdf['Discount_Rate_Pct'].mean()

def kpi_card(label, value, sub="", kind=""):
    return f"""
    <div class="kpi-card {kind}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """

row1 = st.columns(4)
with row1[0]:
    st.markdown(kpi_card("Total Revenue", f"${total_revenue/1e6:.2f}M",
                         f"{total_orders:,} orders"), unsafe_allow_html=True)
with row1[1]:
    st.markdown(kpi_card("Total Profit", f"${total_profit/1e6:.2f}M",
                         "after all costs", "profit"), unsafe_allow_html=True)
with row1[2]:
    st.markdown(kpi_card("Profit Margin", f"{profit_margin:.2f}%",
                         "of revenue", "profit" if profit_margin >= 10 else "loss"),
                unsafe_allow_html=True)
with row1[3]:
    st.markdown(kpi_card("Avg Discount", f"{avg_discount:.2f}%",
                         "across orders"), unsafe_allow_html=True)

st.write("")

row2 = st.columns(4)
with row2[0]:
    st.markdown(kpi_card("Total Customers", f"{total_customers:,}",
                         "unique buyers"), unsafe_allow_html=True)
with row2[1]:
    st.markdown(kpi_card("Loss-Making Orders", f"{loss_orders:,}",
                         f"{loss_rate:.1f}% of orders", "loss"),
                unsafe_allow_html=True)
with row2[2]:
    avg_order_value = total_revenue / total_orders if total_orders else 0
    st.markdown(kpi_card("Avg Order Value", f"${avg_order_value:,.0f}",
                         "revenue per order"), unsafe_allow_html=True)
with row2[3]:
    profit_per_order = total_profit / total_orders if total_orders else 0
    st.markdown(kpi_card("Profit / Order", f"${profit_per_order:,.0f}",
                         "avg profit per order",
                         "profit" if profit_per_order >= 0 else "loss"),
                unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------
# ANALYSIS TABS
# ------------------------------------------------------------
tab_cust, tab_prod, tab_disc, tab_mkt, tab_del = st.tabs([
    "Customer Value",
    "Product & Category",
    "Discount Impact",
    "Market & Region",
    "Delivery Performance"
])

PROFIT = "#2ecc71"
LOSS = "#e74c3c"
NEUTRAL = "#3498db"
PLOT_BG = "rgba(0,0,0,0)"

def style_fig(fig, height=420):
    """Apply consistent dark-theme styling to a plotly figure."""
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color="#c2cad6", size=12),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        title_font=dict(color="#e4e8ef", size=15)
    )
    fig.update_xaxes(gridcolor="#2a3a52", zerolinecolor="#2a3a52")
    fig.update_yaxes(gridcolor="#2a3a52", zerolinecolor="#2a3a52")
    return fig

def insight(title, finding, implication, recommendation):
    st.markdown(f"""
    <div class="insight-box">
        <h4>{title}</h4>
        <p><b>Finding:</b> {finding}</p>
        <p><b>Implication:</b> {implication}</p>
        <p><b>Recommendation:</b> {recommendation}</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TAB 1: CUSTOMER VALUE
# ============================================================
with tab_cust:
    st.markdown('<div class="section-head">Customer Profitability</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Who generates genuine profit '
                'versus who generates revenue but erodes margin.</div>',
                unsafe_allow_html=True)

    cust = fdf.groupby('Customer Id').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Profit', 'count')
    ).reset_index().sort_values('Profit', ascending=False)

    n20 = max(int(len(cust) * 0.20), 1)
    share20 = cust.head(n20)['Profit'].sum() / cust['Profit'].sum() * 100 \
        if cust['Profit'].sum() else 0
    loss_custs = int((cust['Profit'] < 0).sum())

    m = st.columns(3)
    m[0].metric("Profit from Top 20% Customers", f"{share20:.1f}%")
    m[1].metric("Loss-Making Customers", f"{loss_custs:,}")
    m[2].metric("Total Customers", f"{len(cust):,}")

    c1, c2 = st.columns(2)
    with c1:
        top10 = cust.head(10).copy()
        top10['Customer Id'] = top10['Customer Id'].astype(str)
        fig = px.bar(top10, x='Profit', y='Customer Id', orientation='h',
                     title="Top 10 Customers by Profit",
                     color_discrete_sequence=[PROFIT])
        fig.update_yaxes(autorange="reversed", type="category")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        bot10 = cust.tail(10).copy()
        bot10['Customer Id'] = bot10['Customer Id'].astype(str)
        fig = px.bar(bot10, x='Profit', y='Customer Id', orientation='h',
                     title="Bottom 10 Customers by Profit (Loss-Makers)",
                     color_discrete_sequence=[LOSS])
        fig.update_yaxes(autorange="reversed", type="category")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    insight(
        "Customer Profitability",
        f"The top 20% of customers generate {share20:.1f}% of total profit, "
        f"while {loss_custs:,} customers are loss-making in aggregate.",
        "A revenue-only view masks profit risk. High order volume does not "
        "equal high value — loss-making customers consume resources without return.",
        "Introduce a Customer Value Tier system (High / Medium / At-Risk) based "
        "on profit contribution. Review commercial terms for loss-making accounts."
    )

# ============================================================
# TAB 2: PRODUCT & CATEGORY
# ============================================================
with tab_prod:
    st.markdown('<div class="section-head">Product & Category Profitability</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Which categories drive profit '
                'versus which generate revenue at thin or negative margins.</div>',
                unsafe_allow_html=True)

    cat = fdf.groupby('Category Name').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Profit', 'count')
    ).reset_index()
    cat['Margin'] = cat['Profit'] / cat['Revenue'] * 100
    cat = cat.sort_values('Profit', ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        top10c = cat.head(10)
        fig = px.bar(top10c, x='Profit', y='Category Name', orientation='h',
                     title="Top 10 Categories by Profit",
                     color_discrete_sequence=[PROFIT])
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        top15r = cat.sort_values('Revenue', ascending=False).head(15)
        colors = [LOSS if v < 10 else NEUTRAL for v in top15r['Margin']]
        fig = go.Figure(go.Bar(
            x=top15r['Margin'], y=top15r['Category Name'],
            orientation='h', marker_color=colors
        ))
        fig.add_vline(x=10, line_dash="dash", line_color="#7a8699")
        fig.update_layout(title="Profit Margin % — Top 15 by Revenue")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    low_margin = cat[(cat['Revenue'] > cat['Revenue'].median()) &
                     (cat['Margin'] < 10)].sort_values('Margin')
    risk_names = ", ".join(low_margin['Category Name'].head(3).tolist()) \
        if len(low_margin) else "none in current filter"

    insight(
        "Product & Category Profitability",
        f"Several categories generate high revenue but operate below 10% margin. "
        f"Highest-risk: {risk_names}.",
        "High-revenue, low-margin categories appear healthy in top-line reporting "
        "but quietly erode overall profitability through discounting or cost structure.",
        "Run a category-level pricing audit for all segments below 10% margin. "
        "Protect high-margin categories from aggressive discounting."
    )

# ============================================================
# TAB 3: DISCOUNT IMPACT
# ============================================================
with tab_disc:
    st.markdown('<div class="section-head">Discount Impact</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-desc">How discounting affects margin '
                'across the business — the primary margin-erosion diagnostic.</div>',
                unsafe_allow_html=True)

    disc = fdf.groupby('Discount_Band', observed=True).agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Profit', 'count'),
        Avg_Margin=('Profit_Margin_Pct', 'mean'),
        Loss_Orders=('Is_Loss_Making_Order', 'sum')
    ).reset_index()
    disc['Loss_Rate'] = disc['Loss_Orders'] / disc['Orders'] * 100

    zero = fdf[fdf['Discount_Rate'] == 0]
    disc_o = fdf[fdf['Discount_Rate'] > 0]
    zm = (zero['Profit'].sum() / zero['Revenue'].sum() * 100) \
        if zero['Revenue'].sum() else 0
    dm = (disc_o['Profit'].sum() / disc_o['Revenue'].sum() * 100) \
        if disc_o['Revenue'].sum() else 0

    m = st.columns(3)
    m[0].metric("Margin — No Discount", f"{zm:.2f}%")
    m[1].metric("Margin — Discounted", f"{dm:.2f}%")
    m[2].metric("Margin Gap", f"{zm - dm:.2f} pts", delta=f"-{zm-dm:.2f}",
                delta_color="inverse")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(disc, x='Discount_Band', y='Avg_Margin',
                     title="Average Margin by Discount Band",
                     color_discrete_sequence=[NEUTRAL])
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        fig = px.bar(disc, x='Discount_Band', y='Loss_Rate',
                     title="Loss-Making Order Rate by Discount Band",
                     color_discrete_sequence=["#f39c12"])
        st.plotly_chart(style_fig(fig), use_container_width=True)

    insight(
        "Discount Impact",
        f"Non-discounted orders run at {zm:.2f}% margin versus {dm:.2f}% for "
        f"discounted orders — a {zm-dm:.2f} point gap. Margin compresses as "
        "discount bands rise.",
        "The business trades margin for volume through discounting without "
        "evidence of proportionally higher revenue from deeper discounts.",
        "Introduce a discount authorisation policy with management approval above "
        "a set threshold. See the What-If simulator below for recovery potential."
    )

# ============================================================
# TAB 4: MARKET & REGION
# ============================================================
with tab_mkt:
    st.markdown('<div class="section-head">Market & Regional Performance</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Whether profitability varies by '
                'geography — or whether the pattern is structural.</div>',
                unsafe_allow_html=True)

    mkt = fdf.groupby('Market').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Profit', 'count')
    ).reset_index()
    mkt['Margin'] = mkt['Profit'] / mkt['Revenue'] * 100
    mkt = mkt.sort_values('Profit', ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mkt['Market'], y=mkt['Revenue']/1e6,
                             name='Revenue ($M)', marker_color=NEUTRAL))
        fig.add_trace(go.Bar(x=mkt['Market'], y=mkt['Profit']/1e6,
                             name='Profit ($M)', marker_color=PROFIT))
        fig.update_layout(title="Revenue vs Profit by Market ($M)",
                          barmode='group')
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        colors = [LOSS if v < 10 else PROFIT for v in mkt['Margin']]
        fig = go.Figure(go.Bar(x=mkt['Market'], y=mkt['Margin'],
                               marker_color=colors))
        fig.add_hline(y=10, line_dash="dash", line_color="#7a8699")
        fig.update_layout(title="Profit Margin % by Market")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    reg = fdf.groupby('Order Region').agg(
        Profit=('Profit', 'sum')
    ).reset_index().sort_values('Profit', ascending=False).head(10)
    fig = px.bar(reg, x='Profit', y='Order Region', orientation='h',
                 title="Top 10 Regions by Profit",
                 color_discrete_sequence=[NEUTRAL])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style_fig(fig, height=380), use_container_width=True)

    mgn_min, mgn_max = mkt['Margin'].min(), mkt['Margin'].max()
    insight(
        "Market & Regional Performance",
        f"Margins cluster tightly across markets ({mgn_min:.1f}%–{mgn_max:.1f}%). "
        "No single market is an outlier — the pattern is uniform.",
        "Uniform margins confirm profitability challenges are structural, not "
        "geographic. Region is not the lever; pricing and discounting are.",
        "Focus reform on product pricing and discount control, not market-specific "
        "fixes. Pilot in highest-volume regions for maximum impact."
    )

# ============================================================
# TAB 5: DELIVERY PERFORMANCE
# ============================================================
with tab_del:
    st.markdown('<div class="section-head">Delivery Performance</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Whether delivery failures compound '
                'financial risk — or are decoupled from margin.</div>',
                unsafe_allow_html=True)

    dlv = fdf.groupby('Delivery Status').agg(
        Orders=('Profit', 'count'),
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Loss_Orders=('Is_Loss_Making_Order', 'sum')
    ).reset_index()
    dlv['Order_Share'] = dlv['Orders'] / dlv['Orders'].sum() * 100
    dlv['Margin'] = dlv['Profit'] / dlv['Revenue'] * 100
    dlv = dlv.sort_values('Orders', ascending=False)

    late_share = dlv[dlv['Delivery Status'].str.contains('Late', case=False,
                     na=False)]['Order_Share'].sum()

    m = st.columns(2)
    m[0].metric("Late Delivery Share", f"{late_share:.1f}%")
    m[1].metric("Delivery Statuses", f"{dlv['Delivery Status'].nunique()}")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(dlv, x='Delivery Status', y='Order_Share',
                     title="Order Share % by Delivery Status",
                     color_discrete_sequence=[NEUTRAL])
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        colors = [LOSS if v < 10 else PROFIT for v in dlv['Margin']]
        fig = go.Figure(go.Bar(x=dlv['Delivery Status'], y=dlv['Margin'],
                               marker_color=colors))
        fig.add_hline(y=10, line_dash="dash", line_color="#7a8699")
        fig.update_layout(title="Profit Margin % by Delivery Status")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    insight(
        "Delivery Performance",
        f"{late_share:.1f}% of orders are delivered late, yet margins are nearly "
        "identical across all delivery statuses — delivery and profit are decoupled.",
        "Late delivery is a customer-retention and reputational risk rather than a "
        "direct margin driver. Its financial cost is lagged and not visible per-order.",
        "Treat late delivery as a retention risk. Renegotiate underperforming "
        "shipping contracts. Track churn by delivery experience if data allows."
    )

# ------------------------------------------------------------
# WHAT-IF DISCOUNT SIMULATOR
# ------------------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-head">What-If: Discount Cap Simulator</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-desc">Model the profit impact of capping '
            'order-level discounts. Move the slider to set a maximum discount '
            'rate and see how much margin the business could recover.</div>',
            unsafe_allow_html=True)

# Gross order value (pre-discount)
sim = fdf.copy()
sim['Gross'] = sim['Order Item Product Price'] * sim['Order Item Quantity']

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    cap_pct = st.slider(
        "Maximum allowed discount rate (%)",
        min_value=0, max_value=30, value=10, step=1
    )
    cap = cap_pct / 100.0

    # Recompute discount under the cap
    sim['capped_rate'] = sim['Discount_Rate'].clip(upper=cap)
    sim['orig_disc'] = sim['Gross'] * sim['Discount_Rate']
    sim['new_disc'] = sim['Gross'] * sim['capped_rate']
    sim['recovered'] = sim['orig_disc'] - sim['new_disc']

    recovered = sim['recovered'].sum()
    current_profit = sim['Profit'].sum()
    new_profit = current_profit + recovered
    uplift_pct = (recovered / current_profit * 100) if current_profit else 0
    affected = int((sim['Discount_Rate'] > cap).sum())

    st.metric("Profit Recovered", f"${recovered/1e6:.2f}M")
    st.metric("New Total Profit", f"${new_profit/1e6:.2f}M",
              delta=f"+{uplift_pct:.1f}%")
    st.metric("Orders Affected", f"{affected:,}",
              help="Orders currently discounted above the cap")

with sim_col2:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Current Profit", "Recovered", "Projected Profit"],
        y=[current_profit/1e6, recovered/1e6, new_profit/1e6],
        marker_color=[NEUTRAL, PROFIT, "#27ae60"],
        text=[f"${current_profit/1e6:.2f}M",
              f"+${recovered/1e6:.2f}M",
              f"${new_profit/1e6:.2f}M"],
        textposition="outside"
    ))
    fig.update_layout(title=f"Profit Impact of Capping Discounts at {cap_pct}%",
                      yaxis_title="Profit ($M)")
    st.plotly_chart(style_fig(fig, height=400), use_container_width=True)

st.markdown(f"""
<div class="insight-box">
    <h4>How to read this</h4>
    <p>Capping discounts at <b>{cap_pct}%</b> would recover an estimated
    <b>${recovered/1e6:.2f}M</b> in profit across <b>{affected:,}</b> orders —
    a <b>{uplift_pct:.1f}%</b> uplift on current profit for this selection.</p>
    <p><b>Important caveat:</b> This models the maximum recoverable margin and
    assumes capped orders still convert. In practice, some deeply discounted
    orders may be price-sensitive and could be lost if the discount were reduced.
    Treat this as the upper bound of the opportunity, and pilot any cap on a
    subset of orders before rolling it out.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.caption(
    "APL Logistics Profitability Intelligence Dashboard · "
    "Built on 180,519 orders across 5 markets, 23 regions, and 164 countries · "
    "Source: apl_cleaned.csv"
)

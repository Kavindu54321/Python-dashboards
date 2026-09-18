import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="LankaMart Retail Dashboard",
    page_icon="🛒",
    layout="wide"
)

@st.cache_data
def load_data():
    file_paths = [
        "data/CIT308_LankaMart_Retail_Transactions.csv",
        "CIT308_LankaMart_Retail_Transactions.csv",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "CIT308_LankaMart_Retail_Transactions.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "CIT308_LankaMart_Retail_Transactions.csv")
    ]
    file_path = next((p for p in file_paths if os.path.exists(p)), None)
    
    if not file_path:
        st.error("Dataset not found. Please verify the CSV file path.")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df

df = load_data()

if df.empty:
    st.stop()

st.title("🛒 LankaMart Retail Analytics Dashboard")
st.caption("CIT308 - Retail Transaction Analysis & Business Intelligence")

st.sidebar.header("🔍 Filter Options")

all_provinces = sorted(df["province"].dropna().unique())
province = st.sidebar.multiselect("Select Province", options=all_provinces, default=all_provinces)

all_categories = sorted(df["product_category"].dropna().unique())
category = st.sidebar.multiselect("Select Product Category", options=all_categories, default=all_categories)

all_channels = sorted(df["sales_channel"].dropna().unique())
channel = st.sidebar.multiselect("Select Sales Channel", options=all_channels, default=all_channels)

all_segments = sorted(df["customer_segment"].dropna().unique())
segment = st.sidebar.multiselect("Select Customer Segment", options=all_segments, default=all_segments)

filtered_df = df[
    (df["province"].isin(province if province else all_provinces)) &
    (df["product_category"].isin(category if category else all_categories)) &
    (df["sales_channel"].isin(channel if channel else all_channels)) &
    (df["customer_segment"].isin(segment if segment else all_segments))
]

if filtered_df.empty:
    st.warning("No data found for the selected filters. Please broaden your selection.")
    st.stop()

total_revenue = filtered_df["revenue_lkr"].sum()
total_profit = filtered_df["profit_lkr"].sum()
total_orders = filtered_df["order_id"].nunique()
total_units = filtered_df["units"].sum()

average_rating = filtered_df["customer_rating"].mean()
average_delivery = filtered_df["delivery_days"].mean()

returned_orders = (filtered_df["returned"].astype(str).str.strip().str.lower() == "yes").sum()
return_rate = (returned_orders / len(filtered_df) * 100) if len(filtered_df) > 0 else 0

st.markdown("### 📌 Key Performance Indicators (KPIs)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"LKR {total_revenue:,.0f}")
col2.metric("📈 Total Profit", f"LKR {total_profit:,.0f}")
col3.metric("🧾 Total Orders", f"{total_orders:,}")
col4.metric("📦 Units Sold", f"{total_units:,}")

col5, col6, col7 = st.columns(3)
col5.metric("⭐ Average Rating", f"{average_rating:.2f} / 5.0")
col6.metric("🚚 Avg Delivery Time", f"{average_delivery:.1f} days")
col7.metric("↩️ Return Rate", f"{return_rate:.2f}%")

st.divider()

st.markdown("### 📊 Monthly Revenue Trend")
monthly_revenue = filtered_df.groupby("month", as_index=False)["revenue_lkr"].sum()

fig1 = px.line(
    monthly_revenue,
    x="month",
    y="revenue_lkr",
    markers=True,
    title="Monthly Revenue Trend (LKR)",
    labels={"month": "Month", "revenue_lkr": "Revenue (LKR)"},
    template="plotly_white",
    color_discrete_sequence=["#0f766e"]
)
st.plotly_chart(fig1, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    province_revenue = (
        filtered_df
        .groupby("province", as_index=False)["revenue_lkr"]
        .sum()
        .sort_values("revenue_lkr", ascending=False)
    )
    fig2 = px.bar(
        province_revenue,
        x="province",
        y="revenue_lkr",
        title="Revenue by Province",
        labels={"province": "Province", "revenue_lkr": "Revenue (LKR)"},
        color="revenue_lkr",
        color_continuous_scale="Teal",
        template="plotly_white"
    )
    fig2.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    category_profit = (
        filtered_df
        .groupby("product_category", as_index=False)["profit_lkr"]
        .sum()
        .sort_values("profit_lkr", ascending=False)
    )
    fig3 = px.bar(
        category_profit,
        x="product_category",
        y="profit_lkr",
        title="Profit by Product Category",
        labels={"product_category": "Category", "profit_lkr": "Profit (LKR)"},
        color="profit_lkr",
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

col_pie, col_seg = st.columns(2)

with col_pie:
    channel_revenue = (
        filtered_df
        .groupby("sales_channel", as_index=False)["revenue_lkr"]
        .sum()
    )
    fig4 = px.pie(
        channel_revenue,
        names="sales_channel",
        values="revenue_lkr",
        title="Revenue by Sales Channel",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_white"
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_seg:
    segment_revenue = (
        filtered_df
        .groupby("customer_segment", as_index=False)["revenue_lkr"]
        .sum()
        .sort_values("revenue_lkr", ascending=False)
    )
    fig5 = px.bar(
        segment_revenue,
        x="customer_segment",
        y="revenue_lkr",
        title="Revenue by Customer Segment",
        labels={"customer_segment": "Segment", "revenue_lkr": "Revenue (LKR)"},
        color_discrete_sequence=["#3b82f6"],
        template="plotly_white"
    )
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

st.markdown("### 📋 Filtered Transaction Data")
search_query = st.text_input("Search Transactions (by Product Name or Order ID):", placeholder="e.g. Smart Watch, LM26-0005")

display_df = filtered_df.copy()
if search_query:
    display_df = display_df[
        display_df["product_name"].str.contains(search_query, case=False, na=False) |
        display_df["order_id"].str.contains(search_query, case=False, na=False)
    ]

st.dataframe(display_df, use_container_width=True)

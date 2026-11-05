
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Retail Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# THEME / STYLING
# (base colors come from .streamlit/config.toml; this CSS
#  only adds layout polish — cards, spacing, banner, nav)
# ==========================================================

CHART_PALETTE = [
    "#2563eb", "#f97316", "#16a34a", "#dc2626",
    "#9333ea", "#0891b2", "#ca8a04", "#db2777"
]
px.defaults.color_discrete_sequence = CHART_PALETTE
px.defaults.template = "plotly_white"

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        color: #1d4ed8 !important;
        font-weight: 700 !important;
    }

    /* ---------- Header banner ---------- */
    .app-banner {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 60%, #3b82f6 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }
    .app-banner h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 28px;
    }
    .app-banner p {
        color: #dbeafe !important;
        margin: 6px 0 0 0;
        font-size: 14px;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] button {
        border-radius: 10px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
    }
    section[data-testid="stSidebar"] button p {
        text-align: left !important;
    }

    /* ---------- Section cards (chart / table containers) ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        box-shadow: 0 1px 6px rgba(15, 23, 42, 0.06);
        padding: 4px;
    }

    /* ---------- Metric cards ---------- */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 6px rgba(15, 23, 42, 0.06);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1d4ed8 !important;
    }

    /* ---------- Dataframes ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-banner">
        <h1>📊 Retail Sales Analytics Dashboard</h1>
        <p>Snowflake Data Engineering Capstone Project</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SNOWFLAKE CONNECTION
# ==========================================================

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse="CAPSTONE_WH",
        database="CAPSTONE_DB",
        schema="GOLD"
    )


# ==========================================================
# LOAD GOLD TABLES
# ==========================================================

@st.cache_data(ttl=300)
def load_data(table):
    conn = get_connection()

    query = f"SELECT * FROM CAPSTONE_DB.GOLD.{table}"

    return pd.read_sql(query, conn)


def prepare_data(df):
    df.columns = [str(col).upper().strip() for col in df.columns]
    return df


def get_column(df, possible_names):
    for name in possible_names:
        if name.upper() in df.columns:
            return name.upper()
    return None


def show_table(table_name):
    try:
        df = prepare_data(load_data(table_name))
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Unable to load {table_name}.")
        st.exception(e)


def show_chart(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=16,
        legend_title_text="",
    )
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding: 6px 0 16px 0;">
        <div style="font-size:40px; line-height:1;">📊</div>
        <div style="font-size:20px; font-weight:700; margin-top:6px; color:#1d4ed8;">
            Sales Analytics
        </div>
        <div style="font-size:12px; color:#000000; opacity:0.75;">
            Capstone Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.divider()

NAV_OPTIONS = {
    "Overview": "🏠  Overview",
    "Category Analysis": "🗂️  Category Analysis",
    "Regional Analysis": "🌍  Regional Analysis",
    "Monthly Trends": "📈  Monthly Trends",
    "Customer Insights": "👥  Customer Insights",
    "Advanced Analytics": "🔬  Advanced Analytics",
}

if "page" not in st.session_state:
    st.session_state.page = "Overview"

for key, label in NAV_OPTIONS.items():
    st.sidebar.button(
        label,
        key=f"nav_{key}",
        use_container_width=True,
        type="primary" if st.session_state.page == key else "secondary",
        on_click=lambda key=key: st.session_state.update(page=key),
    )

page = st.session_state.page

st.sidebar.divider()
st.sidebar.caption("🔗 Data Source: Snowflake Gold Layer")


# ==========================================================
# 1. OVERVIEW
# ==========================================================

if page == "Overview":

    st.header("Business Overview")

    try:
        category = prepare_data(load_data("GOLD_CATEGORY_INSIGHTS"))
        region = prepare_data(load_data("GOLD_REGION_INSIGHTS"))
        monthly = prepare_data(load_data("GOLD_MONTHLY_SALES"))

        cat_sales = get_column(category, ["TOTAL_SALES", "SALES"])
        cat_profit = get_column(category, ["TOTAL_PROFIT", "PROFIT"])
        cat_quantity = get_column(category, ["TOTAL_QUANTITY", "QUANTITY"])

        total_sales = category[cat_sales].sum() if cat_sales else 0
        total_profit = category[cat_profit].sum() if cat_profit else 0
        total_quantity = category[cat_quantity].sum() if cat_quantity else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Sales", f"₹{total_sales:,.2f}")
        col2.metric("Total Profit", f"₹{total_profit:,.2f}")
        col3.metric("Total Quantity Sold", f"{total_quantity:,.0f}")

        st.divider()

        st.subheader("Sales by Category")

        category_name = get_column(category, ["CATEGORY"])
        if category_name and cat_sales:
            fig = px.bar(
                category,
                x=category_name,
                y=cat_sales,
                title="Category-wise Sales",
                color=category_name
            )
            show_chart(fig)

        st.subheader("Regional Sales")

        region_name = get_column(region, ["REGION"])
        region_sales = get_column(region, ["TOTAL_SALES", "SALES"])

        if region_name and region_sales:
            fig = px.pie(
                region,
                names=region_name,
                values=region_sales,
                title="Sales Contribution by Region",
                hole=0.4
            )
            show_chart(fig)

        st.subheader("Monthly Sales Trend")

        year_col = get_column(monthly, ["SALES_YEAR", "YEAR"])
        month_col = get_column(monthly, ["SALES_MONTH", "MONTH"])
        monthly_sales = get_column(monthly, ["TOTAL_SALES", "SALES"])

        if year_col and month_col and monthly_sales:
            monthly["PERIOD"] = (
                monthly[year_col].astype(str)
                + "-"
                + monthly[month_col].astype(str).str.zfill(2)
            )

            monthly = monthly.sort_values("PERIOD")

            fig = px.line(
                monthly,
                x="PERIOD",
                y=monthly_sales,
                markers=True,
                title="Monthly Sales Trend"
            )
            show_chart(fig)

    except Exception as e:
        st.error("Could not load the overview data.")
        st.exception(e)


# ==========================================================
# 2. CATEGORY ANALYSIS
# ==========================================================

elif page == "Category Analysis":

    st.header("Category Analysis")

    try:
        df = prepare_data(load_data("GOLD_CATEGORY_INSIGHTS"))

        category_col = get_column(df, ["CATEGORY"])
        sales_col = get_column(df, ["TOTAL_SALES", "SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT", "PROFIT"])
        quantity_col = get_column(df, ["TOTAL_QUANTITY", "QUANTITY"])

        if category_col and sales_col:
            fig = px.bar(
                df,
                x=category_col,
                y=sales_col,
                color=category_col,
                title="Sales by Category"
            )
            show_chart(fig)

        if category_col and profit_col:
            fig = px.bar(
                df,
                x=category_col,
                y=profit_col,
                color=category_col,
                title="Profit by Category"
            )
            show_chart(fig)

        if category_col and quantity_col:
            fig = px.pie(
                df,
                names=category_col,
                values=quantity_col,
                title="Quantity Sold by Category",
                hole=0.4
            )
            show_chart(fig)

        st.subheader("Category Data")
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load category analysis.")
        st.exception(e)


# ==========================================================
# 3. REGIONAL ANALYSIS
# ==========================================================

elif page == "Regional Analysis":

    st.header("Regional Analysis")

    try:
        df = prepare_data(load_data("GOLD_REGION_INSIGHTS"))

        region_col = get_column(df, ["REGION"])
        sales_col = get_column(df, ["TOTAL_SALES", "SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT", "PROFIT"])
        quantity_col = get_column(df, ["TOTAL_QUANTITY", "QUANTITY"])

        if region_col and sales_col:
            fig = px.bar(
                df,
                x=region_col,
                y=sales_col,
                color=region_col,
                title="Sales by Region"
            )
            show_chart(fig)

        if region_col and profit_col:
            fig = px.bar(
                df,
                x=region_col,
                y=profit_col,
                color=region_col,
                title="Profit by Region"
            )
            show_chart(fig)

        if region_col and quantity_col:
            fig = px.pie(
                df,
                names=region_col,
                values=quantity_col,
                title="Quantity Sold by Region",
                hole=0.4
            )
            show_chart(fig)

        st.subheader("Regional Data")
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load regional analysis.")
        st.exception(e)


# ==========================================================
# 4. MONTHLY TRENDS
# ==========================================================

elif page == "Monthly Trends":

    st.header("Monthly Sales Trends")

    try:
        df = prepare_data(load_data("GOLD_MONTHLY_SALES"))

        year_col = get_column(df, ["SALES_YEAR", "YEAR"])
        month_col = get_column(df, ["SALES_MONTH", "MONTH"])
        sales_col = get_column(df, ["TOTAL_SALES", "SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT", "PROFIT"])
        quantity_col = get_column(df, ["TOTAL_QUANTITY", "QUANTITY"])

        if year_col and month_col:
            df["PERIOD"] = (
                df[year_col].astype(str)
                + "-"
                + df[month_col].astype(str).str.zfill(2)
            )
            df = df.sort_values("PERIOD")

        if sales_col and "PERIOD" in df.columns:
            fig = px.line(
                df,
                x="PERIOD",
                y=sales_col,
                markers=True,
                title="Monthly Sales"
            )
            show_chart(fig)

        if profit_col and "PERIOD" in df.columns:
            fig = px.bar(
                df,
                x="PERIOD",
                y=profit_col,
                title="Monthly Profit"
            )
            show_chart(fig)

        if quantity_col and "PERIOD" in df.columns:
            fig = px.line(
                df,
                x="PERIOD",
                y=quantity_col,
                markers=True,
                title="Monthly Quantity Sold"
            )
            show_chart(fig)

        st.subheader("Monthly Sales Data")
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load monthly trends.")
        st.exception(e)


# ==========================================================
# 5. CUSTOMER INSIGHTS
# ==========================================================

elif page == "Customer Insights":

    st.header("Customer Insights")

    try:
        df = prepare_data(load_data("GOLD_CUSTOMER_INSIGHTS"))

        customer_col = get_column(
            df, ["CUSTOMER_NAME", "CUSTOMER", "CUSTOMER_ID"]
        )
        sales_col = get_column(df, ["TOTAL_SALES", "SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT", "PROFIT"])
        orders_col = get_column(
            df, ["TOTAL_ORDERS", "ORDER_COUNT", "ORDERS"]
        )

        if customer_col and sales_col:
            top_customers = df.nlargest(10, sales_col)

            fig = px.bar(
                top_customers.sort_values(sales_col),
                x=sales_col,
                y=customer_col,
                orientation="h",
                title="Top 10 Customers by Sales"
            )
            show_chart(fig)

        if customer_col and profit_col:
            top_profit = df.nlargest(10, profit_col)

            fig = px.bar(
                top_profit.sort_values(profit_col),
                x=profit_col,
                y=customer_col,
                orientation="h",
                title="Top 10 Customers by Profit"
            )
            show_chart(fig)

        if customer_col and orders_col:
            top_orders = df.nlargest(10, orders_col)

            fig = px.bar(
                top_orders.sort_values(orders_col),
                x=orders_col,
                y=customer_col,
                orientation="h",
                title="Top 10 Customers by Orders"
            )
            show_chart(fig)

        st.subheader("Customer Data")
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load customer insights.")
        st.exception(e)


# ==========================================================
# 6. ADVANCED ANALYTICS
# ==========================================================

elif page == "Advanced Analytics":

    st.header("Advanced Analytics")
    st.write(
        "Explore additional business trends using the Gold Layer."
    )

    # ------------------------------------------------------
    # A. TOP 10 PROFITABLE PRODUCTS
    # ------------------------------------------------------

    st.subheader("1. Top 10 Profitable Products")

    try:
        df = prepare_data(load_data("GOLD_TOP_PRODUCTS"))

        product_col = get_column(df, ["PRODUCT_NAME"])
        profit_col = get_column(df, ["TOTAL_PROFIT"])
        sales_col = get_column(df, ["TOTAL_SALES"])

        if product_col and profit_col:
            fig = px.bar(
                df.sort_values(profit_col),
                x=profit_col,
                y=product_col,
                orientation="h",
                title="Top 10 Products by Profit"
            )
            show_chart(fig)

        if product_col and sales_col:
            fig = px.bar(
                df.sort_values(sales_col),
                x=sales_col,
                y=product_col,
                orientation="h",
                title="Top Products by Sales"
            )
            show_chart(fig)

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load Top Products analysis.")
        st.exception(e)

    st.divider()

    # ------------------------------------------------------
    # B. STATE-WISE SALES AND PROFIT
    # ------------------------------------------------------

    st.subheader("2. State-wise Sales and Profit")

    try:
        df = prepare_data(load_data("GOLD_STATE_ANALYSIS"))

        state_col = get_column(df, ["STATE"])
        sales_col = get_column(df, ["TOTAL_SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT"])

        if state_col and sales_col:
            top_states = df.nlargest(15, sales_col)

            fig = px.bar(
                top_states.sort_values(sales_col),
                x=sales_col,
                y=state_col,
                orientation="h",
                title="Top 15 States by Sales"
            )
            show_chart(fig)

        if state_col and profit_col:
            top_states = df.nlargest(15, profit_col)

            fig = px.bar(
                top_states.sort_values(profit_col),
                x=profit_col,
                y=state_col,
                orientation="h",
                title="Top 15 States by Profit"
            )
            show_chart(fig)

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load State Analysis.")
        st.exception(e)

    st.divider()

    # ------------------------------------------------------
    # C. MONTHLY PROFIT TRENDS
    # ------------------------------------------------------

    st.subheader("3. Monthly Profit Trends")

    try:
        df = prepare_data(load_data("GOLD_MONTHLY_PROFIT"))

        year_col = get_column(df, ["SALES_YEAR"])
        month_col = get_column(df, ["SALES_MONTH"])
        sales_col = get_column(df, ["TOTAL_SALES"])
        profit_col = get_column(df, ["TOTAL_PROFIT"])

        if year_col and month_col:
            df["PERIOD"] = (
                df[year_col].astype(str)
                + "-"
                + df[month_col].astype(str).str.zfill(2)
            )

            df = df.sort_values("PERIOD")

        if "PERIOD" in df.columns and profit_col:
            fig = px.line(
                df,
                x="PERIOD",
                y=profit_col,
                markers=True,
                title="Monthly Profit Trend"
            )
            show_chart(fig)

        if "PERIOD" in df.columns and sales_col:
            fig = px.bar(
                df,
                x="PERIOD",
                y=sales_col,
                title="Monthly Sales Trend"
            )
            show_chart(fig)

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load Monthly Profit analysis.")
        st.exception(e)

    st.divider()

    # ------------------------------------------------------
    # D. DISCOUNT VS PROFIT
    # ------------------------------------------------------

    st.subheader("4. Discount vs Profit Analysis")

    try:
        df = prepare_data(load_data("GOLD_DISCOUNT_ANALYSIS"))

        discount_col = get_column(df, ["DISCOUNT"])
        profit_col = get_column(df, ["TOTAL_PROFIT"])
        average_profit_col = get_column(df, ["AVERAGE_PROFIT"])
        sales_col = get_column(df, ["TOTAL_SALES"])

        if discount_col and average_profit_col:
            fig = px.bar(
                df.sort_values(discount_col),
                x=discount_col,
                y=average_profit_col,
                title="Average Profit at Different Discount Levels",
                labels={
                    discount_col: "Discount",
                    average_profit_col: "Average Profit"
                }
            )
            show_chart(fig)

        if discount_col and profit_col:
            fig = px.line(
                df.sort_values(discount_col),
                x=discount_col,
                y=profit_col,
                markers=True,
                title="Total Profit by Discount Level"
            )
            show_chart(fig)

        if discount_col and sales_col:
            fig = px.bar(
                df.sort_values(discount_col),
                x=discount_col,
                y=sales_col,
                title="Sales by Discount Level"
            )
            show_chart(fig)

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load Discount Analysis.")
        st.exception(e)


# ==========================================================
# FOOTER
# ==========================================================

st.sidebar.divider()
st.sidebar.caption("Retail Sales Analytics")
st.sidebar.caption("⚡ Powered by Snowflake + Streamlit")

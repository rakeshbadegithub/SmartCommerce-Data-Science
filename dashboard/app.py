
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SmartCommerce Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SmartCommerce Analytics Dashboard")
st.markdown("Brazilian E-Commerce Data Analysis")

API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# API DATA LOADING
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_api_data(endpoint):
    response = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


try:
    summary = get_api_data("summary")
    status_data = get_api_data("orders/status")
    monthly_data = get_api_data("orders/monthly")
    review_data = get_api_data("reviews/distribution")

    st.success("Connected to SmartCommerce API")

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to FastAPI: {e}")
    st.info("Make sure your FastAPI server is running on port 8000.")
    st.stop()


# --------------------------------------------------
# LOCAL DATA LOADING
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_local_data():
    orders = pd.read_csv(DATA_PATH / "orders_cleaned.csv")
    products = pd.read_csv(DATA_PATH / "products_cleaned.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

    return orders, products


try:
    orders, products = load_local_data()

except Exception as e:
    st.error(f"Could not load local datasets: {e}")
    st.stop()


# --------------------------------------------------
# SIDEBAR FILTER
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

statuses = sorted(
    orders["order_status"].dropna().unique()
)

selected_status = st.sidebar.multiselect(
    "Filter Recent Orders by Status",
    statuses,
    default=statuses
)

filtered_orders = orders[
    orders["order_status"].isin(selected_status)
].copy()


# --------------------------------------------------
# KPI METRICS - FROM FASTAPI
# --------------------------------------------------

st.subheader("Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Orders",
    f"{summary['total_orders']:,}"
)

col2.metric(
    "Delivered Orders",
    f"{summary['delivered_orders']:,}"
)

col3.metric(
    "Delivery Rate",
    f"{summary['delivery_rate']:.2f}%"
)

col4.metric(
    "Average Review",
    f"{summary['average_review']:.2f}/5"
)

st.divider()


# --------------------------------------------------
# MONTHLY ORDER TREND - FROM FASTAPI
# --------------------------------------------------

st.subheader("Monthly Order Trend")

monthly_df = pd.DataFrame(monthly_data)

if not monthly_df.empty:
    monthly_df = monthly_df.sort_values("month")

    fig = px.line(
        monthly_df,
        x="month",
        y="orders",
        markers=True,
        title="Orders Over Time"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Orders"
    )

    st.plotly_chart(fig, width="stretch")

else:
    st.info("No monthly order data available.")


# --------------------------------------------------
# ORDER STATUS AND REVIEW DISTRIBUTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Order Status Distribution")

    status_df = pd.DataFrame(
        list(status_data.items()),
        columns=["status", "count"]
    )

    if not status_df.empty:
        fig = px.pie(
            status_df,
            names="status",
            values="count",
            hole=0.4
        )

        st.plotly_chart(fig, width="stretch")

    else:
        st.info("No order status data available.")


with col2:
    st.subheader("Customer Review Distribution")

    review_df = pd.DataFrame(
        list(review_data.items()),
        columns=["rating", "count"]
    )

    if not review_df.empty:
        review_df["rating"] = review_df["rating"].astype(int)
        review_df = review_df.sort_values("rating")

        fig = px.bar(
            review_df,
            x="rating",
            y="count",
            labels={
                "rating": "Review Score",
                "count": "Number of Reviews"
            }
        )

        st.plotly_chart(fig, width="stretch")

    else:
        st.info("No review data available.")


# --------------------------------------------------
# PRODUCT CATEGORY ANALYSIS - LOCAL DATA
# --------------------------------------------------

st.subheader("Product Category Distribution")

category_data = (
    products["product_category_name"]
    .fillna("unknown")
    .value_counts()
    .head(10)
    .reset_index()
)

category_data.columns = ["category", "products"]

if not category_data.empty:
    fig = px.bar(
        category_data,
        x="products",
        y="category",
        orientation="h",
        title="Top 10 Product Categories by Catalog Count"
    )

    st.plotly_chart(fig, width="stretch")

else:
    st.info("No product category data available.")


# --------------------------------------------------
# RECENT ORDERS - LOCAL DATA
# --------------------------------------------------

st.subheader("Recent Orders")

display_columns = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp"
]

available_columns = [
    column
    for column in display_columns
    if column in filtered_orders.columns
]

st.dataframe(
    filtered_orders[available_columns].head(20),
    width="stretch"
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "SmartCommerce | Brazilian E-Commerce Analytics | "
    "Powered by Streamlit and FastAPI"
)

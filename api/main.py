
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from functools import lru_cache
import pandas as pd

# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title="SmartCommerce API",
    description="Brazilian E-Commerce Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed"


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_orders():

    file_path = DATA_PATH / "orders_cleaned.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Orders dataset not found"
        )

    try:
        df = pd.read_csv(file_path)

        df["order_purchase_timestamp"] = pd.to_datetime(
            df["order_purchase_timestamp"],
            errors="coerce"
        )

        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading orders dataset: {str(e)}"
        )


@lru_cache(maxsize=1)
def load_reviews():

    file_path = DATA_PATH / "reviews_cleaned.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Reviews dataset not found"
        )

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading reviews dataset: {str(e)}"
        )


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to SmartCommerce API",
        "status": "Running",
        "documentation": "/docs"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "Healthy",
        "application": "SmartCommerce"
    }


# --------------------------------------------------
# SUMMARY ENDPOINT
# --------------------------------------------------

@app.get("/summary")
def get_summary():

    orders = load_orders()
    reviews = load_reviews()

    total_orders = len(orders)

    delivered_orders = int(
        (orders["order_status"] == "delivered").sum()
    )

    delivery_rate = (
        delivered_orders / total_orders * 100
        if total_orders > 0 else 0
    )

    average_review = reviews["review_score"].mean()

    return {
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "delivery_rate": round(delivery_rate, 2),
        "average_review": round(float(average_review), 2)
    }


# --------------------------------------------------
# ORDER STATUS ENDPOINT
# --------------------------------------------------

@app.get("/orders/status")
def get_order_status():

    orders = load_orders()

    status_counts = (
        orders["order_status"]
        .value_counts()
        .to_dict()
    )

    return status_counts


# --------------------------------------------------
# MONTHLY ORDER TREND
# --------------------------------------------------

@app.get("/orders/monthly")
def get_monthly_orders():

    orders = load_orders()

    monthly = (
        orders.dropna(subset=["order_purchase_timestamp"])
        .assign(
            month=lambda df:
                df["order_purchase_timestamp"]
                .dt.to_period("M")
                .astype(str)
        )
        .groupby("month")
        .size()
        .reset_index(name="orders")
        .sort_values("month")
    )

    return monthly.to_dict(orient="records")


# --------------------------------------------------
# CUSTOMER REVIEW ANALYSIS
# --------------------------------------------------

@app.get("/reviews/distribution")
def get_review_distribution():

    reviews = load_reviews()

    distribution = (
        reviews["review_score"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return distribution


# --------------------------------------------------
# DATASET INFORMATION
# --------------------------------------------------

@app.get("/data-info")
def get_data_info():

    orders = load_orders()
    reviews = load_reviews()

    return {
        "orders_dataset": {
            "total_records": len(orders),
            "columns": len(orders.columns)
        },
        "reviews_dataset": {
            "total_records": len(reviews),
            "columns": len(reviews.columns)
        }
    }

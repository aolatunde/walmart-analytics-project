import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_data import get_sales_performance_data


st.set_page_config(page_title="Sales Performance", layout="wide")
st.title("Sales Performance")

df = get_sales_performance_data()

metrics = df[df["VIEW_NAME"] == "Metric"].iloc[0]
weekly = df[df["VIEW_NAME"] == "Weekly Trend"].copy()
stores = df[df["VIEW_NAME"] == "Store Ranking"].copy()
departments = df[df["VIEW_NAME"] == "Department Ranking"].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${metrics['TOTAL_SALES']:,.2f}")
col2.metric("Avg Weekly Sales", f"${metrics['AVG_WEEKLY_SALES']:,.2f}")
col3.metric("Stores", f"{int(metrics['STORE_COUNT']):,}")
col4.metric("Departments", f"{int(metrics['DEPT_COUNT']):,}")

st.subheader("Sales Trend")

weekly["STORE_DATE"] = pd.to_datetime(weekly["DIMENSION"], errors="coerce")
weekly = weekly.dropna(subset=["STORE_DATE"]).sort_values("STORE_DATE")

if weekly["STORE_DATE"].nunique() > 1:
    fig = px.line(
        weekly,
        x="STORE_DATE",
        y="TOTAL_SALES",
        markers=True,
        title="Total Sales by Week",
        labels={"STORE_DATE": "Week", "TOTAL_SALES": "Total Sales"},
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Weekly trend will appear after the GOLD fact table is rebuilt with STORE_DATE.")

col_a, col_b = st.columns(2)

with col_a:
    top_departments = departments.sort_values("TOTAL_SALES", ascending=False).head(15)
    fig2 = px.bar(
        top_departments,
        x="DIMENSION",
        y="TOTAL_SALES",
        title="Top 15 Departments by Sales",
        labels={"DIMENSION": "Department", "TOTAL_SALES": "Total Sales"},
    )
    st.plotly_chart(fig2, width="stretch")

with col_b:
    top_stores = stores.sort_values("TOTAL_SALES", ascending=False).head(15)
    fig3 = px.bar(
        top_stores,
        x="DIMENSION",
        y="TOTAL_SALES",
        title="Top 15 Stores by Sales",
        labels={"DIMENSION": "Store", "TOTAL_SALES": "Total Sales"},
    )
    st.plotly_chart(fig3, width="stretch")

st.subheader("Department Ranking")

department_table = departments.sort_values("TOTAL_SALES", ascending=False).rename(
    columns={
        "DIMENSION": "DEPT_ID",
        "TOTAL_SALES": "TOTAL_SALES",
        "AVG_WEEKLY_SALES": "AVG_WEEKLY_SALES",
        "STORE_COUNT": "STORES",
        "ROW_COUNT": "ROWS",
    }
)

st.dataframe(
    department_table[["DEPT_ID", "TOTAL_SALES", "AVG_WEEKLY_SALES", "STORES", "ROWS"]],
    width="stretch",
    hide_index=True,
)

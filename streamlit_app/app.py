import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_data import get_markdown_analysis_data, get_sales_performance_data


st.set_page_config(
    page_title="Walmart Sales Analytics",
    layout="wide",
)

st.title("Walmart Sales Analytics Dashboard")
st.markdown("Snowflake + dbt + Streamlit dashboard using Gold layer tables.")

sales_df = get_sales_performance_data()
analysis_df = get_markdown_analysis_data()

metrics = sales_df[sales_df["VIEW_NAME"] == "Metric"].iloc[0]
weekly = sales_df[sales_df["VIEW_NAME"] == "Weekly Trend"].copy()
stores = sales_df[sales_df["VIEW_NAME"] == "Store Ranking"].copy()
departments = sales_df[sales_df["VIEW_NAME"] == "Department Ranking"].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${metrics['TOTAL_SALES']:,.2f}")
col2.metric("Avg Weekly Sales", f"${metrics['AVG_WEEKLY_SALES']:,.2f}")
col3.metric("Stores", f"{int(metrics['STORE_COUNT']):,}")
col4.metric("Departments", f"{int(metrics['DEPT_COUNT']):,}")

st.divider()

st.subheader("Sales Overview")

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
    top_stores = stores.sort_values("TOTAL_SALES", ascending=False).head(10)
    fig2 = px.bar(
        top_stores,
        x="DIMENSION",
        y="TOTAL_SALES",
        title="Top 10 Stores by Sales",
        labels={"DIMENSION": "Store", "TOTAL_SALES": "Total Sales"},
    )
    st.plotly_chart(fig2, width="stretch")

with col_b:
    top_departments = departments.sort_values("TOTAL_SALES", ascending=False).head(10)
    fig3 = px.bar(
        top_departments,
        x="DIMENSION",
        y="TOTAL_SALES",
        title="Top 10 Departments by Sales",
        labels={"DIMENSION": "Department", "TOTAL_SALES": "Total Sales"},
    )
    st.plotly_chart(fig3, width="stretch")

st.subheader("Business Factors")

markdown_df = analysis_df[analysis_df["FACTOR"] == "Markdown"]
unemployment_df = analysis_df[analysis_df["FACTOR"] == "Unemployment"]

col_c, col_d = st.columns(2)

with col_c:
    fig4 = px.scatter(
        markdown_df,
        x="FACTOR_VALUE",
        y="AVG_WEEKLY_SALES",
        size="ROW_COUNT",
        title="Markdown vs Average Weekly Sales",
        labels={
            "FACTOR_VALUE": "Total Markdown",
            "AVG_WEEKLY_SALES": "Average Weekly Sales",
            "ROW_COUNT": "Rows",
        },
    )
    st.plotly_chart(fig4, width="stretch")

with col_d:
    fig5 = px.scatter(
        unemployment_df,
        x="FACTOR_VALUE",
        y="AVG_WEEKLY_SALES",
        size="ROW_COUNT",
        title="Unemployment vs Average Weekly Sales",
        labels={
            "FACTOR_VALUE": "Unemployment",
            "AVG_WEEKLY_SALES": "Average Weekly Sales",
            "ROW_COUNT": "Rows",
        },
    )
    st.plotly_chart(fig5, width="stretch")

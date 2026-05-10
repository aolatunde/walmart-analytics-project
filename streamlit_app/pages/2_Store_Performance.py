import plotly.express as px
import streamlit as st

from dashboard_data import get_store_performance_data


st.set_page_config(page_title="Store Performance", layout="wide")
st.title("Store Performance")

summary = get_store_performance_data()

col1, col2, col3 = st.columns(3)
col1.metric("Stores", f"{summary['STORE_ID'].nunique():,}")
col2.metric("Total Sales", f"${summary['TOTAL_SALES'].sum():,.2f}")
col3.metric("Avg Store Sales", f"${summary['TOTAL_SALES'].mean():,.2f}")

fig = px.scatter(
    summary.dropna(subset=["STORE_SIZE"]),
    x="STORE_SIZE",
    y="TOTAL_SALES",
    color="STORE_TYPE",
    size="DEPARTMENTS",
    hover_data=["STORE_ID", "AVG_WEEKLY_SALES"],
    title="Store Size vs Total Sales",
)

if summary["STORE_SIZE"].notna().any():
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Store size values are not populated in the current GOLD store dimension.")

top_stores = summary.head(15)

fig2 = px.bar(
    top_stores,
    x="STORE_ID",
    y="TOTAL_SALES",
    color="STORE_TYPE" if top_stores["STORE_TYPE"].notna().any() else None,
    title="Top 15 Stores by Total Sales",
)

st.plotly_chart(fig2, width="stretch")

st.dataframe(summary, width="stretch", hide_index=True)

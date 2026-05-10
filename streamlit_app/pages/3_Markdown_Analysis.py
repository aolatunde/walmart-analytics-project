import plotly.express as px
import streamlit as st

from dashboard_data import get_markdown_analysis_data


st.set_page_config(page_title="Markdown Analysis", layout="wide")
st.title("Markdown & Economic Analysis")

df = get_markdown_analysis_data()

markdown_df = df[df["FACTOR"] == "Markdown"]

fig = px.scatter(
    markdown_df,
    x="FACTOR_VALUE",
    y="AVG_WEEKLY_SALES",
    size="ROW_COUNT",
    title="Markdown Impact on Average Weekly Sales",
    labels={
        "FACTOR_VALUE": "Total Markdown",
        "AVG_WEEKLY_SALES": "Average Weekly Sales",
        "ROW_COUNT": "Rows",
    },
)

st.plotly_chart(fig, width="stretch")

col1, col2 = st.columns(2)

with col1:
    unemployment_df = df[df["FACTOR"] == "Unemployment"]
    fig2 = px.scatter(
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
    st.plotly_chart(fig2, width="stretch")

with col2:
    cpi_df = df[df["FACTOR"] == "CPI"]
    fig3 = px.scatter(
        cpi_df,
        x="FACTOR_VALUE",
        y="AVG_WEEKLY_SALES",
        size="ROW_COUNT",
        title="CPI vs Average Weekly Sales",
        labels={
            "FACTOR_VALUE": "CPI",
            "AVG_WEEKLY_SALES": "Average Weekly Sales",
            "ROW_COUNT": "Rows",
        },
    )
    st.plotly_chart(fig3, width="stretch")

fuel_df = df[df["FACTOR"] == "Fuel Price"]
fig4 = px.scatter(
    fuel_df,
    x="FACTOR_VALUE",
    y="AVG_WEEKLY_SALES",
    size="ROW_COUNT",
    title="Fuel Price vs Average Weekly Sales",
    labels={
        "FACTOR_VALUE": "Fuel Price",
        "AVG_WEEKLY_SALES": "Average Weekly Sales",
        "ROW_COUNT": "Rows",
    },
)

st.plotly_chart(fig4, width="stretch")

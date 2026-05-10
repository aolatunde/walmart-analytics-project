import pandas as pd
import streamlit as st

from snowflake_connection import run_query


FACT_COLUMNS_QUERY = """
    SELECT UPPER(COLUMN_NAME) AS COLUMN_NAME
    FROM WALMART_PROJECT_DB.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'GOLD'
        AND TABLE_NAME = 'WALMART_FACT_TABLE'
"""

STORE_PERFORMANCE_QUERY = """
    SELECT
        f.STORE_ID,
        SUM(f.STORE_WEEKLY_SALES) AS TOTAL_SALES,
        AVG(f.STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
        COUNT(DISTINCT f.DEPT_ID) AS DEPARTMENTS,
        MAX(TRY_TO_NUMBER(s.STORE_SIZE)) AS STORE_SIZE,
        MAX(s.STORE_TYPE) AS STORE_TYPE
    FROM WALMART_PROJECT_DB.GOLD.WALMART_FACT_TABLE f
    LEFT JOIN (
        SELECT
            STORE_ID,
            MAX(STORE_TYPE) AS STORE_TYPE,
            MAX(TRY_TO_NUMBER(STORE_SIZE)) AS STORE_SIZE
        FROM WALMART_PROJECT_DB.GOLD.WALMART_STORE_DIM
        GROUP BY STORE_ID
    ) s
        ON f.STORE_ID = s.STORE_ID
    GROUP BY f.STORE_ID
"""

MARKDOWN_ANALYSIS_QUERY = """
    WITH base AS (
        SELECT
            STORE_WEEKLY_SALES,
            COALESCE(MARKDOWN1, 0)
                + COALESCE(MARKDOWN2, 0)
                + COALESCE(MARKDOWN3, 0)
                + COALESCE(MARKDOWN4, 0)
                + COALESCE(MARKDOWN5, 0) AS TOTAL_MARKDOWN,
            UNEMPLOYMENT,
            CPI,
            FUEL_PRICE,
            STORE_TEMPERATURE
        FROM WALMART_PROJECT_DB.GOLD.WALMART_FACT_TABLE
    ),
    markdown_bins AS (
        SELECT
            'Markdown' AS FACTOR,
            ROUND(TOTAL_MARKDOWN, -2) AS FACTOR_VALUE,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT
        FROM base
        GROUP BY ROUND(TOTAL_MARKDOWN, -2)
    ),
    unemployment_bins AS (
        SELECT
            'Unemployment' AS FACTOR,
            ROUND(UNEMPLOYMENT, 1) AS FACTOR_VALUE,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT
        FROM base
        WHERE UNEMPLOYMENT IS NOT NULL
        GROUP BY ROUND(UNEMPLOYMENT, 1)
    ),
    cpi_bins AS (
        SELECT
            'CPI' AS FACTOR,
            ROUND(CPI, 1) AS FACTOR_VALUE,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT
        FROM base
        WHERE CPI IS NOT NULL
        GROUP BY ROUND(CPI, 1)
    ),
    fuel_bins AS (
        SELECT
            'Fuel Price' AS FACTOR,
            ROUND(FUEL_PRICE, 2) AS FACTOR_VALUE,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT
        FROM base
        WHERE FUEL_PRICE IS NOT NULL
        GROUP BY ROUND(FUEL_PRICE, 2)
    )
    SELECT * FROM markdown_bins
    UNION ALL
    SELECT * FROM unemployment_bins
    UNION ALL
    SELECT * FROM cpi_bins
    UNION ALL
    SELECT * FROM fuel_bins
"""


def build_base_query() -> str:
    date_expression = get_fact_date_expression()

    return f"""
    SELECT
        f.STORE_ID,
        f.DEPT_ID,
        {date_expression} AS STORE_DATE,
        f.STORE_WEEKLY_SALES,
        f.FUEL_PRICE,
        f.STORE_TEMPERATURE,
        f.UNEMPLOYMENT,
        f.CPI,
        f.MARKDOWN1,
        f.MARKDOWN2,
        f.MARKDOWN3,
        f.MARKDOWN4,
        f.MARKDOWN5,
        s.STORE_TYPE,
        s.STORE_SIZE
    FROM WALMART_PROJECT_DB.GOLD.WALMART_FACT_TABLE f
    LEFT JOIN (
        SELECT
            STORE_ID,
            MAX(STORE_TYPE) AS STORE_TYPE,
            MAX(TRY_TO_NUMBER(STORE_SIZE)) AS STORE_SIZE
        FROM WALMART_PROJECT_DB.GOLD.WALMART_STORE_DIM
        GROUP BY STORE_ID
    ) s
        ON f.STORE_ID = s.STORE_ID
"""


def get_fact_date_expression() -> str:
    columns_df = run_query(FACT_COLUMNS_QUERY)
    fact_columns = set(columns_df["COLUMN_NAME"].str.upper())

    if "STORE_DATE" in fact_columns:
        return "f.STORE_DATE"
    elif "VRSN_START_DATE" in fact_columns:
        return "f.VRSN_START_DATE"

    return "NULL"


def build_sales_performance_query() -> str:
    date_expression = get_fact_date_expression()

    return f"""
    WITH base AS (
        SELECT
            STORE_ID,
            DEPT_ID,
            {date_expression} AS STORE_DATE,
            STORE_WEEKLY_SALES
        FROM WALMART_PROJECT_DB.GOLD.WALMART_FACT_TABLE f
    ),
    totals AS (
        SELECT
            'Metric' AS VIEW_NAME,
            'All Sales' AS DIMENSION,
            SUM(STORE_WEEKLY_SALES) AS TOTAL_SALES,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT,
            COUNT(DISTINCT STORE_ID) AS STORE_COUNT,
            COUNT(DISTINCT DEPT_ID) AS DEPT_COUNT
        FROM base
    ),
    weekly AS (
        SELECT
            'Weekly Trend' AS VIEW_NAME,
            TO_VARCHAR(CAST(STORE_DATE AS DATE)) AS DIMENSION,
            SUM(STORE_WEEKLY_SALES) AS TOTAL_SALES,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT,
            COUNT(DISTINCT STORE_ID) AS STORE_COUNT,
            COUNT(DISTINCT DEPT_ID) AS DEPT_COUNT
        FROM base
        WHERE STORE_DATE IS NOT NULL
        GROUP BY CAST(STORE_DATE AS DATE)
    ),
    stores AS (
        SELECT
            'Store Ranking' AS VIEW_NAME,
            TO_VARCHAR(STORE_ID) AS DIMENSION,
            SUM(STORE_WEEKLY_SALES) AS TOTAL_SALES,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT,
            1 AS STORE_COUNT,
            COUNT(DISTINCT DEPT_ID) AS DEPT_COUNT
        FROM base
        GROUP BY STORE_ID
    ),
    departments AS (
        SELECT
            'Department Ranking' AS VIEW_NAME,
            TO_VARCHAR(DEPT_ID) AS DIMENSION,
            SUM(STORE_WEEKLY_SALES) AS TOTAL_SALES,
            AVG(STORE_WEEKLY_SALES) AS AVG_WEEKLY_SALES,
            COUNT(*) AS ROW_COUNT,
            COUNT(DISTINCT STORE_ID) AS STORE_COUNT,
            1 AS DEPT_COUNT
        FROM base
        GROUP BY DEPT_ID
    )
    SELECT * FROM totals
    UNION ALL
    SELECT * FROM weekly
    UNION ALL
    SELECT * FROM stores
    UNION ALL
    SELECT * FROM departments
"""


@st.cache_data(ttl=600, show_spinner="Loading sales performance data...")
def load_sales_performance_data() -> pd.DataFrame:
    df = run_query(build_sales_performance_query())
    df.columns = [column.upper() for column in df.columns]

    numeric_columns = [
        "TOTAL_SALES",
        "AVG_WEEKLY_SALES",
        "ROW_COUNT",
        "STORE_COUNT",
        "DEPT_COUNT",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def get_sales_performance_data() -> pd.DataFrame:
    try:
        df = load_sales_performance_data()
    except Exception as exc:
        st.error("Unable to load sales performance data from Snowflake.")
        st.info("Check your `.env` values and confirm the GOLD fact table is built.")
        st.exception(exc)
        st.stop()

    if df.empty:
        st.warning("Snowflake returned no sales performance rows.")
        st.stop()

    return df


@st.cache_data(ttl=600, show_spinner="Loading Walmart analytics data...")
def load_walmart_data() -> pd.DataFrame:
    df = run_query(build_base_query())
    df.columns = [column.upper() for column in df.columns]

    if "STORE_DATE" in df.columns:
        df["STORE_DATE"] = pd.to_datetime(df["STORE_DATE"], errors="coerce")

    numeric_columns = [
        "STORE_ID",
        "DEPT_ID",
        "STORE_WEEKLY_SALES",
        "FUEL_PRICE",
        "STORE_TEMPERATURE",
        "UNEMPLOYMENT",
        "CPI",
        "MARKDOWN1",
        "MARKDOWN2",
        "MARKDOWN3",
        "MARKDOWN4",
        "MARKDOWN5",
        "STORE_SIZE",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def get_dashboard_data() -> pd.DataFrame:
    try:
        df = load_walmart_data()
    except Exception as exc:
        st.error("Unable to load data from Snowflake.")
        st.info("Check your `.env` values and run dbt so the GOLD tables are built.")
        st.exception(exc)
        st.stop()

    if df.empty:
        st.warning("Snowflake returned no rows for the Walmart GOLD tables.")
        st.stop()

    return df


@st.cache_data(ttl=600, show_spinner="Loading store performance data...")
def load_store_performance_data() -> pd.DataFrame:
    df = run_query(STORE_PERFORMANCE_QUERY)
    df.columns = [column.upper() for column in df.columns]

    numeric_columns = [
        "STORE_ID",
        "TOTAL_SALES",
        "AVG_WEEKLY_SALES",
        "DEPARTMENTS",
        "STORE_SIZE",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.sort_values("TOTAL_SALES", ascending=False)


def get_store_performance_data() -> pd.DataFrame:
    try:
        df = load_store_performance_data()
    except Exception as exc:
        st.error("Unable to load store performance data from Snowflake.")
        st.info("Check your `.env` values and confirm the GOLD tables are built.")
        st.exception(exc)
        st.stop()

    if df.empty:
        st.warning("Snowflake returned no store performance rows.")
        st.stop()

    return df


@st.cache_data(ttl=600, show_spinner="Loading markdown analysis data...")
def load_markdown_analysis_data() -> pd.DataFrame:
    df = run_query(MARKDOWN_ANALYSIS_QUERY)
    df.columns = [column.upper() for column in df.columns]

    numeric_columns = ["FACTOR_VALUE", "AVG_WEEKLY_SALES", "ROW_COUNT"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.sort_values(["FACTOR", "FACTOR_VALUE"])


def get_markdown_analysis_data() -> pd.DataFrame:
    try:
        df = load_markdown_analysis_data()
    except Exception as exc:
        st.error("Unable to load markdown analysis data from Snowflake.")
        st.info("Check your `.env` values and confirm the GOLD fact table is built.")
        st.exception(exc)
        st.stop()

    if df.empty:
        st.warning("Snowflake returned no markdown analysis rows.")
        st.stop()

    return df

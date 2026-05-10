# Walmart Analytics Project

Streamlit dashboard and dbt project for Walmart sales analytics on Snowflake.

## Project Structure

- `streamlit_app/` - Streamlit dashboard pages and Snowflake query helpers.
- `dbt_project/` - dbt models, snapshots, and macros for silver/gold transformations.
- `snowflake/` - Snowflake setup SQL for database, schemas, stage, file format, bronze tables, and streams.

## Local Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local `.env` file from `.env.example` and fill in your Snowflake credentials:

```bash
cp .env.example .env
```

4. Run the Streamlit dashboard:

```bash
streamlit run streamlit_app/app.py
```

## Required Environment Variables

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ROLE`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`


# Retail Sales Analytics Dashboard

A Streamlit dashboard for exploring retail sales data stored in Snowflake (capstone project). It connects to the `CAPSTONE_DB.GOLD` schema and visualizes sales performance across several views.

## Features

- 🏠 **Overview** — high-level business KPIs
- 🗂️ **Category Analysis** — sales breakdown by product category
- 🌍 **Regional Analysis** — sales breakdown by region
- 📈 **Monthly Trends** — sales trends over time
- 👥 **Customer Insights** — customer-level metrics
- 🔬 **Advanced Analytics** — deeper analytical views

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI
- [Snowflake](https://www.snowflake.com/) — data warehouse (`snowflake-connector-python`)
- [Pandas](https://pandas.pydata.org/) — data wrangling
- [Plotly Express](https://plotly.com/python/plotly-express/) — charts

## Project Structure

```
honours/
├── app.py                   # Streamlit app (pages, queries, charts)
├── first.sql                # Snowflake schema/warehouse setup (databases, schemas, warehouse)
├── .streamlit/
│   ├── config.toml          # Streamlit theme config
│   └── secrets.toml         # Snowflake credentials (NOT committed — see below)
└── requirements.txt
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd honours
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet, generate one with:

```bash
pip install streamlit snowflake-connector-python pandas plotly
pip freeze > requirements.txt
```

### 3. Set up the Snowflake schema

Run `first.sql` against your Snowflake account to create the `CAPSTONE_DB` database, schemas (`BRONZE`, `SILVER`, `GOLD`, `CONTROL`), and the `CAPSTONE_WH` warehouse.

### 4. Configure secrets

Create `.streamlit/secrets.toml` (this file is gitignored and must **never** be committed):

```toml
[snowflake]
account = "your-account"
user = "your-username"
password = "your-password"
warehouse = "CAPSTONE_WH"
database = "CAPSTONE_DB"
schema = "GOLD"
role = "your-role"
```

### 5. Run the app

```bash
streamlit run app.py
```

## Security Notes

- `.streamlit/secrets.toml` contains live database credentials and is excluded via `.gitignore`. Never commit it.
- Rotate your Snowflake password if it was ever committed or shared accidentally.

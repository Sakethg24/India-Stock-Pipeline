# 🇮🇳 India Stock Data Pipeline

An end-to-end **ELT pipeline** for the Indian stock market (NSE — Nifty 50), built as a data engineering portfolio project.

Collects daily stock prices, company metadata, and financial news. Transforms raw data into a structured warehouse using dbt. Visualize with pgAdmin or any BI tool.

## Architecture

```
yfinance (NSE prices)   ─┐
Nifty 50 company list   ─┤─→ Python extract ─→ PostgreSQL (raw) ─→ dbt ─→ warehouse schema
Economic Times RSS      ─┘

          Docker · .env · psycopg2              dbt models
```

## Tech Stack

| Layer           | Tool                        |
|-----------------|-----------------------------|
| Containerization| Docker + Docker Compose      |
| Data Source     | yfinance (NSE prices)        |
| News Source     | Economic Times RSS           |
| Raw Database    | PostgreSQL 16                |
| Transformation  | dbt-postgres                 |
| Warehouse       | PostgreSQL (`warehouse` schema) |
| Language        | Python, SQL                  |

## Project Structure

```
india-stock-pipeline/
├── extract/
│   ├── companies.py       # Nifty 50 company list
│   ├── yfinance_ohlc.py   # Daily OHLC prices via yfinance
│   └── news_scraper.py    # News from Economic Times RSS
├── load/
│   ├── schema.sql         # Raw PostgreSQL table definitions
│   └── postgres_loader.py # Idempotent upsert into PostgreSQL
├── stock_transform/       # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml
│       ├── schema.yml
│       ├── staging/       # Clean raw data (VIEWs)
│       │   ├── stg_companies.sql
│       │   ├── stg_candles.sql
│       │   └── stg_news.sql
│       └── marts/         # Dimensional model (TABLEs)
│           ├── dim_companies.sql
│           ├── dim_times.sql
│           ├── fact_candles.sql
│           └── fact_news.sql
├── main.py                # Pipeline entry point
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/india-stock-pipeline
cd india-stock-pipeline
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and set your passwords
```

### 3. Start Docker (PostgreSQL + pgAdmin)

```bash
docker-compose up -d
```

### 4. Create the database schema

**Mac/Linux:**
```bash
docker exec -i stock_postgres psql -U admin -d stock_raw < load/schema.sql
```

**Windows (PowerShell):**
```powershell
Get-Content load/schema.sql | docker exec -i stock_postgres psql -U admin -d stock_raw
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the pipeline (Extract + Load)

```bash
python main.py
```

### 7. Run dbt transformations

```bash
cd stock_transform

# Copy profiles.yml to ~/.dbt/ OR run with --profiles-dir flag
dbt run --profiles-dir .

# Run data quality tests
dbt test --profiles-dir .

# Generate and view documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir . --port 8081
```

Open `http://localhost:8081` to explore the data lineage graph.

### 8. Browse data in pgAdmin

Open `http://localhost:8080` and log in with your `PGADMIN_EMAIL` and `PGADMIN_PASSWORD` from `.env`.

## Data Model

### Raw Layer (`public` schema)
| Table | Description |
|-------|-------------|
| `raw_companies` | Nifty 50 company list |
| `raw_candles` | Daily OHLC price data |
| `raw_news` | News headlines from Economic Times |

### Warehouse Layer (`warehouse` schema)
| Table | Type | Description |
|-------|------|-------------|
| `dim_companies` | Dimension | One row per company |
| `dim_times` | Dimension | One row per trading date (with financial year) |
| `fact_candles` | Fact | Daily prices + derived metrics (price_change, volatility) |
| `fact_news` | Fact | News articles + time breakdown |

## Key Concepts

- **ELT** (not ETL): Raw data is loaded first, transformed inside the DB using SQL
- **Idempotency**: All inserts use `ON CONFLICT DO NOTHING` — safe to re-run daily
- **dbt**: Manages SQL transforms, runs tests, and generates a data lineage graph
- **Indian Financial Year**: April–March (handled in `dim_times`)

## Author

Built as a data engineering portfolio project.

"""
ETL Loader: loads scraped data into PostgreSQL.
Usage: python -m etl.loader
"""
import os
import json
from dotenv import load_dotenv
from app.db import execute, query

load_dotenv()

DATA_FILE = os.path.join(os.path.dirname(__file__), "scraped_data.json")
DEFAULT_SOURCE = "ETL Auto"


def ensure_source(name):
    rows = query("SELECT id FROM kpi_sources WHERE name = %s", (name,))
    if rows:
        return rows[0]["id"]
    execute(
        "INSERT INTO kpi_sources (name, source_type) VALUES (%s, %s)",
        (name, "etl"),
    )
    rows = query("SELECT id FROM kpi_sources WHERE name = %s", (name,))
    return rows[0]["id"]


def load():
    if not os.path.exists(DATA_FILE):
        print(f"No data file found at {DATA_FILE}. Run scraper first.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    source_id = ensure_source(DEFAULT_SOURCE)
    loaded = 0

    for r in records:
        execute(
            "INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES (%s, %s, %s, %s, %s)",
            (source_id, r["metric_name"], r["metric_value"], r.get("unit", ""), r["period_date"]),
        )
        loaded += 1

    print(f"Loaded {loaded} metrics into database.")


if __name__ == "__main__":
    load()

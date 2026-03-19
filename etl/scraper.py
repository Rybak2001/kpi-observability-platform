"""
ETL Scraper: extracts data from a configured web source.
Usage: python -m etl.scraper
"""
import os
import json
from datetime import date
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "scraped_data.json")


def scrape():
    url = os.environ.get("ETL_SOURCE_URL")
    if not url:
        print("No ETL_SOURCE_URL configured. Generating sample data.")
        return generate_sample_data()

    print(f"Fetching data from {url}...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Example: extract table rows — adapt selector to real source
    rows = []
    table = soup.find("table")
    if table:
        for tr in table.find_all("tr")[1:]:  # skip header
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) >= 3:
                rows.append({
                    "metric_name": cells[0],
                    "metric_value": cells[1],
                    "unit": cells[2] if len(cells) > 2 else "",
                    "period_date": str(date.today()),
                })

    print(f"Extracted {len(rows)} records.")
    return rows


def generate_sample_data():
    """Generates sample KPI data for demo purposes."""
    import random
    today = str(date.today())
    metrics = [
        ("Ingresos Mensuales", random.uniform(50000, 150000), "MXN"),
        ("Clientes Nuevos", random.randint(10, 100), "count"),
        ("Tasa de Retención", random.uniform(70, 98), "%"),
        ("Tiempo de Respuesta", random.uniform(0.5, 5.0), "s"),
        ("Tickets Resueltos", random.randint(50, 500), "count"),
        ("NPS Score", random.randint(20, 90), "pts"),
    ]
    return [
        {"metric_name": m[0], "metric_value": round(m[1], 2), "unit": m[2], "period_date": today}
        for m in metrics
    ]


if __name__ == "__main__":
    data = scrape()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {OUTPUT_FILE}")

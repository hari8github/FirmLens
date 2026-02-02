import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data.data_extraction import extract_all
import re

# ------------------------
# Cleaning helpers
# ------------------------

def clean_number(val):
    if not val:
        return None
    val = val.replace(",", "")
    m = re.findall(r"-?\d+", val)
    return int(m[0]) if m else None


def clean_float(val):
    if not val:
        return None
    return float(val.replace(",", ""))


def clean_percent(val):
    if not val:
        return None
    return int(float(val.replace("%", "")))


def quarter_to_date(label):
    # "Dec 2025" → "2025-12-31"
    month_map = {
        "Mar": "03-31",
        "Jun": "06-30",
        "Sep": "09-30",
        "Dec": "12-31"
    }
    m, y = label.split()
    return f"{y}-{month_map[m]}"


def year_to_date(label):
    # "Mar 2025" → "2025-03-31"
    y = label.split()[1]
    return f"{y}-03-31"


# ------------------------
# Normalization
# ------------------------

def normalize():
    raw = extract_all()

    company_id = raw["company_name"].upper().replace(" ", "_")

    company = {
        "company_id": company_id,
        "name": raw["company_name"],
        "sector": raw["sector"],
        "industry": raw["industry"],
        "market_cap_cr": clean_number(raw["market_cap"]),
        "current_price": clean_number(raw["current_price"]),
        "description": raw.get("description"),
        "description_sources": raw.get("description_sources", [])
    }

    # Quarterly
    q = raw["quarterly"]
    quarterly_financials = []

    for i, label in enumerate(q["quarters"]):
        quarterly_financials.append({
            "company_id": company_id,
            "period_type": "quarter",
            "period_end": quarter_to_date(label),
            "label": label,
            "sales": clean_number(q["metrics"]["sales"][i]),
            "operating_profit": clean_number(q["metrics"]["operating_profit"][i]),
            "opm_percent": clean_percent(q["metrics"]["opm_percent"][i]),
            "net_profit": clean_number(q["metrics"]["net_profit"][i]),
            "eps": clean_float(q["metrics"]["eps"][i]),
            "source_url": q["sources"][i]
        })

    # Annual P&L
    pl = raw["pl"]
    annual_financials = []

    for i, year in enumerate(pl["years"]):
        annual_financials.append({
            "company_id": company_id,
            "period_type": "year",
            "period_end": year_to_date(year),
            "label": f"FY{year.split()[1]}",
            "sales": clean_number(pl["sales"][i]),
            "operating_profit": clean_number(pl["operating_profit"][i]),
            "opm_percent": clean_percent(pl["opm_percent"][i]),
            "net_profit": clean_number(pl["net_profit"][i]),
            "eps": clean_float(pl["eps"][i])
        })

    normalized_payload = {
        "company": company,
        "quarterly_financials": quarterly_financials,
        "annual_financials": annual_financials
    }

    return normalized_payload


# ------------------------
# Run directly
# ------------------------

if __name__ == "__main__":
    data = normalize()

    print("\n--- COMPANY ---")
    print(data["company"])

    print("\n--- QUARTERS ---", len(data["quarterly_financials"]))
    print(data["quarterly_financials"][-1])

    print("\n--- ANNUAL P&L ---")
    for row in data["annual_financials"]:
        print(row)

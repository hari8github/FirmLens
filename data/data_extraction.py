import requests
from bs4 import BeautifulSoup

def fetch_soup(url: str) -> BeautifulSoup:
    """Fetch the page and return a BeautifulSoup object."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

def get_company_name(soup: BeautifulSoup) -> str | None:
    """Extract company name from the page heading."""
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else None


def get_sector_and_industry(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Extract sector and industry from the peers section."""
    sector = None
    industry = None
    peers_section = soup.find("section", id="peers")
    if peers_section:
        sub_p = peers_section.find("p", class_="sub")
        if sub_p:
            links = sub_p.find_all("a")
            if len(links) >= 2:
                sector = links[1].get_text(strip=True)
                industry = links[-1].get_text(strip=True)
    return sector, industry

def get_market_data(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Extract market cap and current price from the ratios section."""
    market_cap = None
    current_price = None
    ratios_div = soup.find("div", class_="company-ratios")
    if ratios_div:
        ratios_ul = ratios_div.find("ul", id="top-ratios")
        if ratios_ul:
            for li in ratios_ul.find_all("li"):
                name_span = li.find("span", class_="name")
                if not name_span:
                    continue
                name = name_span.get_text(strip=True)
                value_span = li.find("span", class_="value")
                if not value_span:
                    continue
                value = value_span.get_text(" ", strip=True)
                if name == "Market Cap":
                    market_cap = value
                elif name == "Current Price":
                    current_price = value
    return market_cap, current_price

def get_description_and_sources(soup: BeautifulSoup) -> tuple[str | None, list[str]]:
    """Extract company description and source links from the profile section."""
    description = None
    sources = []
    company_info = soup.find("div", class_="company-info")
    if company_info:
        profile_div = company_info.find("div", class_="company-profile")
        if profile_div:
            about_div = profile_div.find("div", class_=["sub", "about"])
            if about_div:
                p_tag = about_div.find("p")
                if p_tag:
                    description = p_tag.get_text(" ", strip=True)
                    for a in p_tag.find_all("a", href=True):
                        sources.append(a["href"])
    return description, sources

def get_quarter_labels(soup):
    quarters = []

    section = soup.find("section", id="quarters")
    if not section:
        return quarters

    thead = section.find("thead")
    if not thead:
        return quarters

    ths = thead.find_all("th")[1:]  # skip first empty header
    for th in ths:
        quarters.append(th.get_text(strip=True))

    return quarters

def extract_metric_row(tbody, metric_name):
    row = None
    for tr in tbody.find_all("tr"):
        first_td = tr.find("td", class_="text")
        if first_td and metric_name in first_td.get_text(strip=True):
            row = tr
            break

    if not row:
        return []

    values = []
    tds = row.find_all("td")[1:]  # skip metric name column
    for td in tds:
        values.append(td.get_text(strip=True))

    return values

def get_quarterly_financials(soup):
    data = {}

    section = soup.find("section", id="quarters")
    if not section:
        return data

    tbody = section.find("tbody")
    if not tbody:
        return data

    data["sales"] = extract_metric_row(tbody, "Sales")
    data["operating_profit"] = extract_metric_row(tbody, "Operating Profit")
    data["opm_percent"] = extract_metric_row(tbody, "OPM")
    data["net_profit"] = extract_metric_row(tbody, "Net Profit")
    data["eps"] = extract_metric_row(tbody, "EPS")

    return data

def get_quarterly_pdf_sources(soup):
    sources = []

    section = soup.find("section", id="quarters")
    if not section:
        return sources

    tbody = section.find("tbody")
    if not tbody:
        return sources

    for tr in tbody.find_all("tr"):
        first_td = tr.find("td", class_="text")
        if first_td and "Raw PDF" in first_td.get_text(strip=True):
            tds = tr.find_all("td")[1:]
            for td in tds:
                a = td.find("a", href=True)
                if a:
                    sources.append("https://www.screener.in" + a["href"])
                else:
                    sources.append(None)

    return sources

def get_quarterly_results(soup):
    quarters = get_quarter_labels(soup)
    financials = get_quarterly_financials(soup)
    pdf_sources = get_quarterly_pdf_sources(soup)

    return {
        "quarters": quarters,
        "metrics": financials,
        "sources": pdf_sources
    }

def get_profit_and_loss(soup):
    pl_data = {
        "years": [],
        "sales": [],
        "operating_profit": [],
        "opm_percent": [],
        "net_profit": [],
        "eps": []
    }

    section = soup.find("section", id="profit-loss")
    if not section:
        return pl_data

    # --- Extract years (Mar 2022 → Mar 2025) ---
    thead = section.find("thead")
    if not thead:
        return pl_data

    all_years = [th.get_text(strip=True) for th in thead.find_all("th")[1:]]
    target_years = ["Mar 2022", "Mar 2023", "Mar 2024", "Mar 2025"]

    year_indices = []
    for i, year in enumerate(all_years):
        if year in target_years:
            pl_data["years"].append(year)
            year_indices.append(i)

    if not year_indices:
        return pl_data

    # --- Extract metrics ---
    tbody = section.find("tbody")
    if not tbody:
        return pl_data

    for tr in tbody.find_all("tr"):
        first_td = tr.find("td", class_="text")
        if not first_td:
            continue

        metric_name = first_td.get_text(strip=True)
        values = [td.get_text(strip=True) for td in tr.find_all("td")[1:]]

        selected_values = [values[i] for i in year_indices if i < len(values)]

        if "Sales" in metric_name:
            pl_data["sales"] = selected_values
        elif "Operating Profit" in metric_name:
            pl_data["operating_profit"] = selected_values
        elif "OPM" in metric_name:
            pl_data["opm_percent"] = selected_values
        elif "Net Profit" in metric_name:
            pl_data["net_profit"] = selected_values
        elif "EPS" in metric_name:
            pl_data["eps"] = selected_values


    return pl_data

def extract_all():
    url = "https://www.screener.in/company/TATAELXSI/"
    soup = fetch_soup(url)

    company_name = get_company_name(soup)
    sector, industry = get_sector_and_industry(soup)
    market_cap, current_price = get_market_data(soup)
    description, sources = get_description_and_sources(soup)

    quarterly = get_quarterly_results(soup)
    pl = get_profit_and_loss(soup)

    return {
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "market_cap": market_cap,
        "current_price": current_price,
        "description": description,
        "description_sources": sources,
        "quarterly": quarterly,
        "pl": pl
    }




"""def main():
    url = "https://www.screener.in/company/TATAELXSI/"
    soup = fetch_soup(url)

    company_name = get_company_name(soup)
    print("Company name:", company_name)

    sector, industry = get_sector_and_industry(soup)
    print("Sector:", sector, "Industry:", industry)

    market_cap, current_price = get_market_data(soup)
    print("Market Cap:", market_cap, "Current Price:", current_price)

    description, sources = get_description_and_sources(soup)
    print("Description:", description)
    print("Sources:", sources)

    quarterly = get_quarterly_results(soup)
    print("\n--- Quarterly results ---")
    print("Quarters:", quarterly["quarters"])
    print("Metrics:", quarterly["metrics"])
    print("PDF sources:", quarterly["sources"])

    pl = get_profit_and_loss(soup)
    print("\n--- Profit & Loss ---")
    print("Years:", pl["years"])
    print("Sales:", pl["sales"])
    print("Operating Profit:", pl["operating_profit"])
    print("OPM %:", pl["opm_percent"])
    print("Net Profit:", pl["net_profit"])
    print("EPS:", pl["eps"])"""

if __name__ == "__main__":
    #main()
    print("This module is for extraction only. Use normalize_numbers.py to run.")

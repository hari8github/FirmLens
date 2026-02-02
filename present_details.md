Project : FirmLens

FirmLens is a company intelligence platform designed to help users understand how a company is evolving by combining financial performance with real‑world events and qualitative context.

Traditional financial platforms present large volumes of raw data—tables, ratios, and historical numbers—but often leave users to interpret why those numbers change. FirmLens focuses on bridging this gap by connecting financial metrics with business events, news, and explainable insights.

The platform begins by presenting a clear overview of a company, including its business description, sector, and basic market information. It then shows both quarterly financial performance and annual profit‑and‑loss trends, aligned over the same time period to ensure clarity and comparability.

Rather than overwhelming users with every available metric, FirmLens intentionally limits its financial scope to core indicators such as revenue, operating profit, operating margins, net profit, and earnings per share. This allows users to focus on meaningful trends instead of noise.

A curated news section highlights only the most relevant developments—such as expansions, strategic shifts, or operational challenges—that may help explain observed financial trends. These news items are tagged and summarized to provide context without information overload.

On top of the data, FirmLens generates concise, plain‑language insights that explain what the numbers indicate about the company’s recent evolution. These insights do not provide investment advice or predictions; instead, they aim to improve understanding and financial literacy.

To further support exploration, FirmLens includes a lightweight conversational assistant that answers questions based solely on the displayed data and insights. This allows users to ask natural questions such as “Why did margins decline?” or “How has the company performed over the last few years?” while maintaining transparency and factual grounding.

Overall, FirmLens is built to help users move from data consumption to understanding, enabling clearer, more informed thinking about companies without encouraging speculative behavior.




Company name: Tata Elxsi Ltd
Sector: Information Technology Industry: Computers - Software & Consulting
Market Cap: ₹ 33,964 Cr. Current Price: ₹ 5,452
Description: Tata Elxsi is amongst the world’s leading providers of design and technology services across industries including Automotive, Media, Communications and Healthcare. Tata Elxsi provides integrated services from research and strategy, to electronics and mechanical design, software development, validation and deployment, and is supported by a network of design studios, global development centers and offices worldwide. [1]
Sources: ['https://tataelxsi.com/investors/Fact-Sheet/FY21-Q3-Fact-Sheet.pdf#page=12']

--- Quarterly results ---
Quarters: ['Dec 2022', 'Mar 2023', 'Jun 2023', 'Sep 2023', 'Dec 2023', 'Mar 2024', 'Jun 2024', 'Sep 2024', 'Dec 2024', 'Mar 2025', 'Jun 2025', 'Sep 2025', 'Dec 2025']
Metrics: {'sales': ['818', '838', '850', '882', '914', '906', '926', '955', '939', '908', '892', '918', '953'], 'operating_profit': ['247', '250', '251', '264', '270', '261', '252', '266', '247', '208', '187', '193', '222'], 'opm_percent': ['30%', '30%', '30%', '30%', '30%', '29%', '27%', '28%', '26%', '23%', '21%', '21%', '23%'], 'net_profit': ['195', '202', '189', '200', '206', '197', '184', '229', '199', '172', '144', '155', '109'], 'eps': ['31.26', '32.36', '30.32', '32.12', '33.15', '31.62', '29.56', '36.84', '31.95', '27.68', '23.18', '24.85', '17.48']}
PDF sources: ['https://www.screener.in/company/source/quarter/3366/12/2022/', 'https://www.screener.in/company/source/quarter/3366/3/2023/', 'https://www.screener.in/company/source/quarter/3366/6/2023/', 'https://www.screener.in/company/source/quarter/3366/9/2023/', 'https://www.screener.in/company/source/quarter/3366/12/2023/', 'https://www.screener.in/company/source/quarter/3366/3/2024/', 'https://www.screener.in/company/source/quarter/3366/6/2024/', 'https://www.screener.in/company/source/quarter/3366/9/2024/', 'https://www.screener.in/company/source/quarter/3366/12/2024/', 'https://www.screener.in/company/source/quarter/3366/3/2025/', 'https://www.screener.in/company/source/quarter/3366/6/2025/', 'https://www.screener.in/company/source/quarter/3366/9/2025/', 'https://www.screener.in/company/source/quarter/3366/12/2025/']

--- Profit & Loss ---
Years: ['Mar 2022', 'Mar 2023', 'Mar 2024', 'Mar 2025']
Sales: ['2,471', '3,145', '3,552', '3,729']
Operating Profit: ['767', '962', '1,047', '974']
OPM %: ['31%', '31%', '29%', '26%']
Net Profit: ['550', '755', '792', '785']
EPS: ['88.26', '121.26', '127.21', '126.03']



✅ 1. Company Identity & Basics (Static / Low‑frequency)
From Screener – Company Header & Info section

Company Profile

Company Name

Sector

Industry

Business Description

About / Company overview (text)

Source links for description (PDF / external links)

👉 Usage:

Company landing page

Context for chatbot

Background for insights

✅ 2. Market Snapshot (Near‑real‑time, lightweight)
From Top Ratios section

Market Capitalization

Current Stock Price

52W High / Low

Stock P/E

Book Value

Dividend Yield

ROCE

ROE

Face Value

👉 Usage:

Top KPI cards

Quick valuation context (not deep analysis)

✅ 3. Quarterly Financials (High‑importance, core engine)
From Quarterly Results table

Time Axis

Quarter labels (e.g., Dec 2022 → Dec 2025)

Metrics (per quarter)

Sales

Expenses (optional, but available)

Operating Profit

Operating Margin (OPM %)

Net Profit

EPS

Supporting Data

Quarterly PDF source links

👉 Usage:

QoQ calculations

Trend charts

News alignment

Insight generation

✅ 4. Annual Profit & Loss (Medium‑term performance)
From Profit & Loss statement (filtered: 2022–2025)

Time Axis

Financial Years (Mar 2022 → Mar 2025)

Metrics

Sales

Expenses

Operating Profit

OPM %

Other Income

Interest

Depreciation

Profit Before Tax

Tax %

Net Profit

EPS

Dividend Payout %

👉 Usage:

YoY calculations

Structural vs short‑term analysis

Annual trend validation

✅ 5. Derived Financial Metrics (Calculated, not scraped)
Based on quarterly + annual data:

Growth & Change

QoQ % change (Sales, Profit, EPS)

YoY % change (Sales, Profit, EPS)

OPM change (percentage points)

Signals (Boolean / Labels)

Revenue growth / decline / flat

Margin compression / expansion

Profit volatility

Revenue stable but profit down

👉 Usage:

Core “financial signals” layer

Triggers for insights

News relevance filtering

✅ 6. News Data (Non‑financial, contextual)
From NewsAPI

For each article:

Title

Short description / snippet

Source name

Published date

URL

👉 Notes:

Partial summaries are expected

Source linking is intentional

No full‑article scraping (by design)

👉 Usage:

Contextual explanation

Event alignment with quarters

Insight grounding

✅ 7. Relationship Data (Conceptual – Neo4j‑ready)
Not scraped directly, but constructed:

Company → Financial Metric

Company → Quarter / Year

Company → News Article

News Article → Event Type (cost, demand, regulation, growth)

Event Type → Financial Impact (margin, revenue, profit)

👉 Usage:

Explainability

Graph traversal

Chatbot reasoning

🧠 What We Do NOT Scrape (Intentionally)
❌ Stock price history (for now)
❌ Intraday data
❌ Social media sentiment
❌ Forecasts / analyst targets
❌ Buy/sell recommendations

This keeps FIRMLENS:

Explainable

Defensible

MVP‑clean
# FirmLens  
**Explainable Financial Insights using News + Numbers**

FirmLens is a **graph‑driven company intelligence platform** that combines **structured financial data** with **unstructured news** to generate **clear, explainable insights** about a company’s performance.

Instead of showing raw numbers or isolated headlines, FirmLens connects *what happened* (news/events) with *what changed* (financials) — and explains the relationship transparently.

This project was built as a hackathon MVP and successfully validated in a live demo environment.

---

## 🚀 Problem Statement

Most investors and analysts face three major issues:

- Financial statements are dense and hard to interpret in isolation  
- News articles lack direct linkage to financial impact  
- Existing tools rarely explain *why* metrics changed  

As a result, users are forced to manually correlate:
- Earnings reports  
- Quarterly/annual trends  
- News events and market commentary  

This is slow, error‑prone, and not scalable.

---

## 💡 Solution: FirmLens

FirmLens solves this by:

- Structuring financial data (quarterly + annual)
- Normalizing company‑specific news
- Storing both in a **graph database**
- Exposing insights via a **dashboard + chatbot**
- Ensuring **zero hallucinations** by grounding all answers in data

The result is an **explainable, trust‑first financial intelligence system**.

---

## 🧠 Core Idea

> **Numbers don’t tell stories. Relationships do.**

FirmLens uses a **graph model** to represent:
- Companies
- Financial periods
- Financial metrics
- News events

This allows fast traversal such as:
- *Which news coincided with a profit drop?*
- *How did margins change after a regulatory event?*
- *What financial trend aligns with recent market sentiment?*

---

## 🏗️ Architecture Overview

### 1. Data Extraction
- Financial data scraped from public sources (quarterly + P&L)
- News fetched via APIs (Economic Times, Livemint, etc.)

### 2. Data Normalization
- Raw scraped data converted into clean, consistent schemas
- Numerical data normalized by period and metric
- News normalized with title, summary, source, date, and event type

### 3. Graph Storage (Neo4j)
- **Company** nodes
- **FinancialPeriod** nodes (Quarter / Year)
- **FinancialMetrics** nodes
- **News** nodes
- Relationships such as:
  - `HAS_PERIOD`
  - `HAS_METRICS`
  - `MENTIONED_IN`

This enables precise, explainable querying.

### 4. Backend (Flask)
- Acts as a thin API layer
- Queries Neo4j using Cypher
- Returns clean JSON responses
- No business logic in the frontend

### 5. Frontend (HTML / JS / CSS)
- Minimal, fast, demo‑friendly UI
- Visualizes charts instead of raw tables
- Fetches all data via Flask APIs

### 6. Chatbot (Graph‑Grounded LLM)
- Uses Neo4j as the **only context source**
- Strict system prompt:
  - No guessing
  - No external knowledge
  - Cite sources when referencing news
- Produces concise, explainable answers

---

## 🔐 Hallucination Control

FirmLens is intentionally designed to **prevent hallucinations**:

- LLM receives only Neo4j‑derived context
- If data is missing, the bot responds:
  > *“I don’t have that in the database yet.”*
- No embeddings or speculative reasoning in MVP

Trust > creativity.

---

## 📊 What Data FirmLens Uses

### Financial (Numerical)
- Sales / Revenue
- Operating Profit
- Net Profit
- Operating Margin (OPM)
- EPS
- Quarterly trends
- Annual performance

### Non‑Financial (News)
- Earnings commentary
- Regulatory or policy events
- Sector outlook
- Market sentiment
- Broker opinions

Each news item is stored with:
- Source
- URL
- Publish date
- Summary
- Event type

---

## 🧪 Current Scope (MVP)

Included:
- Single‑company deep dive (e.g., Tata Elxsi)
- Quarterly & annual financials
- Company‑specific news
- Graph visualization
- Explainable chatbot
- Web dashboard

Excluded (intentionally):
- Stock price prediction
- Buy/sell recommendations
- Peer comparison
- Authentication
- Large‑scale ingestion

---

## 🎯 Why Graphs (and not traditional RAG)

Traditional RAG:
- Flattens context
- Struggles with relationships
- Hard to explain *why* an answer exists

Graph‑based approach:
- Explicit relationships
- Deterministic traversal
- High accuracy
- Transparent reasoning
- Scales naturally with more entities

---

## 🏆 Hackathon Outcome

- Project completed end‑to‑end
- Fully functional demo (dashboard + chatbot)
- Demonstrated real‑world explainability
- **Won the hackathon**

This validated:
- Technical feasibility
- Product relevance
- User clarity

---

## 🔮 Future Roadmap

Planned improvements:
- Multi‑company support
- Peer and sector comparison
- Deeper fundamental ratios
- Event impact scoring
- Time‑aware financial analysis
- Advanced UI/UX
- Production‑grade ingestion pipelines

FirmLens is positioned to evolve from a demo into a **serious financial intelligence product**.

---

## 🧠 Philosophy

- Explainability over prediction  
- Trust over speculation  
- Relationships over raw data  

---

## 📌 Summary

FirmLens proves that combining **clean data pipelines**, **knowledge graphs**, and **strictly grounded LLMs** can dramatically improve how financial information is understood.

It doesn’t tell users what to think —  
it helps them **understand why**.

---



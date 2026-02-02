from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from neo4j import Driver

# LangChain (Groq)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()



SYSTEM_PROMPT = """You are FirmLens Assistant.

Rules (must follow):
- Answer ONLY using the provided CONTEXT from the Neo4j database.
- If the context does not contain the answer, say exactly: "I don't have that in the database yet."
- Do NOT guess, do NOT use outside knowledge.
- If you reference a news item, include its source name and URL if present in context.
- If you cite numbers (sales, profit, margins), they must appear in the context.
- Keep answers concise (4-10 sentences). Use bullet points when helpful.
"""


PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "CONTEXT (Neo4j):\n{context}\n\nUSER QUESTION:\n{question}\n\nAnswer:",
        ),
    ]
)


def _env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return v


def _safe(v: Any) -> str:
    if v is None:
        return "—"
    return str(v)


def _fmt_context(bundle: dict[str, Any]) -> str:
    c = bundle.get("company", {}) or {}
    q = bundle.get("quarterly", []) or []
    a = bundle.get("annual", []) or []
    n = bundle.get("news", []) or []

    lines: list[str] = []
    lines.append("== Company ==")
    lines.append(f"company_id: {_safe(c.get('company_id'))}")
    lines.append(f"name: {_safe(c.get('name'))}")
    lines.append(f"sector: {_safe(c.get('sector'))}")
    lines.append(f"industry: {_safe(c.get('industry'))}")
    lines.append(f"market_cap_cr: {_safe(c.get('market_cap_cr'))}")
    lines.append(f"current_price: {_safe(c.get('current_price'))}")
    lines.append(f"description: {_safe(c.get('description'))}")
    lines.append("")

    lines.append("== Quarterly financials (oldest → latest) ==")
    for row in q:
        lines.append(
            f"- {row.get('label')} | period_end={row.get('period_end')} | "
            f"sales={row.get('sales')} | op_profit={row.get('operating_profit')} | "
            f"opm%={row.get('opm_percent')} | net_profit={row.get('net_profit')} | eps={row.get('eps')} | "
            f"source_url={row.get('source_url')}"
        )
    if not q:
        lines.append("- (no quarterly data)")
    lines.append("")

    lines.append("== Annual financials ==")
    for row in a:
        lines.append(
            f"- {row.get('label')} | period_end={row.get('period_end')} | "
            f"sales={row.get('sales')} | op_profit={row.get('operating_profit')} | "
            f"opm%={row.get('opm_percent')} | net_profit={row.get('net_profit')} | eps={row.get('eps')}"
        )
    if not a:
        lines.append("- (no annual data)")
    lines.append("")

    lines.append("== News (latest first) ==")
    for item in n:
        lines.append(
            f"- {item.get('published_at')} | {item.get('event_type')} | {item.get('title')} "
            f"(source={item.get('source')}) url={item.get('url')}"
        )
        if item.get("summary"):
            lines.append(f"  summary: {item.get('summary')}")
    if not n:
        lines.append("- (no news)")

    return "\n".join(lines)


def fetch_company_context(
    neo4j_driver: Driver,
    company_id: str,
    *,
    limit_quarters: int = 10,
    limit_annual: int = 4,
    limit_news: int = 10,
) -> dict[str, Any]:
    with neo4j_driver.session() as session:
        company_rec = session.run(
            """
            MATCH (c:Company {company_id: $company_id})
            RETURN c AS company
            """,
            {"company_id": company_id},
        ).single()
        if not company_rec:
            raise ValueError(f"Company not found: {company_id}")
        company = dict(company_rec["company"]._properties)  # noqa: SLF001

        # Quarterly (descending then reversed for human readability)
        q_rows = list(
            session.run(
                """
                MATCH (:Company {company_id: $company_id})-[:HAS_PERIOD]->(p:FinancialPeriod {period_type: "quarter"})
                      -[:HAS_METRICS]->(m:FinancialMetrics)
                RETURN p.period_end AS period_end, p.label AS label,
                       m.sales AS sales, m.operating_profit AS operating_profit,
                       m.net_profit AS net_profit, m.opm_percent AS opm_percent,
                       m.eps AS eps, m.source_url AS source_url
                ORDER BY p.period_end DESC
                LIMIT $limit
                """,
                {"company_id": company_id, "limit": int(limit_quarters)},
            )
        )
        quarterly = [dict(r) for r in reversed(q_rows)]

        annual = [
            dict(r)
            for r in session.run(
                """
                MATCH (:Company {company_id: $company_id})-[:HAS_PERIOD]->(p:FinancialPeriod {period_type: "year"})
                      -[:HAS_METRICS]->(m:FinancialMetrics)
                RETURN p.period_end AS period_end, p.label AS label,
                       m.sales AS sales, m.operating_profit AS operating_profit,
                       m.net_profit AS net_profit, m.opm_percent AS opm_percent,
                       m.eps AS eps
                ORDER BY p.period_end ASC
                LIMIT $limit
                """,
                {"company_id": company_id, "limit": int(limit_annual)},
            )
        ]

        news = [
            dict(r)
            for r in session.run(
                """
                MATCH (:Company {company_id: $company_id})-[:MENTIONED_IN]->(nw:News)
                RETURN nw.news_id AS news_id, nw.title AS title, nw.summary AS summary,
                       nw.source AS source, nw.published_at AS published_at, nw.url AS url,
                       nw.event_type AS event_type, nw.time_context AS time_context
                ORDER BY nw.published_at DESC
                LIMIT $limit
                """,
                {"company_id": company_id, "limit": int(limit_news)},
            )
        ]

    return {"company": company, "quarterly": quarterly, "annual": annual, "news": news}


def answer_from_neo4j(
    *,
    neo4j_driver: Driver,
    company_id: str,
    question: str,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Main entrypoint used by the Flask API.
    Returns a JSON-serializable dict.
    """
    q = (question or "").strip()
    if not q:
        return {"reply": "Ask a question about the company’s financials or news.", "meta": {"ok": True}}

    groq_key = _env("GROQ_API_KEY")
    if not groq_key:
        return {
            "reply": "Chatbot is not configured yet. Set the GROQ_API_KEY environment variable and restart the server.",
            "meta": {"ok": False, "error": "missing_groq_api_key"},
        }

    # User requested llama-8b-instruct; allow override via env later.
    model_name = model or _env("GROQ_MODEL", "llama-8b-instruct") or "llama-8b-instruct"

    bundle = fetch_company_context(neo4j_driver, company_id)
    context = _fmt_context(bundle)

    llm = ChatGroq(
        api_key=groq_key,
        model=model_name,
        temperature=float(_env("GROQ_TEMPERATURE", "0") or "0"),
        max_tokens=int(_env("GROQ_MAX_TOKENS", "512") or "512"),
    )

    chain = PROMPT | llm | StrOutputParser()
    reply = chain.invoke({"context": context, "question": q})

    return {
        "reply": reply,
        "meta": {
            "ok": True,
            "company_id": company_id,
            "model": model_name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        },
    }


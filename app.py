import os
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from graph.neo4j_connection import Neo4jConnection
from chatbot.chatbot import answer_from_neo4j

# --------------------------------------------------
# Load environment variables (.env)
# --------------------------------------------------
load_dotenv()

def _env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v is not None and v.strip() != "" else default

# --------------------------------------------------
# Neo4j config
# --------------------------------------------------
NEO4J_URI = _env("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = _env("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = _env("NEO4J_PASSWORD", "firmlens")

# --------------------------------------------------
# Flask app
# --------------------------------------------------
app = Flask(__name__, template_folder="templates")

def get_driver() -> Neo4jConnection:
    """Singleton Neo4j connection for dev/MVP."""
    if not hasattr(app, "_neo4j"):
        app._neo4j = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)  # type: ignore[attr-defined]
    return app._neo4j  # type: ignore[attr-defined]

def _record_to_dict(obj: Any) -> Any:
    if hasattr(obj, "_properties"):
        return dict(obj._properties)  # noqa
    return obj

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def home():
    # Main FIRMLENS UI
    return render_template("intro.html")

@app.get("/api/health")
def health():
    try:
        driver = get_driver()
        with driver.driver.session() as session:
            session.run("RETURN 1").consume()
        return jsonify({"ok": True, "neo4j": True})
    except Exception as e:
        return jsonify({"ok": False, "neo4j": False, "error": str(e)}), 500

@app.get("/api/companies")
def list_companies():
    driver = get_driver()
    with driver.driver.session() as session:
        res = session.run(
            """
            MATCH (c:Company)
            RETURN c.company_id AS company_id,
                   c.name AS name,
                   c.sector AS sector,
                   c.industry AS industry
            ORDER BY c.name
            LIMIT 50
            """
        )
        companies = [dict(r) for r in res]
    return jsonify({"companies": companies})

@app.get("/api/company/<company_id>/overview")
def company_overview(company_id: str):
    driver = get_driver()
    limit_news = int(request.args.get("newsLimit", "10"))

    with driver.driver.session() as session:
        company_rec = session.run(
            """
            MATCH (c:Company {company_id: $company_id})
            RETURN c AS company
            """,
            {"company_id": company_id},
        ).single()

        if not company_rec:
            return jsonify({"error": f"Company not found: {company_id}"}), 404

        company = _record_to_dict(company_rec["company"])

        quarterly = [
            dict(r)
            for r in session.run(
                """
                MATCH (c:Company {company_id: $company_id})
                      -[:HAS_PERIOD]->(p:FinancialPeriod {period_type: "quarter"})
                      -[:HAS_METRICS]->(m:FinancialMetrics)
                RETURN p.period_end AS period_end,
                       p.label AS label,
                       m.sales AS sales,
                       m.operating_profit AS operating_profit,
                       m.net_profit AS net_profit,
                       m.opm_percent AS opm_percent,
                       m.eps AS eps,
                       m.source_url AS source_url
                ORDER BY p.period_end ASC
                """,
                {"company_id": company_id},
            )
        ]

        annual = [
            dict(r)
            for r in session.run(
                """
                MATCH (c:Company {company_id: $company_id})
                      -[:HAS_PERIOD]->(p:FinancialPeriod {period_type: "year"})
                      -[:HAS_METRICS]->(m:FinancialMetrics)
                RETURN p.period_end AS period_end,
                       p.label AS label,
                       m.sales AS sales,
                       m.operating_profit AS operating_profit,
                       m.net_profit AS net_profit,
                       m.opm_percent AS opm_percent,
                       m.eps AS eps,
                       m.source_url AS source_url
                ORDER BY p.period_end ASC
                """,
                {"company_id": company_id},
            )
        ]

        news = [
            dict(r)
            for r in session.run(
                """
                MATCH (c:Company {company_id: $company_id})-[:MENTIONED_IN]->(n:News)
                RETURN n.news_id AS news_id,
                       n.title AS title,
                       n.summary AS summary,
                       n.source AS source,
                       n.published_at AS published_at,
                       n.url AS url,
                       n.event_type AS event_type,
                       n.time_context AS time_context
                ORDER BY n.published_at DESC
                LIMIT $limit
                """,
                {"company_id": company_id, "limit": limit_news},
            )
        ]

    return jsonify({
        "company": company,
        "quarterly": quarterly,
        "annual": annual,
        "news": news,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    })

@app.post("/api/chat")
def chat():
    """
    Chat endpoint for FIRMLENS.
    Accepts BOTH:
      { "question": "..." }  or
      { "message": "..." }
    """
    data = request.get_json(force=True, silent=True) or {}

    company_id = (data.get("company_id") or "TATA_ELXSI").strip()
    question = (data.get("question") or data.get("message") or "").strip()

    if not question:
        return jsonify({"reply": "Ask a question about the company.", "meta": {"ok": True}})

    driver = get_driver()

    try:
        result = answer_from_neo4j(
            neo4j_driver=driver.driver,
            company_id=company_id,
            question=question,
        )
        return jsonify(result)
    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return jsonify({
            "reply": "Chat failed.",
            "meta": {"ok": False, "error": str(e)}
        }), 500

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(_env("PORT", "5000") or 5000),
        debug=True,
    )

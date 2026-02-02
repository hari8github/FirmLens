import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from graph.neo4j_connection import Neo4jConnection
from normalizations.normalize_numbers import normalize
from normalizations.normalize_news import normalize_news

# Try bolt:// for direct connection (recommended for local Neo4j)
# Use neo4j:// for routing/clustering setups
URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "firmlens"


def ingest_company(tx, company):
    tx.run("""
        MERGE (c:Company {company_id: $company_id})
        SET c.name = $name,
            c.sector = $sector,
            c.industry = $industry,
            c.market_cap_cr = $market_cap_cr,
            c.current_price = $current_price,
            c.description = $description,
            c.description_sources = $description_sources
    """, company)


def ingest_financials(tx, company_id, records):
    for r in records:
        # Ensure source_url is present (default to None for annual financials)
        params = {
            **r,
            "company_id": company_id,
            "source_url": r.get("source_url")  # Will be None if not present
        }
        tx.run("""
            MERGE (p:FinancialPeriod {
                company_id: $company_id,
                period_end: $period_end,
                period_type: $period_type
            })
            SET p.label = $label

            CREATE (m:FinancialMetrics {
                sales: $sales,
                operating_profit: $operating_profit,
                net_profit: $net_profit,
                opm_percent: $opm_percent,
                eps: $eps,
                source_url: $source_url
            })

            MERGE (c:Company {company_id: $company_id})
            MERGE (c)-[:HAS_PERIOD]->(p)
            MERGE (p)-[:HAS_METRICS]->(m)
        """, params)


def ingest_news(tx, company_id, news):
    for n in news:
        tx.run("""
            MERGE (nw:News {news_id: $news_id})
            SET nw.title = $title,
                nw.summary = $summary,
                nw.source = $source,
                nw.published_at = $published_at,
                nw.url = $url,
                nw.event_type = $event_type,
                nw.time_context = $time_context

            MERGE (c:Company {company_id: $company_id})
            MERGE (c)-[:MENTIONED_IN]->(nw)
        """, {**n, "company_id": company_id})


def verify_connection(driver):
    """Verify Neo4j connection is working."""
    try:
        with driver.driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.consume()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print(f"\nTroubleshooting steps:")
        print(f"  1. Check if Neo4j is running:")
        print(f"     - Windows: Check Services or Task Manager")
        print(f"     - Or open Neo4j Desktop/Browser")
        print(f"  2. Verify connection URI: {URI}")
        print(f"     - Try 'bolt://127.0.0.1:7687' for direct connection")
        print(f"     - Try 'neo4j://127.0.0.1:7687' for routing")
        print(f"  3. Check credentials (user: {USER})")
        print(f"  4. Verify Neo4j is listening on port 7687")
        print(f"\nTo start Neo4j:")
        print(f"  - Neo4j Desktop: Click 'Start' on your database")
        print(f"  - Command line: neo4j start")
        print(f"  - Docker: docker start <neo4j-container>")
        return False


def try_connect(uri, user, password):
    """Try to create a connection and return driver if successful."""
    try:
        driver = Neo4jConnection(uri, user, password)
        # Test the connection immediately
        with driver.driver.session() as session:
            session.run("RETURN 1").consume()
        return driver
    except Exception:
        return None


def main():
    print("🔄 Connecting to Neo4j...")
    print(f"   URI: {URI}")
    print(f"   User: {USER}")
    
    driver = None
    
    # Try the configured URI first
    driver = try_connect(URI, USER, PASSWORD)
    
    # If that fails and URI uses neo4j://, try bolt:// instead
    if not driver and URI.startswith("neo4j://"):
        alt_uri = URI.replace("neo4j://", "bolt://")
        print(f"\n⚠️  Trying alternative URI: {alt_uri}")
        driver = try_connect(alt_uri, USER, PASSWORD)
        if driver:
            print("✅ Connected using bolt:// protocol")
    
    # If that fails and URI uses bolt://, try neo4j:// instead
    if not driver and URI.startswith("bolt://"):
        alt_uri = URI.replace("bolt://", "neo4j://")
        print(f"\n⚠️  Trying alternative URI: {alt_uri}")
        driver = try_connect(alt_uri, USER, PASSWORD)
        if driver:
            print("✅ Connected using neo4j:// protocol")
    
    if not driver:
        print(f"\n❌ Could not connect to Neo4j")
        print(f"\nTroubleshooting steps:")
        print(f"  1. Check if Neo4j is running:")
        print(f"     - Windows: Check Services or Task Manager")
        print(f"     - Or open Neo4j Desktop/Browser")
        print(f"  2. Verify connection URI: {URI}")
        print(f"     - Try 'bolt://127.0.0.1:7687' for direct connection")
        print(f"     - Try 'neo4j://127.0.0.1:7687' for routing")
        print(f"  3. Check credentials (user: {USER})")
        print(f"  4. Verify Neo4j is listening on port 7687")
        print(f"\nTo start Neo4j:")
        print(f"  - Neo4j Desktop: Click 'Start' on your database")
        print(f"  - Command line: neo4j start")
        print(f"  - Docker: docker start <neo4j-container>")
        return
    
    try:
        # Connection already verified in try_connect, but verify again for safety
        if not verify_connection(driver):
            driver.close()
            return
        
        print("✅ Connected to Neo4j successfully")
        print("\n🔄 Fetching and normalizing data...")
        
        numeric_data = normalize()
        news_data = normalize_news()
        
        print(f"✅ Normalized {len(numeric_data['quarterly_financials'])} quarterly periods")
        print(f"✅ Normalized {len(numeric_data['annual_financials'])} annual periods")
        print(f"✅ Normalized {len(news_data)} news articles")
        
        company = numeric_data["company"]
        company_id = company["company_id"]
        
        print(f"\n🔄 Ingesting data for company: {company['name']} ({company_id})...")
        
        with driver.driver.session() as session:
            print("  → Ingesting company data...")
            session.execute_write(ingest_company, company)
            
            print("  → Ingesting quarterly financials...")
            session.execute_write(
                ingest_financials, company_id,
                numeric_data["quarterly_financials"]
            )
            
            print("  → Ingesting annual financials...")
            session.execute_write(
                ingest_financials, company_id,
                numeric_data["annual_financials"]
            )
            
            print("  → Ingesting news articles...")
            session.execute_write(
                ingest_news, company_id, news_data
            )
        
        driver.close()
        print("\n✅ Data successfully ingested into Neo4j")
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

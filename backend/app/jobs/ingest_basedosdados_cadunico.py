"""CadÚnico data ingestion from Base dos Dados (BigQuery).

This script extracts CadÚnico data from Base dos Dados, which provides
free access to the CadÚnico microdados via Google BigQuery.

Source: https://basedosdados.org/dataset/cadastro-unico
Dataset: basedosdados.br_mds_cadastro_unico

Prerequisites:
    1. Install basedosdados: pip install basedosdados
    2. Create a Google Cloud project
    3. Authenticate: basedosdados auth (first time only)

Usage:
    # Test connection and list available tables
    python -m app.jobs.ingest_basedosdados_cadunico --test

    # Run for all municipalities
    python -m app.jobs.ingest_basedosdados_cadunico

    # Run for a specific state
    python -m app.jobs.ingest_basedosdados_cadunico --state SP

    # Specify reference year-month
    python -m app.jobs.ingest_basedosdados_cadunico --periodo 202312
"""

import argparse
import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BigQuery dataset info
DATASET_ID = "br_mds_cadastro_unico"
TABLE_FAMILIA = "microdados_familia"
TABLE_PESSOA = "microdados_pessoa"


def get_fresh_db_session() -> Session:
    """Get a fresh database session."""
    return SessionLocal()


def check_basedosdados_installed() -> bool:
    """Check if basedosdados package is installed."""
    try:
        import basedosdados as bd
        return True
    except ImportError:
        return False


def list_available_tables() -> list:
    """List available tables in the CadÚnico dataset."""
    try:
        import basedosdados as bd

        # List tables in the dataset
        tables = bd.list_tables(dataset_id=DATASET_ID)
        return tables
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return []


def get_cadunico_aggregated_data(
    state_code: Optional[str] = None,
    periodo: Optional[str] = None
) -> list:
    """
    Query CadÚnico data from BigQuery, aggregated by municipality.

    Args:
        state_code: Two-letter state code (e.g., 'SP')
        periodo: Reference period in YYYYMM format

    Returns:
        List of dicts with aggregated data per municipality
    """
    try:
        import basedosdados as bd

        # Build the query for aggregated data by municipality
        where_clauses = []

        if state_code:
            where_clauses.append(f"sigla_uf = '{state_code}'")

        if periodo:
            year = periodo[:4]
            month = periodo[4:]
            where_clauses.append(f"ano = {year}")
            where_clauses.append(f"mes = {month}")
        else:
            # Get the most recent period
            where_clauses.append("ano = (SELECT MAX(ano) FROM `basedosdados.br_mds_cadastro_unico.microdados_familia`)")

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
        SELECT
            id_municipio,
            sigla_uf,
            ano,
            mes,
            COUNT(DISTINCT id_familia) as total_families,
            COUNT(*) as total_persons,
            -- Income brackets (simplified - actual logic depends on data structure)
            SUM(CASE WHEN renda_mensal_familia / qtde_pessoas_domic_fam < 105 THEN 1 ELSE 0 END) as families_extreme_poverty,
            SUM(CASE WHEN renda_mensal_familia / qtde_pessoas_domic_fam >= 105 AND renda_mensal_familia / qtde_pessoas_domic_fam < 218 THEN 1 ELSE 0 END) as families_poverty,
            -- Age demographics would require joining with pessoa table
        FROM `basedosdados.{DATASET_ID}.{TABLE_FAMILIA}`
        WHERE {where_clause}
        GROUP BY id_municipio, sigla_uf, ano, mes
        ORDER BY id_municipio
        """

        logger.info("Executing BigQuery query...")
        logger.debug(f"Query: {query}")

        # Execute query
        df = bd.read_sql(query, billing_project_id=None)  # Uses default project

        if df is None or df.empty:
            logger.warning("No data returned from BigQuery")
            return []

        # Convert to list of dicts
        results = df.to_dict(orient='records')
        logger.info(f"Retrieved {len(results)} municipality records")

        return results

    except Exception as e:
        logger.error(f"Error querying BigQuery: {e}")
        raise


def get_simple_cadunico_summary(
    state_code: Optional[str] = None,
    year: int = 2023
) -> list:
    """
    Get a simple summary of CadÚnico data.
    This is a simpler query that should work with the available data.
    """
    try:
        import basedosdados as bd

        where_clause = f"ano = {year}"
        if state_code:
            where_clause += f" AND sigla_uf = '{state_code}'"

        # Simple count query
        query = f"""
        SELECT
            id_municipio,
            sigla_uf,
            ano,
            COUNT(DISTINCT id_familia) as total_families
        FROM `basedosdados.{DATASET_ID}.{TABLE_FAMILIA}`
        WHERE {where_clause}
        GROUP BY id_municipio, sigla_uf, ano
        LIMIT 100
        """

        logger.info(f"Executing simple query for {state_code or 'all states'}, year {year}")

        df = bd.read_sql(query)

        if df is None or df.empty:
            return []

        return df.to_dict(orient='records')

    except Exception as e:
        logger.error(f"Error in simple query: {e}")
        raise


def save_to_database(data: list, db: Session) -> int:
    """
    Save CadÚnico data to the database.

    Args:
        data: List of dicts with municipality data
        db: Database session

    Returns:
        Number of records saved
    """
    saved = 0

    for record in data:
        try:
            ibge_code = str(record['id_municipio'])

            # Find municipality
            municipality = db.query(Municipality).filter(
                Municipality.ibge_code == ibge_code
            ).first()

            if not municipality:
                logger.warning(f"Municipality not found: {ibge_code}")
                continue

            # Build reference date
            year = int(record.get('ano', 2023))
            month = int(record.get('mes', 12))
            ref_date = date(year, month, 1)

            # Check if record exists
            existing = db.query(CadUnicoData).filter(
                CadUnicoData.municipality_id == municipality.id,
                CadUnicoData.reference_date == ref_date
            ).first()

            if existing:
                # Update existing record
                existing.total_families = record.get('total_families')
                existing.total_persons = record.get('total_persons')
                existing.families_extreme_poverty = record.get('families_extreme_poverty')
                existing.families_poverty = record.get('families_poverty')
            else:
                # Create new record
                cadunico = CadUnicoData(
                    municipality_id=municipality.id,
                    reference_date=ref_date,
                    total_families=record.get('total_families'),
                    total_persons=record.get('total_persons'),
                    families_extreme_poverty=record.get('families_extreme_poverty'),
                    families_poverty=record.get('families_poverty'),
                )
                db.add(cadunico)

            saved += 1

        except Exception as e:
            logger.error(f"Error saving record: {e}")
            continue

    db.commit()
    return saved


def test_connection():
    """Test BigQuery connection and list available data."""
    print("\n=== Testing Base dos Dados Connection ===\n")

    if not check_basedosdados_installed():
        print("ERROR: basedosdados package not installed!")
        print("Install with: pip install basedosdados")
        print("\nAfter installing, run: basedosdados auth")
        return False

    print("basedosdados package is installed")

    # List tables
    print("\nListing available tables in br_mds_cadastro_unico:")
    tables = list_available_tables()
    for table in tables:
        print(f"  - {table}")

    if not tables:
        print("  (no tables found or error occurred)")
        print("\nMake sure you have authenticated with:")
        print("  basedosdados auth")
        return False

    # Try a simple query
    print("\nTrying a simple query for SP (limit 5)...")
    try:
        results = get_simple_cadunico_summary(state_code='SP', year=2023)
        print(f"Retrieved {len(results)} records")

        if results:
            print("\nSample data:")
            for r in results[:5]:
                print(f"  - Município {r['id_municipio']}: {r['total_families']} famílias")

        return True

    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you authenticated: basedosdados auth")
        print("2. Check if you have a Google Cloud project set up")
        print("3. The free tier allows 1TB of queries per month")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest CadÚnico data from Base dos Dados (BigQuery)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test connection and list available tables"
    )
    parser.add_argument(
        "--state",
        type=str,
        help="Filter by state (e.g., SP, RJ, MG)"
    )
    parser.add_argument(
        "--periodo",
        type=str,
        help="Reference period in YYYYMM format (e.g., 202312)"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2023,
        help="Reference year (default: 2023)"
    )

    args = parser.parse_args()

    if args.test:
        test_connection()
        return

    # Check prerequisites
    if not check_basedosdados_installed():
        print("ERROR: basedosdados package not installed!")
        print("Install with: pip install basedosdados")
        return

    # Get data from BigQuery
    logger.info("Fetching CadÚnico data from Base dos Dados...")
    logger.info(f"State filter: {args.state or 'All'}")
    logger.info(f"Year: {args.year}")

    try:
        data = get_simple_cadunico_summary(
            state_code=args.state,
            year=args.year
        )

        if not data:
            logger.warning("No data retrieved from BigQuery")
            return

        logger.info(f"Retrieved {len(data)} municipality records")

        # Save to database
        db = get_fresh_db_session()
        try:
            saved = save_to_database(data, db)
            logger.info(f"Saved {saved} records to database")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise


if __name__ == "__main__":
    main()

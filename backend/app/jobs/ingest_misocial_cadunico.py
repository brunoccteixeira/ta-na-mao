"""CadÚnico data ingestion from MiSocial API.

This script extracts CadÚnico data from the SAGI MiSocial SOLR API,
which provides comprehensive data about families and individuals
registered in the Cadastro Único.

Source: https://aplicacoes.mds.gov.br/sagi/servicos/misocial/
Documentation: https://dados.gov.br/dados/conjuntos-dados/familias-inscritas-no-cadastro-unico

Available fields:
    - cadun_qtd_familias_cadastradas_i: Total families registered
    - cadun_qtde_fam_sit_extrema_pobreza_s: Families in extreme poverty
    - cadun_qtde_fam_sit_pobreza_s: Families in poverty
    - cadun_qtd_familias_cadastradas_baixa_renda_i: Low income families
    - cadun_qtd_pessoas_cadastradas_i: Total persons registered
    - Age distribution by gender (0-4, 5-6, 7-15, 16-17, 18+, 65+)

Usage:
    # Test with latest period
    python -m app.jobs.ingest_misocial_cadunico --test

    # Ingest specific period (YYYYMM)
    python -m app.jobs.ingest_misocial_cadunico --periodo 202412

    # Ingest all available data for a year
    python -m app.jobs.ingest_misocial_cadunico --year 2024

    # Ingest historical data (2019-2024)
    python -m app.jobs.ingest_misocial_cadunico --historical
"""

import argparse
import logging
from datetime import date
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MiSocial API configuration
MISOCIAL_BASE_URL = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"

# Fields to extract from the API
CADUNICO_FIELDS = [
    "codigo_ibge",
    "anomes_s",
    # Families
    "cadun_qtd_familias_cadastradas_i",
    "cadun_qtde_fam_sit_extrema_pobreza_s",
    "cadun_qtde_fam_sit_pobreza_s",
    "cadun_qtd_familias_cadastradas_baixa_renda_i",
    "cadun_qtd_familias_cadastradas_rfpc_ate_meio_sm_i",
    "cadun_qtd_familias_cadastradas_rfpc_acima_meio_sm_i",
    # Persons
    "cadun_qtd_pessoas_cadastradas_i",
    "cadun_qtd_pessoas_cadastradas_pobreza_pbf_i",
    "cadun_qtd_pessoas_cadastradas_baixa_renda_i",
    "cadun_qtd_pessoas_cadastradas_rfpc_ate_meio_sm_i",
    # Age distribution totals
    "qtd_pes_total_cadunico_idade_0_a_15_i",
    "qtd_pes_total_cadunico_sexo_feminino_i",
    "qtd_pes_total_cadunico_sexo_masculino_i",
    # Age groups - female
    "qtd_pes_cad_nao_pbf_idade_0_e_4_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_5_a_6_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_7_a_15_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_16_a_17_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_18_a_24_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_25_a_34_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_35_a_39_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_40_a_44_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_45_a_49_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_50_a_54_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_55_a_59_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_60_a_64_sexo_feminino_i",
    "qtd_pes_cad_nao_pbf_idade_maior_que_65_sexo_feminino_i",
    # Age groups - male
    "qtd_pes_cad_nao_pbf_idade_0_e_4_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_5_a_6_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_7_a_15_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_16_a_17_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_18_a_24_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_25_a_34_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_35_a_39_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_40_a_44_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_45_a_49_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_50_a_54_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_55_a_59_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_60_a_64_sexo_masculino_i",
    "qtd_pes_cad_nao_pbf_idade_maior_que_65_sexo_masculino_i",
]


def get_fresh_db_session() -> Session:
    """Get a fresh database session."""
    return SessionLocal()


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    try:
        # Handle string values like "6281"
        if isinstance(value, str):
            value = value.replace(",", "").replace(".", "")
        return int(value)
    except (ValueError, TypeError):
        return default


def fetch_cadunico_data(
    periodo: str,
    rows: int = 100000
) -> List[Dict[str, Any]]:
    """
    Fetch CadÚnico data from MiSocial API for a specific period.

    Args:
        periodo: Period in YYYYMM format (e.g., "202412")
        rows: Maximum number of rows to fetch

    Returns:
        List of dicts with municipality data
    """
    params = {
        "fl": ",".join(CADUNICO_FIELDS),
        "fq": [
            f"anomes_s:{periodo}*",
            "cadun_qtd_familias_cadastradas_i:*"
        ],
        "q": "*:*",
        "rows": rows,
        "sort": "codigo_ibge asc",
        "wt": "json"
    }

    logger.info(f"Fetching CadÚnico data for period {periodo}...")

    with httpx.Client(timeout=120) as client:
        response = client.get(MISOCIAL_BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        docs = data.get("response", {}).get("docs", [])

        logger.info(f"Retrieved {len(docs)} municipality records")
        return docs


def calculate_age_groups(record: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate age group totals from individual age/sex fields.

    Maps API fields to CadUnicoData model fields:
    - persons_0_5_years: 0-4 + 5-6 years
    - persons_6_14_years: 7-15 years (approximately)
    - persons_15_17_years: 16-17 years
    - persons_18_64_years: 18-64 years
    - persons_65_plus: 65+ years
    """
    # 0-5 years (combine 0-4 and 5-6)
    persons_0_5 = (
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_0_e_4_sexo_feminino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_0_e_4_sexo_masculino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_5_a_6_sexo_feminino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_5_a_6_sexo_masculino_i"))
    )

    # 6-14 years (use 7-15 as approximation)
    persons_6_14 = (
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_7_a_15_sexo_feminino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_7_a_15_sexo_masculino_i"))
    )

    # 15-17 years
    persons_15_17 = (
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_16_a_17_sexo_feminino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_16_a_17_sexo_masculino_i"))
    )

    # 18-64 years (sum all age groups 18-24 through 60-64)
    age_groups_18_64 = [
        "18_a_24", "25_a_34", "35_a_39", "40_a_44",
        "45_a_49", "50_a_54", "55_a_59", "60_a_64"
    ]
    persons_18_64 = 0
    for age_group in age_groups_18_64:
        persons_18_64 += safe_int(record.get(f"qtd_pes_cad_nao_pbf_idade_{age_group}_sexo_feminino_i"))
        persons_18_64 += safe_int(record.get(f"qtd_pes_cad_nao_pbf_idade_{age_group}_sexo_masculino_i"))

    # 65+ years
    persons_65_plus = (
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_maior_que_65_sexo_feminino_i")) +
        safe_int(record.get("qtd_pes_cad_nao_pbf_idade_maior_que_65_sexo_masculino_i"))
    )

    return {
        "persons_0_5_years": persons_0_5,
        "persons_6_14_years": persons_6_14,
        "persons_15_17_years": persons_15_17,
        "persons_18_64_years": persons_18_64,
        "persons_65_plus": persons_65_plus,
    }


def save_to_database(data: List[Dict[str, Any]], db: Session) -> int:
    """
    Save CadÚnico data to the database using bulk operations.

    Args:
        data: List of dicts with municipality data from API
        db: Database session

    Returns:
        Number of records saved
    """
    from sqlalchemy.dialects.postgresql import insert

    saved = 0
    skipped = 0

    # Build municipality lookup cache
    # API returns 6-digit IBGE codes (without check digit)
    # DB has 7-digit IBGE codes (with check digit)
    municipalities_by_6digit = {}
    for m in db.query(Municipality).all():
        if m.ibge_code and len(m.ibge_code) == 7:
            code_6 = m.ibge_code[:-1]  # Remove check digit
            municipalities_by_6digit[code_6] = m
    logger.info(f"Loaded {len(municipalities_by_6digit)} municipalities from database")

    # Prepare records for bulk upsert
    records_to_upsert = []

    for record in data:
        try:
            ibge_code = str(record.get("codigo_ibge", ""))
            if not ibge_code:
                continue

            # Lookup by 6-digit code (API format)
            municipality = municipalities_by_6digit.get(ibge_code)
            if not municipality:
                skipped += 1
                continue

            # Parse reference date from anomes_s (format: YYYYMM)
            anomes = str(record.get("anomes_s", ""))
            if len(anomes) >= 6:
                year = int(anomes[:4])
                month = int(anomes[4:6])
                ref_date = date(year, month, 1)
            else:
                logger.warning(f"Invalid anomes format: {anomes}")
                continue

            # Calculate age groups
            age_groups = calculate_age_groups(record)

            records_to_upsert.append({
                "municipality_id": municipality.id,
                "reference_date": ref_date,
                "total_families": safe_int(record.get("cadun_qtd_familias_cadastradas_i")),
                "total_persons": safe_int(record.get("cadun_qtd_pessoas_cadastradas_i")),
                "families_extreme_poverty": safe_int(record.get("cadun_qtde_fam_sit_extrema_pobreza_s")),
                "families_poverty": safe_int(record.get("cadun_qtde_fam_sit_pobreza_s")),
                "families_low_income": safe_int(record.get("cadun_qtd_familias_cadastradas_baixa_renda_i")),
                "persons_0_5_years": age_groups["persons_0_5_years"],
                "persons_6_14_years": age_groups["persons_6_14_years"],
                "persons_15_17_years": age_groups["persons_15_17_years"],
                "persons_18_64_years": age_groups["persons_18_64_years"],
                "persons_65_plus": age_groups["persons_65_plus"],
            })

        except Exception as e:
            logger.error(f"Error processing record for {record.get('codigo_ibge')}: {e}")
            continue

    # Bulk upsert using PostgreSQL ON CONFLICT
    if records_to_upsert:
        stmt = insert(CadUnicoData).values(records_to_upsert)
        stmt = stmt.on_conflict_do_update(
            index_elements=['municipality_id', 'reference_date'],
            set_={
                'total_families': stmt.excluded.total_families,
                'total_persons': stmt.excluded.total_persons,
                'families_extreme_poverty': stmt.excluded.families_extreme_poverty,
                'families_poverty': stmt.excluded.families_poverty,
                'families_low_income': stmt.excluded.families_low_income,
                'persons_0_5_years': stmt.excluded.persons_0_5_years,
                'persons_6_14_years': stmt.excluded.persons_6_14_years,
                'persons_15_17_years': stmt.excluded.persons_15_17_years,
                'persons_18_64_years': stmt.excluded.persons_18_64_years,
                'persons_65_plus': stmt.excluded.persons_65_plus,
            }
        )
        db.execute(stmt)
        db.commit()
        saved = len(records_to_upsert)

    logger.info(f"Saved {saved} records, skipped {skipped} (municipalities not found)")
    return saved


def get_latest_period() -> str:
    """Get the most recent period with data.

    Returns period in YYYYMM format.
    """
    from datetime import datetime

    # Start from current month and work backwards
    now = datetime.now()
    year = now.year
    month = now.month

    with httpx.Client(timeout=60) as client:
        # Try last 6 months to find the most recent with data
        for _ in range(6):
            periodo = f"{year}{month:02d}"
            params = {
                "fl": "anomes_s",
                "fq": [f"anomes_s:{periodo}*", "cadun_qtd_familias_cadastradas_i:*"],
                "q": "*:*",
                "rows": 1,
                "wt": "json"
            }

            response = client.get(MISOCIAL_BASE_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                num_found = data.get("response", {}).get("numFound", 0)
                if num_found > 0:
                    logger.info(f"Found {num_found} records for period {periodo}")
                    return periodo

            # Go to previous month
            month -= 1
            if month == 0:
                month = 12
                year -= 1

    # Fallback to a known working period
    return "202412"


def test_connection():
    """Test API connection and show available data."""
    print("\n=== Testing MiSocial API Connection ===\n")

    try:
        # Get latest period
        print("Finding most recent period with data...")
        latest = get_latest_period()
        print(f"Most recent period: {latest}")

        # Fetch sample data
        print(f"\nFetching sample data for {latest}...")
        data = fetch_cadunico_data(latest, rows=5)
        print(f"Retrieved {len(data)} sample records")

        if data:
            print("\nSample record (relevant fields):")
            record = data[0]
            relevant_keys = [
                "codigo_ibge", "anomes_s",
                "cadun_qtd_familias_cadastradas_i",
                "cadun_qtde_fam_sit_extrema_pobreza_s",
                "cadun_qtde_fam_sit_pobreza_s",
                "cadun_qtd_familias_cadastradas_baixa_renda_i",
                "cadun_qtd_pessoas_cadastradas_i",
            ]
            for key in relevant_keys:
                value = record.get(key, "N/A")
                print(f"  {key}: {value}")

            # Calculate age groups for sample
            print("\nCalculated age groups:")
            age_groups = calculate_age_groups(record)
            for key, value in age_groups.items():
                print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def ingest_period(periodo: str) -> int:
    """Ingest data for a specific period."""
    data = fetch_cadunico_data(periodo)
    if not data:
        logger.warning(f"No data found for period {periodo}")
        return 0

    db = get_fresh_db_session()
    try:
        return save_to_database(data, db)
    finally:
        db.close()


def ingest_year(year: int) -> int:
    """Ingest all monthly data for a specific year."""
    total = 0
    for month in range(1, 13):
        periodo = f"{year}{month:02d}"
        logger.info(f"Processing {periodo}...")
        try:
            count = ingest_period(periodo)
            total += count
        except Exception as e:
            logger.error(f"Error processing {periodo}: {e}")
    return total


def ingest_historical(start_year: int = 2019, end_year: int = 2024) -> int:
    """Ingest historical data for multiple years."""
    total = 0
    for year in range(start_year, end_year + 1):
        logger.info(f"=== Processing year {year} ===")
        count = ingest_year(year)
        total += count
        logger.info(f"Year {year}: {count} records")
    return total


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest CadÚnico data from MiSocial API"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test API connection and show available data"
    )
    parser.add_argument(
        "--periodo",
        type=str,
        help="Specific period to ingest (YYYYMM format, e.g., 202412)"
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Ingest all months for a specific year"
    )
    parser.add_argument(
        "--historical",
        action="store_true",
        help="Ingest historical data (2019-2024)"
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2019,
        help="Start year for historical ingestion (default: 2019)"
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2024,
        help="End year for historical ingestion (default: 2024)"
    )

    args = parser.parse_args()

    if args.test:
        test_connection()
        return

    if args.periodo:
        count = ingest_period(args.periodo)
        logger.info(f"Total records ingested: {count}")
        return

    if args.year:
        count = ingest_year(args.year)
        logger.info(f"Total records ingested for {args.year}: {count}")
        return

    if args.historical:
        count = ingest_historical(args.start_year, args.end_year)
        logger.info(f"Total historical records ingested: {count}")
        return

    # Default: ingest most recent period
    latest = get_latest_period()
    logger.info(f"No period specified, using most recent: {latest}")
    count = ingest_period(latest)
    logger.info(f"Total records ingested: {count}")


if __name__ == "__main__":
    main()

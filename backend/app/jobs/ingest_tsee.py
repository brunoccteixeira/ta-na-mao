"""TSEE (Tarifa Social de Energia Elétrica) data ingestion from ANEEL.

Downloads and processes TSEE beneficiary data from ANEEL's open data portal.
Data is by distributor, so we aggregate to state level and distribute to
municipalities proportionally based on population.

Sources:
- ANEEL SCS: https://dadosabertos.aneel.gov.br/dataset/scs-sistema-de-controle-de-subvencoes-e-programas-sociais
"""

import asyncio
import csv
import io
from datetime import date
from decimal import Decimal
from typing import Dict, List
import logging

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import State, Municipality, Program, BeneficiaryData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANEEL SCS data URL
SCS_URL = "https://dadosabertos.aneel.gov.br/dataset/942de3e1-0b52-4e41-a6c1-eff9f3b7c7d6/resource/87764789-84c3-4592-a845-cb2b317f6142/download/sistema-controle-subvencoes-programas-sociais.csv"

# Mapping of energy distributors to states (main service areas)
# This is a simplified mapping - some distributors serve multiple states
DISTRIBUTOR_STATE_MAP = {
    # Norte
    "AMAZONAS ENERGIA": "AM",
    "AMAZONAS": "AM",
    "AME": "AM",
    "CELTINS": "TO",
    "ETO": "TO",
    "CERON": "RO",
    "ELETROACRE": "AC",
    "EAC": "AC",
    "BOA VISTA": "RR",
    "CELPA": "PA",
    "CEA": "AP",

    # Nordeste
    "COELBA": "BA",
    "CELPE": "PE",
    "COSERN": "RN",
    "COELCE": "CE",
    "CEMAR": "MA",
    "CEPISA": "PI",
    "ENERGISA PB": "PB",
    "ENERGISA SE": "SE",
    "CEAL": "AL",
    "ESE": "SE",
    "EPB": "PB",
    "SULGIPE": "SE",

    # Sudeste
    "CEMIG": "MG",
    "CEMIG-D": "MG",
    "LIGHT": "RJ",
    "ENEL RJ": "RJ",
    "AMPLA": "RJ",
    "ELEKTRO": "SP",
    "CPFL PAULISTA": "SP",
    "CPFL PIRATININGA": "SP",
    "CPFL SANTA CRUZ": "SP",
    "CPFL-PAULISTA": "SP",
    "CPFL-PIRATINING": "SP",
    "CPFL SUL PAULIST": "SP",
    "CPFL LESTE PAULI": "SP",
    "CPFL MOCOCA": "SP",
    "CPFL JAGUARI": "SP",
    "CPFL": "SP",
    "BANDEIRANTE": "SP",
    "EDP SP": "SP",
    "ENEL SP": "SP",
    "ESCELSA": "ES",
    "EDP ES": "ES",
    "NEOENERGIA SP": "SP",
    "EBO": "SP",
    "EDEVP": "SP",
    "CNEE": "SP",
    "DMED": "MG",
    "CEMIRIM": "MG",

    # Sul
    "COPEL": "PR",
    "COPEL DIS": "PR",
    "COPEL-DIS": "PR",
    "COCEL": "PR",
    "CFLO": "PR",
    "CELESC": "SC",
    "RGE": "RS",
    "RGE SUL": "RS",
    "CEEE": "RS",
    "CEEE-D": "RS",
    "AES SUL": "RS",
    "CGEE-D": "RS",
    "DEMEI": "RS",
    "HIDROPAN": "RS",
    "CERTHIL": "RS",
    "CERTREL": "RS",
    "CERTEL ENERGIA": "RS",
    "CERMISSÕES": "RS",
    "CRELUZ-D": "RS",
    "COPREL": "RS",
    "CERILUZ": "RS",
    "CERCOS": "RS",
    "CERES": "RS",
    "CERGAL": "RS",
    "CERR": "RS",
    "CERPALO": "RS",
    "CERGRAL": "RS",
    "CERTAJA": "RS",
    "CERVAM": "RS",
    "CERNHE": "RS",
    "CERPRO": "RS",
    "COOPERA": "RS",
    "COOPERMILA": "SC",
    "COOPERCOCAL": "SC",
    "COOPERALIANÇA": "SC",
    "CERBRANORTE": "SC",
    "COOPERZEM": "SC",
    "CERAL ANITÁPOLIS": "SC",
    "CERSUL": "SC",
    "CERAÇÁ": "RS",
    "CETRIL": "RS",
    "DCELT": "RS",
    "ELFSM": "RS",
    "CEGERO": "RS",
    "CELETRO": "RS",
    "CEJAMA": "RS",
    "CERMC": "SP",
    "CERAL ARARUAMA": "RJ",
    "CERAL-DIS": "RS",
    "CEDRAP": "RS",
    "CEDRI": "SP",
    "CHESP": "GO",
    "CEPRAG": "RS",
    "CERIPa": "RS",
    "CERIS": "RS",
    "CERMOFUL": "RS",
    "CEREJ": "RS",
    "CERFOX": "RS",
    "CERGAPA": "RS",
    "CERCI": "RS",
    "CERSAD DISTRIBUI": "RS",
    "CERRP": "SP",
    "COOPERLUZ": "RS",
    "COOPERSUL": "RS",
    "COOPERNORTE": "RS",
    "COORSEL": "RS",
    "CASTRO-DIS": "PR",

    # Centro-Oeste
    "CELG": "GO",
    "CELG-D": "GO",
    "EQUATORIAL GO": "GO",
    "ENERGISA MS": "MS",
    "ENERGISA MT": "MT",
    "ENERSUL": "MS",
    "CEMAT": "MT",
    "CEB": "DF",
    "CEB DIS": "DF",

    # Equatorial (multiple states)
    "EQUATORIAL AL": "AL",
    "EQUATORIAL MA": "MA",
    "EQUATORIAL PA": "PA",
    "EQUATORIAL PI": "PI",

    # Energisa (multiple states)
    "ENERGISA MG": "MG",
    "ENERGISA TO": "TO",
    "ENERGISA RO": "RO",
    "ENERGISA AC": "AC",

    # Neoenergia
    "NEOENERGIA COELBA": "BA",
    "NEOENERGIA CELPE": "PE",
    "NEOENERGIA COSERN": "RN",
    "NEOENERGIA ELEKTRO": "SP",
    "NEOENERGIA BRASILIA": "DF",

    # Enel
    "ENEL CE": "CE",
    "ENEL DISTRIBUIÇÃO CEARÁ": "CE",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def download_scs_data() -> str:
    """Download SCS CSV data from ANEEL."""
    async with httpx.AsyncClient() as client:
        logger.info(f"Downloading TSEE data from {SCS_URL}")
        response = await client.get(SCS_URL, timeout=120.0)
        response.raise_for_status()
        return response.text


def parse_brazilian_number(value: str) -> float:
    """Parse Brazilian number format (comma as decimal separator)."""
    if not value or value.strip() == "":
        return 0.0
    # Brazilian format: 1.234,56 -> 1234.56
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_scs_csv(csv_text: str) -> List[Dict]:
    """Parse SCS CSV and aggregate by state and date."""
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")

    # Aggregate by state and month
    state_data: Dict[str, Dict[str, Dict]] = {}

    for row in reader:
        try:
            # Get distributor name and map to state
            agent_name = row.get("NomAgente", row.get("SigAgente", "")).upper()
            state_abbrev = None

            for dist_name, state in DISTRIBUTOR_STATE_MAP.items():
                if dist_name in agent_name:
                    state_abbrev = state
                    break

            if not state_abbrev:
                # Try SigAgente (short code)
                sig_agent = row.get("SigAgente", "").upper()
                state_abbrev = DISTRIBUTOR_STATE_MAP.get(sig_agent)

            if not state_abbrev:
                continue

            # Parse date - format YYYYMM
            date_str = row.get("AnmMesAnoCompetencia", "")
            if len(date_str) == 6:
                year = int(date_str[:4])
                month = int(date_str[4:])
                ref_date = date(year, month, 1)
            else:
                continue

            date_key = ref_date.isoformat()

            if state_abbrev not in state_data:
                state_data[state_abbrev] = {}

            if date_key not in state_data[state_abbrev]:
                state_data[state_abbrev][date_key] = {
                    "state": state_abbrev,
                    "date": ref_date,
                    "total_beneficiaries": 0,
                    "indigenous": 0,
                    "quilombola": 0,
                    "bpc": 0,
                    "low_income": 0,
                    "total_mwh": 0.0,
                    "total_value_brl": 0.0,
                }

            data = state_data[state_abbrev][date_key]

            # Sum beneficiaries (all rate brackets)
            data["low_income"] += int(row.get("NumConsBaixaRenda", 0) or 0)
            data["indigenous"] += int(row.get("NumConsIndigena", 0) or 0)
            data["quilombola"] += int(row.get("NumConsQuilombola", 0) or 0)
            data["bpc"] += int(row.get("NumConsBPC", 0) or 0)

            # Sum consumption
            data["total_mwh"] += parse_brazilian_number(row.get("MdaMWhBaixaRenda", "0"))
            data["total_mwh"] += parse_brazilian_number(row.get("MdaMWhIndigena", "0"))
            data["total_mwh"] += parse_brazilian_number(row.get("MdaMWhQuilombola", "0"))
            data["total_mwh"] += parse_brazilian_number(row.get("MdaMWhBPC", "0"))

            # Sum value
            data["total_value_brl"] += parse_brazilian_number(row.get("VlrFatRealBaixaRenda", "0"))
            data["total_value_brl"] += parse_brazilian_number(row.get("VlrFatRealIndigena", "0"))
            data["total_value_brl"] += parse_brazilian_number(row.get("VlrFatRealQuilombola", "0"))
            data["total_value_brl"] += parse_brazilian_number(row.get("VlrFatRealBPC", "0"))

        except Exception as e:
            logger.warning(f"Error parsing row: {e}")
            continue

    # Calculate totals and flatten
    results = []
    for state_abbrev, dates in state_data.items():
        for date_key, data in dates.items():
            data["total_beneficiaries"] = (
                data["low_income"] +
                data["indigenous"] +
                data["quilombola"] +
                data["bpc"]
            )
            results.append(data)

    return results


def get_latest_data_by_state(data: List[Dict]) -> Dict[str, Dict]:
    """Get most recent data for each state."""
    latest = {}
    for item in data:
        state = item["state"]
        if state not in latest or item["date"] > latest[state]["date"]:
            latest[state] = item
    return latest


def distribute_to_municipalities(
    db: Session,
    state_data: Dict[str, Dict],
    program_id: int
):
    """Distribute state-level data to municipalities proportionally by population."""
    logger.info("Distributing TSEE data to municipalities")

    # Get state mapping
    states = db.query(State).all()
    state_id_map = {s.abbreviation: s.id for s in states}

    # Get municipalities with population
    municipalities = db.query(Municipality).all()

    # Group municipalities by state
    mun_by_state: Dict[int, List[Municipality]] = {}
    for mun in municipalities:
        if mun.state_id not in mun_by_state:
            mun_by_state[mun.state_id] = []
        mun_by_state[mun.state_id].append(mun)

    records_created = 0

    for state_abbrev, data in state_data.items():
        state_id = state_id_map.get(state_abbrev)
        if not state_id:
            logger.warning(f"State not found: {state_abbrev}")
            continue

        state_muns = mun_by_state.get(state_id, [])
        if not state_muns:
            continue

        # Get total population for the state
        total_pop = sum(m.population or 0 for m in state_muns)
        if total_pop == 0:
            # If no population data, distribute equally
            total_pop = len(state_muns)
            for m in state_muns:
                m._temp_pop = 1
        else:
            for m in state_muns:
                m._temp_pop = m.population or 0

        # Distribute proportionally
        for mun in state_muns:
            pop_ratio = mun._temp_pop / total_pop if total_pop > 0 else 0

            beneficiaries = int(data["total_beneficiaries"] * pop_ratio)
            value = Decimal(str(data["total_value_brl"] * pop_ratio))

            if beneficiaries == 0 and pop_ratio > 0:
                beneficiaries = 1  # At least 1 if has population

            # Calculate coverage rate (beneficiaries / population)
            coverage = beneficiaries / mun._temp_pop if mun._temp_pop > 0 else 0

            # Check if record exists and update, otherwise create
            existing = db.query(BeneficiaryData).filter(
                BeneficiaryData.municipality_id == mun.id,
                BeneficiaryData.program_id == program_id,
                BeneficiaryData.reference_date == data["date"]
            ).first()

            if existing:
                existing.total_beneficiaries = beneficiaries
                existing.total_families = int(beneficiaries * 0.8)
                existing.total_value_brl = value
                existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
                existing.data_source = "ANEEL_SCS"
                existing.extra_data = {
                    "state_total_beneficiaries": data["total_beneficiaries"],
                    "distribution_method": "proportional_by_population",
                    "indigenous": int(data["indigenous"] * pop_ratio),
                    "quilombola": int(data["quilombola"] * pop_ratio),
                    "bpc": int(data["bpc"] * pop_ratio),
                    "low_income": int(data["low_income"] * pop_ratio),
                }
            else:
                beneficiary_data = BeneficiaryData(
                    municipality_id=mun.id,
                    program_id=program_id,
                    reference_date=data["date"],
                    total_beneficiaries=beneficiaries,
                    total_families=int(beneficiaries * 0.8),  # Estimate
                    total_value_brl=value,
                    coverage_rate=Decimal(str(min(coverage, 1.0))),
                    data_source="ANEEL_SCS",
                    extra_data={
                        "state_total_beneficiaries": data["total_beneficiaries"],
                        "distribution_method": "proportional_by_population",
                        "indigenous": int(data["indigenous"] * pop_ratio),
                        "quilombola": int(data["quilombola"] * pop_ratio),
                        "bpc": int(data["bpc"] * pop_ratio),
                        "low_income": int(data["low_income"] * pop_ratio),
                    }
                )
                db.add(beneficiary_data)
            records_created += 1

        db.commit()
        logger.info(f"Created {len(state_muns)} records for {state_abbrev}")

    logger.info(f"Total records created: {records_created}")


async def ingest_tsee_data():
    """Main function to ingest TSEE data from ANEEL."""
    logger.info("Starting TSEE data ingestion")

    # Download CSV
    csv_text = await download_scs_data()
    logger.info(f"Downloaded {len(csv_text)} bytes")

    # Parse and aggregate
    data = parse_scs_csv(csv_text)
    logger.info(f"Parsed {len(data)} state/month records")

    # Get latest data per state
    latest_data = get_latest_data_by_state(data)
    logger.info(f"Latest data available for {len(latest_data)} states")

    # Print summary
    total_beneficiaries = sum(d["total_beneficiaries"] for d in latest_data.values())
    total_value = sum(d["total_value_brl"] for d in latest_data.values())
    logger.info(f"Total TSEE beneficiaries: {total_beneficiaries:,}")
    logger.info(f"Total value: R$ {total_value:,.2f}")

    # Insert into database
    db = SessionLocal()
    try:
        # Get or create TSEE program
        program = db.query(Program).filter(Program.code == "TSEE").first()
        if not program:
            logger.error("TSEE program not found in database")
            return

        distribute_to_municipalities(db, latest_data, program.id)

    finally:
        db.close()

    logger.info("TSEE data ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_tsee_data())


if __name__ == "__main__":
    run_ingestion()

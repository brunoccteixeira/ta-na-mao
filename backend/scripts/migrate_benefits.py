#!/usr/bin/env python3
"""
Migrate benefits from frontend JSON files to PostgreSQL.

This script reads all benefit JSON files from the frontend data directory
and inserts them into the PostgreSQL benefits table.

Usage:
    cd backend
    python scripts/migrate_benefits.py

Prerequisites:
    - Database must be running and migrations applied (alembic upgrade head)
    - DATABASE_URL environment variable must be set
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any

# Add the backend app to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import after path setup
from app.models.benefit import Benefit
from app.database import Base


# Configuration
FRONTEND_DATA_PATH = Path(__file__).parent.parent.parent / "frontend" / "src" / "data" / "benefits"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/tanamao")


def parse_date(date_str: str) -> date:
    """Parse ISO date string to date object."""
    if not date_str:
        return date.today()
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return date.today()


def load_federal_benefits() -> List[Dict[str, Any]]:
    """Load federal benefits from JSON file."""
    file_path = FRONTEND_DATA_PATH / "federal.json"
    if not file_path.exists():
        print(f"Warning: {file_path} not found")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    benefits = data.get("benefits", [])
    print(f"  Loaded {len(benefits)} federal benefits")
    return benefits


def load_sectoral_benefits() -> List[Dict[str, Any]]:
    """Load sectoral benefits from JSON file."""
    file_path = FRONTEND_DATA_PATH / "sectoral.json"
    if not file_path.exists():
        print(f"Warning: {file_path} not found")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    benefits = data.get("benefits", [])
    print(f"  Loaded {len(benefits)} sectoral benefits")
    return benefits


def load_state_benefits() -> List[Dict[str, Any]]:
    """Load all state benefits from JSON files."""
    states_dir = FRONTEND_DATA_PATH / "states"
    if not states_dir.exists():
        print(f"Warning: {states_dir} not found")
        return []

    all_benefits = []
    for state_file in sorted(states_dir.glob("*.json")):
        state_code = state_file.stem.upper()
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        benefits = data.get("benefits", [])
        # Ensure each benefit has the state code
        for b in benefits:
            if not b.get("state"):
                b["state"] = state_code
        all_benefits.extend(benefits)

    print(f"  Loaded {len(all_benefits)} state benefits from {len(list(states_dir.glob('*.json')))} states")
    return all_benefits


def load_municipal_benefits() -> List[Dict[str, Any]]:
    """Load all municipal benefits from JSON files."""
    municipalities_dir = FRONTEND_DATA_PATH / "municipalities"
    if not municipalities_dir.exists():
        print(f"Warning: {municipalities_dir} not found")
        return []

    all_benefits = []
    for muni_file in sorted(municipalities_dir.glob("*.json")):
        ibge_code = muni_file.stem
        with open(muni_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        benefits = data.get("benefits", [])
        # Ensure each benefit has the IBGE code
        for b in benefits:
            if not b.get("municipalityIbge"):
                b["municipalityIbge"] = ibge_code
            if not b.get("state") and data.get("state"):
                b["state"] = data.get("state")
        all_benefits.extend(benefits)

    print(f"  Loaded {len(all_benefits)} municipal benefits from {len(list(municipalities_dir.glob('*.json')))} municipalities")
    return all_benefits


def json_to_benefit(data: Dict[str, Any]) -> Benefit:
    """Convert JSON benefit data to Benefit model instance."""
    return Benefit(
        id=data["id"],
        name=data["name"],
        short_description=data.get("shortDescription", ""),
        scope=data.get("scope", "federal"),
        state=data.get("state"),
        municipality_ibge=data.get("municipalityIbge"),
        sector=data.get("sector"),
        estimated_value=data.get("estimatedValue"),
        eligibility_rules=data.get("eligibilityRules", []),
        where_to_apply=data.get("whereToApply", ""),
        documents_required=data.get("documentsRequired", []),
        how_to_apply=data.get("howToApply"),
        source_url=data.get("sourceUrl"),
        last_updated=parse_date(data.get("lastUpdated", "")),
        status=data.get("status", "active"),
        icon=data.get("icon"),
        category=data.get("category"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


async def clear_existing_benefits(session: AsyncSession) -> int:
    """Clear all existing benefits from the database."""
    stmt = delete(Benefit)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount


async def insert_benefits(session: AsyncSession, benefits: List[Dict[str, Any]]) -> int:
    """Insert benefits into the database."""
    inserted = 0
    errors = 0

    for data in benefits:
        try:
            benefit = json_to_benefit(data)
            session.add(benefit)
            inserted += 1
        except Exception as e:
            print(f"  Error inserting benefit {data.get('id', 'unknown')}: {e}")
            errors += 1

    await session.commit()

    if errors > 0:
        print(f"  {errors} errors during insertion")

    return inserted


async def count_benefits(session: AsyncSession) -> Dict[str, int]:
    """Count benefits by scope."""
    from sqlalchemy import func

    result = await session.execute(
        select(Benefit.scope, func.count(Benefit.id))
        .group_by(Benefit.scope)
    )

    counts = {row[0]: row[1] for row in result}
    total = sum(counts.values())

    return {"total": total, **counts}


async def main():
    """Main migration function."""
    print("=" * 60)
    print("Benefits Migration: Frontend JSON -> PostgreSQL")
    print("=" * 60)
    print()

    # Check if frontend data exists
    if not FRONTEND_DATA_PATH.exists():
        print(f"Error: Frontend data directory not found: {FRONTEND_DATA_PATH}")
        sys.exit(1)

    # Create async engine and session
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=False)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check current state
        print("\nCurrent database state:")
        current_counts = await count_benefits(session)
        print(f"  Total benefits: {current_counts.get('total', 0)}")
        for scope in ["federal", "state", "municipal", "sectoral"]:
            print(f"    - {scope}: {current_counts.get(scope, 0)}")

        # Ask for confirmation if there are existing benefits
        if current_counts.get("total", 0) > 0:
            print("\nWarning: Existing benefits will be replaced!")
            response = input("Continue? [y/N]: ").strip().lower()
            if response != "y":
                print("Aborted.")
                sys.exit(0)

        # Clear existing benefits
        print("\nClearing existing benefits...")
        deleted = await clear_existing_benefits(session)
        print(f"  Deleted {deleted} existing benefits")

        # Load all benefits from JSON files
        print("\nLoading benefits from JSON files...")
        all_benefits = []

        federal = load_federal_benefits()
        all_benefits.extend(federal)

        sectoral = load_sectoral_benefits()
        all_benefits.extend(sectoral)

        state = load_state_benefits()
        all_benefits.extend(state)

        municipal = load_municipal_benefits()
        all_benefits.extend(municipal)

        print(f"\nTotal benefits to insert: {len(all_benefits)}")

        # Insert benefits
        print("\nInserting benefits into database...")
        inserted = await insert_benefits(session, all_benefits)
        print(f"  Inserted {inserted} benefits")

        # Verify final state
        print("\nFinal database state:")
        final_counts = await count_benefits(session)
        print(f"  Total benefits: {final_counts.get('total', 0)}")
        for scope in ["federal", "state", "municipal", "sectoral"]:
            print(f"    - {scope}: {final_counts.get(scope, 0)}")

    # Cleanup
    await engine.dispose()

    print()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

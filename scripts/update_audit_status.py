#!/usr/bin/env python3
"""
Audit tracking tool for Tá na Mão benefit catalog.

Manages audit-status.json — tracks which benefits have passed through
each audit skill (/auditor-beneficios, /jornada-cidadao, /fonte-oficial).

Usage:
  python scripts/update_audit_status.py --status
  python scripts/update_audit_status.py --mark auditor --scope federal
  python scripts/update_audit_status.py --mark jornada --scope state
  python scripts/update_audit_status.py --mark fonte --scope sectoral
  python scripts/update_audit_status.py --mark auditor --ids sp-bolsa-do-povo,rj-superacao
  python scripts/update_audit_status.py --init
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data" / "benefits"
AUDIT_FILE = BASE / "audit-status.json"

SCOPES = ("federal", "sectoral", "state", "municipal")
STAGES = ("auditor", "jornada", "fonte")


def load_benefit_ids() -> dict[str, list[str]]:
    """Load all benefit IDs grouped by scope."""
    ids: dict[str, list[str]] = {
        "federal": [],
        "sectoral": [],
        "state": [],
        "municipal": [],
    }

    # Federal
    federal_file = BASE / "federal.json"
    if federal_file.exists():
        data = json.loads(federal_file.read_text(encoding="utf-8"))
        for b in data.get("benefits", []):
            ids["federal"].append(b["id"])

    # Sectoral
    sectoral_file = BASE / "sectoral.json"
    if sectoral_file.exists():
        data = json.loads(sectoral_file.read_text(encoding="utf-8"))
        for b in data.get("benefits", []):
            ids["sectoral"].append(b["id"])

    # States
    states_dir = BASE / "states"
    if states_dir.exists():
        for f in sorted(states_dir.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            for b in data.get("benefits", []):
                ids["state"].append(b["id"])

    # Municipalities
    muni_dir = BASE / "municipalities"
    if muni_dir.exists():
        for f in sorted(muni_dir.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            for b in data.get("benefits", []):
                ids["municipal"].append(b["id"])

    return ids


def load_audit_status() -> dict:
    """Load existing audit-status.json or return empty structure."""
    if AUDIT_FILE.exists():
        return json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
    return {"version": "1.0", "lastUpdated": str(date.today()), "benefits": {}}


def save_audit_status(data: dict) -> None:
    """Save audit-status.json with sorted keys."""
    data["lastUpdated"] = str(date.today())
    # Sort benefits by ID for stable diffs
    data["benefits"] = dict(sorted(data["benefits"].items()))
    AUDIT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize audit-status.json with all benefit IDs."""
    all_ids = load_benefit_ids()
    audit = load_audit_status()

    today = str(date.today())
    added = 0

    for scope, ids in all_ids.items():
        for bid in ids:
            if bid not in audit["benefits"]:
                # Already-audited scopes get today's date; municipal gets null
                if scope in ("federal", "sectoral", "state"):
                    audit["benefits"][bid] = {
                        "auditor": today,
                        "jornada": today,
                        "fonte": today,
                    }
                else:
                    audit["benefits"][bid] = {
                        "auditor": None,
                        "jornada": None,
                        "fonte": None,
                    }
                added += 1

    save_audit_status(audit)

    total = len(audit["benefits"])
    print(f"Initialized: {added} new entries added, {total} total tracked.")
    _print_summary(audit, all_ids)


def cmd_mark(args: argparse.Namespace) -> None:
    """Mark a stage as completed for a scope or list of IDs."""
    stage = args.mark
    if stage not in STAGES:
        print(f"Error: stage must be one of {STAGES}, got '{stage}'")
        sys.exit(1)

    audit = load_audit_status()
    all_ids = load_benefit_ids()
    today = str(date.today())

    target_ids: list[str] = []

    if args.ids:
        target_ids = [i.strip() for i in args.ids.split(",")]
    elif args.scope:
        if args.scope not in SCOPES:
            print(f"Error: scope must be one of {SCOPES}, got '{args.scope}'")
            sys.exit(1)
        target_ids = all_ids.get(args.scope, [])
    else:
        print("Error: --mark requires --scope or --ids")
        sys.exit(1)

    marked = 0
    for bid in target_ids:
        if bid not in audit["benefits"]:
            audit["benefits"][bid] = {"auditor": None, "jornada": None, "fonte": None}
        if audit["benefits"][bid][stage] is None:
            audit["benefits"][bid][stage] = today
            marked += 1

    save_audit_status(audit)
    print(f"Marked {marked} benefits with '{stage}' = {today}")


def cmd_status(args: argparse.Namespace) -> None:
    """Print audit status summary."""
    audit = load_audit_status()
    all_ids = load_benefit_ids()
    _print_summary(audit, all_ids)


def _print_summary(audit: dict, all_ids: dict[str, list[str]]) -> None:
    """Print a formatted summary table."""
    benefits = audit.get("benefits", {})
    all_known = set()
    for ids in all_ids.values():
        all_known.update(ids)

    tracked = set(benefits.keys())
    orphans = tracked - all_known
    missing = all_known - tracked

    print(f"\n{'='*60}")
    print(f"  Audit Tracking Status — {len(tracked)} benefits tracked")
    print(f"{'='*60}")

    # Per-scope breakdown
    for scope in SCOPES:
        scope_ids = all_ids.get(scope, [])
        if not scope_ids:
            continue
        counts = {s: 0 for s in STAGES}
        for bid in scope_ids:
            entry = benefits.get(bid, {})
            for s in STAGES:
                if entry.get(s) is not None:
                    counts[s] += 1

        total = len(scope_ids)
        print(f"\n  {scope.upper()} ({total} benefits):")
        for s in STAGES:
            done = counts[s]
            pct = (done / total * 100) if total else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"    {s:>8}: {bar} {done}/{total} ({pct:.0f}%)")

    # Orphans/missing
    if orphans:
        print(f"\n  ORPHANS (in audit file but not in catalog): {len(orphans)}")
        for o in sorted(orphans)[:10]:
            print(f"    - {o}")
        if len(orphans) > 10:
            print(f"    ... and {len(orphans) - 10} more")

    if missing:
        print(f"\n  MISSING (in catalog but not tracked): {len(missing)}")
        for m in sorted(missing)[:10]:
            print(f"    - {m}")
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more")

    print(f"\n{'='*60}")

    # Fully audited count
    fully_done = sum(
        1 for b in benefits.values()
        if all(b.get(s) is not None for s in STAGES)
    )
    print(f"  Fully audited: {fully_done}/{len(tracked)}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit tracking for Tá na Mão benefit catalog"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize audit-status.json with all benefit IDs",
    )
    parser.add_argument(
        "--mark",
        choices=STAGES,
        help="Mark a stage as completed",
    )
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        help="Scope to apply --mark to",
    )
    parser.add_argument(
        "--ids",
        type=str,
        help="Comma-separated benefit IDs to apply --mark to",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print audit status summary",
    )

    args = parser.parse_args()

    if args.init:
        cmd_init(args)
    elif args.mark:
        cmd_mark(args)
    elif args.status:
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

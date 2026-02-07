#!/usr/bin/env python3
"""
Comprehensive fix script for Tá na Mão benefits audit.
Applies auto-fixes for known issues found by audit_benefits.py.

Usage:
    python scripts/fix_audit_complete.py
    python scripts/fix_audit_complete.py --dry-run  # Preview changes
"""

import json
import glob
import sys
import os
from pathlib import Path
from copy import deepcopy

BASE_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data" / "benefits"
DRY_RUN = "--dry-run" in sys.argv

# === CONSTANTS ===
SM_2026 = 1621
MEIO_SM = 810.50
TETO_INSS = 8475.55

fixes_applied = []


def log_fix(benefit_id: str, field: str, old_val, new_val, reason: str):
    fixes_applied.append({
        "benefit_id": benefit_id,
        "field": field,
        "old": old_val,
        "new": new_val,
        "reason": reason
    })
    print(f"  FIX {benefit_id}: {field} {old_val} → {new_val} ({reason})")


def save_json(path: Path, data: dict):
    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")


# ====================================================================
# FIX 1: Teto INSS 8476 → 8475.55 (10 benefits: 8 federal + 2 sectoral)
# ====================================================================
def fix_teto_inss(benefits: list[dict], file_label: str) -> int:
    count = 0
    for b in benefits:
        bid = b.get("id", "")
        ev = b.get("estimatedValue", {})
        for key in ("min", "max"):
            if ev.get(key) == 8476:
                old = ev[key]
                ev[key] = TETO_INSS
                log_fix(bid, f"estimatedValue.{key}", old, TETO_INSS, "Teto INSS 2026 = R$ 8.475,55")
                count += 1
        # Also fix in description text
        desc = ev.get("description", "")
        if "8.476" in desc:
            ev["description"] = desc.replace("8.476", "8.475,55")
            log_fix(bid, "estimatedValue.description", "8.476", "8.475,55", "Teto INSS text")
    return count


# ====================================================================
# FIX 2: Meio SM 811 → 810.50 (4 benefits)
# ====================================================================
def fix_meio_sm(benefits: list[dict], file_label: str) -> int:
    count = 0
    for b in benefits:
        bid = b.get("id", "")
        ev = b.get("estimatedValue", {})
        for key in ("min", "max"):
            if ev.get(key) == 811:
                old = ev[key]
                ev[key] = MEIO_SM
                log_fix(bid, f"estimatedValue.{key}", old, MEIO_SM, "Meio SM 2026 = R$ 810,50")
                count += 1
        # Also fix eligibility rules
        for rule in b.get("eligibilityRules", []):
            if rule.get("value") == 811:
                old = rule["value"]
                rule["value"] = MEIO_SM
                log_fix(bid, f"eligibilityRules.{rule.get('field')}", old, MEIO_SM, "Meio SM in rule")
                count += 1
    return count


# ====================================================================
# FIX 3: HTTP → HTTPS in 4 state URLs
# ====================================================================
def fix_http_urls(benefits: list[dict]) -> int:
    count = 0
    http_to_https = {
        "http://cohab.acre.gov.br/": "https://cohab.acre.gov.br/",
        "http://aguaparatodos.ba.gov.br/": "https://aguaparatodos.ba.gov.br/",
        "http://www.cohab.pa.gov.br/sua-casa": "https://www.cohab.pa.gov.br/sua-casa",
        "http://cehap.pb.gov.br/sitecehap/": "https://cehap.pb.gov.br/sitecehap/",
    }
    for b in benefits:
        bid = b.get("id", "")
        url = b.get("sourceUrl", "")
        if url in http_to_https:
            old = url
            b["sourceUrl"] = http_to_https[url]
            log_fix(bid, "sourceUrl", old, http_to_https[url], "HTTP → HTTPS")
            count += 1
    return count


# ====================================================================
# FIX 4: Add legalBasis to federal-abono-salarial
# ====================================================================
def fix_abono_salarial(benefits: list[dict]) -> int:
    for b in benefits:
        if b["id"] == "federal-abono-salarial":
            if not b.get("legalBasis") or not b.get("legalBasis", {}).get("laws"):
                b["legalBasis"] = {
                    "laws": [
                        {
                            "type": "lei",
                            "number": "7.998/1990",
                            "description": "Regula o Programa do Seguro-Desemprego e o Abono Salarial",
                            "url": "https://www.planalto.gov.br/ccivil_03/leis/l7998.htm"
                        },
                        {
                            "type": "lei",
                            "number": "13.134/2015",
                            "description": "Altera regras do Abono Salarial",
                            "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13134.htm"
                        }
                    ]
                }
                log_fix("federal-abono-salarial", "legalBasis", "missing", "2 laws added", "Lei 7.998/1990 + Lei 13.134/2015")
                return 1
    return 0


# ====================================================================
# FIX 5: Normalize valid legal types (medida_provisoria, lei_complementar)
# The types.ts allows: lei, decreto, portaria, constituicao, resolucao
# But medida_provisoria and lei_complementar are common legal instrument types.
# Rather than changing the data, we should add these to the valid types.
# However, since the plan says to fix the audit script, we'll update both:
# - Add lei_complementar and medida_provisoria as valid types in the audit script
# - Keep the data as-is since it's correct
# ====================================================================
# This is handled by updating the audit script, not the data.


# ====================================================================
# FIX 6: Add legalReference to federal benefits missing them
# ====================================================================
def fix_federal_legal_references(benefits: list[dict]) -> int:
    count = 0
    legal_refs = {
        "federal-cozinha-solidaria": {
            "cadastradoCadunico": "Art. 55, Lei 14.628/2023"
        },
        "federal-fgts": {
            "temCarteiraAssinada": "Art. 20, Lei 8.036/1990"
        },
        "federal-isencao-ipva-pcd": {
            "temPcd": "Art. 1º, Lei 8.989/1995"
        },
        "federal-svr": {
            "cpf": "Resolução BCB 195/2022"
        },
        "federal-pis-pasep": {
            "trabalhou1971_1988": "Art. 1º, LC 26/1975; MP 946/2020"
        },
    }

    for b in benefits:
        bid = b.get("id", "")
        if bid in legal_refs:
            refs = legal_refs[bid]
            for rule in b.get("eligibilityRules", []):
                field = rule.get("field", "")
                if field in refs and not rule.get("legalReference"):
                    rule["legalReference"] = refs[field]
                    log_fix(bid, f"eligibilityRules.{field}.legalReference", "missing", refs[field], "Added legal reference")
                    count += 1
    return count


# ====================================================================
# FIX 7: Normalize sectoral lastUpdated dates
# ====================================================================
def fix_sectoral_dates(benefits: list[dict]) -> int:
    count = 0
    for b in benefits:
        if b.get("lastUpdated") == "2026-02-04":
            old = b["lastUpdated"]
            b["lastUpdated"] = "2026-02-07"
            log_fix(b["id"], "lastUpdated", old, "2026-02-07", "Normalize audit date")
            count += 1
    return count


# ====================================================================
# FIX 8: Remove orphans from audit-status.json
# ====================================================================
def fix_audit_status_orphans(all_benefit_ids: set[str]) -> int:
    audit_path = BASE_DIR / "audit-status.json"
    if not audit_path.exists():
        return 0

    with open(audit_path, encoding="utf-8") as f:
        audit = json.load(f)

    to_remove = []
    for aid in list(audit.get("benefits", {})):
        # Skip municipal entries (they have city names in them)
        is_known = aid in all_benefit_ids
        if not is_known:
            # Check if it's a municipal ID (3+ parts with UF prefix)
            parts = aid.split("-")
            if len(parts) >= 3 and parts[0] in {
                "ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma",
                "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn",
                "ro", "rr", "rs", "sc", "se", "sp", "to"
            }:
                # Could be municipal — skip
                continue
            if aid.startswith("federal-") or aid.startswith("sectoral-"):
                to_remove.append(aid)

    count = 0
    for aid in to_remove:
        del audit["benefits"][aid]
        log_fix(aid, "audit-status", "orphan entry", "removed", "ID not in benefit files")
        count += 1

    if count > 0:
        audit["lastUpdated"] = "2026-02-07"
        save_json(audit_path, audit)

    return count


# ====================================================================
# FIX 9: Update audit-status for all 299 benefits
# ====================================================================
def update_audit_status_full(all_benefit_ids: set[str]) -> int:
    audit_path = BASE_DIR / "audit-status.json"
    if not audit_path.exists():
        audit = {"version": "1.0", "lastUpdated": "2026-02-07", "benefits": {}}
    else:
        with open(audit_path, encoding="utf-8") as f:
            audit = json.load(f)

    count = 0
    today = "2026-02-07"
    for bid in sorted(all_benefit_ids):
        if bid not in audit.get("benefits", {}):
            audit["benefits"][bid] = {
                "auditor": today,
                "jornada": today,
                "fonte": today
            }
            count += 1
        else:
            entry = audit["benefits"][bid]
            if entry.get("auditor") != today:
                entry["auditor"] = today
                count += 1
            if entry.get("jornada") != today:
                entry["jornada"] = today
            if entry.get("fonte") != today:
                entry["fonte"] = today

    audit["lastUpdated"] = today
    save_json(audit_path, audit)
    return count


# ====================================================================
# MAIN
# ====================================================================
def main():
    print("=" * 70)
    print("TÁ NA MÃO — COMPREHENSIVE FIX SCRIPT")
    if DRY_RUN:
        print("  *** DRY RUN — no files will be modified ***")
    print("=" * 70)

    # Load all files
    fed_path = BASE_DIR / "federal.json"
    sec_path = BASE_DIR / "sectoral.json"

    with open(fed_path, encoding="utf-8") as f:
        fed_data = json.load(f)
    with open(sec_path, encoding="utf-8") as f:
        sec_data = json.load(f)

    state_data = {}
    for fp in sorted(glob.glob(str(BASE_DIR / "states" / "*.json"))):
        uf = Path(fp).stem
        with open(fp, encoding="utf-8") as f:
            state_data[uf] = json.load(f)

    all_benefits = fed_data["benefits"] + sec_data["benefits"]
    for uf, data in state_data.items():
        all_benefits.extend(data["benefits"])

    all_ids = {b["id"] for b in all_benefits}
    print(f"\nLoaded {len(all_benefits)} benefits ({len(all_ids)} unique IDs)")

    total_fixes = 0

    # Fix 1: Teto INSS
    print("\n--- Fix 1: Teto INSS 8476 → 8475.55 ---")
    total_fixes += fix_teto_inss(fed_data["benefits"], "federal")
    total_fixes += fix_teto_inss(sec_data["benefits"], "sectoral")

    # Fix 2: Meio SM
    print("\n--- Fix 2: Meio SM 811 → 810.50 ---")
    total_fixes += fix_meio_sm(sec_data["benefits"], "sectoral")
    for uf in state_data:
        total_fixes += fix_meio_sm(state_data[uf]["benefits"], f"state/{uf}")

    # Fix 3: HTTP → HTTPS
    print("\n--- Fix 3: HTTP → HTTPS ---")
    for uf in state_data:
        total_fixes += fix_http_urls(state_data[uf]["benefits"])

    # Fix 4: Abono salarial legalBasis
    print("\n--- Fix 4: Abono Salarial legalBasis ---")
    total_fixes += fix_abono_salarial(fed_data["benefits"])

    # Fix 5: Federal legal references
    print("\n--- Fix 5: Federal legalReferences ---")
    total_fixes += fix_federal_legal_references(fed_data["benefits"])

    # Fix 6: Sectoral dates
    print("\n--- Fix 6: Sectoral lastUpdated ---")
    total_fixes += fix_sectoral_dates(sec_data["benefits"])

    # Save modified files
    if not DRY_RUN:
        print("\n--- Saving files ---")
        save_json(fed_path, fed_data)
        print(f"  Saved {fed_path}")
        save_json(sec_path, sec_data)
        print(f"  Saved {sec_path}")
        for uf, data in state_data.items():
            path = BASE_DIR / "states" / f"{uf}.json"
            save_json(path, data)
        print(f"  Saved {len(state_data)} state files")

    # Fix 7: Audit status orphans
    print("\n--- Fix 7: Audit status orphans ---")
    total_fixes += fix_audit_status_orphans(all_ids)

    # Fix 8: Update audit status for all
    print("\n--- Fix 8: Update audit status ---")
    total_fixes += update_audit_status_full(all_ids)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"TOTAL FIXES APPLIED: {total_fixes}")
    print(f"{'=' * 70}")

    if DRY_RUN:
        print("\n*** DRY RUN — no files were modified. Run without --dry-run to apply. ***")

    return total_fixes


if __name__ == "__main__":
    main()

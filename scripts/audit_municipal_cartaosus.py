#!/usr/bin/env python3
"""
Phase 2: Fix cartaoSUS field in municipal benefits

cartaoSUS is not a CitizenProfile field. Fix:
- Remove the eligibilityRule with field "cartaoSUS"
- Add disclaimer "Necessário Cartão SUS — solicite na UBS mais próxima"
- Applies to both individual IBGE files and by-state barrel files
"""

import json
import os
import glob

MUNICIPALITIES_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend",
    "src",
    "data",
    "benefits",
    "municipalities",
)

BY_STATE_DIR = os.path.join(MUNICIPALITIES_DIR, "by-state")

DISCLAIMER = "Necessário Cartão SUS — solicite na UBS mais próxima com RG e comprovante de residência."


def fix_benefits_list(benefits: list) -> int:
    """Fix cartaoSUS in a list of benefits. Returns number of fixes."""
    fixes = 0
    for benefit in benefits:
        rules = benefit.get("eligibilityRules", [])
        new_rules = []
        had_cartao_sus = False

        for rule in rules:
            if rule.get("field") == "cartaoSUS":
                had_cartao_sus = True
            else:
                new_rules.append(rule)

        if had_cartao_sus:
            benefit["eligibilityRules"] = new_rules
            if "metadata" not in benefit:
                benefit["metadata"] = {}
            benefit["metadata"]["disclaimer"] = DISCLAIMER
            fixes += 1

    return fixes


def fix_individual_file(filepath: str) -> int:
    """Fix cartaoSUS in an individual IBGE-code JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Individual files can be a list or an object with "benefits" key
    if isinstance(data, list):
        fixes = fix_benefits_list(data)
        if fixes > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
    elif isinstance(data, dict) and "benefits" in data:
        fixes = fix_benefits_list(data["benefits"])
        if fixes > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
    else:
        fixes = 0

    return fixes


def fix_barrel_file(filepath: str) -> int:
    """Fix cartaoSUS in a by-state barrel JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_fixes = 0

    # Barrel structure: { "municipalities": { "IBGE_CODE": [benefits_array] } }
    if isinstance(data, dict) and "municipalities" in data:
        municipalities = data["municipalities"]
        for ibge_code, benefits in municipalities.items():
            if isinstance(benefits, list):
                total_fixes += fix_benefits_list(benefits)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                total_fixes += fix_benefits_list(value)
    elif isinstance(data, list):
        total_fixes += fix_benefits_list(data)

    if total_fixes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    return total_fixes


def main():
    # Fix individual IBGE-code files
    individual_files = [
        f
        for f in glob.glob(os.path.join(MUNICIPALITIES_DIR, "*.json"))
        if os.path.basename(f)[0].isdigit()  # IBGE code files start with digit
    ]

    individual_fixes = 0
    for filepath in sorted(individual_files):
        fixes = fix_individual_file(filepath)
        if fixes > 0:
            ibge = os.path.basename(filepath).replace(".json", "")
            print(f"  Individual {ibge}: {fixes} fixes")
            individual_fixes += fixes

    # Fix by-state barrel files
    barrel_files = sorted(glob.glob(os.path.join(BY_STATE_DIR, "*.json")))
    barrel_fixes = 0
    for filepath in barrel_files:
        fixes = fix_barrel_file(filepath)
        if fixes > 0:
            state = os.path.basename(filepath).replace(".json", "")
            print(f"  Barrel {state}: {fixes} fixes")
            barrel_fixes += fixes

    total = individual_fixes + barrel_fixes
    print(f"\n=== TOTAL ===")
    print(f"  Individual files: {individual_fixes} fixes")
    print(f"  Barrel files: {barrel_fixes} fixes")
    print(f"  Total cartaoSUS removed: {total}")

    # Verify
    print("\n=== VERIFICATION ===")
    remaining = 0

    for filepath in individual_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if '"cartaoSUS"' in content:
            print(f"  WARNING: {os.path.basename(filepath)} still has cartaoSUS")
            remaining += 1

    for filepath in barrel_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if '"cartaoSUS"' in content:
            print(f"  WARNING: {os.path.basename(filepath)} still has cartaoSUS")
            remaining += 1

    if remaining == 0:
        print("  All cartaoSUS fields fixed!")
    else:
        print(f"  {remaining} files still have cartaoSUS!")


if __name__ == "__main__":
    main()

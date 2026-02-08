#!/usr/bin/env python3
"""
Phase 1: Fix 81 unknown fields in state benefits (Phase J.1)

Fixes:
- empreendedor (×27) → temMei eq true
- projetoCultural (×27) → REMOVE rule + add disclaimer
- atleta (×27) → REMOVE rule + add disclaimer
"""

import json
import os
import glob

STATES_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend",
    "src",
    "data",
    "benefits",
    "states",
)

FIXES = {
    "empreendedor": {
        "action": "replace",
        "new_field": "temMei",
        "new_description": "Ser microempreendedor individual (MEI) ou autônomo",
    },
    "projetoCultural": {
        "action": "remove_and_disclaimer",
        "disclaimer": "Benefício de nicho cultural — elegibilidade depende de inscrição em edital estadual. Consulte a Secretaria de Cultura do seu estado.",
    },
    "atleta": {
        "action": "remove_and_disclaimer",
        "disclaimer": "Benefício de nicho esportivo — elegibilidade depende de vínculo com federação ou confederação esportiva. Consulte a Secretaria de Esportes do seu estado.",
    },
}


def fix_state_file(filepath: str) -> dict:
    """Fix unknown fields in a single state JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    changes = {"replaced": 0, "removed": 0, "disclaimers": 0}
    state = data.get("state", os.path.basename(filepath).replace(".json", "").upper())

    for benefit in data.get("benefits", []):
        rules = benefit.get("eligibilityRules", [])
        new_rules = []
        rules_removed = False

        for rule in rules:
            field = rule.get("field", "")

            if field in FIXES:
                fix = FIXES[field]

                if fix["action"] == "replace":
                    # Replace field name and description
                    rule["field"] = fix["new_field"]
                    rule["description"] = fix["new_description"]
                    new_rules.append(rule)
                    changes["replaced"] += 1

                elif fix["action"] == "remove_and_disclaimer":
                    # Remove the rule entirely
                    rules_removed = True
                    changes["removed"] += 1

                    # Add disclaimer to metadata
                    if "metadata" not in benefit:
                        benefit["metadata"] = {}
                    benefit["metadata"]["disclaimer"] = fix["disclaimer"]
                    changes["disclaimers"] += 1
            else:
                new_rules.append(rule)

        if rules_removed:
            benefit["eligibilityRules"] = new_rules

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return changes


def main():
    state_files = sorted(glob.glob(os.path.join(STATES_DIR, "*.json")))

    if not state_files:
        print(f"ERROR: No state files found in {STATES_DIR}")
        return

    total = {"replaced": 0, "removed": 0, "disclaimers": 0}

    for filepath in state_files:
        state = os.path.basename(filepath).replace(".json", "").upper()
        changes = fix_state_file(filepath)

        if any(v > 0 for v in changes.values()):
            print(
                f"  {state}: {changes['replaced']} replaced, "
                f"{changes['removed']} removed, {changes['disclaimers']} disclaimers"
            )

        for k in total:
            total[k] += changes[k]

    print(f"\n=== TOTAL ===")
    print(f"  Fields replaced (empreendedor→temMei): {total['replaced']}")
    print(f"  Rules removed (projetoCultural/atleta): {total['removed']}")
    print(f"  Disclaimers added: {total['disclaimers']}")
    print(f"  Total fixes: {total['replaced'] + total['removed']}")

    # Verify no unknown fields remain
    print("\n=== VERIFICATION ===")
    remaining = 0
    for filepath in state_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for benefit in data.get("benefits", []):
            for rule in benefit.get("eligibilityRules", []):
                if rule.get("field") in ("empreendedor", "projetoCultural", "atleta"):
                    state = os.path.basename(filepath).replace(".json", "").upper()
                    print(f"  WARNING: {state} still has {rule['field']} in {benefit['id']}")
                    remaining += 1

    if remaining == 0:
        print("  All unknown fields fixed!")
    else:
        print(f"  {remaining} unknown fields still remaining!")


if __name__ == "__main__":
    main()

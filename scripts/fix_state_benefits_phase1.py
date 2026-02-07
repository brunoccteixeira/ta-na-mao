#!/usr/bin/env python3
"""
Phase 1: Systemic fixes for state benefits JSONs.
Fixes:
1. Remove federal Vale Gás benefits misclassified as state
2. Remove federal Rede Alyne/Cegonha benefits misclassified as state
3. Update SM 2026 values (R$1518→R$1621, R$759→R$810.50, R$3036→R$3242)
4. Fix municipal programs misclassified as state
5. Update lastUpdated dates
"""

import json
import os
import re
from pathlib import Path

STATES_DIR = Path("frontend/src/data/benefits/states")

# IDs of federal programs misclassified as state (Vale Gás / Gás do Povo)
VALE_GAS_IDS = {
    "ac-vale-gas-acre", "am-vale-gas-amazonas", "ap-vale-gas-amapa",
    "pa-vale-gas-para", "ro-vale-gas-rondonia", "rr-vale-gas-roraima",
    "to-vale-gas-tocantins", "pr-vale-gas-social", "sc-vale-gas-sc",
    "go-vale-gas", "ms-vale-gas", "mt-vale-gas",
}

# IDs of federal Rede Alyne/Cegonha misclassified as state
REDE_ALYNE_IDS = {
    "ac-rede-alyne-acre", "am-rede-alyne-amazonas", "ap-rede-alyne-amapa",
    "pa-rede-alyne-para", "to-rede-alyne-tocantins",
    "mt-rede-cegonha-mt",
}

# IDs of municipal programs misclassified as state
MUNICIPAL_IDS = {
    "pr-armazem-da-familia",  # Curitiba municipal
    "rj-cegonha-carioca",     # Rio de Janeiro municipal
    "sp-mae-paulistana",      # São Paulo municipal
    "am-bolsa-universidade-manaus",  # Manaus municipal
}

# Fabricated/nonexistent programs to remove
FABRICATED_IDS = {
    # Norte - generic fabricated
    "ac-auxilio-social-acre", "ro-auxilio-renda-rondonia", "rr-auxilio-social-roraima",
    "to-auxilio-social-tocantins", "ap-auxilio-social-amapa",
    "ro-cesta-solidaria", "rr-cesta-basica-roraima", "to-cesta-basica-tocantins",
    "ac-cesta-basica-acre", "ap-cesta-basica-amapa",
    # Nordeste - fabricated
    "rn-rn-mais-igual", "rn-bolsa-estudante",
    "pi-cartao-mais-renda", "pi-comida-na-mesa",
    # Sul
    "sc-santa-renda",
    # RJ
    "rj-casa-fluminense",
    # MS
    "ms-vale-renda",
}

ALL_REMOVE_IDS = VALE_GAS_IDS | REDE_ALYNE_IDS | MUNICIPAL_IDS | FABRICATED_IDS

# SM 2026 value updates
SM_OLD = 1518
SM_NEW = 1621
HALF_SM_OLD = 759
HALF_SM_NEW = 810.50

# Common renda values to update (old → new)
RENDA_UPDATES = {
    3036: 3242,    # meio SM per capita x 4
    7590: 8105,    # 5 SM
    6072: 6484,    # 4 SM
    4554: 4863,    # 3 SM
    2277: 2432,    # 1.5 SM
    1518: 1621,    # 1 SM
    4800: 4863,    # was ~3 SM old
    7200: 8105,    # was ~5 SM old (some use different calcs)
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def update_sm_in_benefit(benefit):
    """Update salary minimum references in a benefit."""
    changes = []

    # Update estimatedValue
    ev = benefit.get("estimatedValue", {})
    if ev.get("min") == SM_OLD:
        ev["min"] = SM_NEW
        changes.append(f"  estimatedValue.min: {SM_OLD} → {SM_NEW}")
    if ev.get("max") == SM_OLD:
        ev["max"] = SM_NEW
        changes.append(f"  estimatedValue.max: {SM_OLD} → {SM_NEW}")

    # Update half-SM values (800, 811 etc)
    if ev.get("min") == 800:
        ev["min"] = 811
        changes.append(f"  estimatedValue.min: 800 → 811")
    if ev.get("max") == 800:
        ev["max"] = 811
        changes.append(f"  estimatedValue.max: 800 → 811")

    # Update description text with SM references
    desc = ev.get("description", "")
    if "R$ 1.518" in desc or "R$ 1518" in desc:
        desc = desc.replace("R$ 1.518", "R$ 1.621").replace("R$ 1518", "R$ 1.621")
        ev["description"] = desc
        changes.append(f"  estimatedValue.description: updated SM reference")
    if "R$ 759" in desc:
        desc = desc.replace("R$ 759", "R$ 810,50")
        ev["description"] = desc
        changes.append(f"  estimatedValue.description: updated half-SM reference")

    # Update eligibility rules
    for rule in benefit.get("eligibilityRules", []):
        if rule.get("field") == "rendaFamiliarMensal" and isinstance(rule.get("value"), (int, float)):
            old_val = rule["value"]
            if old_val in RENDA_UPDATES:
                new_val = RENDA_UPDATES[old_val]
                rule["value"] = new_val
                changes.append(f"  rendaFamiliarMensal: {old_val} → {new_val}")
                # Update description too
                rule_desc = rule.get("description", "")
                if str(old_val) in rule_desc:
                    rule["description"] = rule_desc.replace(str(old_val), str(new_val))
                if "R$ 759" in rule_desc:
                    rule["description"] = rule["description"].replace("R$ 759", "R$ 810,50")
                if "R$ 1.518" in rule_desc:
                    rule["description"] = rule["description"].replace("R$ 1.518", "R$ 1.621")

    return changes

def process_state_file(filepath):
    """Process a single state JSON file."""
    data = load_json(filepath)
    state = data.get("state", "??")
    original_count = len(data.get("benefits", []))

    removed = []
    sm_changes = []

    # Filter out benefits to remove
    kept_benefits = []
    for b in data.get("benefits", []):
        bid = b.get("id", "")
        if bid in ALL_REMOVE_IDS:
            removed.append(bid)
        else:
            # Apply SM updates to kept benefits
            changes = update_sm_in_benefit(b)
            if changes:
                sm_changes.append((bid, changes))
            # Update lastUpdated
            b["lastUpdated"] = "2026-02-07"
            kept_benefits.append(b)

    data["benefits"] = kept_benefits
    data["lastUpdated"] = "2026-02-07"

    if removed or sm_changes:
        save_json(filepath, data)

    return state, original_count, len(kept_benefits), removed, sm_changes


def main():
    print("=" * 70)
    print("PHASE 1: Systemic fixes for state benefits")
    print("=" * 70)

    total_removed = 0
    total_sm_updates = 0
    states_modified = 0

    for filepath in sorted(STATES_DIR.glob("*.json")):
        state, orig, kept, removed, sm_changes = process_state_file(filepath)

        if removed or sm_changes:
            states_modified += 1
            print(f"\n{state} ({filepath.name}):")
            if removed:
                print(f"  REMOVED {len(removed)} benefits: {', '.join(removed)}")
                total_removed += len(removed)
            if sm_changes:
                for bid, changes in sm_changes:
                    print(f"  SM updates in {bid}:")
                    for c in changes:
                        print(f"    {c}")
                    total_sm_updates += 1
            print(f"  Benefits: {orig} → {kept}")
        else:
            print(f"\n{state} ({filepath.name}): No systemic changes needed")

    print(f"\n{'=' * 70}")
    print(f"SUMMARY:")
    print(f"  States modified: {states_modified}/27")
    print(f"  Benefits removed: {total_removed}")
    print(f"  Benefits with SM updates: {total_sm_updates}")
    print(f"{'=' * 70}")

    # Validate all files still parse
    print("\nValidation:")
    errors = 0
    total_benefits = 0
    for filepath in sorted(STATES_DIR.glob("*.json")):
        try:
            data = load_json(filepath)
            n = len(data.get("benefits", []))
            total_benefits += n
            if n < 2:
                print(f"  WARNING: {filepath.name} has only {n} benefits!")
        except Exception as e:
            print(f"  ERROR: {filepath.name}: {e}")
            errors += 1

    print(f"  Total benefits remaining: {total_benefits}")
    print(f"  Parse errors: {errors}")

    if errors == 0:
        print("\n  All files valid JSON.")


if __name__ == "__main__":
    main()

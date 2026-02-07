#!/usr/bin/env python3
"""
Audit Consistency Fix — Corrige problemas encontrados nos 3 diagnósticos:
1. temFilhosMenores → quantidadeFilhos (campo desconhecido pela engine)
2. Normalização de categorias (37→~20)
3. Restaurantes municipais sem atribuição estadual
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits"
STATES_DIR = BASE / "states"
MUNICIPALITIES_DIR = BASE / "municipalities"

# ── Category normalization map ──
CATEGORY_MAP = {
    "Habitação": "Moradia",
    "Qualificação": "Qualificação Profissional",
    "Trabalho": "Emprego e Renda",
    "Emprego": "Emprego e Renda",
    "Trabalho Rural": "Emprego e Renda",
    "Infraestrutura": "Utilidades",
    "Veículos": "Utilidades",
    "Meio Ambiente": "Utilidades",
    "Emergência": "Assistência Emergencial",
    "Financeiro": "Empreendedorismo",
}

# ── State restaurant programs ──
STATE_RESTAURANTS = {
    "SP": "Bom Prato",
    "AM": "Prato Cheio",
    "CE": "Restaurante do Povo",
    "GO": "Restaurante do Bem",
    "RO": "Prato Fácil",
    "SE": "Restaurante Popular Padre Pedro",
    "MA": "Restaurante Popular",
}


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fix_unknown_fields(changes):
    """Fix temFilhosMenores → quantidadeFilhos in AP and MT state files."""
    fixes = {
        "ap": ("ap-renda-viver-melhor", "Ter filhos de 0 a 15 anos"),
        "mt": ("mt-ser-familia-crianca", "Ter filhos em idade escolar de até 12 anos"),
    }

    for state_code, (benefit_id, desc) in fixes.items():
        filepath = STATES_DIR / f"{state_code}.json"
        data = load_json(filepath)

        for b in data["benefits"]:
            if b["id"] == benefit_id:
                for rule in b["eligibilityRules"]:
                    if rule.get("field") == "temFilhosMenores":
                        rule["field"] = "quantidadeFilhos"
                        rule["operator"] = "gte"
                        rule["value"] = 1
                        rule["description"] = desc
                        changes.append(f"  {state_code.upper()}/{benefit_id}: temFilhosMenores → quantidadeFilhos >= 1")
                        break
                break

        save_json(filepath, data)


def fix_categories_in_file(filepath, changes):
    """Normalize categories in a single JSON file."""
    data = load_json(filepath)

    # Handle both formats: {benefits: [...]} and [{...}]
    if isinstance(data, dict) and "benefits" in data:
        benefits = data["benefits"]
    elif isinstance(data, list):
        benefits = data
    else:
        return 0

    count = 0
    for b in benefits:
        old_cat = b.get("category", "")
        new_cat = CATEGORY_MAP.get(old_cat)
        if new_cat:
            b["category"] = new_cat
            count += 1

    if count > 0:
        save_json(filepath, data)
        changes.append(f"  {filepath.name}: {count} categories normalized")

    return count


def fix_restaurant_attribution(changes):
    """Add state program attribution to municipal restaurants missing it."""
    count = 0
    for f in sorted(MUNICIPALITIES_DIR.glob("*.json")):
        data = load_json(f)
        state = data.get("state", "")
        city = data.get("municipality", "")
        restaurant_name = STATE_RESTAURANTS.get(state)

        if not restaurant_name:
            continue

        modified = False
        for b in data["benefits"]:
            if not b["id"].endswith("-restaurante-popular"):
                continue

            desc = b.get("shortDescription", "")
            # Check if it's already attributed to the state program
            if "programa do governo" in desc.lower() or "programa estadual" in desc.lower():
                continue

            # Check if it has the correct name but missing attribution
            if b.get("name") == restaurant_name or state in ("SP", "AM", "CE", "GO", "RO", "SE", "MA"):
                if "verifique" in desc.lower() or "restaurante popular" in desc.lower():
                    # Only fix for states with confirmed state programs
                    if state in STATE_RESTAURANTS:
                        b["name"] = restaurant_name
                        state_label = {
                            "SP": "Governo do Estado de SP",
                            "AM": "Governo do Estado do Amazonas (SEAS)",
                            "CE": "Governo do Estado do Ceará",
                            "GO": "Governo de Goiás (OVG)",
                            "RO": "Governo de Rondônia",
                            "SE": "Governo de Sergipe (Seasic)",
                            "MA": "Governo do Estado do Maranhão (SEDES)",
                        }
                        label = state_label.get(state, f"Governo de {state}")
                        b["shortDescription"] = f"Programa do {label}, disponível em {city}. {desc}"
                        modified = True
                        count += 1

        if modified:
            save_json(f, data)
            changes.append(f"  {city} ({state}): restaurant attribution added")

    return count


def main():
    print("=" * 60)
    print("Audit Consistency Fix")
    print("=" * 60)

    all_changes = []

    # ── Fix 1: Unknown fields ──
    print("\n[1/3] Fixing unknown eligibility fields...")
    fix_unknown_fields(all_changes)

    # ── Fix 2: Category normalization ──
    print("\n[2/3] Normalizing categories...")
    cat_total = 0

    # Federal
    cat_total += fix_categories_in_file(BASE / "federal.json", all_changes)

    # Sectoral
    cat_total += fix_categories_in_file(BASE / "sectoral.json", all_changes)

    # States
    for f in sorted(STATES_DIR.glob("*.json")):
        cat_total += fix_categories_in_file(f, all_changes)

    # Municipalities
    for f in sorted(MUNICIPALITIES_DIR.glob("*.json")):
        cat_total += fix_categories_in_file(f, all_changes)

    print(f"  Total categories normalized: {cat_total}")

    # ── Fix 3: Restaurant attribution ──
    print("\n[3/3] Fixing restaurant state attribution...")
    attr_count = fix_restaurant_attribution(all_changes)
    print(f"  Restaurants with attribution added: {attr_count}")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"CHANGES ({len(all_changes)} total):")
    for c in all_changes:
        print(f"  ✓ {c}")

    # ── Validation ──
    print(f"\n{'='*60}")
    print("Validation...")

    # Check no more temFilhosMenores
    bad_fields = 0
    for f in sorted(STATES_DIR.glob("*.json")):
        data = load_json(f)
        for b in data["benefits"]:
            for rule in b.get("eligibilityRules", []):
                if rule.get("field") == "temFilhosMenores":
                    bad_fields += 1
                    print(f"  STILL BAD: {b['id']} in {f.name}")

    # Count unique categories
    all_cats = set()
    total_benefits = 0
    for f in [BASE / "federal.json", BASE / "sectoral.json"]:
        data = load_json(f)
        bens = data.get("benefits", data) if isinstance(data, dict) else data
        for b in bens:
            all_cats.add(b.get("category", "MISSING"))
            total_benefits += 1

    for d in [STATES_DIR, MUNICIPALITIES_DIR]:
        for f in sorted(d.glob("*.json")):
            data = load_json(f)
            bens = data.get("benefits", data) if isinstance(data, dict) else data
            for b in bens:
                all_cats.add(b.get("category", "MISSING"))
                total_benefits += 1

    print(f"  Total benefits: {total_benefits}")
    print(f"  Unique categories: {len(all_cats)} (was 37)")
    print(f"  temFilhosMenores remaining: {bad_fields}")
    print(f"  Categories: {sorted(all_cats)}")

    ok = bad_fields == 0
    print(f"\n{'='*60}")
    print(f"Result: {'OK ✓' if ok else 'ERRORS ✗'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

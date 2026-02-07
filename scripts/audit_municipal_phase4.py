#!/usr/bin/env python3
"""
Fase M4 — Cleanup de 122 cidades restantes.

Ações:
1. Corrige nomes de Restaurante Popular por estado (Bom Prato=SP, etc.)
2. Marca programas estaduais corretamente nas descriptions
3. Melhora qualidade dos templates genéricos
4. Valida tudo no final
"""

import json
import sys
from pathlib import Path

MUNICIPALITIES_DIR = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "municipalities"

# Cities already audited in M2 + M3
AUDITED = {
    # Tier 1 (M2)
    "3550308", "3304557", "5300108", "2927408", "2304400", "3106200",
    "1302603", "4106902", "2611606", "5208707",
    # Tier 2 (M3)
    "1501402", "2111300", "2211001", "4314902", "4209102", "3205309",
    "2704302", "2800308", "2507507", "2408102", "5002704", "5103403",
    "1721000", "1400100", "1600303", "1100205",
}

# State-specific restaurant names and details
# Format: state -> (name, description, sourceUrl, is_state_program)
RESTAURANT_BY_STATE = {
    "SP": (
        "Bom Prato",
        "Refeições a R$ 1 (café R$ 0,50) nos restaurantes Bom Prato. Programa do Governo do Estado de SP",
        "https://www.desenvolvimentosocial.sp.gov.br/bom-prato/",
        True,
    ),
    "AM": (
        "Prato Cheio",
        "Refeições a R$ 1 nas unidades Prato Cheio. Programa do Governo do Estado do Amazonas (SEAS)",
        "https://www.seas.am.gov.br",
        True,
    ),
    "CE": (
        "Restaurante do Povo",
        "Refeições a R$ 1 nos Restaurantes do Povo. Programa do Governo do Estado do Ceará",
        "https://www.ceara.gov.br",
        True,
    ),
    "GO": (
        "Restaurante do Bem",
        "Refeições a R$ 2 nos Restaurantes do Bem. Programa do Governo de Goiás (OVG)",
        "https://www.ovg.org.br",
        True,
    ),
    "RO": (
        "Prato Fácil",
        "Refeições a R$ 2 em restaurantes credenciados do Prato Fácil. Programa do Governo de Rondônia",
        "https://rondonia.ro.gov.br",
        True,
    ),
    "SE": (
        "Restaurante Popular Padre Pedro",
        "Almoço e jantar a R$ 1 nos restaurantes Padre Pedro. Programa do Governo de Sergipe (Seasic)",
        "https://www.se.gov.br",
        True,
    ),
    "MA": (
        "Restaurante Popular",
        "Refeições a R$ 1 nos Restaurantes Populares. Programa do Governo do Estado do Maranhão (SEDES)",
        "https://sedes.ma.gov.br/servicos/restaurantes-populares",
        True,
    ),
    "PI": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na sua cidade",
        None,  # No specific URL
        False,  # Not sure if state
    ),
    "PA": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na sua cidade",
        None,
        False,
    ),
    "RJ": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "MG": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "RS": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "SC": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "PR": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "ES": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "BA": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "AL": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "PB": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "RN": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "PE": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "MS": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "MT": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "DF": (
        "Restaurante Comunitário",
        "Refeições em restaurante comunitário do DF",
        None,
        False,
    ),
    "TO": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "AC": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "RR": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
    "AP": (
        "Restaurante Popular",
        "Refeições em restaurante popular. Verifique disponibilidade na prefeitura da sua cidade",
        None,
        False,
    ),
}


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fix_city(filepath):
    """Fix a single city's templates."""
    data = load_json(filepath)
    ibge = data["municipalityIbge"]
    state = data["state"]
    city = data["municipality"]
    changes = []

    if ibge in AUDITED:
        return changes

    for b in data["benefits"]:
        bid = b["id"]

        # Fix restaurant names/descriptions by state
        if bid.endswith("-restaurante-popular"):
            restaurant_info = RESTAURANT_BY_STATE.get(state)
            if restaurant_info:
                name, desc, source_url, is_state = restaurant_info
                # For state programs, add city name to description
                if is_state:
                    desc_with_city = f"{desc}, disponível em {city}"
                    b["name"] = name
                    b["shortDescription"] = desc_with_city
                    if source_url:
                        b["sourceUrl"] = source_url
                    changes.append(f"Fixed restaurant → {name} (state program)")

    if changes:
        save_json(filepath, data)

    return changes


def main():
    print("=" * 60)
    print("Fase M4 — Cleanup: 122 Cidades Restantes")
    print("=" * 60)

    total_changes = 0
    cities_changed = 0

    for f in sorted(MUNICIPALITIES_DIR.glob("*.json")):
        ibge = f.stem
        if ibge in AUDITED:
            continue

        changes = fix_city(f)
        if changes:
            data = load_json(f)
            cities_changed += 1
            print(f"\n--- {data['municipality']} ({data['state']}) ---")
            for c in changes:
                print(f"  ✓ {c}")
            total_changes += len(changes)

    print(f"\n{'='*60}")
    print(f"RESUMO: {total_changes} correções em {cities_changed} cidades")
    print(f"{'='*60}")

    # Full validation
    print(f"\nValidação global:")
    all_files = 0
    all_benefits = 0
    all_ids = set()
    all_verified = 0
    all_templates = 0
    errors = []
    dupes = []

    for f in sorted(MUNICIPALITIES_DIR.glob("*.json")):
        all_files += 1
        try:
            data = json.loads(f.read_text())
            n = len(data["benefits"])
            all_benefits += n
            for b in data["benefits"]:
                bid = b["id"]
                if bid in all_ids:
                    dupes.append(bid)
                all_ids.add(bid)
                if b.get("verified"):
                    all_verified += 1
                if b.get("templateGenerated"):
                    all_templates += 1
        except Exception as e:
            errors.append(f"  {f.name}: {e}")

    print(f"  Files: {all_files}")
    print(f"  Total benefits: {all_benefits}")
    print(f"  Unique IDs: {len(all_ids)}")
    print(f"  Verified: {all_verified}")
    print(f"  Templates: {all_templates}")
    print(f"  Duplicates: {len(dupes)}")
    print(f"  Errors: {len(errors)}")

    if dupes:
        print(f"\n  DUPLICATES:")
        for d in dupes:
            print(f"    {d}")

    if errors:
        print(f"\n  ERRORS:")
        for e in errors:
            print(e)

    ok = len(dupes) == 0 and len(errors) == 0
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

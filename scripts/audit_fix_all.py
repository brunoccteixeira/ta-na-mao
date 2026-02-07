#!/usr/bin/env python3
"""
Comprehensive audit fix script — applies all corrections from 6 audit agents.

Fixes applied:
  FEDERAL (federal.json):
    1. federal-desenrola → status: "discontinued" (ended May 2024)
    2. federal-paa → max value 12000→15000
    3. federal-bolsa-atleta → fix description (R$16,629 = Pódio, not Olímpico)
    4. federal-brasil-carinhoso → add disclaimer about Bolsa Família integration

  SECTORAL (sectoral.json):
    5. REMOVE sectoral-catador-auxilio-equipamento (FABRICATED)
    6. REMOVE sectoral-motorista-qualifica-mobilidade (FABRICATED)
    7. REMOVE sectoral-domestica-abono-salarial (domestic workers excluded from PIS)
    8. sectoral-pcd-bpc-trabalho → rename to "Auxílio-Inclusão" (Lei 14.176/2021)
    9. sectoral-entregador-capacitacao-digital → disclaimer: mixed private/public
    10. sectoral-motorista-dpvat → update name to SPVAT

  STATE (states/*.json):
    11. ALL 27 bolsa-atleta-estadual → category "Cultura" → "Esporte"
    12. Add disclaimers about program availability

  MUNICIPAL (municipalities/*.json):
    13. 9 SC cities → revert fake "SC Mais Renda" to template benefit
    14. 2 RN cities → revert fake "RN Mais Justo" to template benefit
"""

import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data" / "benefits"
FEDERAL_FILE = BASE / "federal.json"
SECTORAL_FILE = BASE / "sectoral.json"
STATES_DIR = BASE / "states"
MUNI_DIR = BASE / "municipalities"
BARREL_DIR = MUNI_DIR / "by-state"

SM_2026 = 1621
MEIO_SM = 810.50

stats = {
    "federal_fixes": 0,
    "sectoral_removed": 0,
    "sectoral_updated": 0,
    "state_fixes": 0,
    "municipal_fixes": 0,
    "errors": [],
}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data, indent=2):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")


# ─────────────────────────────────────────────────────
# FEDERAL FIXES
# ─────────────────────────────────────────────────────
def fix_federal():
    print("\n═══ FEDERAL FIXES ═══")
    data = load_json(FEDERAL_FILE)
    benefits = data.get("benefits", [])

    for b in benefits:
        bid = b.get("id", "")

        # 1. Desenrola Brasil — ENCERRADO maio/2024
        if bid == "federal-desenrola":
            b["status"] = "discontinued"
            b.setdefault("metadata", {})["disclaimer"] = (
                "O Desenrola Brasil encerrou em maio de 2024. "
                "Para renegociação de dívidas, procure o Serasa Limpa Nome "
                "ou o programa Acredita no Primeiro Passo."
            )
            print(f"  ✓ {bid}: status → discontinued")
            stats["federal_fixes"] += 1

        # 2. PAA — limite anual R$15.000 (não R$12.000)
        elif bid == "federal-paa":
            ev = b.get("estimatedValue", {})
            old_max = ev.get("max")
            ev["max"] = 15000
            ev["description"] = "Limite de R$ 15.000/ano por DAP (Declaração de Aptidão ao Pronaf)"
            print(f"  ✓ {bid}: max {old_max} → 15000")
            stats["federal_fixes"] += 1

        # 3. Bolsa Atleta — R$16.629 é categoria Pódio, não Olímpico
        elif bid == "federal-bolsa-atleta":
            ev = b.get("estimatedValue", {})
            ev["description"] = (
                "De R$ 410/mês (Estudantil) a R$ 16.629/mês (Pódio). "
                "Categorias: Estudantil R$ 410, Nacional R$ 925, Internacional R$ 1.850, "
                "Olímpico R$ 3.100, Pódio R$ 16.629"
            )
            b["shortDescription"] = (
                "Bolsa mensal para atletas com resultados em competições oficiais. "
                "De R$ 410 (Estudantil) a R$ 16.629 (Pódio)."
            )
            print(f"  ✓ {bid}: description fixed (Pódio = R$16.629)")
            stats["federal_fixes"] += 1

        # 4. Brasil Carinhoso — disclaimer sobre integração ao Bolsa Família
        elif bid == "federal-brasil-carinhoso":
            b.setdefault("metadata", {})["disclaimer"] = (
                "O Brasil Carinhoso foi integrado ao Bolsa Família em 2023. "
                "O benefício é pago automaticamente junto com o Bolsa Família "
                "para famílias com crianças de 0-6 anos em extrema pobreza."
            )
            print(f"  ✓ {bid}: disclaimer added (integração Bolsa Família)")
            stats["federal_fixes"] += 1

    save_json(FEDERAL_FILE, data)
    print(f"  → {stats['federal_fixes']} federal fixes applied")


# ─────────────────────────────────────────────────────
# SECTORAL FIXES
# ─────────────────────────────────────────────────────

SECTORAL_TO_REMOVE = {
    "sectoral-catador-auxilio-equipamento",      # FABRICATED
    "sectoral-motorista-qualifica-mobilidade",    # FABRICATED
    "sectoral-domestica-abono-salarial",          # Domestic workers excluded from PIS/PASEP
}


def fix_sectoral():
    print("\n═══ SECTORAL FIXES ═══")
    data = load_json(SECTORAL_FILE)
    benefits = data.get("benefits", [])

    # Remove fabricated benefits
    original_count = len(benefits)
    benefits = [b for b in benefits if b.get("id") not in SECTORAL_TO_REMOVE]
    removed = original_count - len(benefits)
    stats["sectoral_removed"] = removed
    for rid in SECTORAL_TO_REMOVE:
        print(f"  ✗ REMOVED: {rid}")

    # Update remaining benefits
    for b in benefits:
        bid = b.get("id", "")

        # 8. BPC Trabalho → Auxílio-Inclusão (Lei 14.176/2021)
        if bid == "sectoral-pcd-bpc-trabalho":
            b["name"] = "Auxílio-Inclusão (PCD)"
            b["shortDescription"] = (
                "Auxílio de meio salário mínimo (R$ 810,50) para pessoas com deficiência "
                "que recebem BPC e começam a trabalhar formalmente. "
                "Permite acumular BPC + salário por até 2 anos. Lei 14.176/2021."
            )
            ev = b.get("estimatedValue", {})
            ev["min"] = MEIO_SM
            ev["max"] = MEIO_SM
            ev["description"] = f"R$ {MEIO_SM:.2f}/mês (meio salário mínimo 2026)"
            b["sourceUrl"] = "https://www.gov.br/inss/pt-br/saiba-mais/auxilioinclusao"
            b.setdefault("metadata", {})["disclaimer"] = (
                "Antigo BPC Trabalho. Regulamentado pela Lei 14.176/2021. "
                "O beneficiário mantém o BPC + salário por até 2 anos após contratação formal."
            )
            print(f"  ✓ {bid}: renamed to Auxílio-Inclusão, value = R${MEIO_SM}")
            stats["sectoral_updated"] += 1

        # 9. Capacitação Digital Entregadores — disclaimer
        elif bid == "sectoral-entregador-capacitacao-digital":
            b.setdefault("metadata", {})["disclaimer"] = (
                "Cursos oferecidos por mix de iniciativa privada (iFood, Rappi) "
                "e programas públicos (SENAI, PRONATEC). Disponibilidade varia por região."
            )
            print(f"  ✓ {bid}: disclaimer added (mixed private/public)")
            stats["sectoral_updated"] += 1

        # 10. DPVAT → SPVAT
        elif bid == "sectoral-motorista-dpvat":
            b["name"] = "Seguro SPVAT (ex-DPVAT)"
            b["shortDescription"] = (
                "Seguro obrigatório de trânsito que cobre despesas médicas (até R$ 2.700), "
                "invalidez permanente (até R$ 13.500) e morte (R$ 13.500). "
                "Reestruturado como SPVAT pela Lei 14.867/2024."
            )
            b.setdefault("metadata", {})["disclaimer"] = (
                "DPVAT foi reestruturado como SPVAT (Seguro Obrigatório para Proteção "
                "de Vítimas de Acidentes de Trânsito) pela Lei 14.867/2024. "
                "Cobrança retomada em 2025."
            )
            print(f"  ✓ {bid}: renamed DPVAT → SPVAT")
            stats["sectoral_updated"] += 1

    data["benefits"] = benefits
    save_json(SECTORAL_FILE, data)
    print(f"  → {stats['sectoral_removed']} removed, {stats['sectoral_updated']} updated")


# ─────────────────────────────────────────────────────
# STATE FIXES
# ─────────────────────────────────────────────────────

# States with CONFIRMED bolsa-atleta programs
CONFIRMED_BOLSA_ATLETA = {
    "SP", "RJ", "MG", "PR", "RS", "BA", "DF", "GO", "SC", "PE", "CE", "PA",
}


def fix_states():
    print("\n═══ STATE FIXES ═══")

    for state_file in sorted(STATES_DIR.glob("*.json")):
        data = load_json(state_file)
        state = data.get("state", state_file.stem.upper())
        benefits = data.get("benefits", [])
        modified = False

        for b in benefits:
            bid = b.get("id", "")

            # 11. All bolsa-atleta-estadual: category "Cultura" → "Esporte"
            if "bolsa-atleta" in bid:
                old_cat = b.get("category")
                if old_cat != "Esporte":
                    b["category"] = "Esporte"
                    print(f"  ✓ {bid}: category '{old_cat}' → 'Esporte'")
                    stats["state_fixes"] += 1
                    modified = True

                # Add disclaimer for unconfirmed states
                if state not in CONFIRMED_BOLSA_ATLETA:
                    b.setdefault("metadata", {})["disclaimer"] = (
                        f"Programa de bolsa atleta estadual em {state} não confirmado. "
                        "Verifique junto à secretaria de esportes do estado."
                    )
                    b.setdefault("metadata", {})["verified"] = False
                    modified = True

        if modified:
            save_json(state_file, data)

    print(f"  → {stats['state_fixes']} state bolsa-atleta category fixes")


# ─────────────────────────────────────────────────────
# MUNICIPAL FIXES — Revert SC and RN fake programs
# ─────────────────────────────────────────────────────

SC_CITIES_WITH_FAKE = [
    "4203204", "4218707", "4202008", "4209300",
    "4208906", "4211900", "4208203", "4216602", "4202404",
]

RN_CITIES_WITH_FAKE = [
    "2412005", "2403251",
]

FAKE_IDS_SC = "renda-extra-sc"
FAKE_IDS_RN = "rn-mais-justo"


def build_template_cesta_basica(ibge: str, city_name: str, state: str) -> dict:
    """Build a generic template Cesta Básica benefit to replace fabricated ones."""
    slug = city_name.lower().replace(" ", "").replace("'", "").replace("-", "")
    return {
        "id": f"{state.lower()}-{slug}-cesta-basica",
        "name": "Programa de Segurança Alimentar",
        "shortDescription": (
            f"Cesta básica ou vale-alimentação para famílias em vulnerabilidade "
            f"em {city_name}. Procure o CRAS para saber os programas disponíveis."
        ),
        "scope": "municipal",
        "state": state,
        "municipalityIbge": ibge,
        "estimatedValue": {
            "type": "monthly",
            "min": 0,
            "max": 200,
            "description": "Valor varia conforme programa municipal/estadual"
        },
        "eligibilityRules": [
            {
                "field": "municipioIbge",
                "operator": "eq",
                "value": ibge,
                "description": f"Morar em {city_name}"
            },
            {
                "field": "cadastradoCadunico",
                "operator": "eq",
                "value": True,
                "description": "Estar no CadÚnico"
            },
            {
                "field": "rendaPerCapita",
                "operator": "lte",
                "value": MEIO_SM,
                "description": "Renda por pessoa até meio salário mínimo"
            }
        ],
        "whereToApply": f"CRAS de {city_name}",
        "documentsRequired": [
            "CPF", "RG", "NIS", "Comprovante de residência"
        ],
        "howToApply": [
            f"Procure o CRAS de {city_name}",
            "Informe-se sobre programas de segurança alimentar disponíveis",
            "Apresente documentos e solicite inclusão"
        ],
        "sourceUrl": f"https://www.gov.br/mds/pt-br/acoes-e-programas",
        "lastUpdated": "2026-02-07",
        "status": "active",
        "icon": "🛒",
        "category": "Alimentação",
        "verified": False,
        "templateGenerated": True,
        "metadata": {
            "template": True,
            "disclaimer": (
                f"Não identificamos programa estadual de transferência de renda "
                f"confirmado em {state}. Procure o CRAS local para conhecer "
                "os programas sociais disponíveis na sua cidade e estado."
            )
        }
    }


def fix_municipal():
    print("\n═══ MUNICIPAL FIXES ═══")

    all_cities = [
        (ibge, FAKE_IDS_SC, "SC") for ibge in SC_CITIES_WITH_FAKE
    ] + [
        (ibge, FAKE_IDS_RN, "RN") for ibge in RN_CITIES_WITH_FAKE
    ]

    for ibge, fake_id_part, state in all_cities:
        city_file = MUNI_DIR / f"{ibge}.json"
        if not city_file.exists():
            stats["errors"].append(f"City file not found: {city_file}")
            continue

        data = load_json(city_file)
        city_name = data.get("municipality", "")
        benefits = data.get("benefits", [])

        # Find and replace the fake benefit
        replaced = False
        for i, b in enumerate(benefits):
            bid = b.get("id", "")
            if fake_id_part in bid:
                replacement = build_template_cesta_basica(ibge, city_name, state)
                benefits[i] = replacement
                replaced = True
                print(f"  ✓ {ibge} ({city_name}): replaced '{bid}' → template")
                stats["municipal_fixes"] += 1
                break

        if not replaced:
            print(f"  ⚠ {ibge} ({city_name}): fake benefit not found, skipping")

        data["benefits"] = benefits
        save_json(city_file, data)

    print(f"  → {stats['municipal_fixes']} municipal replacements")


# ─────────────────────────────────────────────────────
# BARREL REGENERATION
# ─────────────────────────────────────────────────────
def regenerate_barrels():
    """Regenerate by-state barrel files for affected states."""
    print("\n═══ REGENERATING BARRELS ═══")
    affected_states = {"SC", "RN"}

    for state in sorted(affected_states):
        barrel_file = BARREL_DIR / f"{state}.json"
        if not barrel_file.exists():
            print(f"  ⚠ Barrel not found: {barrel_file}")
            continue

        # Load existing barrel
        barrel = load_json(barrel_file)
        municipalities = barrel.get("municipalities", {})

        # Update from individual city files
        updated = 0
        for ibge in list(municipalities.keys()):
            city_file = MUNI_DIR / f"{ibge}.json"
            if city_file.exists():
                city_data = load_json(city_file)
                municipalities[ibge] = city_data.get("benefits", [])
                updated += 1

        barrel["municipalities"] = municipalities
        # Save barrel as minified (matching original format)
        with open(barrel_file, "w", encoding="utf-8") as f:
            json.dump(barrel, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

        print(f"  ✓ {state}.json: {updated} cities updated")


# ─────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────
def validate():
    print("\n═══ VALIDATION ═══")
    all_ids = set()
    duplicates = []

    # Federal
    fed = load_json(FEDERAL_FILE)
    for b in fed.get("benefits", []):
        bid = b.get("id")
        if bid in all_ids:
            duplicates.append(bid)
        all_ids.add(bid)
    fed_count = len(fed.get("benefits", []))
    fed_active = sum(1 for b in fed.get("benefits", []) if b.get("status") != "discontinued")

    # Check no fabricated IDs remain in sectoral
    sec = load_json(SECTORAL_FILE)
    sec_ids = {b.get("id") for b in sec.get("benefits", [])}
    for rid in SECTORAL_TO_REMOVE:
        if rid in sec_ids:
            stats["errors"].append(f"STILL PRESENT: {rid}")
    for b in sec.get("benefits", []):
        bid = b.get("id")
        if bid in all_ids:
            duplicates.append(bid)
        all_ids.add(bid)
    sec_count = len(sec.get("benefits", []))

    # States
    state_count = 0
    for sf in sorted(STATES_DIR.glob("*.json")):
        sd = load_json(sf)
        for b in sd.get("benefits", []):
            bid = b.get("id")
            if bid in all_ids:
                duplicates.append(bid)
            all_ids.add(bid)
            state_count += 1

    # Check no fake programs in SC/RN municipalities
    for ibge in SC_CITIES_WITH_FAKE + RN_CITIES_WITH_FAKE:
        cf = MUNI_DIR / f"{ibge}.json"
        if cf.exists():
            cd = load_json(cf)
            for b in cd.get("benefits", []):
                bid = b.get("id", "")
                if FAKE_IDS_SC in bid or FAKE_IDS_RN in bid:
                    stats["errors"].append(f"FAKE STILL PRESENT: {bid} in {ibge}")

    # Check bolsa-atleta categories
    wrong_cat = 0
    for sf in STATES_DIR.glob("*.json"):
        sd = load_json(sf)
        for b in sd.get("benefits", []):
            if "bolsa-atleta" in b.get("id", "") and b.get("category") != "Esporte":
                wrong_cat += 1

    print(f"  Federal: {fed_count} total ({fed_active} active)")
    print(f"  Sectoral: {sec_count}")
    print(f"  State: {state_count}")
    print(f"  Duplicates: {len(duplicates)}")
    print(f"  Wrong bolsa-atleta categories: {wrong_cat}")
    print(f"  Errors: {len(stats['errors'])}")

    if duplicates:
        print(f"  ⚠ DUPLICATES: {duplicates[:10]}")
    if stats["errors"]:
        for e in stats["errors"]:
            print(f"  ❌ {e}")

    return len(stats["errors"]) == 0 and len(duplicates) == 0 and wrong_cat == 0


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────
def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 DRY RUN — no files will be modified")
        # Just validate current state
        validate()
        return

    print("🔧 Applying audit corrections...")

    fix_federal()
    fix_sectoral()
    fix_states()
    fix_municipal()
    regenerate_barrels()

    ok = validate()

    print("\n═══ SUMMARY ═══")
    print(f"  Federal fixes:     {stats['federal_fixes']}")
    print(f"  Sectoral removed:  {stats['sectoral_removed']}")
    print(f"  Sectoral updated:  {stats['sectoral_updated']}")
    print(f"  State fixes:       {stats['state_fixes']}")
    print(f"  Municipal fixes:   {stats['municipal_fixes']}")
    print(f"  Errors:            {len(stats['errors'])}")

    if ok:
        print("\n✅ All corrections applied successfully!")
    else:
        print("\n❌ Some issues remain — check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()

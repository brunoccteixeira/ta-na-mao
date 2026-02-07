#!/usr/bin/env python3
"""
Master Municipal Benefits Generator v2
Generates benefits for all 5,570 Brazilian municipalities.

Usage:
  python3 scripts/generate_all_municipalities.py --tier 1          # Generate tier 1 (200k+)
  python3 scripts/generate_all_municipalities.py --tier 2          # Generate tier 2 (100k-200k)
  python3 scripts/generate_all_municipalities.py --state SP        # Generate all for state
  python3 scripts/generate_all_municipalities.py --validate-only   # Validate existing
  python3 scripts/generate_all_municipalities.py --catalog-only    # Regenerate catalog.ts
  python3 scripts/generate_all_municipalities.py --stats           # Show statistics
  python3 scripts/generate_all_municipalities.py --generate-all    # Generate all missing (use with --tier)

Flags:
  --skip-existing    Don't overwrite existing city files (default: True)
  --dry-run          Show what would be generated without writing files
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
BENEFITS_DIR = FRONTEND_DIR / "src" / "data" / "benefits" / "municipalities"
CATALOG_PATH = FRONTEND_DIR / "src" / "engine" / "catalog.ts"
IBGE_DATA_PATH = SCRIPT_DIR / "data" / "ibge_population_lookup.json"
IBGE_FULL_PATH = SCRIPT_DIR / "data" / "ibge_municipalities_raw.json"

# Constants
SM_2026 = 1621
MEIO_SM = 810.50
EXTREMA_POBREZA = 218
DATE_UPDATED = "2026-02-07"

# =============================================================================
# SLUG & NAME UTILITIES
# =============================================================================

def slugify(name: str) -> str:
    """Convert city name to slug (remove accents, lowercase, remove spaces/hyphens)."""
    # Normalize unicode (NFD decomposition)
    nfkd = unicodedata.normalize('NFKD', name)
    # Remove diacritics
    ascii_text = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Lowercase, remove non-alphanumeric
    slug = re.sub(r'[^a-z0-9]', '', ascii_text.lower())
    return slug


# =============================================================================
# RESTAURANT NAMES BY STATE (audited in Phases M3-M4)
# =============================================================================

RESTAURANTE_NAMES: dict[str, dict[str, str]] = {
    "SP": {"name": "Bom Prato", "price": "R$ 1 (café R$ 0,50)"},
    "RJ": {"name": "Restaurante Popular Carioca", "price": "R$ 2"},
    "MG": {"name": "Restaurante Popular", "price": "R$ 2"},
    "BA": {"name": "Restaurante Popular", "price": "gratuita"},
    "CE": {"name": "Restaurante do Povo", "price": "R$ 1"},
    "PE": {"name": "Restaurante Popular", "price": "R$ 1"},
    "RS": {"name": "Restaurante Popular", "price": "R$ 1"},
    "PR": {"name": "Restaurante Popular", "price": "R$ 1"},
    "PA": {"name": "Restaurante Popular", "price": "R$ 1"},
    "AM": {"name": "Prato Cheio", "price": "R$ 1"},
    "GO": {"name": "Restaurante do Bem", "price": "R$ 2"},
    "DF": {"name": "Restaurante Comunitário", "price": "R$ 1"},
    "SC": {"name": "Restaurante Popular", "price": "R$ 2"},
    "ES": {"name": "Restaurante Popular", "price": "R$ 1"},
    "MT": {"name": "Restaurante Popular", "price": "R$ 2"},
    "MS": {"name": "Restaurante Popular", "price": "R$ 2"},
    "MA": {"name": "Restaurante Popular SEDES", "price": "R$ 1"},
    "SE": {"name": "Padre Pedro", "price": "R$ 1"},
    "RO": {"name": "Prato Fácil", "price": "R$ 2"},
    # States without known restaurant program: use generic
    "AC": {"name": "Restaurante Popular", "price": "R$ 2"},
    "AL": {"name": "Restaurante Popular", "price": "R$ 2"},
    "AP": {"name": "Restaurante Popular", "price": "R$ 2"},
    "PI": {"name": "Restaurante Popular", "price": "R$ 2"},
    "RN": {"name": "Restaurante Popular", "price": "R$ 2"},
    "PB": {"name": "Restaurante Popular", "price": "R$ 2"},
    "RR": {"name": "Restaurante Popular", "price": "R$ 2"},
    "TO": {"name": "Restaurante Popular", "price": "R$ 2"},
}


# =============================================================================
# IBGE DATA LOADING
# =============================================================================

def load_ibge_data() -> dict[str, dict]:
    """Load IBGE municipality data with population."""
    if not IBGE_DATA_PATH.exists():
        print(f"ERROR: {IBGE_DATA_PATH} not found. Run the IBGE data download first.")
        sys.exit(1)

    with open(IBGE_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ibge_full() -> list[dict]:
    """Load full IBGE municipality list (for state extraction)."""
    if not IBGE_FULL_PATH.exists():
        print(f"ERROR: {IBGE_FULL_PATH} not found.")
        sys.exit(1)

    with open(IBGE_FULL_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_state_from_ibge(ibge_code: str, ibge_data: dict) -> str:
    """Get 2-letter state code from IBGE data."""
    entry = ibge_data.get(ibge_code)
    if entry:
        return entry.get("uf", "")
    return ""


def get_municipality_name(ibge_code: str, ibge_data: dict) -> str:
    """Get municipality name from IBGE data."""
    entry = ibge_data.get(ibge_code)
    if entry:
        return entry.get("nome", "")
    return ""


def get_population(ibge_code: str, ibge_data: dict) -> int:
    """Get population from IBGE data."""
    entry = ibge_data.get(ibge_code)
    if entry:
        pop = entry.get("populacao_2022", 0)
        return int(pop) if pop else 0
    return 0


def get_tier(population: int) -> int:
    """Determine tier based on population."""
    if population >= 200_000:
        return 1
    elif population >= 100_000:
        return 2
    elif population >= 50_000:
        return 3
    elif population >= 20_000:
        return 4
    else:
        return 5


# =============================================================================
# BENEFIT GENERATION
# =============================================================================

def make_benefit(
    ibge: str, state: str, slug: str, city_name: str,
    program_id: str, name: str, short_desc: str,
    value_type: str, value_min: float, value_max: float, value_desc: str,
    rules: list[dict], where: str, docs: list[str], how: list[str],
    source_url: str, icon: str, category: str,
    metadata: dict | None = None,
) -> dict[str, Any]:
    """Create a single benefit entry."""
    base_rules = [
        {
            "field": "municipioIbge",
            "operator": "eq",
            "value": ibge,
            "description": f"Morar em {city_name}"
        }
    ]
    benefit = {
        "id": f"{state.lower()}-{slug}-{program_id}",
        "name": name,
        "shortDescription": short_desc,
        "scope": "municipal",
        "state": state,
        "municipalityIbge": ibge,
        "estimatedValue": {
            "type": value_type,
            "min": value_min,
            "max": value_max,
            "description": value_desc
        },
        "eligibilityRules": base_rules + rules,
        "whereToApply": where,
        "documentsRequired": docs,
        "howToApply": how,
        "sourceUrl": source_url,
        "lastUpdated": DATE_UPDATED,
        "status": "active",
        "icon": icon,
        "category": category
    }
    if metadata:
        benefit["metadata"] = metadata
    return benefit


def get_city_url(slug: str, state: str) -> str:
    """Generate city government URL."""
    # Known special URLs for major cities
    SPECIAL_URLS: dict[str, str] = {
        "saopaulo": "https://www.prefeitura.sp.gov.br",
        "riodejaneiro": "https://prefeitura.rio",
        "belohorizonte": "https://prefeitura.pbh.gov.br",
        "curitiba": "https://www.curitiba.pr.gov.br",
        "portoalegre": "https://prefeitura.poa.br",
        "salvador": "https://www.salvador.ba.gov.br",
        "fortaleza": "https://www.fortaleza.ce.gov.br",
        "recife": "https://www2.recife.pe.gov.br",
        "brasilia": "https://www.df.gov.br",
        "manaus": "https://www.manaus.am.gov.br",
        "belem": "https://www.belem.pa.gov.br",
        "goiania": "https://www.goiania.go.gov.br",
        "natal": "https://www.natal.rn.gov.br",
        "teresina": "https://www.teresina.pi.gov.br",
        "saoluis": "https://www.saoluis.ma.gov.br",
        "joaopessoa": "https://www.joaopessoa.pb.gov.br",
        "maceio": "https://www.maceio.al.gov.br",
        "aracaju": "https://www.aracaju.se.gov.br",
        "campogrande": "https://www.campogrande.ms.gov.br",
        "cuiaba": "https://www.cuiaba.mt.gov.br",
        "macapa": "https://www.macapa.ap.gov.br",
        "portovelho": "https://www.portovelho.ro.gov.br",
        "florianopolis": "https://www.pmf.sc.gov.br",
        "vitoria": "https://www.vitoria.es.gov.br",
        "riobranco": "https://www.riobranco.ac.gov.br",
        "boavista": "https://www.boavista.rr.gov.br",
        "palmas": "https://www.palmas.to.gov.br",
    }
    if slug in SPECIAL_URLS:
        return SPECIAL_URLS[slug]
    return f"https://www.{slug}.{state.lower()}.gov.br"


def generate_7_benefits(ibge: str, city_name: str, state: str, slug: str, population: int) -> list[dict]:
    """Generate 7 universal municipal benefits for a city."""
    url = get_city_url(slug, state)
    benefits = []
    tier = get_tier(population)

    # For small cities (<20k), add disclaimer
    disclaimer = ""
    if tier == 5:
        disclaimer = " Verifique disponibilidade na prefeitura."
    elif tier == 4:
        disclaimer = " Verifique disponibilidade na prefeitura."

    # 1. RESTAURANTE POPULAR / ALIMENTAÇÃO
    rest_info = RESTAURANTE_NAMES.get(state, {"name": "Restaurante Popular", "price": "R$ 2"})
    rest_name = rest_info["name"]
    rest_price = rest_info["price"]

    # Small cities unlikely to have restaurant program
    if tier >= 4:
        benefits.append(make_benefit(
            ibge, state, slug, city_name,
            "restaurante-popular", rest_name,
            f"Refeições a preço popular em {city_name}. Programa estadual — verifique se há unidade no município.",
            "monthly", 0, 0, f"Refeição por {rest_price}",
            [],
            f"Prefeitura de {city_name} ou CRAS",
            [],
            [f"Verifique se há {rest_name} no município", "Não precisa de cadastro prévio"],
            url, "🍽️", "Alimentação",
            {"template": True, "disclaimer": f"Nem todos os municípios possuem unidade de {rest_name}."}
        ))
    else:
        benefits.append(make_benefit(
            ibge, state, slug, city_name,
            "restaurante-popular", rest_name,
            f"Refeições a {rest_price} em restaurantes populares de {city_name}",
            "monthly", 0, 0, f"Refeição por {rest_price}",
            [],
            f"Restaurantes Populares de {city_name}",
            [],
            [f"Vá a qualquer {rest_name} da cidade", "Não precisa de cadastro"],
            url, "🍽️", "Alimentação"
        ))

    # 2. TRANSPORTE SOCIAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "transporte-social", "Transporte Social",
        f"Meia-passagem ou gratuidade no transporte para baixa renda em {city_name}.{disclaimer}",
        "monthly", 0, 0, "Desconto de 50% a 100% na tarifa",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "rendaPerCapita", "operator": "lte", "value": MEIO_SM, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"Terminal de ônibus ou secretaria de transporte de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência", "Foto 3x4"],
        ["Procure o terminal de ônibus ou CRAS", "Apresente documentos", "Aguarde emissão do cartão"],
        url, "🚌", "Transporte",
        {"template": True} if tier >= 4 else None
    ))

    # 3. IPTU SOCIAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "iptu-social", "IPTU Social",
        f"Isenção ou desconto no IPTU para famílias de baixa renda em {city_name}.{disclaimer}",
        "annual", 0, 2000, "Isenção de até 100% do IPTU",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "temCasaPropria", "operator": "eq", "value": True, "description": "Ter imóvel próprio"},
            {"field": "rendaPerCapita", "operator": "lte", "value": MEIO_SM, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"Secretaria da Fazenda de {city_name} ou site da prefeitura",
        ["CPF", "RG", "Comprovante de residência", "Carnê do IPTU", "NIS"],
        ["Acesse o site da prefeitura", "Solicite isenção no período de cadastro", "Aguarde análise"],
        url, "🏠", "Moradia",
        {"template": True} if tier >= 4 else None
    ))

    # 4. HABITAÇÃO MUNICIPAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "habitacao-municipal", f"Programa Habitacional de {city_name}",
        f"Moradia popular ou aluguel social para famílias em vulnerabilidade em {city_name}.{disclaimer}",
        "monthly", 300, 600, "Aluguel social de R$ 300 a R$ 600",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
            {"field": "rendaPerCapita", "operator": "lte", "value": MEIO_SM, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"CRAS ou Secretaria de Habitação de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência", "Comprovante de renda"],
        ["Procure o CRAS do seu bairro", "Solicite inclusão no programa habitacional", "Aguarde avaliação social"],
        url, "🏡", "Moradia",
        {"template": True} if tier >= 4 else None
    ))

    # 5. CAPACITAÇÃO / EMPREGO
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "capacitacao-emprego", f"Qualifica {city_name}",
        f"Cursos gratuitos de qualificação profissional com bolsa-auxílio em {city_name}.{disclaimer}",
        "monthly", 200, 500, "Bolsa de R$ 200 a R$ 500 durante o curso",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "idade", "operator": "gte", "value": 16, "description": "Ter pelo menos 16 anos"},
            {"field": "rendaPerCapita", "operator": "lte", "value": MEIO_SM, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"CRAS, SINE ou Secretaria de Trabalho de {city_name}",
        ["CPF", "RG", "Comprovante de residência", "Comprovante de escolaridade"],
        ["Acesse o site da prefeitura ou procure o SINE", "Inscreva-se nos cursos disponíveis", "Aguarde início das turmas"],
        url, "📚", "Qualificação Profissional",
        {"template": True} if tier >= 4 else None
    ))

    # 6. SAÚDE / FARMÁCIA MUNICIPAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "farmacia-municipal", "Farmácia Municipal",
        f"Medicamentos gratuitos nas farmácias municipais e UBS de {city_name}",
        "monthly", 0, 0, "Medicamentos gratuitos",
        [],
        f"UBS ou Farmácia Municipal de {city_name}",
        ["CPF", "Cartão SUS", "Receita médica do SUS"],
        ["Vá à UBS ou Farmácia Municipal", "Apresente receita médica", "Retire os medicamentos disponíveis"],
        url, "💊", "Saúde"
    ))

    # 7. PROGRAMA LOCAL — Cesta Básica (default for template cities)
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "cesta-basica", "Cesta Básica Municipal",
        f"Cesta básica para famílias em vulnerabilidade social de {city_name}",
        "monthly", 0, 0, "Cesta básica mensal",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "rendaPerCapita", "operator": "lte", "value": EXTREMA_POBREZA, "description": "Renda por pessoa até R$ 218"}
        ],
        f"CRAS de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência"],
        ["Procure o CRAS do seu bairro", "Solicite a cesta básica", "Aguarde avaliação social"],
        url, "🧺", "Alimentação",
        {"template": True} if tier >= 3 else None
    ))

    return benefits


def create_city_json(ibge: str, city_name: str, state: str, population: int) -> dict:
    """Create the full JSON structure for a city."""
    slug = slugify(city_name)
    benefits = generate_7_benefits(ibge, city_name, state, slug, population)

    return {
        "municipality": city_name,
        "municipalityIbge": ibge,
        "state": state,
        "lastUpdated": DATE_UPDATED,
        "benefits": benefits
    }


# =============================================================================
# ID COLLISION DETECTION
# =============================================================================

def check_slug_collisions(
    municipalities: list[tuple[str, str, str, int]],
    existing_slugs: set[str] | None = None,
) -> dict[str, list]:
    """Check for slug collisions (e.g., multiple 'São José' in same state).
    Also checks against existing cities' slugs to avoid ID conflicts.
    """
    slug_map: dict[str, list] = {}

    # Add existing slugs first (so new cities will detect conflicts)
    if existing_slugs:
        for key in existing_slugs:
            slug_map[key] = [("existing", "existing", "")]

    for ibge, name, state, pop in municipalities:
        slug = slugify(name)
        key = f"{state.lower()}-{slug}"
        if key not in slug_map:
            slug_map[key] = []
        slug_map[key].append((ibge, name, state))

    # Return only collisions
    return {k: v for k, v in slug_map.items() if len(v) > 1}


def resolve_slug(ibge: str, name: str, state: str, collisions: dict[str, list]) -> str:
    """Resolve slug collision by appending IBGE code suffix."""
    slug = slugify(name)
    key = f"{state.lower()}-{slug}"
    if key in collisions:
        # Append last 4 digits of IBGE code to disambiguate
        return f"{slug}{ibge[-4:]}"
    return slug


# =============================================================================
# CATALOG.TS GENERATION
# =============================================================================

def generate_state_barrel_files():
    """Generate per-state barrel JSON files that consolidate all municipalities for each state."""
    barrel_dir = BENEFITS_DIR / "by-state"
    barrel_dir.mkdir(exist_ok=True)

    # Group municipalities by state
    state_municipalities: dict[str, dict[str, list]] = {}

    for filepath in sorted(BENEFITS_DIR.glob("*.json")):
        if filepath.parent.name != "municipalities":
            continue  # Skip by-state subdirectory
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state = data.get("state", "")
            ibge = filepath.stem
            benefits = data.get("benefits", [])
            if state:
                if state not in state_municipalities:
                    state_municipalities[state] = {}
                state_municipalities[state][ibge] = benefits
        except (json.JSONDecodeError, KeyError):
            continue

    # Write barrel files
    total_municipalities = 0
    for state, municipalities in sorted(state_municipalities.items()):
        barrel_path = barrel_dir / f"{state}.json"
        barrel_data = {"municipalities": municipalities}
        with open(barrel_path, 'w', encoding='utf-8') as f:
            json.dump(barrel_data, f, ensure_ascii=False, separators=(',', ':'))
        total_municipalities += len(municipalities)
        size_kb = barrel_path.stat().st_size / 1024
        print(f"  {state}: {len(municipalities)} municipalities ({size_kb:.0f} KB)")

    print(f"\n  Total: {total_municipalities} municipalities across {len(state_municipalities)} states")
    return state_municipalities


def generate_catalog_ts():
    """Regenerate catalog.ts using per-state barrel imports (27 imports instead of 5573)."""
    # First generate barrel files
    print("Generating per-state barrel files...")
    state_municipalities = generate_state_barrel_files()
    states_with_municipal = sorted(state_municipalities.keys())

    print(f"\nGenerating catalog.ts with {len(states_with_municipal)} state barrel imports...")

    # Read the existing catalog.ts to preserve the non-municipal parts
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        existing_content = f.read()

    # Extract the header (imports + state modules - everything before municipal imports)
    mun_import_start = existing_content.find("// Import municipal benefits")
    if mun_import_start == -1:
        print("ERROR: Could not find '// Import municipal benefits' marker in catalog.ts")
        return False

    mun_modules_end = existing_content.find("/**\n * Load all benefits from the catalog")
    if mun_modules_end == -1:
        print("ERROR: Could not find catalog function marker in catalog.ts")
        return False

    header = existing_content[:mun_import_start]
    footer = existing_content[mun_modules_end:]

    # Generate state-barrel imports (27 imports instead of 5573)
    imports_lines = [
        f"// Import municipal benefits by state — {sum(len(v) for v in state_municipalities.values())} municipalities (auto-generated)",
        "// Using per-state barrel files to avoid TypeScript OOM with individual imports",
    ]
    for state in states_with_municipal:
        imports_lines.append(
            f"import munState{state} from '../data/benefits/municipalities/by-state/{state}.json';"
        )

    # Generate the municipalModules record from barrel files
    modules_lines = [
        "",
        "// Build municipalModules from state barrels",
        "type MunicipalBarrel = { municipalities: Record<string, Benefit[]> };",
        "const municipalModules: Record<string, Benefit[]> = {};",
        "",
    ]

    for state in states_with_municipal:
        modules_lines.append(
            f"for (const [ibge, benefits] of Object.entries((munState{state} as unknown as MunicipalBarrel).municipalities)) {{"
        )
        modules_lines.append(f"  municipalModules[ibge] = benefits;")
        modules_lines.append("}")

    modules_lines.append("")

    # Combine
    new_content = header + "\n".join(imports_lines) + "\n" + "\n".join(modules_lines) + "\n" + footer

    # Update the loadBenefitsCatalog function to use the new flat map
    # The old code iterates municipalModules as Record<string, { benefits: Benefit[] }>
    # The new code uses Record<string, Benefit[]> directly
    new_content = new_content.replace(
        "  for (const [ibgeCode, municipalData] of Object.entries(municipalModules)) {\n"
        "    municipal[ibgeCode] = municipalData.benefits || [];\n"
        "  }",
        "  for (const [ibgeCode, benefits] of Object.entries(municipalModules)) {\n"
        "    municipal[ibgeCode] = benefits || [];\n"
        "  }"
    )

    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    total_mun = sum(len(v) for v in state_municipalities.values())
    print(f"  catalog.ts regenerated: {len(states_with_municipal)} state barrel imports ({total_mun} municipalities)")
    return True


# =============================================================================
# VALIDATION
# =============================================================================

def validate_all() -> bool:
    """Validate all municipal JSON files."""
    all_ids: set[str] = set()
    errors: list[str] = []
    warnings: list[str] = []
    total_benefits = 0
    total_cities = 0
    template_count = 0

    for filepath in sorted(BENEFITS_DIR.glob("*.json")):
        total_cities += 1
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error in {filepath.name}: {e}")
            continue

        ibge = filepath.stem
        benefits = data.get("benefits", [])
        total_benefits += len(benefits)

        # Validate IBGE consistency
        if data.get("municipalityIbge") != ibge:
            errors.append(f"{filepath.name}: municipalityIbge mismatch ({data.get('municipalityIbge')} vs {ibge})")

        for b in benefits:
            # Check duplicate IDs
            if b["id"] in all_ids:
                errors.append(f"{filepath.name}: duplicate ID '{b['id']}'")
            all_ids.add(b["id"])

            # Count templates
            if b.get("metadata", {}).get("template"):
                template_count += 1

            # Check required fields
            for field in ["id", "name", "shortDescription", "scope", "state", "municipalityIbge",
                         "eligibilityRules", "whereToApply", "documentsRequired", "lastUpdated", "status"]:
                if field not in b:
                    errors.append(f"{filepath.name}: benefit '{b.get('id', '?')}' missing field '{field}'")

            # Check IBGE match
            if b.get("municipalityIbge") != ibge:
                errors.append(f"{filepath.name}: benefit '{b['id']}' has wrong IBGE ({b.get('municipalityIbge')})")

            # Check first eligibility rule
            if b.get("eligibilityRules") and b["eligibilityRules"][0].get("field") != "municipioIbge":
                errors.append(f"{filepath.name}: benefit '{b['id']}' first rule is not municipioIbge")

    print(f"\n{'='*60}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Total cities:      {total_cities}")
    print(f"Total benefits:    {total_benefits}")
    print(f"Unique IDs:        {len(all_ids)}")
    print(f"Template benefits: {template_count}")
    print(f"Errors:            {len(errors)}")

    if errors:
        print(f"\nERRORS:")
        for e in errors[:50]:  # Limit output
            print(f"  {e}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
    else:
        print(f"\nAll validations passed!")

    return len(errors) == 0


# =============================================================================
# STATISTICS
# =============================================================================

def show_stats():
    """Show statistics about current coverage vs total."""
    ibge_data = load_ibge_data()
    existing = {f.stem for f in BENEFITS_DIR.glob("*.json")}

    total = len(ibge_data)
    covered = len(existing)
    missing = total - covered

    # Tier breakdown
    tier_total = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    tier_covered = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    # State breakdown
    state_total: dict[str, int] = {}
    state_covered: dict[str, int] = {}

    for ibge_code, info in ibge_data.items():
        pop = int(info.get("populacao_2022", 0) or 0)
        tier = get_tier(pop)
        state = info.get("uf", "??")

        tier_total[tier] += 1
        state_total[state] = state_total.get(state, 0) + 1

        if ibge_code in existing:
            tier_covered[tier] += 1
            state_covered[state] = state_covered.get(state, 0) + 1

    print(f"\n{'='*60}")
    print(f"COVERAGE STATISTICS")
    print(f"{'='*60}")
    print(f"Total municipalities (IBGE): {total}")
    print(f"Currently covered:           {covered} ({covered*100/total:.1f}%)")
    print(f"Missing:                     {missing}")
    print()

    print(f"{'Tier':<8} {'Pop Range':<20} {'Total':<8} {'Covered':<10} {'Missing':<10} {'%':<6}")
    print("-" * 60)
    tier_labels = {
        1: "200k+",
        2: "100k-200k",
        3: "50k-100k",
        4: "20k-50k",
        5: "<20k"
    }
    for tier in range(1, 6):
        t = tier_total[tier]
        c = tier_covered[tier]
        m = t - c
        pct = c*100/t if t > 0 else 0
        print(f"Tier {tier}  {tier_labels[tier]:<20} {t:<8} {c:<10} {m:<10} {pct:.0f}%")

    print()
    print(f"{'State':<6} {'Total':<8} {'Covered':<10} {'Missing':<10} {'%':<6}")
    print("-" * 45)
    for state in sorted(state_total.keys()):
        t = state_total[state]
        c = state_covered.get(state, 0)
        m = t - c
        pct = c*100/t if t > 0 else 0
        print(f"{state:<6} {t:<8} {c:<10} {m:<10} {pct:.0f}%")


# =============================================================================
# GENERATION
# =============================================================================

def generate_municipalities(
    tier: int | None = None,
    state: str | None = None,
    skip_existing: bool = True,
    dry_run: bool = False,
    limit: int | None = None,
) -> int:
    """Generate municipal benefit files."""
    ibge_data = load_ibge_data()
    existing = {f.stem for f in BENEFITS_DIR.glob("*.json")}

    # Build list of municipalities to generate
    to_generate: list[tuple[str, str, str, int]] = []  # (ibge, name, state, pop)

    for ibge_code, info in ibge_data.items():
        name = info.get("nome", "")
        uf = info.get("uf", "")
        pop = int(info.get("populacao_2022", 0) or 0)

        # Skip existing if requested
        if skip_existing and ibge_code in existing:
            continue

        # Filter by tier
        if tier is not None and get_tier(pop) != tier:
            continue

        # Filter by state
        if state is not None and uf != state.upper():
            continue

        to_generate.append((ibge_code, name, uf, pop))

    # Sort by population (descending) for predictable order
    to_generate.sort(key=lambda x: x[3], reverse=True)

    if limit:
        to_generate = to_generate[:limit]

    if not to_generate:
        print("No municipalities to generate (all covered or no matches).")
        return 0

    # Build existing slugs set from existing JSON files to avoid ID collisions
    existing_slugs: set[str] = set()
    for filepath in BENEFITS_DIR.glob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for b in data.get("benefits", []):
                bid = b.get("id", "")
                # Extract state-slug prefix from ID like "sc-saojose-restaurante-popular"
                parts = bid.split("-")
                if len(parts) >= 3:
                    st = parts[0]
                    # The slug is between the state and program_id. Find it by
                    # removing the known program suffixes
                    program_ids = ["restaurante-popular", "transporte-social",
                                   "iptu-social", "habitacao-municipal",
                                   "capacitacao-emprego", "farmacia-municipal",
                                   "cesta-basica"]
                    for pid in program_ids:
                        if bid.endswith(f"-{pid}"):
                            slug_part = bid[len(st)+1:-(len(pid)+1)]
                            existing_slugs.add(f"{st}-{slug_part}")
                            break
        except (json.JSONDecodeError, KeyError):
            continue

    # Check for slug collisions (including existing cities)
    collisions = check_slug_collisions(to_generate, existing_slugs)
    if collisions:
        print(f"Found {len(collisions)} slug collisions, will append IBGE suffix:")
        for key, cities in list(collisions.items())[:10]:
            names = [f"{c[1]} ({c[0]})" for c in cities]
            print(f"  {key}: {', '.join(names)}")

    print(f"\nGenerating {len(to_generate)} municipalities" +
          (f" (tier {tier})" if tier else "") +
          (f" (state {state})" if state else "") +
          (" [DRY RUN]" if dry_run else ""))

    created = 0
    for ibge_code, name, uf, pop in to_generate:
        slug = resolve_slug(ibge_code, name, uf, collisions)
        filepath = BENEFITS_DIR / f"{ibge_code}.json"

        if dry_run:
            print(f"  [DRY] {name} ({uf}, {ibge_code}, pop={pop:,}, tier={get_tier(pop)}, slug={slug})")
            created += 1
            continue

        data = create_city_json(ibge_code, name, uf, pop)
        # Override slug in all benefit IDs if collision was resolved
        if resolve_slug(ibge_code, name, uf, collisions) != slugify(name):
            for b in data["benefits"]:
                old_slug = slugify(name)
                new_slug = slug
                b["id"] = b["id"].replace(f"-{old_slug}-", f"-{new_slug}-")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        created += 1
        if created % 100 == 0:
            print(f"  ... {created}/{len(to_generate)} created")

    print(f"\nCreated: {created} municipal JSON files")
    return created


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Master Municipal Benefits Generator v2")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5],
                       help="Generate only municipalities in this tier")
    parser.add_argument("--state", type=str,
                       help="Generate only municipalities in this state (e.g., SP, RJ)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                       help="Don't overwrite existing city files (default)")
    parser.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing city files")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate existing files")
    parser.add_argument("--catalog-only", action="store_true",
                       help="Only regenerate catalog.ts")
    parser.add_argument("--stats", action="store_true",
                       help="Show coverage statistics")
    parser.add_argument("--generate-all", action="store_true",
                       help="Generate all missing municipalities (use with --tier)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be generated without writing files")
    parser.add_argument("--limit", type=int,
                       help="Limit number of municipalities to generate")

    args = parser.parse_args()

    if args.validate_only:
        success = validate_all()
        sys.exit(0 if success else 1)

    if args.catalog_only:
        success = generate_catalog_ts()
        sys.exit(0 if success else 1)

    if args.stats:
        show_stats()
        sys.exit(0)

    if args.generate_all or args.tier or args.state:
        skip = not args.overwrite
        created = generate_municipalities(
            tier=args.tier,
            state=args.state,
            skip_existing=skip,
            dry_run=args.dry_run,
            limit=args.limit,
        )

        if created > 0 and not args.dry_run:
            print("\nValidating...")
            validate_all()

            print("\nRegenerating catalog.ts...")
            generate_catalog_ts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

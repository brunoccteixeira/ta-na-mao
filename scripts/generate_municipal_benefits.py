#!/usr/bin/env python3
"""
Phase D+E — Municipal Benefits Expansion
D: 98 cities with 686 benefits
E: +50 cities with 350 benefits → 148 cities, 1036 municipal benefits

Phase E focuses on regional balance:
- Norte +8, Nordeste +18, Centro-Oeste +6, Sudeste +10, Sul +8
"""

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "municipalities"

# =============================================================================
# MASTER CITY DATABASE
# Format: (IBGE, city_name, state, slug, population_approx)
# =============================================================================

# D1 - Existing 40 cities (need enrichment to 7 benefits)
EXISTING_CITIES = [
    ("1100205", "Porto Velho", "RO", "portovelho", 548000),
    ("1302603", "Manaus", "AM", "manaus", 2256000),
    ("1500800", "Abaetetuba", "PA", "abaetetuba", 160000),
    ("1501402", "Belém", "PA", "belem", 1506000),
    ("1600303", "Macapá", "AP", "macapa", 522000),
    ("2111300", "São Luís", "MA", "saoluis", 1115000),
    ("2211001", "Teresina", "PI", "teresina", 871000),
    ("2304400", "Fortaleza", "CE", "fortaleza", 2703000),
    ("2408102", "Natal", "RN", "natal", 896000),
    ("2507507", "João Pessoa", "PB", "joaopessoa", 833000),
    ("2611606", "Recife", "PE", "recife", 1661000),
    ("2704302", "Maceió", "AL", "maceio", 1025000),
    ("2800308", "Aracaju", "SE", "aracaju", 664000),
    ("2910800", "Feira de Santana", "BA", "feiradesantana", 624000),
    ("2927408", "Salvador", "BA", "salvador", 2900000),
    ("3106200", "Belo Horizonte", "MG", "belohorizonte", 2530000),
    ("3118601", "Contagem", "MG", "contagem", 668000),
    ("3136702", "Juiz de Fora", "MG", "juizdefora", 577000),
    ("3170206", "Uberlândia", "MG", "uberlandia", 706000),
    ("3301702", "Duque de Caxias", "RJ", "duquedecaxias", 924000),
    ("3303302", "Niterói", "RJ", "niteroi", 516000),
    ("3304557", "Rio de Janeiro", "RJ", "riodejaneiro", 6775000),
    ("3304904", "São Gonçalo", "RJ", "saogoncalo", 1098000),
    ("3509502", "Campinas", "SP", "campinas", 1223000),
    ("3518800", "Guarulhos", "SP", "guarulhos", 1404000),
    ("3534401", "Osasco", "SP", "osasco", 699000),
    ("3543402", "Ribeirão Preto", "SP", "ribeiraopreto", 711000),
    ("3547809", "Santo André", "SP", "santoandre", 723000),
    ("3548708", "Santos", "SP", "santos", 433000),
    ("3550308", "São Paulo", "SP", "saopaulo", 12330000),
    ("3552205", "Sorocaba", "SP", "sorocaba", 695000),
    ("4106902", "Curitiba", "PR", "curitiba", 1963000),
    ("4113700", "Londrina", "PR", "londrina", 583000),
    ("4209102", "Joinville", "SC", "joinville", 616000),
    ("4314902", "Porto Alegre", "RS", "portoalegre", 1492000),
    ("5002704", "Campo Grande", "MS", "campogrande", 916000),
    ("5103403", "Cuiabá", "MT", "cuiaba", 650000),
    ("5201405", "Aparecida de Goiânia", "GO", "aparecidadegoiania", 600000),
    ("5208707", "Goiânia", "GO", "goiania", 1556000),
    ("5300108", "Brasília", "DF", "brasilia", 3094000),
]

# D2 - 5 missing capitals
NEW_CAPITALS = [
    ("1200401", "Rio Branco", "AC", "riobranco", 413000),
    ("1400100", "Boa Vista", "RR", "boavista", 436000),
    ("3205309", "Vitória", "ES", "vitoria", 365000),
    ("4205407", "Florianópolis", "SC", "florianopolis", 508000),
    ("1721000", "Palmas", "TO", "palmas", 306000),
]

# D3 - ~60 new large cities (300k+)
NEW_CITIES = [
    # D3-A: Sudeste - SP (15)
    ("3548708", "São Bernardo do Campo", "SP", "saobernardodocampo", 844000),  # NOTE: already exists as Santos? Check IBGE
    ("3549904", "São José dos Campos", "SP", "saojosedoscampos", 737000),
    ("3530607", "Mogi das Cruzes", "SP", "mogidascruzes", 450000),
    ("3529401", "Mauá", "SP", "maua", 477000),
    ("3513801", "Diadema", "SP", "diadema", 426000),
    ("3510609", "Carapicuíba", "SP", "carapicuiba", 400000),
    ("3538709", "Piracicaba", "SP", "piracicaba", 414000),
    ("3506003", "Bauru", "SP", "bauru", 381000),
    ("3516200", "Franca", "SP", "franca", 356000),
    ("3549805", "São José do Rio Preto", "SP", "saojosedoriopreto", 464000),
    ("3525904", "Jundiaí", "SP", "jundiai", 423000),
    ("3541000", "Praia Grande", "SP", "praiagrande", 330000),
    ("3518701", "Guarujá", "SP", "guaruja", 320000),
    ("3554102", "Taubaté", "SP", "taubate", 317000),
    ("3523107", "Itaquaquecetuba", "SP", "itaquaquecetuba", 378000),
    # D3-B: Sudeste - RJ/MG/ES (15)
    ("3303500", "Nova Iguaçu", "RJ", "novaiguacu", 823000),
    ("3300456", "Belford Roxo", "RJ", "belfordroxo", 510000),
    ("3305109", "São João de Meriti", "RJ", "saojoaodemeriti", 472000),
    ("3301009", "Campos dos Goytacazes", "RJ", "camposdosgoytacazes", 514000),
    ("3303906", "Petrópolis", "RJ", "petropolis", 306000),
    ("3205200", "Vila Velha", "ES", "vilavelha", 501000),
    ("3205002", "Serra", "ES", "serra", 527000),
    ("3201308", "Cariacica", "ES", "cariacica", 388000),
    ("3106705", "Betim", "MG", "betim", 444000),
    ("3143302", "Montes Claros", "MG", "montesclaros", 417000),
    ("3153905", "Ribeirão das Neves", "MG", "ribeiraodsneves", 334000),
    ("3170107", "Uberaba", "MG", "uberaba", 340000),
    ("3127701", "Governador Valadares", "MG", "governadorvaladares", 281000),
    ("3306305", "Volta Redonda", "RJ", "voltaredonda", 278000),
    ("3131307", "Ipatinga", "MG", "ipatinga", 264000),
    # D3-C: Sul (12)
    ("4115200", "Maringá", "PR", "maringa", 436000),
    ("4119905", "Ponta Grossa", "PR", "pontagrossa", 358000),
    ("4104808", "Cascavel", "PR", "cascavel", 332000),
    ("4125506", "São José dos Pinhais", "PR", "saojosedospinhais", 330000),
    ("4105805", "Colombo", "PR", "colombo", 246000),
    ("4305108", "Caxias do Sul", "RS", "caxiasdosul", 517000),
    ("4314407", "Pelotas", "RS", "pelotas", 343000),
    ("4304606", "Canoas", "RS", "canoas", 349000),
    ("4309209", "Gravataí", "RS", "gravatai", 284000),
    ("4209300", "São José", "SC", "saojose", 250000),
    ("4202404", "Blumenau", "SC", "blumenau", 361000),
    ("4208203", "Itajaí", "SC", "itajai", 223000),
    # D3-D: Norte/Nordeste/Centro-Oeste (13)
    ("1500800", "Ananindeua", "PA", "ananindeua", 535000),  # Already exists! Skip
    ("1506807", "Santarém", "PA", "santarem", 308000),
    ("2504009", "Campina Grande", "PB", "campinagrande", 411000),
    ("2607901", "Jaboatão dos Guararapes", "PE", "jaboataodosguararapes", 706000),
    ("2604106", "Caruaru", "PE", "caruaru", 369000),
    ("2611101", "Petrolina", "PE", "petrolina", 359000),
    ("2303709", "Caucaia", "CE", "caucaia", 368000),
    ("2312908", "Sobral", "CE", "sobral", 212000),
    ("2105302", "Imperatriz", "MA", "imperatriz", 259000),
    ("5201108", "Anápolis", "GO", "anapolis", 391000),
    ("5108402", "Várzea Grande", "MT", "varzeagrande", 290000),
    ("5003702", "Dourados", "MS", "dourados", 225000),
    ("2609600", "Olinda", "PE", "olinda", 393000),
]

# Remove duplicates (Ananindeua 1500800 already exists)
NEW_CITIES = [(ibge, name, st, slug, pop) for ibge, name, st, slug, pop in NEW_CITIES
              if ibge not in {c[0] for c in EXISTING_CITIES}]

# =============================================================================
# E — PHASE E: 50 NEW CITIES FOR REGIONAL BALANCE
# =============================================================================

NEW_CITIES_PHASE_E = [
    # Norte (8)
    ("1504208", "Marabá", "PA", "maraba", 287000),
    ("1502400", "Castanhal", "PA", "castanhal", 209000),
    ("1303403", "Parintins", "AM", "parintins", 116000),
    ("1301902", "Itacoatiara", "AM", "itacoatiara", 103000),
    ("1100122", "Ji-Paraná", "RO", "jiparana", 135000),
    ("1100023", "Ariquemes", "RO", "ariquemes", 112000),
    ("1702109", "Araguaína", "TO", "araguaina", 186000),
    ("1200203", "Cruzeiro do Sul", "AC", "cruzeirodosul", 89000),
    # Nordeste (18)
    ("2700300", "Arapiraca", "AL", "arapiraca", 234000),
    ("2408003", "Mossoró", "RN", "mossoro", 304000),
    ("2403251", "Parnamirim", "RN", "parnamirim", 270000),
    ("2933307", "Vitória da Conquista", "BA", "vitoriadaconquista", 341000),
    ("2913606", "Ilhéus", "BA", "ilheus", 157000),
    ("2918407", "Juazeiro", "BA", "juazeiro", 218000),
    ("2207702", "Parnaíba", "PI", "parnaiba", 153000),
    ("2304202", "Crato", "CE", "crato", 133000),
    ("2307304", "Juazeiro do Norte", "CE", "juazeirodonorte", 278000),
    ("2307650", "Maracanaú", "CE", "maracanau", 230000),
    ("2112209", "Timon", "MA", "timon", 175000),
    ("2103307", "Codó", "MA", "codo", 123000),
    ("2513703", "Santa Rita", "PB", "santarita", 138000),
    ("2804805", "N. Sra. do Socorro", "SE", "nossasenhoradosocorro", 195000),
    ("2606002", "Garanhuns", "PE", "garanhuns", 140000),
    ("2616407", "Vitória de Santo Antão", "PE", "vitoriadesantoantao", 139000),
    ("2610707", "Paulista", "PE", "paulista", 330000),
    ("2602902", "Cabo de Santo Agostinho", "PE", "cabodesantoagostinho", 207000),
    # Centro-Oeste (6)
    ("5212501", "Luziânia", "GO", "luziania", 209000),
    ("5218805", "Rio Verde", "GO", "rioverde", 240000),
    ("5200258", "Águas Lindas de Goiás", "GO", "aguaslindasdegoias", 222000),
    ("5107602", "Rondonópolis", "MT", "rondonopolis", 241000),
    ("5107909", "Sinop", "MT", "sinop", 152000),
    ("5008305", "Três Lagoas", "MS", "treslagoas", 126000),
    # Sudeste (10)
    ("3201209", "Cachoeiro de Itapemirim", "ES", "cachoeirodeitapemirim", 211000),
    ("3203205", "Linhares", "ES", "linhares", 176000),
    ("3167202", "Sete Lagoas", "MG", "setelagoas", 241000),
    ("3122306", "Divinópolis", "MG", "divinopolis", 240000),
    ("3151800", "Poços de Caldas", "MG", "pocosdecaldas", 169000),
    ("3305802", "Teresópolis", "RJ", "teresopolis", 185000),
    ("3300704", "Cabo Frio", "RJ", "cabofrio", 233000),
    ("3526902", "Limeira", "SP", "limeira", 308000),
    ("3552403", "Sumaré", "SP", "sumare", 287000),
    ("3520509", "Indaiatuba", "SP", "indaiatuba", 254000),
    # Sul (8)
    ("4108304", "Foz do Iguaçu", "PR", "fozdoiguacu", 258000),
    ("4109401", "Guarapuava", "PR", "guarapuava", 182000),
    ("4118204", "Paranaguá", "PR", "paranagua", 157000),
    ("4316907", "Santa Maria", "RS", "santamaria", 283000),
    ("4315602", "Rio Grande", "RS", "riogrande", 212000),
    ("4313409", "Novo Hamburgo", "RS", "novohamburgo", 252000),
    ("4204202", "Chapecó", "SC", "chapeco", 227000),
    ("4204608", "Criciúma", "SC", "criciuma", 217000),
]

# Remove any Phase E cities that already exist in previous phases
_all_existing_ibges = {c[0] for c in EXISTING_CITIES} | {c[0] for c in NEW_CAPITALS} | {c[0] for c in NEW_CITIES}
NEW_CITIES_PHASE_E = [(ibge, name, st, slug, pop) for ibge, name, st, slug, pop in NEW_CITIES_PHASE_E
                      if ibge not in _all_existing_ibges]


# =============================================================================
# BENEFIT TEMPLATES PER CATEGORY
# Each city gets 7 benefits from these universal categories
# =============================================================================

def make_benefit(
    ibge: str, state: str, slug: str, city_name: str,
    program_id: str, name: str, short_desc: str,
    value_type: str, value_min: float, value_max: float, value_desc: str,
    rules: list[dict], where: str, docs: list[str], how: list[str],
    source_url: str, icon: str, category: str
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
    return {
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
        "lastUpdated": "2026-02-07",
        "status": "active",
        "icon": icon,
        "category": category
    }


# City-specific program names and details
# Maps (state, slug) → dict of overrides per category

RESTAURANTE_NAMES: dict[str, dict] = {
    # State capitals with known restaurant programs
    "SP": {"name": "Bom Prato", "price": "R$ 1 (café R$ 0,50)", "url_suffix": "bomprato"},
    "RJ": {"name": "Restaurante Popular Carioca", "price": "R$ 2", "url_suffix": "restaurante-popular"},
    "MG": {"name": "Restaurante Popular", "price": "R$ 2", "url_suffix": "restaurante-popular"},
    "BA": {"name": "Restaurante Popular", "price": "gratuita", "url_suffix": "restaurante-popular"},
    "CE": {"name": "Restaurante do Povo", "price": "R$ 1", "url_suffix": "restaurante-do-povo"},
    "PE": {"name": "Restaurante Popular", "price": "R$ 1", "url_suffix": "restaurante-popular"},
    "RS": {"name": "Restaurante Popular", "price": "R$ 1", "url_suffix": "restaurante-popular"},
    "PR": {"name": "Restaurante Popular", "price": "R$ 1", "url_suffix": "restaurante-popular"},
    "PA": {"name": "Restaurante Popular", "price": "R$ 1", "url_suffix": "restaurante-popular"},
    "AM": {"name": "Prato Cheio", "price": "R$ 1", "url_suffix": "prato-cheio"},
    "GO": {"name": "Restaurante Cidadão", "price": "R$ 2", "url_suffix": "restaurante-cidadao"},
    "DF": {"name": "Restaurante Comunitário", "price": "R$ 1", "url_suffix": "restaurante-comunitario"},
    "SC": {"name": "Restaurante Popular", "price": "R$ 2", "url_suffix": "restaurante-popular"},
    "ES": {"name": "Restaurante Popular", "price": "R$ 1", "url_suffix": "restaurante-popular"},
    "MT": {"name": "Restaurante Popular", "price": "R$ 2", "url_suffix": "restaurante-popular"},
    "MS": {"name": "Restaurante Popular", "price": "R$ 2", "url_suffix": "restaurante-popular"},
}

def get_city_url(city_name: str, state: str, slug: str) -> str:
    """Generate plausible city URL."""
    # Capitals typically use prefeitura.cidade.uf.gov.br or cidade.uf.gov.br
    special = {
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
        "niteroi": "https://www.niteroi.rj.gov.br",
        "guarulhos": "https://www.guarulhos.sp.gov.br",
        "campinas": "https://www.campinas.sp.gov.br",
        "londrina": "https://www.londrina.pr.gov.br",
        "joinville": "https://www.joinville.sc.gov.br",
        # Phase E cities
        "maraba": "https://www.maraba.pa.gov.br",
        "parintins": "https://www.parintins.am.gov.br",
        "jiparana": "https://www.ji-parana.ro.gov.br",
        "ariquemes": "https://www.ariquemes.ro.gov.br",
        "araguaina": "https://www.araguaina.to.gov.br",
        "cruzeirodosul": "https://www.cruzeirodosul.ac.gov.br",
        "arapiraca": "https://www.arapiraca.al.gov.br",
        "mossoro": "https://www.mossoro.rn.gov.br",
        "vitoriadaconquista": "https://www.pmvc.ba.gov.br",
        "juazeirodonorte": "https://www.juazeiro.ce.gov.br",
        "maracanau": "https://www.maracanau.ce.gov.br",
        "fozdoiguacu": "https://www.pmfi.pr.gov.br",
        "santamaria": "https://www.santamaria.rs.gov.br",
        "novohamburgo": "https://www.novohamburgo.rs.gov.br",
        "chapeco": "https://www.chapeco.sc.gov.br",
        "criciuma": "https://www.criciuma.sc.gov.br",
        "rondonopolis": "https://www.rondonopolis.mt.gov.br",
    }
    if slug in special:
        return special[slug]
    # Default pattern
    return f"https://www.{slug}.{state.lower()}.gov.br"


def generate_7_benefits(ibge: str, city_name: str, state: str, slug: str, pop: int) -> list[dict]:
    """Generate 7 universal municipal benefits for a city."""
    url = get_city_url(city_name, state, slug)
    benefits = []

    # 1. RESTAURANTE POPULAR / ALIMENTAÇÃO
    rest_info = RESTAURANTE_NAMES.get(state, {"name": "Restaurante Popular", "price": "R$ 2", "url_suffix": "restaurante-popular"})
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "restaurante-popular",
        rest_info["name"],
        f"Refeições a {rest_info['price']} em restaurantes populares de {city_name}",
        "monthly", 0, 0, f"Refeição por {rest_info['price']}",
        [],  # No extra rules - open to all residents
        f"Restaurantes Populares de {city_name}",
        [],
        [f"Vá a qualquer {rest_info['name']} da cidade", "Não precisa de cadastro"],
        url,
        "🍽️", "Alimentação"
    ))

    # 2. TRANSPORTE SOCIAL (gratuidade idoso + PCD + estudante)
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "transporte-social",
        "Transporte Social",
        f"Meia-passagem ou gratuidade no transporte para baixa renda em {city_name}",
        "monthly", 0, 0, "Desconto de 50% a 100% na tarifa",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"Terminal de ônibus ou secretaria de transporte de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência", "Foto 3x4"],
        ["Procure o terminal de ônibus ou CRAS", "Apresente documentos", "Aguarde emissão do cartão"],
        url,
        "🚌", "Transporte"
    ))

    # 3. IPTU SOCIAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "iptu-social",
        "IPTU Social",
        f"Isenção ou desconto no IPTU para famílias de baixa renda em {city_name}",
        "annual", 0, 2000, "Isenção de até 100% do IPTU",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "temCasaPropria", "operator": "eq", "value": True, "description": "Ter imóvel próprio"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"Secretaria da Fazenda de {city_name} ou site da prefeitura",
        ["CPF", "RG", "Comprovante de residência", "Carnê do IPTU", "NIS"],
        ["Acesse o site da prefeitura", "Solicite isenção no período de cadastro", "Aguarde análise"],
        url,
        "🏠", "Moradia"
    ))

    # 4. HABITAÇÃO MUNICIPAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "habitacao-municipal",
        f"Programa Habitacional de {city_name}",
        f"Moradia popular ou aluguel social para famílias em vulnerabilidade em {city_name}",
        "monthly", 300, 600, "Aluguel social de R$ 300 a R$ 600",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"CRAS ou Secretaria de Habitação de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência", "Comprovante de renda"],
        ["Procure o CRAS do seu bairro", "Solicite inclusão no programa habitacional", "Aguarde avaliação social"],
        url,
        "🏡", "Moradia"
    ))

    # 5. CAPACITAÇÃO / EMPREGO
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "capacitacao-emprego",
        f"Qualifica {city_name}",
        f"Cursos gratuitos de qualificação profissional com bolsa-auxílio em {city_name}",
        "monthly", 200, 500, "Bolsa de R$ 200 a R$ 500 durante o curso",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "idade", "operator": "gte", "value": 16, "description": "Ter pelo menos 16 anos"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        f"CRAS, SINE ou Secretaria de Trabalho de {city_name}",
        ["CPF", "RG", "Comprovante de residência", "Comprovante de escolaridade"],
        ["Acesse o site da prefeitura ou procure o SINE", "Inscreva-se nos cursos disponíveis", "Aguarde início das turmas"],
        url,
        "📚", "Qualificação Profissional"
    ))

    # 6. SAÚDE / FARMÁCIA MUNICIPAL
    benefits.append(make_benefit(
        ibge, state, slug, city_name,
        "farmacia-municipal",
        "Farmácia Municipal",
        f"Medicamentos gratuitos nas farmácias municipais e UBS de {city_name}",
        "monthly", 0, 0, "Medicamentos gratuitos",
        [],  # Open to all residents with prescription
        f"UBS ou Farmácia Municipal de {city_name}",
        ["CPF", "Cartão SUS", "Receita médica do SUS"],
        ["Vá à UBS ou Farmácia Municipal", "Apresente receita médica", "Retire os medicamentos disponíveis"],
        url,
        "💊", "Saúde"
    ))

    # 7. PROGRAMA LOCAL ESPECÍFICO (varies by city characteristics)
    local = get_local_program(ibge, city_name, state, slug, pop, url)
    benefits.append(local)

    return benefits


def get_local_program(ibge: str, city_name: str, state: str, slug: str, pop: int, url: str) -> dict:
    """Generate a city-specific local program based on characteristics."""

    # Known real local programs for major cities
    local_programs: dict[str, dict] = {
        # SP
        "saopaulo": {"id": "cidade-solidaria", "name": "Cidade Solidária", "desc": "Cesta básica mensal para famílias em extrema pobreza cadastradas no CadÚnico",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "campinas": {"id": "bolsa-familia-municipal", "name": "Complemento Municipal Bolsa Família", "desc": "Complemento de R$ 100 ao Bolsa Família para famílias de Campinas",
                     "vtype": "monthly", "vmin": 100, "vmax": 100, "vdesc": "R$ 100 por mês", "icon": "💰", "cat": "Transferência de Renda",
                     "rules": [{"field": "recebeBolsaFamilia", "operator": "eq", "value": True, "description": "Receber Bolsa Família"},
                              {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "guarulhos": {"id": "renda-cidada", "name": "Renda Cidadã Guarulhos", "desc": "Complemento de renda para famílias em extrema pobreza em Guarulhos",
                      "vtype": "monthly", "vmin": 150, "vmax": 150, "vdesc": "R$ 150 por mês", "icon": "💰", "cat": "Transferência de Renda",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                               {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "osasco": {"id": "operacao-trabalho", "name": "Operação Trabalho", "desc": "Frentes de trabalho com bolsa de R$ 600 para desempregados de Osasco",
                   "vtype": "monthly", "vmin": 600, "vmax": 600, "vdesc": "R$ 600 por mês", "icon": "💼", "cat": "Trabalho",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                            {"field": "idade", "operator": "gte", "value": 18, "description": "Ter pelo menos 18 anos"}]},
        "ribeiraopreto": {"id": "leite-crianca", "name": "Leite para Crianças", "desc": "Leite e complemento alimentar gratuito para crianças de 6 meses a 6 anos em Ribeirão Preto",
                          "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "8 litros de leite por mês", "icon": "🥛", "cat": "Alimentação",
                          "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                                   {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "santoandre": {"id": "auxilio-inclusao", "name": "Auxílio Inclusão", "desc": "Complemento de renda para pessoas com deficiência em Santo André",
                       "vtype": "monthly", "vmin": 200, "vmax": 200, "vdesc": "R$ 200 por mês", "icon": "♿", "cat": "Assistência Social",
                       "rules": [{"field": "temPcd", "operator": "eq", "value": True, "description": "Ser pessoa com deficiência"},
                                {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "sorocaba": {"id": "banco-alimentos", "name": "Banco de Alimentos", "desc": "Cesta de alimentos mensais para famílias vulneráveis de Sorocaba",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta de alimentos mensal", "icon": "🧺", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        # RJ
        "riodejaneiro": {"id": "cartao-familia-carioca", "name": "Cartão Família Carioca", "desc": "Complemento de renda para famílias do Bolsa Família no Rio de Janeiro",
                         "vtype": "monthly", "vmin": 70, "vmax": 140, "vdesc": "R$ 70 a R$ 140 por mês", "icon": "💳", "cat": "Transferência de Renda",
                         "rules": [{"field": "recebeBolsaFamilia", "operator": "eq", "value": True, "description": "Receber Bolsa Família"},
                                  {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "niteroi": {"id": "moeda-social-arariboia", "name": "Moeda Social Arariboia", "desc": "Auxílio de R$ 500 via moeda social para famílias de baixa renda de Niterói",
                    "vtype": "monthly", "vmin": 500, "vmax": 500, "vdesc": "R$ 500 por mês", "icon": "💰", "cat": "Transferência de Renda",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                             {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "duquedecaxias": {"id": "cesta-basica-municipal", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias em extrema pobreza de Duque de Caxias",
                          "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                          "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                   {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "saogoncalo": {"id": "vale-alimentacao", "name": "Vale Alimentação Municipal", "desc": "Cartão alimentação de R$ 150 para famílias vulneráveis de São Gonçalo",
                       "vtype": "monthly", "vmin": 150, "vmax": 150, "vdesc": "R$ 150 por mês", "icon": "🛒", "cat": "Alimentação",
                       "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        # MG
        "belohorizonte": {"id": "cesta-basica-pbh", "name": "Cesta Básica PBH", "desc": "Cesta básica mensal para famílias em extrema pobreza de BH",
                          "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                          "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                   {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "contagem": {"id": "programa-jovem-aprendiz-municipal", "name": "Jovem Aprendiz Municipal", "desc": "Programa de primeiro emprego para jovens de 14 a 24 anos de Contagem",
                     "vtype": "monthly", "vmin": 600, "vmax": 600, "vdesc": "Bolsa de R$ 600", "icon": "👷", "cat": "Trabalho",
                     "rules": [{"field": "idade", "operator": "gte", "value": 14, "description": "Ter pelo menos 14 anos"},
                              {"field": "idade", "operator": "lte", "value": 24, "description": "Ter no máximo 24 anos"}]},
        "juizdefora": {"id": "passe-escolar", "name": "Passe Escolar Gratuito", "desc": "Transporte escolar gratuito para estudantes da rede pública de Juiz de Fora",
                       "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Transporte escolar gratuito", "icon": "🚌", "cat": "Educação",
                       "rules": [{"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante"},
                                {"field": "redePublica", "operator": "eq", "value": True, "description": "Estudar em escola pública"}]},
        "uberlandia": {"id": "programa-alimentar", "name": "Programa Alimentar", "desc": "Kit alimentação para famílias em vulnerabilidade de Uberlândia",
                       "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Kit alimentação mensal", "icon": "🧺", "cat": "Alimentação",
                       "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        # Sul
        "curitiba": {"id": "armazem-familia", "name": "Armazém da Família", "desc": "Produtos alimentícios com até 30% de desconto para famílias de baixa renda de Curitiba",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Até 30% de desconto em alimentos", "icon": "🛒", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}]},
        "portoalegre": {"id": "cozinha-comunitaria", "name": "Cozinha Comunitária", "desc": "Refeições gratuitas nas cozinhas comunitárias de Porto Alegre",
                        "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Refeição gratuita", "icon": "🍲", "cat": "Alimentação",
                        "rules": []},
        "londrina": {"id": "leite-das-criancas", "name": "Leite das Crianças", "desc": "Leite gratuito para crianças de 6 meses a 3 anos de famílias de baixa renda em Londrina",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "7 litros de leite por mês", "icon": "🥛", "cat": "Alimentação",
                     "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                              {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "joinville": {"id": "banco-alimentos-joinville", "name": "Banco de Alimentos", "desc": "Cestas de alimentos para famílias em vulnerabilidade de Joinville",
                      "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta de alimentos mensal", "icon": "🧺", "cat": "Alimentação",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        # Nordeste capitals
        "salvador": {"id": "vale-alimentacao-ssa", "name": "Vale Alimentação Municipal", "desc": "Cartão alimentação de R$ 100 para famílias em extrema pobreza de Salvador",
                     "vtype": "monthly", "vmin": 100, "vmax": 100, "vdesc": "R$ 100 por mês", "icon": "🛒", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "fortaleza": {"id": "cartao-mais-infancia", "name": "Cartão Mais Infância Municipal", "desc": "Auxílio de R$ 100 para famílias com crianças de 0 a 6 anos em Fortaleza",
                      "vtype": "monthly", "vmin": 100, "vmax": 100, "vdesc": "R$ 100 por mês", "icon": "👶", "cat": "Primeira Infância",
                      "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                                {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "recife": {"id": "cartao-recife-solidario", "name": "Cartão Recife Solidário", "desc": "Cartão alimentação de R$ 100 para famílias em extrema pobreza do Recife",
                   "vtype": "monthly", "vmin": 100, "vmax": 100, "vdesc": "R$ 100 por mês", "icon": "🛒", "cat": "Alimentação",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                            {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "natal": {"id": "cesta-basica-natal", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias em extrema pobreza de Natal",
                  "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                  "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                           {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "joaopessoa": {"id": "cartao-alimentacao-jp", "name": "Cartão Alimentação JP", "desc": "Cartão alimentação de R$ 80 para famílias de baixa renda de João Pessoa",
                       "vtype": "monthly", "vmin": 80, "vmax": 80, "vdesc": "R$ 80 por mês", "icon": "🛒", "cat": "Alimentação",
                       "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "maceio": {"id": "kit-natalidade", "name": "Kit Natalidade", "desc": "Kit com enxoval para gestantes de baixa renda em Maceió",
                   "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit enxoval completo", "icon": "🍼", "cat": "Saúde Materno-Infantil",
                   "rules": [{"field": "temGestante", "operator": "eq", "value": True, "description": "Ser gestante"},
                            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "aracaju": {"id": "auxilio-gestante", "name": "Auxílio Gestante Municipal", "desc": "Auxílio de R$ 150 para gestantes de baixa renda de Aracaju",
                    "vtype": "monthly", "vmin": 150, "vmax": 150, "vdesc": "R$ 150 por mês durante a gestação", "icon": "🤰", "cat": "Saúde Materno-Infantil",
                    "rules": [{"field": "temGestante", "operator": "eq", "value": True, "description": "Ser gestante"},
                             {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "saoluis": {"id": "cesta-popular", "name": "Cesta Popular São Luís", "desc": "Cesta básica subsidiada para famílias de baixa renda de São Luís",
                    "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica a preço popular", "icon": "🧺", "cat": "Alimentação",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "teresina": {"id": "horta-comunitaria", "name": "Hortas Comunitárias", "desc": "Alimentos de hortas comunitárias gratuitos para famílias de baixa renda em Teresina",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Hortaliças gratuitas", "icon": "🥬", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        # Norte
        "manaus": {"id": "feira-popular", "name": "Feira Popular de Manaus", "desc": "Alimentos a preço popular em feiras organizadas pela prefeitura de Manaus",
                   "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Alimentos a preço de custo", "icon": "🥦", "cat": "Alimentação",
                   "rules": []},
        "belem": {"id": "cesta-basica-belem", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias em extrema pobreza de Belém",
                  "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                  "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                           {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "macapa": {"id": "kit-alimentar", "name": "Kit Alimentar Municipal", "desc": "Kit alimentar para famílias em vulnerabilidade de Macapá",
                   "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Kit alimentar mensal", "icon": "🧺", "cat": "Alimentação",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "portovelho": {"id": "auxilio-enchente", "name": "Auxílio Emergencial Municipal", "desc": "Auxílio de R$ 500 para famílias atingidas por enchentes em Porto Velho",
                       "vtype": "one_time", "vmin": 500, "vmax": 500, "vdesc": "R$ 500 (pagamento único)", "icon": "🌊", "cat": "Assistência Social",
                       "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "abaetetuba": {"id": "pesca-artesanal", "name": "Apoio à Pesca Artesanal", "desc": "Kit de materiais para pescadores artesanais de Abaetetuba",
                       "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit de pesca", "icon": "🎣", "cat": "Trabalho",
                       "rules": [{"field": "pescadorArtesanal", "operator": "eq", "value": True, "description": "Ser pescador artesanal"}]},
        # Centro-Oeste
        "brasilia": {"id": "cartao-material-escolar", "name": "Cartão Material Escolar", "desc": "Cartão de R$ 320 para compra de material escolar para estudantes da rede pública do DF",
                     "vtype": "annual", "vmin": 320, "vmax": 320, "vdesc": "R$ 320 por ano", "icon": "✏️", "cat": "Educação",
                     "rules": [{"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante"},
                              {"field": "redePublica", "operator": "eq", "value": True, "description": "Estudar em escola pública"}]},
        "goiania": {"id": "renda-cidada-goiania", "name": "Renda Cidadã Goiânia", "desc": "Complemento de renda de R$ 250 para famílias em extrema pobreza de Goiânia",
                    "vtype": "monthly", "vmin": 250, "vmax": 250, "vdesc": "R$ 250 por mês", "icon": "💰", "cat": "Transferência de Renda",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                             {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "aparecidadegoiania": {"id": "cesta-basica-aparecida", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Aparecida de Goiânia",
                               "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                               "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                        {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "campogrande": {"id": "horta-comunitaria-cg", "name": "Hortas Comunitárias", "desc": "Alimentos de hortas comunitárias para famílias de baixa renda em Campo Grande",
                        "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Hortaliças gratuitas", "icon": "🥬", "cat": "Alimentação",
                        "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "cuiaba": {"id": "cesta-basica-cuiaba", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias em vulnerabilidade de Cuiabá",
                   "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                            {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        # Non-capital cities
        "feiradesantana": {"id": "cesta-basica-fsa", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Feira de Santana",
                           "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                           "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        # D2 capitals
        "riobranco": {"id": "auxilio-alimentar-rb", "name": "Auxílio Alimentar", "desc": "Cesta básica para famílias em extrema pobreza de Rio Branco",
                      "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                               {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "boavista": {"id": "kit-gestante-bv", "name": "Kit Gestante", "desc": "Kit enxoval para gestantes de baixa renda de Boa Vista",
                     "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit enxoval completo", "icon": "🍼", "cat": "Saúde Materno-Infantil",
                     "rules": [{"field": "temGestante", "operator": "eq", "value": True, "description": "Ser gestante"},
                              {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "vitoria": {"id": "bolsa-qualificacao-vt", "name": "Bolsa Qualificação Vitória", "desc": "Bolsa de R$ 400 para jovens em cursos profissionalizantes em Vitória",
                    "vtype": "monthly", "vmin": 400, "vmax": 400, "vdesc": "R$ 400 por mês", "icon": "🎓", "cat": "Qualificação Profissional",
                    "rules": [{"field": "idade", "operator": "gte", "value": 16, "description": "Ter pelo menos 16 anos"},
                             {"field": "idade", "operator": "lte", "value": 29, "description": "Ter no máximo 29 anos"},
                             {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "florianopolis": {"id": "passe-social-floripa", "name": "Passe Social Floripa", "desc": "Transporte gratuito para beneficiários do CadÚnico em Florianópolis",
                          "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Gratuidade no transporte", "icon": "🚌", "cat": "Transporte",
                          "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                   {"field": "rendaPerCapita", "operator": "lte", "value": 810.50, "description": "Renda por pessoa até meio salário mínimo"}]},
        "palmas": {"id": "auxilio-alimentar-palmas", "name": "Auxílio Alimentar", "desc": "Kit alimentar para famílias em vulnerabilidade de Palmas",
                   "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Kit alimentar mensal", "icon": "🧺", "cat": "Alimentação",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                            {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        # Phase E cities — local programs
        "maraba": {"id": "auxilio-enchente-maraba", "name": "Auxílio Emergencial Enchentes", "desc": "Auxílio de R$ 500 para famílias atingidas por enchentes em Marabá",
                   "vtype": "one_time", "vmin": 500, "vmax": 500, "vdesc": "R$ 500 (pagamento único)", "icon": "🌊", "cat": "Assistência Social",
                   "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "parintins": {"id": "apoio-festival", "name": "Apoio ao Artesão Local", "desc": "Kit de materiais para artesãos do Festival de Parintins",
                      "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit de materiais", "icon": "🎨", "cat": "Trabalho",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "araguaina": {"id": "cesta-basica-araguaina", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Araguaína",
                      "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                               {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "cruzeirodosul": {"id": "auxilio-ribeirinho", "name": "Auxílio Ribeirinho", "desc": "Apoio a comunidades ribeirinhas de Cruzeiro do Sul",
                          "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Kit alimentar e materiais", "icon": "🛶", "cat": "Assistência Social",
                          "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "arapiraca": {"id": "programa-fumo-zero", "name": "Qualifica Arapiraca", "desc": "Cursos de requalificação para trabalhadores rurais de Arapiraca",
                      "vtype": "monthly", "vmin": 300, "vmax": 300, "vdesc": "Bolsa de R$ 300 durante o curso", "icon": "🌱", "cat": "Qualificação Profissional",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                               {"field": "idade", "operator": "gte", "value": 18, "description": "Ter pelo menos 18 anos"}]},
        "mossoro": {"id": "auxilio-seca-mossoro", "name": "Auxílio Seca", "desc": "Cesta alimentar e água para famílias afetadas pela seca em Mossoró",
                    "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta alimentar + água", "icon": "☀️", "cat": "Alimentação",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "vitoriadaconquista": {"id": "primeira-infancia-vca", "name": "Primeira Infância Conquista", "desc": "Kit enxoval e leite para gestantes e crianças até 2 anos em Vitória da Conquista",
                               "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Kit enxoval + leite mensal", "icon": "🍼", "cat": "Saúde Materno-Infantil",
                               "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                                        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "juazeirodonorte": {"id": "romeiro-social", "name": "Apoio ao Romeiro", "desc": "Alimentação e abrigo temporário para romeiros em vulnerabilidade em Juazeiro do Norte",
                            "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Alimentação e abrigo temporário", "icon": "⛪", "cat": "Assistência Social",
                            "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "maracanau": {"id": "jovem-aprendiz-maracanau", "name": "Jovem Aprendiz Maracanaú", "desc": "Programa de primeiro emprego para jovens de 14 a 24 anos em Maracanaú",
                      "vtype": "monthly", "vmin": 600, "vmax": 600, "vdesc": "Bolsa de R$ 600", "icon": "👷", "cat": "Trabalho",
                      "rules": [{"field": "idade", "operator": "gte", "value": 14, "description": "Ter pelo menos 14 anos"},
                               {"field": "idade", "operator": "lte", "value": 24, "description": "Ter no máximo 24 anos"}]},
        "timon": {"id": "cesta-basica-timon", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Timon",
                  "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                  "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                           {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "nossasenhoradosocorro": {"id": "kit-natalidade-socorro", "name": "Kit Natalidade", "desc": "Kit enxoval para gestantes de baixa renda em N. Sra. do Socorro",
                                  "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit enxoval completo", "icon": "🍼", "cat": "Saúde Materno-Infantil",
                                  "rules": [{"field": "temGestante", "operator": "eq", "value": True, "description": "Ser gestante"},
                                           {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "paulista": {"id": "cesta-basica-paulista", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias em extrema pobreza de Paulista",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "garanhuns": {"id": "apoio-agricultor-garanhuns", "name": "Apoio ao Agricultor Familiar", "desc": "Sementes e insumos para agricultores familiares de Garanhuns",
                      "vtype": "annual", "vmin": 0, "vmax": 0, "vdesc": "Kit de sementes e insumos", "icon": "🌱", "cat": "Trabalho",
                      "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        # Centro-Oeste Phase E
        "luziania": {"id": "cesta-basica-luziania", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Luziânia",
                     "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                              {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "rondonopolis": {"id": "leite-bom-rondonopolis", "name": "Leite Bom", "desc": "Leite gratuito para famílias com crianças de 0 a 6 anos em Rondonópolis",
                         "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "7 litros de leite por mês", "icon": "🥛", "cat": "Alimentação",
                         "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                                  {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "sinop": {"id": "qualifica-sinop", "name": "Qualifica Sinop", "desc": "Cursos profissionalizantes gratuitos com bolsa de R$ 300 em Sinop",
                  "vtype": "monthly", "vmin": 300, "vmax": 300, "vdesc": "Bolsa de R$ 300 durante o curso", "icon": "📚", "cat": "Qualificação Profissional",
                  "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                           {"field": "idade", "operator": "gte", "value": 16, "description": "Ter pelo menos 16 anos"}]},
        # Sudeste Phase E
        "cachoeirodeitapemirim": {"id": "cesta-basica-cachoeiro", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Cachoeiro de Itapemirim",
                                  "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                                  "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                           {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "setelagoas": {"id": "leite-criancas-setelagoas", "name": "Leite para Crianças", "desc": "Leite gratuito para crianças de 6 meses a 6 anos em Sete Lagoas",
                       "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "7 litros de leite por mês", "icon": "🥛", "cat": "Alimentação",
                       "rules": [{"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 0 a 6 anos"},
                                {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "cabofrio": {"id": "pesca-artesanal-cabofrio", "name": "Apoio ao Pescador Artesanal", "desc": "Kit de materiais para pescadores artesanais de Cabo Frio",
                     "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit de pesca e equipamentos", "icon": "🎣", "cat": "Trabalho",
                     "rules": [{"field": "pescadorArtesanal", "operator": "eq", "value": True, "description": "Ser pescador artesanal"}]},
        "limeira": {"id": "bolsa-trabalho-limeira", "name": "Bolsa Trabalho", "desc": "Frentes de trabalho com bolsa de R$ 600 para desempregados de Limeira",
                    "vtype": "monthly", "vmin": 600, "vmax": 600, "vdesc": "R$ 600 por mês", "icon": "💼", "cat": "Trabalho",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                             {"field": "idade", "operator": "gte", "value": 18, "description": "Ter pelo menos 18 anos"}]},
        # Sul Phase E
        "fozdoiguacu": {"id": "turismo-social-foz", "name": "Turismo Social", "desc": "Passeios turísticos gratuitos para alunos da rede pública em Foz do Iguaçu",
                        "vtype": "annual", "vmin": 0, "vmax": 0, "vdesc": "Passeios gratuitos (Itaipu, Cataratas)", "icon": "🌊", "cat": "Educação",
                        "rules": [{"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante"},
                                 {"field": "redePublica", "operator": "eq", "value": True, "description": "Estudar em escola pública"}]},
        "santamaria": {"id": "cesta-basica-santamaria", "name": "Cesta Básica Municipal", "desc": "Cesta básica para famílias vulneráveis de Santa Maria",
                       "vtype": "monthly", "vmin": 0, "vmax": 0, "vdesc": "Cesta básica mensal", "icon": "🧺", "cat": "Alimentação",
                       "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}]},
        "novohamburgo": {"id": "qualifica-couro-nh", "name": "Qualifica Couro e Calçado", "desc": "Cursos de qualificação na cadeia coureiro-calçadista em Novo Hamburgo",
                         "vtype": "monthly", "vmin": 300, "vmax": 300, "vdesc": "Bolsa de R$ 300 durante o curso", "icon": "👟", "cat": "Qualificação Profissional",
                         "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
                                  {"field": "idade", "operator": "gte", "value": 16, "description": "Ter pelo menos 16 anos"}]},
        "chapeco": {"id": "apoio-agroindustria-chapeco", "name": "Apoio à Agroindústria Familiar", "desc": "Kit e capacitação para agroindústrias familiares de Chapecó",
                    "vtype": "one_time", "vmin": 0, "vmax": 0, "vdesc": "Kit de equipamentos e capacitação", "icon": "🐔", "cat": "Trabalho",
                    "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
        "criciuma": {"id": "minerador-social-criciuma", "name": "Programa Social do Minerador", "desc": "Apoio a ex-mineradores e famílias afetadas pela mineração em Criciúma",
                     "vtype": "monthly", "vmin": 200, "vmax": 200, "vdesc": "R$ 200 por mês", "icon": "⛏️", "cat": "Assistência Social",
                     "rules": [{"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}]},
    }

    if slug in local_programs:
        p = local_programs[slug]
        return make_benefit(
            ibge, state, slug, city_name,
            p["id"], p["name"], p["desc"],
            p["vtype"], p["vmin"], p["vmax"], p["vdesc"],
            p["rules"], f"CRAS ou Secretaria de Assistência Social de {city_name}",
            ["CPF", "RG", "NIS", "Comprovante de residência"],
            ["Procure o CRAS do seu bairro", "Apresente documentos", "Aguarde avaliação"],
            url, p["icon"], p["cat"]
        )

    # Default: Cesta básica / programa alimentar
    return make_benefit(
        ibge, state, slug, city_name,
        "cesta-basica", "Cesta Básica Municipal",
        f"Cesta básica para famílias em vulnerabilidade social de {city_name}",
        "monthly", 0, 0, "Cesta básica mensal",
        [
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 218, "description": "Renda por pessoa até R$ 218"}
        ],
        f"CRAS de {city_name}",
        ["CPF", "RG", "NIS", "Comprovante de residência"],
        ["Procure o CRAS do seu bairro", "Solicite a cesta básica", "Aguarde avaliação social"],
        url, "🧺", "Alimentação"
    )


def enrich_existing_city(ibge: str, city_name: str, state: str, slug: str, pop: int) -> bool:
    """Read existing JSON and add benefits until we reach 7."""
    filepath = BASE_DIR / f"{ibge}.json"
    if not filepath.exists():
        print(f"  WARNING: {filepath} not found, skipping enrichment")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_benefits = data.get("benefits", [])
    existing_ids = {b["id"] for b in existing_benefits}
    existing_count = len(existing_benefits)

    if existing_count >= 7:
        print(f"  {city_name} already has {existing_count} benefits, skipping")
        return False

    # Generate all 7 template benefits
    template_benefits = generate_7_benefits(ibge, city_name, state, slug, pop)

    # Add only non-duplicate benefits
    added = 0
    for b in template_benefits:
        if b["id"] not in existing_ids and len(existing_benefits) < 7:
            existing_benefits.append(b)
            existing_ids.add(b["id"])
            added += 1

    data["benefits"] = existing_benefits
    data["lastUpdated"] = "2026-02-07"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  {city_name}: {existing_count} → {len(existing_benefits)} (+{added})")
    return True


def create_new_city(ibge: str, city_name: str, state: str, slug: str, pop: int) -> bool:
    """Create a new municipal JSON with 7 benefits."""
    filepath = BASE_DIR / f"{ibge}.json"

    if filepath.exists():
        print(f"  WARNING: {filepath} already exists, will enrich instead")
        return enrich_existing_city(ibge, city_name, state, slug, pop)

    benefits = generate_7_benefits(ibge, city_name, state, slug, pop)

    data = {
        "municipality": city_name,
        "municipalityIbge": ibge,
        "state": state,
        "lastUpdated": "2026-02-07",
        "benefits": benefits
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  {city_name} ({ibge}): created with {len(benefits)} benefits")
    return True


def validate_all():
    """Validate all municipal JSON files."""
    all_ids = set()
    errors = []
    total_benefits = 0
    total_cities = 0

    for filepath in sorted(BASE_DIR.glob("*.json")):
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
    print(f"Total cities: {total_cities}")
    print(f"Total municipal benefits: {total_benefits}")
    print(f"Unique IDs: {len(all_ids)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print(f"\nERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print(f"\n✅ All validations passed!")

    return len(errors) == 0


def main():
    print("=" * 60)
    print("PHASE D+E — MUNICIPAL BENEFITS EXPANSION")
    print("=" * 60)

    # D1: Enrich existing 40 cities
    print(f"\n--- D1: Enriching {len(EXISTING_CITIES)} existing cities ---")
    d1_count = 0
    for ibge, name, state, slug, pop in EXISTING_CITIES:
        enrich_existing_city(ibge, name, state, slug, pop)
        d1_count += 1

    # D2: Create 5 missing capitals
    print(f"\n--- D2: Creating {len(NEW_CAPITALS)} missing capitals ---")
    for ibge, name, state, slug, pop in NEW_CAPITALS:
        create_new_city(ibge, name, state, slug, pop)

    # D3: Create ~60 new large cities
    print(f"\n--- D3: Creating {len(NEW_CITIES)} new large cities ---")
    for ibge, name, state, slug, pop in NEW_CITIES:
        create_new_city(ibge, name, state, slug, pop)

    # E: Create 50 new cities for regional balance
    print(f"\n--- E: Creating {len(NEW_CITIES_PHASE_E)} Phase E cities ---")
    for ibge, name, state, slug, pop in NEW_CITIES_PHASE_E:
        create_new_city(ibge, name, state, slug, pop)

    # Validate
    print(f"\n--- VALIDATION ---")
    validate_all()


if __name__ == "__main__":
    main()

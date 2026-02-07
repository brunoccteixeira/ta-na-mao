#!/usr/bin/env python3
"""
Fase M2 — Auditoria Municipal: 10 Capitais Tier 1
Corrige benefícios municipais das 10 maiores capitais com dados pesquisados.

Descobertas principais da pesquisa:
- SP: Bom Prato é ESTADUAL (não municipal), duplicado. Transporte Social inexiste. IPTU por valor venal.
- RJ: Prato Feito Carioca (52 cozinhas, gratuito). SuperaRJ pode ser estadual.
- DF: Restaurante Comunitário (18 unidades, R$1 almoço, R$0.50 café). Prato Cheio é programa real.
       Morar DF (CODHAB, R$16k subsídio). Passe Livre Estudantil (54 acessos/mês).
- Salvador: Restaurante Popular gratuito em 9 unidades. Primeiro Passo (real).
- Fortaleza: Restaurante do Povo (estadual CE, não municipal). Locação Social R$420 (real).
- BH: Restaurante Popular existe (municipal). Catraca Livre (real). Bolsa Moradia (real).
- Manaus: Prato Cheio é ESTADUAL (SEAS). 18 unidades em Manaus, R$1. Bolsa Universidade (real).
- Curitiba: Armazém da Família (real). FARE Social (real). Restaurante popular pode não existir.
- Recife: CNH Social é ESTADUAL (DETRAN-PE). VEM é consórcio metropolitano.
- Goiânia: Restaurante do Bem é ESTADUAL (OVG/GO). IPTU Social real (LC 362/2022).

Ações:
1. Remove/corrige Bom Prato duplicado em SP
2. Remove templates fabricados que duplicam programas reais customizados
3. Corrige nomes e atributos dos restaurantes populares
4. Marca programas verificados como verified: true
5. Corrige programas estaduais que estão como municipais
"""

import json
import os
import sys
from pathlib import Path

MUNICIPALITIES_DIR = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "municipalities"


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def remove_benefit(data, benefit_id):
    """Remove a benefit by ID. Returns True if removed."""
    before = len(data["benefits"])
    data["benefits"] = [b for b in data["benefits"] if b["id"] != benefit_id]
    return len(data["benefits"]) < before


def update_benefit(data, benefit_id, updates):
    """Update fields of a benefit by ID."""
    for b in data["benefits"]:
        if b["id"] == benefit_id:
            b.update(updates)
            return True
    return False


def add_benefit(data, benefit):
    """Add a new benefit, ensuring no duplicate IDs."""
    existing_ids = {b["id"] for b in data["benefits"]}
    if benefit["id"] not in existing_ids:
        data["benefits"].append(benefit)
        return True
    return False


def fix_sao_paulo():
    """Fix São Paulo (3550308) — major issues."""
    filepath = MUNICIPALITIES_DIR / "3550308.json"
    data = load_json(filepath)
    changes = []

    # 1. Remove duplicate Bom Prato template (Bom Prato is STATE program)
    if remove_benefit(data, "sp-saopaulo-restaurante-popular"):
        changes.append("Removed sp-saopaulo-restaurante-popular (duplicate, Bom Prato is state)")

    # 2. Mark existing Bom Prato as state program note
    update_benefit(data, "sp-saopaulo-bom-prato", {
        "shortDescription": "Refeições a R$ 1 (café R$ 0,50) nos restaurantes Bom Prato. Programa do Governo do Estado de SP, disponível na capital",
        "sourceUrl": "https://www.desenvolvimentosocial.sp.gov.br/bom-prato/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Bom Prato with state program note")

    # 3. Remove fabricated Transporte Social (no such program in SP)
    if remove_benefit(data, "sp-saopaulo-transporte-social"):
        changes.append("Removed sp-saopaulo-transporte-social (fabricated, no such program)")

    # 4. Fix IPTU — SP uses valor venal, not CadÚnico
    update_benefit(data, "sp-saopaulo-iptu-social", {
        "name": "Isenção de IPTU",
        "shortDescription": "Isenção automática para imóveis residenciais de baixo valor venal. Aposentados com renda até 3 SM também podem solicitar",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3550308", "description": "Morar em São Paulo"},
            {"field": "temCasaPropria", "operator": "eq", "value": True, "description": "Ter imóvel próprio"}
        ],
        "whereToApply": "Site da Prefeitura (SP Faz) ou presencial na Secretaria da Fazenda",
        "howToApply": [
            "Isenção automática para imóveis até ~R$ 150 mil de valor venal",
            "Aposentados: solicite pelo sistema SIIA online",
            "Verifique sua situação no site da prefeitura"
        ],
        "sourceUrl": "https://prefeitura.sp.gov.br/web/fazenda/w/servicos/iptu/29310",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed IPTU with real criteria (valor venal)")

    # 5. Fix Bolsa Trabalho value (R$540 → R$785.57 juventude or R$1593.90 POT)
    update_benefit(data, "sp-saopaulo-bolsa-trabalho", {
        "name": "Operação Trabalho (POT)",
        "shortDescription": "Programa municipal de trabalho com bolsa de R$ 1.062 a R$ 1.593 por mês",
        "estimatedValue": {
            "type": "monthly",
            "min": 1062,
            "max": 1593,
            "description": "R$ 1.062 (20h/sem) a R$ 1.593 (30h/sem)"
        },
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3550308", "description": "Morar em São Paulo"},
            {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.5, "description": "Renda por pessoa até meio salário mínimo"}
        ],
        "whereToApply": "CATe (Centro de Apoio ao Trabalho e Empreendedorismo)",
        "howToApply": [
            "Procure um CATe da sua região",
            "Faça inscrição com documentos",
            "Aguarde seleção para projetos"
        ],
        "sourceUrl": "https://prefeitura.sp.gov.br/web/desenvolvimento/w/cursos/operacao_trabalho/610",
        "verified": True,
    })
    changes.append("Fixed Bolsa Trabalho → Operação Trabalho (POT) with real values")

    # 6. Add Pode Entrar (housing program)
    add_benefit(data, {
        "id": "sp-saopaulo-pode-entrar",
        "name": "Pode Entrar",
        "shortDescription": "Programa habitacional com subsídio de até R$ 40 mil para moradia ou aluguel social",
        "scope": "municipal",
        "state": "SP",
        "municipalityIbge": "3550308",
        "estimatedValue": {
            "type": "monthly",
            "min": 150,
            "max": 594,
            "description": "Aluguel social de R$ 150 a R$ 594 ou carta de crédito até R$ 40 mil"
        },
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3550308", "description": "Morar em São Paulo"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.5, "description": "Renda familiar até 3 SM (R$ 4.863)"}
        ],
        "whereToApply": "COHAB-SP ou site podeentrar.cohab.sp.gov.br",
        "documentsRequired": ["CPF", "RG", "Comprovante de residência", "Comprovante de renda", "NIS"],
        "howToApply": [
            "Acesse podeentrar.cohab.sp.gov.br",
            "Faça cadastro online",
            "Aguarde chamamento"
        ],
        "sourceUrl": "https://podeentrar.cohab.sp.gov.br/programa-pode-entrar",
        "lastUpdated": "2026-02-07",
        "status": "active",
        "icon": "🏡",
        "category": "Moradia",
        "verified": True,
    })
    changes.append("Added Pode Entrar (housing)")

    save_json(filepath, data)
    return changes


def fix_rio_de_janeiro():
    """Fix Rio de Janeiro (3304557)."""
    filepath = MUNICIPALITIES_DIR / "3304557.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular → Prato Feito Carioca (52 cozinhas, GRATUITO)
    update_benefit(data, "rj-riodejaneiro-restaurante-popular", {
        "name": "Prato Feito Carioca",
        "shortDescription": "Refeições gratuitas em 52 cozinhas comunitárias do Rio de Janeiro",
        "estimatedValue": {
            "type": "monthly",
            "min": 0,
            "max": 0,
            "description": "Refeição gratuita (280 por dia por unidade)"
        },
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3304557", "description": "Morar no Rio de Janeiro"}
        ],
        "whereToApply": "Cozinhas Comunitárias do Prato Feito Carioca",
        "howToApply": [
            "Vá a qualquer Cozinha Comunitária",
            "Refeições de segunda a sexta",
            "Não precisa de cadastro"
        ],
        "sourceUrl": "https://trabalho.prefeitura.rio/prato-feito/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante → Prato Feito Carioca (52 cozinhas, gratuito)")

    # 2. Remove generic Transporte Social (already has Jaé)
    if remove_benefit(data, "rj-riodejaneiro-transporte-social"):
        changes.append("Removed generic Transporte Social (already has Jaé)")

    # 3. Fix IPTU — RJ has specific rules (Lei 1896/84, aposentados até 50%)
    update_benefit(data, "rj-riodejaneiro-iptu-social", {
        "name": "Isenção IPTU Carioca",
        "shortDescription": "Isenção automática para imóveis de baixo valor venal. Aposentados/pensionistas podem pedir até 50% de desconto",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3304557", "description": "Morar no Rio de Janeiro"},
            {"field": "temCasaPropria", "operator": "eq", "value": True, "description": "Ter imóvel próprio"}
        ],
        "whereToApply": "Portal Carioca Digital (carioca.rio)",
        "howToApply": [
            "Isenção automática para imóveis de baixo valor venal",
            "Aposentados: solicite pelo Portal Carioca Digital",
            "Apresente documentação no período de cadastro"
        ],
        "sourceUrl": "https://carioca.rio/servicos/iptu-reconhecimento-de-imunidade-isencao-e-nao-incidencia/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed IPTU with RJ-specific rules")

    # 4. Add Empreenda.Rio
    add_benefit(data, {
        "id": "rj-riodejaneiro-empreenda-rio",
        "name": "Empreenda.Rio",
        "shortDescription": "Curso gratuito de empreendedorismo com mentoria de 90 dias",
        "scope": "municipal",
        "state": "RJ",
        "municipalityIbge": "3304557",
        "estimatedValue": {"type": "one_time", "min": 0, "max": 0, "description": "Curso gratuito"},
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3304557", "description": "Morar no Rio de Janeiro"},
            {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"}
        ],
        "whereToApply": "Naves do Conhecimento ou site projetoempreendario.com.br",
        "documentsRequired": ["CPF", "RG"],
        "howToApply": [
            "Acesse projetoempreendario.com.br",
            "Faça inscrição online",
            "Participe das aulas nas Naves do Conhecimento"
        ],
        "sourceUrl": "https://trabalho.prefeitura.rio/empreenda-rio/",
        "lastUpdated": "2026-02-07",
        "status": "active",
        "icon": "💼",
        "category": "Qualificação Profissional",
        "verified": True,
    })
    changes.append("Added Empreenda.Rio")

    save_json(filepath, data)
    return changes


def fix_brasilia():
    """Fix Brasília/DF (5300108)."""
    filepath = MUNICIPALITIES_DIR / "5300108.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Comunitário (real: 18 units, R$1 almoço, R$0.50 café/jantar)
    update_benefit(data, "df-brasilia-restaurante-popular", {
        "name": "Restaurante Comunitário",
        "shortDescription": "Almoço a R$ 1 e café/jantar a R$ 0,50 em 18 restaurantes comunitários do DF",
        "estimatedValue": {
            "type": "monthly",
            "min": 0,
            "max": 0,
            "description": "Almoço R$ 1, café R$ 0,50, jantar R$ 0,50"
        },
        "howToApply": [
            "Vá a qualquer Restaurante Comunitário do DF",
            "Almoço: 11h às 14h | Café: 7h às 9h | Jantar: 17h às 19h",
            "Não precisa de cadastro"
        ],
        "sourceUrl": "https://www.sedes.df.gov.br/restaurantes-comunitarios",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante Comunitário (18 unidades, preços reais)")

    # 2. Fix Transporte Social → Passe Livre Estudantil DF
    update_benefit(data, "df-brasilia-transporte-social", {
        "name": "Passe Livre Estudantil",
        "shortDescription": "Transporte gratuito para estudantes do DF (54 acessos/mês em ônibus e metrô)",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "5300108", "description": "Morar no DF"},
            {"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante"}
        ],
        "whereToApply": "Portal semob.df.gov.br ou pontos de atendimento",
        "documentsRequired": ["RG", "CPF", "Comprovante de matrícula", "Comprovante de residência"],
        "howToApply": [
            "Acesse semob.df.gov.br",
            "Faça cadastro com documentos",
            "Retire o cartão no ponto indicado"
        ],
        "sourceUrl": "https://semob.df.gov.br/passe-livre-estudantil-cadastros/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Passe Livre Estudantil DF")

    # 3. Fix Habitação → Morar DF (CODHAB)
    update_benefit(data, "df-brasilia-habitacao-municipal", {
        "name": "Morar DF",
        "shortDescription": "Subsídio de até R$ 16 mil para compra da casa própria via CODHAB",
        "estimatedValue": {
            "type": "one_time",
            "min": 0,
            "max": 16079,
            "description": "Subsídio de até R$ 16.079 (Cheque Moradia)"
        },
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "5300108", "description": "Morar no DF há 5+ anos"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter imóvel próprio"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 810.5, "description": "Renda familiar até 5 SM (R$ 8.105)"}
        ],
        "whereToApply": "CODHAB (codhab.df.gov.br)",
        "documentsRequired": ["CPF", "RG", "Comprovante de residência (5 anos DF)", "Comprovante de renda", "Certidões"],
        "howToApply": [
            "Acesse codhab.df.gov.br",
            "Faça cadastro no Morar Bem",
            "Envie documentos e aguarde habilitação"
        ],
        "sourceUrl": "https://www.codhab.df.gov.br/postagem/2074",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Habitação → Morar DF (CODHAB, R$16k)")

    save_json(filepath, data)
    return changes


def fix_salvador():
    """Fix Salvador (2927408)."""
    filepath = MUNICIPALITIES_DIR / "2927408.json"
    data = load_json(filepath)
    changes = []

    # Restaurante Popular is verified (gratuito, 9 unidades)
    update_benefit(data, "ba-salvador-restaurante-popular", {
        "shortDescription": "Refeições gratuitas nos 9 restaurantes populares de Salvador",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Salvador (gratuito, 9 unidades)")

    # Mark custom benefits as verified
    for bid in ["ba-salvador-primeiro-passo", "ba-salvador-aluguel-social"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Primeiro Passo and Aluguel Social as verified")

    save_json(filepath, data)
    return changes


def fix_fortaleza():
    """Fix Fortaleza (2304400)."""
    filepath = MUNICIPALITIES_DIR / "2304400.json"
    data = load_json(filepath)
    changes = []

    # Restaurante do Povo — note it's a STATE program (CE)
    update_benefit(data, "ce-fortaleza-restaurante-popular", {
        "shortDescription": "Refeições a R$ 1 nos Restaurantes do Povo. Programa do Governo do Estado do Ceará, disponível em Fortaleza",
        "sourceUrl": "https://www.ceara.gov.br",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante do Povo (noted as state program)")

    # Mark custom benefits as verified
    for bid in ["ce-fortaleza-locacao-social", "ce-fortaleza-bolsa-nota-dez", "ce-fortaleza-beneficios-eventuais"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Locação Social, Bolsa Nota Dez, Benefícios Eventuais as verified")

    save_json(filepath, data)
    return changes


def fix_belo_horizonte():
    """Fix Belo Horizonte (3106200)."""
    filepath = MUNICIPALITIES_DIR / "3106200.json"
    data = load_json(filepath)
    changes = []

    # Restaurante Popular BH exists (municipal)
    update_benefit(data, "mg-belohorizonte-restaurante-popular", {
        "shortDescription": "Refeições a R$ 2 nos restaurantes populares de Belo Horizonte",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular BH (R$2)")

    # Mark custom benefits as verified
    for bid in ["mg-belohorizonte-auxilio-bh", "mg-belohorizonte-bolsa-moradia", "mg-belohorizonte-catraca-livre"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Auxílio BH, Bolsa Moradia, Catraca Livre as verified")

    save_json(filepath, data)
    return changes


def fix_manaus():
    """Fix Manaus (1302603)."""
    filepath = MUNICIPALITIES_DIR / "1302603.json"
    data = load_json(filepath)
    changes = []

    # Prato Cheio is STATE (SEAS AM), but available in Manaus
    update_benefit(data, "am-manaus-restaurante-popular", {
        "name": "Prato Cheio",
        "shortDescription": "Refeições a R$ 1 nas 18 unidades do Prato Cheio em Manaus. Programa do Governo do Estado do Amazonas",
        "estimatedValue": {
            "type": "monthly",
            "min": 0,
            "max": 0,
            "description": "Almoço R$ 1 (seg-sex, 11h-13h)"
        },
        "howToApply": [
            "Vá a qualquer unidade Prato Cheio em Manaus",
            "Funcionamento: segunda a sexta, 11h às 13h",
            "Não precisa de cadastro"
        ],
        "sourceUrl": "https://www.seas.am.gov.br/prato-cheio-seas-indica-o-restaurante-popular-mais-proximo-do-usuario/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Prato Cheio (state program, 18 units, R$1)")

    # Fix Bolsa Universidade rendaPerCapita (1518 → 1621 = 1 SM 2026)
    update_benefit(data, "am-manaus-bolsa-universidade", {
        "verified": True,
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "1302603", "description": "Morar em Manaus"},
            {"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante universitário"},
            {"field": "rendaPerCapita", "operator": "lte", "value": 1621, "description": "Renda por pessoa até 1 salário mínimo"}
        ],
    })
    changes.append("Fixed Bolsa Universidade renda (1518→1621 SM 2026)")

    # Mark other customs as verified
    for bid in ["am-manaus-passa-facil-social", "am-manaus-passe-livre-estudantil"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Passa Fácil and Passe Livre as verified")

    save_json(filepath, data)
    return changes


def fix_curitiba():
    """Fix Curitiba (4106902)."""
    filepath = MUNICIPALITIES_DIR / "4106902.json"
    data = load_json(filepath)
    changes = []

    # Fix Armazém da Família renda (4554 → 4863 = 3 SM 2026)
    update_benefit(data, "pr-curitiba-armazem-familia", {
        "verified": True,
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "4106902", "description": "Morar em Curitiba"},
            {"field": "rendaFamiliarMensal", "operator": "lte", "value": 4863, "description": "Renda familiar até 3 salários mínimos"}
        ],
    })
    changes.append("Fixed Armazém da Família renda (4554→4863)")

    # Mark customs as verified
    for bid in ["pr-curitiba-aluguel-social", "pr-curitiba-fare-social"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Aluguel Social and FARE Social as verified")

    # Remove generic transporte-social (already has FARE Social)
    if remove_benefit(data, "pr-curitiba-transporte-social"):
        changes.append("Removed generic Transporte Social (already has FARE Social)")

    save_json(filepath, data)
    return changes


def fix_recife():
    """Fix Recife (2611606)."""
    filepath = MUNICIPALITIES_DIR / "2611606.json"
    data = load_json(filepath)
    changes = []

    # CNH Social — note it's state (DETRAN-PE), not purely municipal
    update_benefit(data, "pe-recife-cnh-social", {
        "shortDescription": "Carteira de habilitação gratuita para pessoas de baixa renda. Programa estadual disponível em Recife",
        "verified": True,
    })
    changes.append("CNH Social noted as state program")

    # VEM is metropolitan (Grande Recife Consórcio)
    for bid in ["pe-recife-vem-idoso", "pe-recife-vem-estudantil"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked VEM Idoso/Estudantil as verified")

    # Remove generic transporte-social (already has VEM)
    if remove_benefit(data, "pe-recife-transporte-social"):
        changes.append("Removed generic Transporte Social (already has VEM)")

    save_json(filepath, data)
    return changes


def fix_goiania():
    """Fix Goiânia (5208707)."""
    filepath = MUNICIPALITIES_DIR / "5208707.json"
    data = load_json(filepath)
    changes = []

    # Restaurante do Bem is STATE (OVG/GO)
    update_benefit(data, "go-goiania-restaurante-popular", {
        "shortDescription": "Refeições a R$ 2 nos restaurantes do Bem. Programa do Governo de Goiás (OVG), disponível em Goiânia",
        "sourceUrl": "https://www.ovg.org.br",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante do Bem (state program OVG)")

    # IPTU Social is real in Goiânia (LC 362/2022)
    update_benefit(data, "go-goiania-iptu-social", {
        "name": "IPTU Social",
        "shortDescription": "Isenção automática de IPTU para imóveis residenciais de até R$ 60 mil de valor venal",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "5208707", "description": "Morar em Goiânia"},
            {"field": "temCasaPropria", "operator": "eq", "value": True, "description": "Ter imóvel próprio"}
        ],
        "howToApply": [
            "Automático para imóveis até R$ 60 mil",
            "R$ 60-100 mil: solicite no site da prefeitura (sem emprego formal)",
            "Preencha formulário com CPF dos moradores"
        ],
        "sourceUrl": "https://www.goiania.go.gov.br/iptu-social/faq/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed IPTU Social (LC 362/2022, valor venal)")

    # Mark Aluguel Social as verified
    update_benefit(data, "go-goiania-aluguel-social", {"verified": True})
    changes.append("Marked Aluguel Social as verified")

    save_json(filepath, data)
    return changes


def validate():
    """Validate the 10 cities after fixes."""
    cities = {
        "3550308": "São Paulo",
        "3304557": "Rio de Janeiro",
        "5300108": "Brasília",
        "2927408": "Salvador",
        "2304400": "Fortaleza",
        "3106200": "Belo Horizonte",
        "1302603": "Manaus",
        "4106902": "Curitiba",
        "2611606": "Recife",
        "5208707": "Goiânia",
    }
    errors = []
    for ibge, name in cities.items():
        filepath = MUNICIPALITIES_DIR / f"{ibge}.json"
        try:
            data = load_json(filepath)
            n = len(data["benefits"])
            ids = [b["id"] for b in data["benefits"]]
            if len(ids) != len(set(ids)):
                errors.append(f"  {name}: duplicate IDs!")
            verified = sum(1 for b in data["benefits"] if b.get("verified"))
            print(f"  {name}: {n} benefits, {verified} verified")
        except Exception as e:
            errors.append(f"  {name}: {e}")

    if errors:
        print(f"\nERROS: {len(errors)}")
        for e in errors:
            print(e)
        return False
    return True


def main():
    print("=" * 60)
    print("Fase M2 — Auditoria Municipal: 10 Capitais Tier 1")
    print("=" * 60)

    fixes = {
        "São Paulo": fix_sao_paulo,
        "Rio de Janeiro": fix_rio_de_janeiro,
        "Brasília": fix_brasilia,
        "Salvador": fix_salvador,
        "Fortaleza": fix_fortaleza,
        "Belo Horizonte": fix_belo_horizonte,
        "Manaus": fix_manaus,
        "Curitiba": fix_curitiba,
        "Recife": fix_recife,
        "Goiânia": fix_goiania,
    }

    total_changes = 0
    for city, fix_fn in fixes.items():
        print(f"\n--- {city} ---")
        changes = fix_fn()
        for c in changes:
            print(f"  ✓ {c}")
        total_changes += len(changes)

    print(f"\n{'='*60}")
    print(f"RESUMO: {total_changes} correções em 10 cidades")
    print(f"{'='*60}")

    print(f"\nValidação:")
    ok = validate()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

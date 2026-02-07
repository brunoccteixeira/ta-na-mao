#!/usr/bin/env python3
"""
Fase M3 — Auditoria Municipal: 16 Capitais Tier 2 + Grandes Cidades

Descobertas da pesquisa:
- Belém: Bora Belém CANCELADO (mar/2025). Restaurante Popular municipal (R$2). Integra Belém transporte.
- São Luís: Restaurante Popular é ESTADUAL (SEDES, R$1). Poucos programas municipais específicos.
- Teresina: Restaurante Popular municipal R$2. METRÔ TARIFA ZERO desde jan/2025! Único capital BR.
- Porto Alegre: Restaurante Popular GRATUITO (6 unidades). Auxílio Material Escolar real.
- Florianópolis: Rest. da Família e Trabalhador R$6 (fechado fev/2025). Tarifa Zero domingos.
- Vitória: Restaurante Popular R$3 (R$14 geral), GRÁTIS crianças/CadÚnico. Bônus Moradia até R$100k!
- Maceió: Restaurante Popular R$3 (11 unidades). Brota na Grota (maior programa social). Domingo é Livre.
- Aracaju: Restaurante Padre Pedro é ESTADUAL (Seasic, R$1). Poucos municipais.
- João Pessoa: Restaurante Popular R$1 (2 unidades + 6 cozinhas). RUP para universitários.
- Natal: Sem restaurante popular. Tarifa Social (50% feriados). Aluguel Social R$600.
- Campo Grande: Sem restaurante popular. Locação Social até R$1200/mês (100% casos especiais).
- Cuiabá: Restaurante Popular Elza Fortunato R$2. Passe Livre Estudantil. Casa Cuiabana R$25k.
- Palmas: 21 restaurantes credenciados R$3 (grátis ≤R$218). Cartão Estudante 75% subsídio.
- Boa Vista: Sem restaurante popular. Passe Livre Estudantil (2/dia).
- Macapá: Sem restaurante popular. PLE 58 passes/mês (estadual). Macapá Mais Qualificada.
- Porto Velho: Prato Fácil é ESTADUAL (R$2, 11 locais). Auxílio Emergencial Climático R$3k.
"""

import json
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
    before = len(data["benefits"])
    data["benefits"] = [b for b in data["benefits"] if b["id"] != benefit_id]
    return len(data["benefits"]) < before


def update_benefit(data, benefit_id, updates):
    for b in data["benefits"]:
        if b["id"] == benefit_id:
            b.update(updates)
            return True
    return False


def add_benefit(data, benefit):
    existing_ids = {b["id"] for b in data["benefits"]}
    if benefit["id"] not in existing_ids:
        data["benefits"].append(benefit)
        return True
    return False


# ============================================================
# 16 CAPITAIS TIER 2
# ============================================================

def fix_belem():
    """Belém (1501402) — Bora Belém CANCELADO, Restaurante Popular real."""
    filepath = MUNICIPALITIES_DIR / "1501402.json"
    data = load_json(filepath)
    changes = []

    # 1. Bora Belém was CANCELLED March 2025
    update_benefit(data, "pa-belem-bora-belem", {
        "shortDescription": "Programa CANCELADO em março de 2025 pela Câmara Municipal. Não está mais disponível",
        "status": "inactive",
        "verified": True,
    })
    changes.append("Marked Bora Belém as CANCELLED (March 2025)")

    # 2. Fix Restaurante Popular (municipal, R$2, Banco do Povo)
    update_benefit(data, "pa-belem-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Refeições a R$ 2 no Restaurante Popular de Belém (Banco do Povo). Café da manhã R$ 0,50",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Almoço R$ 2, café R$ 0,50"},
        "sourceUrl": "https://bancodopovo.belem.pa.gov.br/programas/restaurante-popular/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Belém (R$2, Banco do Povo)")

    save_json(filepath, data)
    return changes


def fix_sao_luis():
    """São Luís (2111300) — Restaurante é ESTADUAL."""
    filepath = MUNICIPALITIES_DIR / "2111300.json"
    data = load_json(filepath)
    changes = []

    # Restaurante Popular is STATE program (SEDES MA)
    update_benefit(data, "ma-saoluis-restaurante-popular", {
        "shortDescription": "Refeições a R$ 1 nos Restaurantes Populares. Programa do Governo do Estado do Maranhão (SEDES), 17 unidades em São Luís",
        "sourceUrl": "https://sedes.ma.gov.br/servicos/restaurantes-populares",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante Popular (STATE program SEDES MA)")

    save_json(filepath, data)
    return changes


def fix_teresina():
    """Teresina (2211001) — Metrô Tarifa Zero, Restaurante R$2."""
    filepath = MUNICIPALITIES_DIR / "2211001.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (municipal, R$2, reaberto abr/2025)
    update_benefit(data, "pi-teresina-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Refeições a R$ 2 no Restaurante Popular do Mercado Central de Teresina (reinaugurado 2025)",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Refeição por R$ 2"},
        "sourceUrl": "https://pmt.pi.gov.br/2025/04/14/com-comida-de-qualidade-a-preco-acessivel-restaurante-popular-de-teresina-e-reinaugurado/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Teresina (R$2)")

    # 2. Fix Transporte Social → Metrô Tarifa Zero (único no Brasil!)
    update_benefit(data, "pi-teresina-transporte-social", {
        "name": "Metrô Tarifa Zero",
        "shortDescription": "Metrô de Teresina é totalmente gratuito desde janeiro de 2025. Única capital do Brasil com metrô tarifa zero",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Tarifa zero (gratuito)"},
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "2211001", "description": "Morar em Teresina"}
        ],
        "whereToApply": "Estações do Metrô de Teresina",
        "documentsRequired": [],
        "howToApply": [
            "Basta embarcar no metrô",
            "Gratuito para todos desde jan/2025",
            "Funciona de segunda a sábado"
        ],
        "sourceUrl": "https://www.pi.gov.br/noticia/metro-de-teresina-tera-tarifa-zero-a-partir-de-janeiro-de-2025",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Metrô Tarifa Zero (único no Brasil)")

    save_json(filepath, data)
    return changes


def fix_porto_alegre():
    """Porto Alegre (4314902) — Restaurante GRATUITO, customs verified."""
    filepath = MUNICIPALITIES_DIR / "4314902.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (GRATUITO, 6 unidades!)
    update_benefit(data, "rs-portoalegre-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Refeições GRATUITAS nos 6 restaurantes populares de Porto Alegre. Almoço de segunda a sexta (Centro funciona 7 dias)",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Refeição gratuita"},
        "sourceUrl": "https://prefeitura.poa.br/carta-de-servicos/restaurantes-populares",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular POA (GRATUITO, 6 unidades)")

    # 2. Mark customs as verified
    for bid in ["rs-portoalegre-todo-jovem-escola", "rs-portoalegre-pim-primeira-infancia",
                 "rs-portoalegre-auxilio-material-escolar", "rs-portoalegre-passe-livre-poatransporte"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked 4 custom programs as verified")

    save_json(filepath, data)
    return changes


def fix_florianopolis():
    """Florianópolis (4209102) — Restaurante da Família (R$6), Tarifa Zero domingos."""
    filepath = MUNICIPALITIES_DIR / "4209102.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular → Restaurante da Família e do Trabalhador
    update_benefit(data, "sc-florianopolis-restaurante-popular", {
        "name": "Restaurante da Família e do Trabalhador",
        "shortDescription": "Refeições a R$ 6 (almoço/jantar) e R$ 3 (café). 50% desconto para renda até 1 SM. Status: previsão de reabertura 2025",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Almoço R$ 6 (R$ 3 para baixa renda)"},
        "sourceUrl": "https://www.pmf.sc.gov.br",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante da Família e do Trabalhador (R$6/R$3)")

    save_json(filepath, data)
    return changes


def fix_vitoria():
    """Vitória (3205309) — Restaurante Popular R$3, Bônus Moradia R$100k."""
    filepath = MUNICIPALITIES_DIR / "3205309.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (R$3 CadÚnico, R$14 geral, GRÁTIS crianças)
    update_benefit(data, "es-vitoria-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Almoço R$ 3 (CadÚnico) ou R$ 14 (público geral). Gratuito para crianças até 12 anos e pessoas em situação de rua com CadÚnico",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Almoço R$ 3 (CadÚnico), grátis crianças ≤12 anos"},
        "sourceUrl": "https://www.vitoria.es.gov.br/noticia/inauguracao-do-novo-restaurante-popular-de-vitoria-atrai-moradores-e-emociona-familias-54350",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Vitória (R$3 CadÚnico, grátis crianças)")

    # 2. Fix Habitação → Bônus Moradia (até R$100k!)
    update_benefit(data, "es-vitoria-habitacao-municipal", {
        "name": "Bônus Moradia",
        "shortDescription": "Subsídio de até R$ 100 mil para compra da casa própria em Vitória",
        "estimatedValue": {"type": "one_time", "min": 0, "max": 100000, "description": "Subsídio de até R$ 100.000"},
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "3205309", "description": "Morar em Vitória"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}
        ],
        "whereToApply": "Secretaria de Habitação de Vitória",
        "howToApply": [
            "Procure a Secretaria de Habitação",
            "Faça inscrição no programa",
            "Aguarde habilitação e sorteio"
        ],
        "sourceUrl": "https://www.vitoria.es.gov.br/noticias/programa-bonus-moradia-transforma-vidas-e-garante-dignidade-a-familias-de-vitoria-54660",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Habitação → Bônus Moradia (até R$100k)")

    save_json(filepath, data)
    return changes


def fix_maceio():
    """Maceió (2704302) — Restaurante Popular R$3, Brota na Grota, Domingo é Livre."""
    filepath = MUNICIPALITIES_DIR / "2704302.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (municipal, R$3, 11 unidades)
    update_benefit(data, "al-maceio-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Almoço a R$ 3 e café a R$ 1 nas 11 unidades do Restaurante Popular de Maceió",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Almoço R$ 3, café R$ 1"},
        "sourceUrl": "https://maceio.al.gov.br/noticias/semdes/unidades-do-restaurante-popular-oferecem-refeicoes-de-qualidade-com-precos-acessiveis",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Maceió (R$3, 11 unidades)")

    # 2. Fix Transporte Social → Domingo é Livre + Passe Livre Estudantil
    update_benefit(data, "al-maceio-transporte-social", {
        "name": "Domingo é Livre + Passe Livre Estudantil",
        "shortDescription": "Ônibus gratuito todo domingo para todos. Estudantes: 44 passes gratuitos/mês",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "2704302", "description": "Morar em Maceió"}
        ],
        "whereToApply": "Postos DMTT ou site da prefeitura",
        "howToApply": [
            "Domingo: basta embarcar (gratuito para todos)",
            "Estudantes: solicite Passe Livre no DMTT",
            "Necessário Cartão Vamu"
        ],
        "sourceUrl": "https://maceio.al.gov.br/noticias/dmtt/passe-livre-impulsiona-crescimento-de-mais-de-110-no-uso-do-transporte-publico-por-estudantes",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Domingo é Livre + Passe Livre Estudantil")

    # 3. Mark customs as verified
    update_benefit(data, "al-maceio-auxilio-moradia", {"verified": True})
    changes.append("Marked Auxílio-Moradia as verified")

    save_json(filepath, data)
    return changes


def fix_aracaju():
    """Aracaju (2800308) — Restaurante é ESTADUAL, poucos municipais."""
    filepath = MUNICIPALITIES_DIR / "2800308.json"
    data = load_json(filepath)
    changes = []

    # Restaurante Padre Pedro is STATE (Seasic/SE)
    update_benefit(data, "se-aracaju-restaurante-popular", {
        "name": "Restaurante Popular Padre Pedro",
        "shortDescription": "Almoço e jantar a R$ 1 nos restaurantes Padre Pedro. Programa do Governo do Estado de Sergipe (Seasic), 3 unidades em Aracaju",
        "sourceUrl": "https://www.se.gov.br/noticias/inclusao-social/governo_de_sergipe_oferta_almoco_e_jantar_por_r_1_00_no_restaurante_padre_pedro",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Restaurante Padre Pedro (STATE program Seasic/SE)")

    save_json(filepath, data)
    return changes


def fix_joao_pessoa():
    """João Pessoa (2507507) — Restaurante Popular R$1, Cozinhas Comunitárias."""
    filepath = MUNICIPALITIES_DIR / "2507507.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (municipal, R$1, 2 unidades)
    update_benefit(data, "pb-joaopessoa-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Refeições a R$ 1 nos 2 restaurantes populares de João Pessoa (Varadouro e Mangabeira) + 6 cozinhas comunitárias",
        "sourceUrl": "https://www.joaopessoa.pb.gov.br/noticias/prefeitura-de-joao-pessoa-chega-a-quase-15-milhao-de-refeicoes-distribuidas-em-2024/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular JP (R$1, 2 unidades + 6 cozinhas)")

    # 2. Mark customs as verified
    for bid in ["pb-joaopessoa-bolsa-universitaria", "pb-joaopessoa-renda-familia",
                 "pb-joaopessoa-cartao-alimentacao"]:
        update_benefit(data, bid, {"verified": True})
    changes.append("Marked Bolsa Universitária, Renda Família, Cartão Alimentação as verified")

    save_json(filepath, data)
    return changes


def fix_natal():
    """Natal (2408102) — Sem restaurante popular. Tarifa Social feriados."""
    filepath = MUNICIPALITIES_DIR / "2408102.json"
    data = load_json(filepath)
    changes = []

    # 1. No Restaurante Popular found — mark as unverified with note
    update_benefit(data, "rn-natal-restaurante-popular", {
        "shortDescription": "Programa de restaurante popular em Natal não confirmado. Verifique com a prefeitura se há unidades disponíveis",
        "verified": False,
    })
    changes.append("Marked Restaurante Popular Natal as unverified (not found)")

    # 2. Fix Transporte Social → Tarifa Social + Subsídio 40%
    update_benefit(data, "rn-natal-transporte-social", {
        "name": "Tarifa Social",
        "shortDescription": "50% de desconto na passagem de ônibus em feriados. Aprovado subsídio de 40% para custos operacionais a partir de 2026",
        "sourceUrl": "https://agorarn.com.br/ultimas/prefeitura-de-natal-define-calendario-da-tarifa-social-do-transporte-publico-para-2026/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Tarifa Social Natal")

    save_json(filepath, data)
    return changes


def fix_campo_grande():
    """Campo Grande (5002704) — Sem restaurante. Locação Social forte."""
    filepath = MUNICIPALITIES_DIR / "5002704.json"
    data = load_json(filepath)
    changes = []

    # 1. No Restaurante Popular found
    update_benefit(data, "ms-campogrande-restaurante-popular", {
        "shortDescription": "Programa de restaurante popular em Campo Grande não confirmado. Verifique com a prefeitura se há unidades disponíveis",
        "verified": False,
    })
    changes.append("Marked Restaurante Popular CG as unverified (not found)")

    # 2. Fix Habitação → Locação Social (até R$1200/mês, 100% casos especiais)
    update_benefit(data, "ms-campogrande-habitacao-municipal", {
        "name": "Programa de Locação Social",
        "shortDescription": "Subsídio de até 50% do aluguel (máximo R$ 1.200/mês). 100% para idosos, vítimas de violência doméstica e PCD",
        "estimatedValue": {"type": "monthly", "min": 300, "max": 1200, "description": "Até 50% do aluguel (máx R$ 1.200), 100% para idosos/PCD"},
        "sourceUrl": "https://www.campogrande.ms.gov.br/cgnoticias/noticia/prefeita-assina-nova-regulamentacao-do-programa-locacao-social-e-concede-100-de-subsidio-de-aluguel-em-casos-especiais/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Habitação → Locação Social (até R$1200, 100% especiais)")

    save_json(filepath, data)
    return changes


def fix_cuiaba():
    """Cuiabá (5103403) — Restaurante Popular R$2, Casa Cuiabana."""
    filepath = MUNICIPALITIES_DIR / "5103403.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (municipal, R$2, Elza Fortunato Biancardini)
    update_benefit(data, "mt-cuiaba-restaurante-popular", {
        "name": "Restaurante Popular Elza Fortunato",
        "shortDescription": "Refeições a R$ 2 no Restaurante Popular de Cuiabá (Rua Barão de Melgaço, Centro). Segunda a sexta, 11h-14h",
        "sourceUrl": "https://www.cuiaba.mt.gov.br/noticias/restaurante-popular-de-cuiaba-conquista-a-populacao-com-refeicoes-acessiveis-e-de-qualidade",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Cuiabá (R$2, Elza Fortunato)")

    # 2. Fix Habitação → Casa Cuiabana (subsídio R$25k)
    update_benefit(data, "mt-cuiaba-habitacao-municipal", {
        "name": "Casa Cuiabana",
        "shortDescription": "Programa habitacional com subsídio de até R$ 25 mil para famílias com renda até R$ 12 mil/mês",
        "estimatedValue": {"type": "one_time", "min": 0, "max": 25000, "description": "Subsídio de até R$ 25.000"},
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "5103403", "description": "Morar em Cuiabá"},
            {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"}
        ],
        "sourceUrl": "https://www.cuiaba.mt.gov.br/noticias/prefeitura-lanca-programa-habitacional-casa-cuiabana-e-abre-inscricoes",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Habitação → Casa Cuiabana (R$25k)")

    save_json(filepath, data)
    return changes


def fix_palmas():
    """Palmas (1721000) — 21 restaurantes credenciados, Cartão Estudante."""
    filepath = MUNICIPALITIES_DIR / "1721000.json"
    data = load_json(filepath)
    changes = []

    # 1. Fix Restaurante Popular (21 restaurantes credenciados, R$3, grátis ≤R$218)
    update_benefit(data, "to-palmas-restaurante-popular", {
        "name": "Restaurante Popular",
        "shortDescription": "Refeições a R$ 3 em 21 restaurantes credenciados. GRATUITO para quem tem renda per capita até R$ 218 (CadÚnico)",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "R$ 3 (grátis se renda ≤ R$ 218/pessoa)"},
        "sourceUrl": "https://www.palmas.to.gov.br/programa-restaurante-popular-passa-a-contar-com-21-empreendimentos-cadastrados/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Verified Restaurante Popular Palmas (21 locais, R$3/grátis)")

    # 2. Fix Transporte → Cartão do Estudante (75% subsídio)
    update_benefit(data, "to-palmas-transporte-social", {
        "name": "Cartão do Estudante",
        "shortDescription": "75% de subsídio no passe mensal para estudantes de ensino superior/técnico de baixa renda (600 vagas)",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "1721000", "description": "Morar em Palmas"},
            {"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante universitário/técnico"},
            {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no CadÚnico"}
        ],
        "whereToApply": "Portal cidadao.palmas.to.gov.br",
        "howToApply": [
            "Acesse cidadao.palmas.to.gov.br",
            "Inscreva-se no Cartão do Estudante",
            "Necessário 75% de frequência e 80% de aprovação"
        ],
        "sourceUrl": "https://diariodotransporte.com.br/2025/02/08/prefeitura-de-palmas-to-abre-inscricoes-para-cartao-do-estudante-no-transporte-para-alunos-de-baixa-renda/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Cartão do Estudante (75% subsídio)")

    save_json(filepath, data)
    return changes


def fix_boa_vista():
    """Boa Vista (1400100) — Sem restaurante. Passe Livre Estudantil."""
    filepath = MUNICIPALITIES_DIR / "1400100.json"
    data = load_json(filepath)
    changes = []

    # 1. No Restaurante Popular found
    update_benefit(data, "rr-boavista-restaurante-popular", {
        "shortDescription": "Programa de restaurante popular em Boa Vista não confirmado. Verifique com a prefeitura se há unidades disponíveis",
        "verified": False,
    })
    changes.append("Marked Restaurante Popular BV as unverified (not found)")

    # 2. Fix Transporte → Passe Livre Estudantil (2 passes/dia)
    update_benefit(data, "rr-boavista-transporte-social", {
        "name": "Passe Livre Estudantil",
        "shortDescription": "2 passes gratuitos por dia para estudantes em dias letivos. Necessário Boa Vista Card Estudante (6.000+ cadastrados)",
        "eligibilityRules": [
            {"field": "municipioIbge", "operator": "eq", "value": "1400100", "description": "Morar em Boa Vista"},
            {"field": "estudante", "operator": "eq", "value": True, "description": "Ser estudante com 50% de frequência"}
        ],
        "whereToApply": "Terminal Urbano de Boa Vista (sala 4)",
        "documentsRequired": ["RG", "CPF", "Declaração de matrícula", "Comprovante de residência"],
        "howToApply": [
            "Vá ao Terminal Urbano sala 4",
            "Apresente declaração de matrícula",
            "Cartão válido por 6 meses"
        ],
        "sourceUrl": "https://boavista.rr.gov.br/noticias/2026/2/passe-livre-mais-de-6-mil-estudantes-ja-contam-com-beneficio-que-promove-mobilidade-e-incentivo-a-educacao",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Transporte → Passe Livre Estudantil BV (2/dia)")

    save_json(filepath, data)
    return changes


def fix_macapa():
    """Macapá (1600303) — Sem restaurante. PLE estadual. Qualificação municipal."""
    filepath = MUNICIPALITIES_DIR / "1600303.json"
    data = load_json(filepath)
    changes = []

    # 1. No Restaurante Popular found
    update_benefit(data, "ap-macapa-restaurante-popular", {
        "shortDescription": "Programa de restaurante popular em Macapá não confirmado. Verifique com a prefeitura se há unidades disponíveis",
        "verified": False,
    })
    changes.append("Marked Restaurante Popular Macapá as unverified (not found)")

    # 2. Fix Capacitação → Macapá Mais Qualificada (real, 2000+ treinados)
    update_benefit(data, "ap-macapa-capacitacao-emprego", {
        "name": "Macapá Mais Qualificada",
        "shortDescription": "Cursos gratuitos de qualificação profissional (SENAI, SENAC, empreendedorismo). 2.000+ pessoas treinadas em 2025",
        "whereToApply": "Hub Macapá (Av. Padre Júlio, 1614, Centro)",
        "howToApply": [
            "Procure o Hub Macapá no Centro",
            "Inscreva-se nos cursos disponíveis",
            "Cursos de tecnologia, serviços e economia criativa"
        ],
        "sourceUrl": "https://agencia.macapa.ap.gov.br/prefeitura-de-macapa-qualifica-mais-de-2-000-pessoas-para-o-mercado-de-trabalho-em-2025/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Fixed Capacitação → Macapá Mais Qualificada")

    save_json(filepath, data)
    return changes


def fix_porto_velho():
    """Porto Velho (1100205) — Prato Fácil é ESTADUAL."""
    filepath = MUNICIPALITIES_DIR / "1100205.json"
    data = load_json(filepath)
    changes = []

    # 1. Prato Fácil is STATE (Rondônia)
    update_benefit(data, "ro-portovelho-restaurante-popular", {
        "name": "Prato Fácil",
        "shortDescription": "Refeições a R$ 2 em 11 restaurantes credenciados. Programa do Governo do Estado de Rondônia, disponível em Porto Velho",
        "estimatedValue": {"type": "monthly", "min": 0, "max": 0, "description": "Refeição por R$ 2"},
        "sourceUrl": "https://rondonia.ro.gov.br/com-refeicoes-ao-custo-de-r-2-restaurante-prato-facil-e-inaugurado-em-porto-velho/",
        "verified": True,
        "templateGenerated": False,
    })
    changes.append("Updated Prato Fácil (STATE program Rondônia, R$2)")

    save_json(filepath, data)
    return changes


def validate():
    """Validate the 16 Tier 2 cities after fixes."""
    cities = {
        "1501402": "Belém",
        "2111300": "São Luís",
        "2211001": "Teresina",
        "4314902": "Porto Alegre",
        "4209102": "Florianópolis",
        "3205309": "Vitória",
        "2704302": "Maceió",
        "2800308": "Aracaju",
        "2507507": "João Pessoa",
        "2408102": "Natal",
        "5002704": "Campo Grande",
        "5103403": "Cuiabá",
        "1721000": "Palmas",
        "1400100": "Boa Vista",
        "1600303": "Macapá",
        "1100205": "Porto Velho",
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
    print("Fase M3 — Auditoria Municipal: 16 Capitais Tier 2")
    print("=" * 60)

    fixes = {
        "Belém": fix_belem,
        "São Luís": fix_sao_luis,
        "Teresina": fix_teresina,
        "Porto Alegre": fix_porto_alegre,
        "Florianópolis": fix_florianopolis,
        "Vitória": fix_vitoria,
        "Maceió": fix_maceio,
        "Aracaju": fix_aracaju,
        "João Pessoa": fix_joao_pessoa,
        "Natal": fix_natal,
        "Campo Grande": fix_campo_grande,
        "Cuiabá": fix_cuiaba,
        "Palmas": fix_palmas,
        "Boa Vista": fix_boa_vista,
        "Macapá": fix_macapa,
        "Porto Velho": fix_porto_velho,
    }

    total_changes = 0
    for city, fix_fn in fixes.items():
        print(f"\n--- {city} ---")
        changes = fix_fn()
        for c in changes:
            print(f"  ✓ {c}")
        total_changes += len(changes)

    print(f"\n{'='*60}")
    print(f"RESUMO: {total_changes} correções em 16 cidades")
    print(f"{'='*60}")

    print(f"\nValidação:")
    ok = validate()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

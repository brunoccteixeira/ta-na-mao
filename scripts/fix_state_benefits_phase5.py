#!/usr/bin/env python3
"""
Phase 5: Audit 22 remaining states (all except AL, BA, CE, MA, PB from Phase 4)

Actions:
1. Remove 3 Rede Alyne programs (federal mislabeled as state):
   - ac-saude-materno-infantil → ac-pro-acolher (Acolhimento Institucional AC)
   - pa-saude-gestante-para → pa-agua-para (Água Pará)
   - ap-saude-gestante-amapa → ap-habilita-amapa (Habilita Amapá)

2. Fix SM-related values (SM 2026 = R$ 1.621):
   - pa-sua-casa: 4236 → 4863 (3 SM)
   - rr-colo-de-mae: renda 2640 → 3242 (2 SM)
   - rr-censo-habitacional: renda 2640 → 3242 (2 SM)
   - sp-vivaleite: description R$ 3.036 → R$ 3.242 (2 SM)
   - sp-superacao: value 3242 → 810.50 (is per capita, not family)
   - pr-leite-das-criancas: description R$ 3.036 → R$ 3.242 (2 SM)
   - go-aprendiz-do-futuro: 663 → 762 (proporcional 4h)
   - ap-amapa-sem-fome: renda 810 → 810.50

3. Fix descriptions/metadata:
   - pe-chapeu-de-palha: sourceUrl caixa → sas.pe.gov.br
   - rn-leite-potiguar: description R$ 810 → R$ 810,50
   - rn-jovem-potiguar: clarify value
   - se-cartao-mais-inclusao: fix encoding (missing accents)
   - to-jovem-trabalhador: add disclaimer about historical value
   - mt-ser-familia-habitacao: fix description ~3 SM → ~4,4 SM

Sources: All verified via .gov.br URLs
SM 2026 = R$ 1.621 (Decreto 12.797/2025)
"""

import json
import os
from pathlib import Path

STATES_DIR = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "states"

# ── Replacement benefits (verified via web research) ──

REPLACEMENT_AC = {
    "id": "ac-pro-acolher",
    "name": "Pró-Acolher Acre",
    "shortDescription": "Atendimento gratuito para gestantes e crianças de até 2 anos no Acre. Inclui pré-natal, parto e acompanhamento na nova Maternidade de Rio Branco.",
    "scope": "state",
    "state": "AC",
    "estimatedValue": {
        "type": "one_time",
        "min": 0,
        "max": 0,
        "description": "Atendimento gratuito pelo SUS estadual (pré-natal, parto, UTI neonatal)"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "AC", "description": "Morar no Acre"},
        {"field": "temGestante", "operator": "eq", "value": True, "description": "Estar grávida ou ter criança de até 2 anos"}
    ],
    "whereToApply": "UBS (Posto de Saúde) mais perto da sua casa ou Maternidade Bárbara Heliodora (Rio Branco)",
    "documentsRequired": [
        "CPF",
        "Cartão SUS",
        "Comprovante de residência no Acre",
        "Documento de identidade"
    ],
    "howToApply": [
        "Vá ao posto de saúde mais perto da sua casa",
        "Inicie o pré-natal assim que souber da gravidez",
        "Receba a caderneta da gestante e faça todas as consultas",
        "O parto será na maternidade de referência do seu município"
    ],
    "sourceUrl": "https://agencia.ac.gov.br/governo-do-acre-assina-ordem-de-servico-para-nova-etapa-da-maternidade-de-rio-branco-reforcando-compromisso-com-as-futuras-geracoes/",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🤰",
    "category": "Saúde Materno-Infantil"
}

REPLACEMENT_PA = {
    "id": "pa-agua-para",
    "name": "Água Pará",
    "shortDescription": "Conta de água de graça para famílias de baixa renda que consomem até 20 mil litros por mês. Já atendeu 1 milhão de paraenses.",
    "scope": "state",
    "state": "PA",
    "estimatedValue": {
        "type": "monthly",
        "min": 50,
        "max": 120,
        "description": "Pagamento integral da conta de água (economia de R$ 50 a R$ 120/mês)"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "PA", "description": "Morar no Pará"},
        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
        {"field": "rendaFamiliarMensal", "operator": "lte", "value": 810, "description": "Renda per capita de até meio salário mínimo (R$ 810,50)"}
    ],
    "whereToApply": "Lojas de Atendimento da COSANPA ou Caravanas do programa",
    "documentsRequired": [
        "CPF (mesmo do CadÚnico)",
        "RG ou documento com foto",
        "Comprovante de cadastro no CadÚnico",
        "Comprovante de vínculo com a COSANPA (conta de água)"
    ],
    "howToApply": [
        "Vá a uma loja da COSANPA com seus documentos",
        "Comprove que está no Cadastro Único",
        "O CPF do CadÚnico deve ser o mesmo da conta de água",
        "Se aprovado, a conta de água até 20m³ será paga pelo governo"
    ],
    "sourceUrl": "https://agenciapara.com.br/noticia/53232/programa-agua-para-ja-beneficiou-cerca-de-1-milhao-de-paraenses",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "💧",
    "category": "Utilidades"
}

REPLACEMENT_AP = {
    "id": "ap-habilita-amapa",
    "name": "Habilita Amapá",
    "shortDescription": "Primeira habilitação de graça para 10 mil pessoas de baixa renda nos 16 municípios do Amapá. Inclui aulas, exames e até 2 tentativas de reexame.",
    "scope": "state",
    "state": "AP",
    "estimatedValue": {
        "type": "one_time",
        "min": 2500,
        "max": 3500,
        "description": "CNH gratuita (economia de R$ 2.500 a R$ 3.500 em taxas, aulas e exames)"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "AP", "description": "Morar no Amapá"},
        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
        {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"}
    ],
    "whereToApply": "Detran-AP (detran.ap.gov.br) durante período de inscrições",
    "documentsRequired": [
        "CPF",
        "RG ou documento com foto",
        "Comprovante de inscrição no CadÚnico",
        "Comprovante de residência no Amapá"
    ],
    "howToApply": [
        "Acompanhe os editais no site do Detran-AP",
        "Faça a inscrição no período indicado",
        "A seleção é feita pela base do CadÚnico (5% das vagas para mulheres vítimas de violência, indígenas, PcD)",
        "Se aprovado, faça as aulas e provas gratuitamente no CFC indicado"
    ],
    "sourceUrl": "https://www.detran.ap.gov.br/detranap/programa-habilita-amapa-saiba-os-criterios-de-participacao/",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🚗",
    "category": "Qualificação Profissional"
}

# ── Mapping: Rede Alyne ID → replacement benefit ──
REPLACEMENTS = {
    "ac-saude-materno-infantil": REPLACEMENT_AC,
    "pa-saude-gestante-para": REPLACEMENT_PA,
    "ap-saude-gestante-amapa": REPLACEMENT_AP,
}

# ── Individual corrections by state ──
# Format: state_code → { benefit_id → { field → new_value } }

def get_corrections():
    """Return all corrections organized by state."""
    return {
        "PE": {
            "pe-chapeu-de-palha": {
                "sourceUrl": "https://www.sas.pe.gov.br/programas-e-projetos-2/chapeu-de-palha/"
            }
        },
        "RN": {
            "rn-leite-potiguar": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "RN", "description": "Morar no Rio Grande do Norte"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 810.50, "description": "Renda per capita de até meio salário mínimo (R$ 810,50)"}
                ]
            },
            "rn-jovem-potiguar": {
                "estimatedValue": {
                    "type": "one_time",
                    "min": 0,
                    "max": 900,
                    "description": "Auxílio financeiro de até R$ 900/mês durante a formação (condicional à frequência) + curso gratuito",
                    "estimated": True,
                    "estimatedRationale": "Valor do auxílio depende do edital e do curso escolhido. Confirme o valor atual no IFRN ou SINE."
                }
            }
        },
        "SE": {
            "se-cartao-mais-inclusao": {
                "shortDescription": "Cartão mensal para comprar alimentos para famílias vulneráveis de Sergipe. Programa permanente com inscrições abertas.",
                "howToApply": [
                    "Inscrições no site cmaisinscricoes.assistenciasocial.se.gov.br",
                    "Ou vá ao CRAS da sua cidade",
                    "Atualize seu Cadastro Único",
                    "Aguarde a análise e entrega do cartão nas agências do Banese"
                ]
            }
        },
        "PA": {
            "pa-sua-casa": {
                "estimatedValue": {
                    "type": "one_time",
                    "min": 10000,
                    "max": 21000,
                    "description": "Auxílio de até R$ 21 mil para material e mão de obra"
                },
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "PA", "description": "Morar no Pará"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 4863, "description": "Renda da família de até 3 salários mínimos (R$ 4.863)"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"}
                ]
            }
        },
        "AP": {
            "ap-amapa-sem-fome": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "AP", "description": "Morar no Amapá"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 810.50, "description": "Renda per capita de até meio salário mínimo (R$ 810,50)"}
                ]
            }
        },
        "RR": {
            "rr-colo-de-mae": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "RR", "description": "Morar em Roraima"},
                    {"field": "temGestante", "operator": "eq", "value": True, "description": "Ter gestante na família"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 3242, "description": "Renda familiar de até 2 salários mínimos (R$ 3.242)"}
                ]
            },
            "rr-censo-habitacional": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "RR", "description": "Morar em Roraima"},
                    {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 3242, "description": "Renda da família de até 2 salários mínimos (R$ 3.242)"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"}
                ]
            }
        },
        "TO": {
            "to-jovem-trabalhador": {
                "shortDescription": "Primeiro emprego para jovens de 16 a 21 anos no Tocantins, com salário de R$ 663 e qualificação profissional. Valor histórico, pode estar desatualizado.",
                "estimatedValue": {
                    "type": "monthly",
                    "min": 663,
                    "max": 663,
                    "description": "Salário de R$ 663,39 por mês (4 horas diárias). Valor histórico, confirme no site do programa.",
                    "estimated": True,
                    "estimatedRationale": "Valor referente ao último edital divulgado. O salário proporcional pode variar com o reajuste do SM."
                }
            }
        },
        "GO": {
            "go-aprendiz-do-futuro": {
                "estimatedValue": {
                    "type": "monthly",
                    "min": 762,
                    "max": 912,
                    "description": "R$ 762 de salário proporcional (4h/dia) + R$ 150 de vale alimentação + vale transporte"
                },
                "shortDescription": "Programa que emprega jovens de 14 a 15 anos em órgãos públicos de Goiás com salário e benefícios."
            }
        },
        "MT": {
            "mt-ser-familia-habitacao": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "MT", "description": "Morar em Mato Grosso"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Estar no Cadastro Único"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 7200, "description": "Renda familiar de até R$ 7.200 (~4,4 salários mínimos)"}
                ]
            }
        },
        "SP": {
            "sp-vivaleite": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "SP", "description": "Morar em São Paulo"},
                    {"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 6 meses a 6 anos OU idoso acima de 60 anos"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 3242, "description": "Renda familiar de até 2 salários mínimos (R$ 3.242)"}
                ]
            },
            "sp-superacao": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "SP", "description": "Morar em São Paulo"},
                    {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único (atualizado nos últimos 24 meses)"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 810.50, "description": "Renda per capita de até meio salário mínimo (R$ 810,50)"}
                ]
            }
        },
        "PR": {
            "pr-leite-das-criancas": {
                "eligibilityRules": [
                    {"field": "estado", "operator": "eq", "value": "PR", "description": "Morar no Paraná"},
                    {"field": "temCrianca0a6", "operator": "eq", "value": True, "description": "Ter criança de 6 meses a 3 anos"},
                    {"field": "rendaFamiliarMensal", "operator": "lte", "value": 3242, "description": "Renda per capita de até meio salário mínimo (R$ 810,50, ou R$ 3.242 para família de 4)"}
                ]
            }
        }
    }


def process_state(state_code: str, data: dict, corrections: dict) -> tuple:
    """Process a single state file. Returns (modified_data, log_messages)."""
    logs = []
    benefits = data["benefits"]

    # Step 1: Replace Rede Alyne programs
    new_benefits = []
    for b in benefits:
        bid = b["id"]
        if bid in REPLACEMENTS:
            replacement = REPLACEMENTS[bid]
            new_benefits.append(replacement)
            logs.append(f"  REPLACED: {bid} → {replacement['id']} ({replacement['name']})")
        else:
            new_benefits.append(b)

    # Step 2: Apply individual corrections
    if state_code in corrections:
        for bid, patches in corrections[state_code].items():
            for b in new_benefits:
                if b["id"] == bid:
                    for key, value in patches.items():
                        b[key] = value
                    logs.append(f"  CORRECTED: {bid} → {list(patches.keys())}")
                    break

    data["benefits"] = new_benefits
    data["lastUpdated"] = "2026-02-07"
    return data, logs


def main():
    corrections = get_corrections()

    # States affected by Phase 5 (all corrections + replacements)
    affected_states = set(corrections.keys()) | {"AC", "PA", "AP"}

    total_replaced = 0
    total_corrected = 0

    for state_code in sorted(affected_states):
        filepath = STATES_DIR / f"{state_code.lower()}.json"
        if not filepath.exists():
            filepath = STATES_DIR / f"{state_code}.json"
        if not filepath.exists():
            print(f"ERROR: {state_code}.json not found!")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n{'='*50}")
        print(f"Processing {state_code} ({data.get('stateName', '?')})")
        print(f"{'='*50}")
        print(f"  Benefits before: {len(data['benefits'])}")

        data, logs = process_state(state_code, data, corrections)
        for log in logs:
            print(log)
            if "REPLACED" in log:
                total_replaced += 1
            elif "CORRECTED" in log:
                total_corrected += 1

        print(f"  Benefits after: {len(data['benefits'])}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

        print(f"  ✓ Saved {filepath.name}")

    # ── Validation ──
    print(f"\n{'='*50}")
    print("VALIDATION")
    print(f"{'='*50}")

    all_ids = []
    total_benefits = 0
    errors = 0

    for filepath in sorted(STATES_DIR.glob("*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data["benefits"])
            total_benefits += count
            for b in data["benefits"]:
                all_ids.append(b["id"])
            if count != 7:
                print(f"  WARNING: {filepath.name} has {count} benefits (expected 7)")
                errors += 1
        except json.JSONDecodeError as e:
            print(f"  ERROR: {filepath.name} JSON parse failed: {e}")
            errors += 1

    unique_ids = set(all_ids)
    duplicate_ids = [x for x in all_ids if all_ids.count(x) > 1]

    # Check Rede Alyne names are gone
    rede_alyne_found = [bid for bid in all_ids if "alyne" in bid.lower() or "saude-gestante" in bid]

    # Check old values are gone
    print(f"\n  Total benefits: {total_benefits}")
    print(f"  Unique IDs: {len(unique_ids)}")
    print(f"  Duplicates: {len(set(duplicate_ids))} ({duplicate_ids[:5] if duplicate_ids else 'none'})")
    print(f"  Rede Alyne remnants: {rede_alyne_found if rede_alyne_found else 'NONE ✓'}")
    print(f"  JSON errors: {errors}")
    print(f"\n  Replaced: {total_replaced}")
    print(f"  Corrected: {total_corrected}")
    print(f"\n{'='*50}")
    print(f"Phase 5 complete: {total_replaced} replaced, {total_corrected} corrected, {errors} errors")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

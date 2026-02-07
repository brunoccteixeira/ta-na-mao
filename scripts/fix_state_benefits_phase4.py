#!/usr/bin/env python3
"""
Phase 4: Fix Nordeste 1 audit findings (AL, BA, CE, MA, PB)

Actions:
1. Remove 4 fabricated programs:
   - al-nossa-casa (AL) → replace with al-cnh-trabalhador
   - ce-cartao-superacao (CE) → replace with ce-cnh-popular
   - ce-programa-hora-de-construir (CE) → replace with ce-entrada-moradia
   - pb-pbsocial (PB) → replace with pb-cartao-alimentacao

2. Apply individual corrections:
   - AL: al-cartao-cria values (min/max 100/300 → 150/150)
   - BA: ba-primeiro-emprego SM update (1600 → 1621)
   - MA: ma-maranhao-livre-da-fome value (200→300, max 350→450)
   - MA: ma-cheque-gestante renda (1600 → 1621)

Sources: All verified via .gov.br URLs in Phase 4 research
"""

import json
import os
from pathlib import Path

STATES_DIR = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "states"

# ── Replacement benefits (verified via web research) ──

REPLACEMENT_AL = {
    "id": "al-cnh-trabalhador",
    "name": "CNH do Trabalhador",
    "shortDescription": "Primeira habilitação de graça (carro ou moto) para quem é de baixa renda em Alagoas. O governo paga taxas, exames e aulas.",
    "scope": "state",
    "state": "AL",
    "estimatedValue": {
        "type": "one_time",
        "min": 2000,
        "max": 2000,
        "description": "Economia de ~R$ 2.000 (custo total da CNH coberto pelo governo)"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "AL", "description": "Morar em Alagoas"},
        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
        {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"}
    ],
    "whereToApply": "Site do Detran-AL (www.detran.al.gov.br) quando abrir inscrição",
    "documentsRequired": [
        "CPF",
        "RG ou documento com foto",
        "NIS do Cadastro Único",
        "Comprovante de residência em Alagoas",
        "Comprovante de escolaridade (ensino fundamental completo)"
    ],
    "howToApply": [
        "Atualize seu Cadastro Único no CRAS",
        "Fique atento ao edital no site do Detran-AL",
        "Quando abrir inscrição, cadastre-se online em www.detran.al.gov.br",
        "Se selecionado, faça matrícula no CFC indicado e inicie as aulas"
    ],
    "sourceUrl": "https://www.detran.al.gov.br/habilitacao/cnh-trabalhador/",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🚗",
    "category": "Transporte"
}

REPLACEMENT_CE_1 = {
    "id": "ce-cnh-popular",
    "name": "CNH Popular Ceará",
    "shortDescription": "Primeira habilitação gratuita (carro ou moto) para pessoas de baixa renda no Ceará. 35 mil vagas em 2025.",
    "scope": "state",
    "state": "CE",
    "estimatedValue": {
        "type": "one_time",
        "min": 1500,
        "max": 2500,
        "description": "CNH gratuita (economia de R$ 1.500 a R$ 2.500 em taxas e aulas)"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "CE", "description": "Morar no Ceará"},
        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
        {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"}
    ],
    "whereToApply": "Site do Detran-CE (detran.ce.gov.br) ou postos do Detran nos municípios",
    "documentsRequired": [
        "CPF",
        "RG",
        "NIS (Número do Cadastro Único)",
        "Comprovante de residência no Ceará"
    ],
    "howToApply": [
        "Acesse detran.ce.gov.br e procure CNH Popular",
        "Faça a inscrição no período do edital",
        "Apresente os documentos e comprove baixa renda",
        "Se aprovado, faça as aulas e provas gratuitamente"
    ],
    "sourceUrl": "https://www.detran.ce.gov.br/carteira-de-motorista-popular/",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🚗",
    "category": "Qualificação Profissional"
}

REPLACEMENT_CE_2 = {
    "id": "ce-entrada-moradia",
    "name": "Entrada Moradia Ceará",
    "shortDescription": "R$ 20 mil de ajuda do governo do Ceará para pagar a entrada da casa própria pelo Minha Casa, Minha Vida.",
    "scope": "state",
    "state": "CE",
    "estimatedValue": {
        "type": "one_time",
        "min": 20000,
        "max": 20000,
        "description": "Subsídio de R$ 20.000 para entrada + ITBI e registro pagos pelo programa"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "CE", "description": "Morar no Ceará há pelo menos 1 ano"},
        {"field": "temCasaPropria", "operator": "eq", "value": False, "description": "Não ter casa própria"},
        {"field": "rendaFamiliarMensal", "operator": "lte", "value": 4700, "description": "Renda familiar de até R$ 4.700 por mês"},
        {"field": "idade", "operator": "gte", "value": 18, "description": "Ter 18 anos ou mais"}
    ],
    "whereToApply": "Site entradamoradia.ce.gov.br ou correspondentes Caixa",
    "documentsRequired": [
        "CPF e RG",
        "Comprovante de residência no Ceará (mínimo 1 ano)",
        "Comprovante de renda",
        "Certidão negativa de propriedade de imóvel"
    ],
    "howToApply": [
        "Acesse entradamoradia.ce.gov.br",
        "Faça o pré-cadastro com seus dados",
        "Escolha o empreendimento aprovado pelo MCMV",
        "Apresente os documentos na Caixa e finalize o financiamento"
    ],
    "sourceUrl": "https://www.entradamoradia.ce.gov.br/",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🏠",
    "category": "Habitação"
}

REPLACEMENT_PB = {
    "id": "pb-cartao-alimentacao",
    "name": "Cartão Alimentação PB",
    "shortDescription": "Cartão com R$ 50 por mês para comprar comida em mercados credenciados da Paraíba. Atende 52 mil famílias.",
    "scope": "state",
    "state": "PB",
    "estimatedValue": {
        "type": "monthly",
        "min": 50,
        "max": 50,
        "description": "R$ 50 por mês no cartão, só para comprar alimentos"
    },
    "eligibilityRules": [
        {"field": "estado", "operator": "eq", "value": "PB", "description": "Morar na Paraíba"},
        {"field": "cadastradoCadunico", "operator": "eq", "value": True, "description": "Inscrito no Cadastro Único"},
        {"field": "rendaFamiliarMensal", "operator": "lte", "value": 872, "description": "Renda familiar de até R$ 872 (equivale a ~R$ 218 por pessoa para família de 4)"}
    ],
    "whereToApply": "CRAS do seu município",
    "documentsRequired": [
        "CPF de todos da família",
        "NIS do Cadastro Único",
        "Comprovante de endereço"
    ],
    "howToApply": [
        "Vá ao CRAS da sua cidade",
        "Atualize seu Cadastro Único",
        "A seleção é feita pelo mapa de insegurança alimentar",
        "Se selecionado, receba o cartão e use em mercados credenciados"
    ],
    "sourceUrl": "https://paraiba.pb.gov.br/diretas/secretaria-de-desenvolvimento-humano/programas/cartao-alimentacao",
    "lastUpdated": "2026-02-07",
    "status": "active",
    "icon": "🛒",
    "category": "Alimentação"
}

# ── Mapping: fabricated ID → replacement benefit ──
REPLACEMENTS = {
    "al-nossa-casa": REPLACEMENT_AL,
    "ce-cartao-superacao": REPLACEMENT_CE_1,
    "ce-programa-hora-de-construir": REPLACEMENT_CE_2,
    "pb-pbsocial": REPLACEMENT_PB,
}

# ── Individual corrections ──
CORRECTIONS = {
    "AL": {
        "al-cartao-cria": {
            "estimatedValue": {
                "type": "monthly",
                "min": 150,
                "max": 150,
                "description": "R$ 150 por mês por família com crianças de 0 a 6 anos"
            }
        }
    },
    "BA": {
        "ba-primeiro-emprego": {
            "estimatedValue": {
                "type": "monthly",
                "min": 1621,
                "max": 1621,
                "description": "Salário CLT (valor varia conforme função, mínimo R$ 1.621)"
            }
        }
    },
    "MA": {
        "ma-maranhao-livre-da-fome": {
            "estimatedValue": {
                "type": "monthly",
                "min": 300,
                "max": 450,
                "description": "R$ 300 base + R$ 50 por criança de 0 a 6 anos"
            },
            "shortDescription": "R$ 300 por mês + R$ 50 por criança de 0 a 6 anos para famílias em extrema pobreza. Atende 95 mil famílias."
        },
        "ma-cheque-gestante": {
            "eligibilityRules": [
                {"field": "estado", "operator": "eq", "value": "MA", "description": "Morar no Maranhão"},
                {"field": "temGestante", "operator": "eq", "value": True, "description": "Estar grávida"},
                {"field": "rendaFamiliarMensal", "operator": "lte", "value": 1621, "description": "Renda da família de até 1 salário mínimo (R$ 1.621)"}
            ]
        }
    }
}


def process_state(state_code: str, data: dict) -> tuple[dict, list[str]]:
    """Process a single state file. Returns (modified_data, log_messages)."""
    logs = []
    benefits = data["benefits"]

    # Step 1: Replace fabricated programs
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
    if state_code in CORRECTIONS:
        for bid, patches in CORRECTIONS[state_code].items():
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
    affected_states = {"AL", "BA", "CE", "MA", "PB"}
    total_replaced = 0
    total_corrected = 0

    for state_code in sorted(affected_states):
        filepath = STATES_DIR / f"{state_code}.json"
        if not filepath.exists():
            # Try lowercase
            filepath = STATES_DIR / f"{state_code.lower()}.json"
        if not filepath.exists():
            print(f"ERROR: {state_code}.json not found!")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n{'='*50}")
        print(f"Processing {state_code} ({data.get('stateName', '?')})")
        print(f"{'='*50}")
        print(f"  Benefits before: {len(data['benefits'])}")

        data, logs = process_state(state_code, data)
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

    # Check fabricated IDs are gone
    fabricated_gone = all(fid not in all_ids for fid in REPLACEMENTS.keys())

    print(f"\n  Total benefits: {total_benefits}")
    print(f"  Unique IDs: {len(unique_ids)}")
    print(f"  Duplicates: {len(set(duplicate_ids))} ({duplicate_ids[:5] if duplicate_ids else 'none'})")
    print(f"  Fabricated removed: {'YES ✓' if fabricated_gone else 'NO ✗'}")
    print(f"  JSON errors: {errors}")
    print(f"\n  Replaced: {total_replaced}")
    print(f"  Corrected: {total_corrected}")
    print(f"\n{'='*50}")
    print(f"Phase 4 complete: {total_replaced} replaced, {total_corrected} corrected, {errors} errors")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

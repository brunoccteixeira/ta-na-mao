#!/usr/bin/env python3
"""
Auditoria dos 15 benefícios federais da Phase H.

Correções:
A) 5 regras de elegibilidade com campos desconhecidos → campos válidos do CitizenProfile
B) 6 benefícios sem legalBasis → base legal pesquisada
C) 1 categoria errada → Bolsa Atleta "Cultura" → "Esporte"

Uso:
  python scripts/audit_federal_phase_h.py              # aplica correções
  python scripts/audit_federal_phase_h.py --dry-run    # mostra diff sem aplicar
"""

import json
import sys
from pathlib import Path

FEDERAL_JSON = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "federal.json"

DRY_RUN = "--dry-run" in sys.argv


def load_benefits():
    with open(FEDERAL_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_benefits(data):
    with open(FEDERAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def find_benefit(benefits, benefit_id):
    for b in benefits:
        if b["id"] == benefit_id:
            return b
    return None


def fix_eligibility_rules(benefits):
    """A) Corrigir campos desconhecidos pelo evaluator."""
    changes = []

    # federal-pnmpo: empreendedor → temMei, rendaBruta → rendaFamiliarMensal
    b = find_benefit(benefits, "federal-pnmpo")
    if b:
        old_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        b["eligibilityRules"] = [
            {
                "field": "temMei",
                "operator": "eq",
                "value": True,
                "description": "Ser MEI ou empreendedor de pequeno porte",
                "legalReference": "Art. 1º, Lei 13.636/2018"
            },
            {
                "field": "rendaFamiliarMensal",
                "operator": "lte",
                "value": 30000,
                "description": "Receita bruta anual de até R$ 360 mil (≈ R$ 30 mil/mês)",
                "legalReference": "Art. 1º, §1º, Lei 13.636/2018"
            }
        ]
        new_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        if old_rules != new_rules:
            changes.append("federal-pnmpo: empreendedor→temMei, rendaBruta→rendaFamiliarMensal")

    # federal-cras-paif: vulnerabilidadeSocial → cadastradoCadunico
    b = find_benefit(benefits, "federal-cras-paif")
    if b:
        old_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        b["eligibilityRules"] = [
            {
                "field": "cadastradoCadunico",
                "operator": "eq",
                "value": True,
                "description": "Inscrito no Cadastro Único (proxy para vulnerabilidade social)",
                "legalReference": "Resolução CNAS 109/2009"
            }
        ]
        new_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        if old_rules != new_rules:
            changes.append("federal-cras-paif: vulnerabilidadeSocial→cadastradoCadunico")

    # federal-credito-instalacao: assentado → agricultorFamiliar + moradiaZonaRural
    b = find_benefit(benefits, "federal-credito-instalacao")
    if b:
        old_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        b["eligibilityRules"] = [
            {
                "field": "agricultorFamiliar",
                "operator": "eq",
                "value": True,
                "description": "Ser agricultor familiar ou assentado da reforma agrária",
                "legalReference": "Decreto 11.451/2023"
            },
            {
                "field": "moradiaZonaRural",
                "operator": "eq",
                "value": True,
                "description": "Residir em zona rural (assentamento INCRA)",
                "legalReference": "Decreto 11.451/2023"
            }
        ]
        new_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        if old_rules != new_rules:
            changes.append("federal-credito-instalacao: assentado→agricultorFamiliar+moradiaZonaRural")

    # federal-pronera: assentado → agricultorFamiliar + moradiaZonaRural
    b = find_benefit(benefits, "federal-pronera")
    if b:
        old_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        b["eligibilityRules"] = [
            {
                "field": "agricultorFamiliar",
                "operator": "eq",
                "value": True,
                "description": "Ser assentado, acampado da reforma agrária ou trabalhador rural",
                "legalReference": "Decreto 7.352/2010"
            },
            {
                "field": "moradiaZonaRural",
                "operator": "eq",
                "value": True,
                "description": "Residir em zona rural ou assentamento",
                "legalReference": "Decreto 7.352/2010"
            },
            {
                "field": "idade",
                "operator": "gte",
                "value": 15,
                "description": "Ter 15 anos ou mais (para alfabetização) ou idade escolar",
                "legalReference": "Decreto 7.352/2010"
            }
        ]
        new_rules = json.dumps(b["eligibilityRules"], ensure_ascii=False)
        if old_rules != new_rules:
            changes.append("federal-pronera: assentado→agricultorFamiliar+moradiaZonaRural (mantém idade)")

    return changes


def fix_legal_basis(benefits):
    """B) Adicionar legalBasis ausente em 6 benefícios."""
    changes = []

    legal_basis_map = {
        "federal-auxilio-reconstrucao": {
            "laws": [
                {
                    "type": "medida_provisoria",
                    "number": "1.219/2024",
                    "description": "Auxílio Reconstrução para famílias atingidas por desastres",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/mpv/mpv1219.htm"
                },
                {
                    "type": "decreto",
                    "number": "11.219/2022",
                    "description": "Auxílio financeiro emergencial para atingidos por desastres",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/decreto/d11219.htm"
                }
            ]
        },
        "federal-cisternas": {
            "laws": [
                {
                    "type": "lei",
                    "number": "12.873/2013",
                    "description": "Programa Nacional de Apoio à Captação de Água de Chuva (Programa Cisternas), Art. 11",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12873.htm"
                }
            ]
        },
        "federal-tarifa-social-telecom": {
            "laws": [
                {
                    "type": "resolucao",
                    "number": "Resolução ANATEL 586/2012",
                    "description": "Acesso Individual Classe Especial (AICE) — Telefone Popular",
                    "url": "https://informacoes.anatel.gov.br/legislacao/resolucoes/2012/442-resolucao-586"
                }
            ]
        },
        "federal-credito-instalacao": {
            "laws": [
                {
                    "type": "decreto",
                    "number": "11.451/2023",
                    "description": "Regulamenta o Crédito Instalação para assentados da reforma agrária",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11451.htm"
                }
            ]
        },
        "federal-cras-paif": {
            "laws": [
                {
                    "type": "resolucao",
                    "number": "Resolução CNAS 109/2009",
                    "description": "Tipificação Nacional de Serviços Socioassistenciais",
                    "url": "https://www.mds.gov.br/webarquivos/publicacao/assistencia_social/Normativas/tipificacao.pdf"
                },
                {
                    "type": "lei",
                    "number": "8.742/1993",
                    "description": "Lei Orgânica de Assistência Social (LOAS)",
                    "url": "https://www.planalto.gov.br/ccivil_03/leis/l8742.htm"
                }
            ]
        },
        "federal-brasil-carinhoso": {
            "laws": [
                {
                    "type": "lei",
                    "number": "12.722/2012",
                    "description": "Ação Brasil Carinhoso (complemento Bolsa Família para primeira infância)",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12722.htm"
                },
                {
                    "type": "lei",
                    "number": "14.601/2023",
                    "description": "Lei do Bolsa Família (integrou o Brasil Carinhoso)",
                    "url": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14601.htm"
                }
            ]
        }
    }

    for benefit_id, legal_basis in legal_basis_map.items():
        b = find_benefit(benefits, benefit_id)
        if b:
            had_basis = "legalBasis" in b
            b["legalBasis"] = legal_basis
            if not had_basis:
                changes.append(f"{benefit_id}: legalBasis ADICIONADO")
            else:
                changes.append(f"{benefit_id}: legalBasis ATUALIZADO")

    return changes


def fix_category(benefits):
    """C) Corrigir categoria do Bolsa Atleta: Cultura → Esporte."""
    changes = []

    b = find_benefit(benefits, "federal-bolsa-atleta")
    if b and b.get("category") == "Cultura":
        b["category"] = "Esporte"
        changes.append("federal-bolsa-atleta: Cultura → Esporte")

    return changes


def main():
    data = load_benefits()
    benefits = data["benefits"]

    print("=" * 60)
    print("AUDITORIA FEDERAL PHASE H — 15 benefícios novos")
    print("=" * 60)

    # A) Eligibility rules
    print("\n--- A) Correções de elegibilidade ---")
    elig_changes = fix_eligibility_rules(benefits)
    for c in elig_changes:
        print(f"  ✓ {c}")
    if not elig_changes:
        print("  (nenhuma mudança)")

    # B) Legal basis
    print("\n--- B) Base legal (legalBasis) ---")
    legal_changes = fix_legal_basis(benefits)
    for c in legal_changes:
        print(f"  ✓ {c}")
    if not legal_changes:
        print("  (nenhuma mudança)")

    # C) Category
    print("\n--- C) Categorias ---")
    cat_changes = fix_category(benefits)
    for c in cat_changes:
        print(f"  ✓ {c}")
    if not cat_changes:
        print("  (nenhuma mudança)")

    total = len(elig_changes) + len(legal_changes) + len(cat_changes)
    print(f"\nTotal: {total} correções")

    if DRY_RUN:
        print("\n⚠️  --dry-run: nenhuma alteração salva.")
    else:
        save_benefits(data)
        print(f"\n✅ Salvo em {FEDERAL_JSON}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 3: Individual corrections per state based on audit findings.
Applies specific fixes for wrong values, names, eligibility rules, etc.
"""

import json
from pathlib import Path

STATES_DIR = Path("frontend/src/data/benefits/states")


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def find_benefit(benefits, bid):
    for b in benefits:
        if b.get("id") == bid:
            return b
    return None


def apply_fixes():
    changes_log = []

    # === PR (Paraná) ===
    data = load_json(STATES_DIR / "pr.json")

    b = find_benefit(data["benefits"], "pr-cartao-futuro")
    if b:
        b["shortDescription"] = "Subsídio de R$ 300/mês ao empregador que contratar jovem aprendiz de baixa renda no Paraná."
        b["estimatedValue"]["min"] = 0
        b["estimatedValue"]["max"] = 0
        b["estimatedValue"]["description"] = "Subsídio de R$ 300/mês ao empregador (R$ 450 para PcD). Jovem recebe salário de aprendiz pago pela empresa."
        b["category"] = "Emprego e Renda"
        changes_log.append("PR: pr-cartao-futuro - fixed value (R$900→subsidy to employer), description, category")

    b = find_benefit(data["benefits"], "pr-casa-facil")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal" and rule.get("value") == 6000:
                rule["value"] = 6484
                rule["description"] = "Renda familiar de até 4 salários mínimos (R$ 6.484)"
        changes_log.append("PR: pr-casa-facil - renda R$6000→R$6484 (4 SM 2026)")

    save_json(STATES_DIR / "pr.json", data)

    # === RS (Rio Grande do Sul) ===
    data = load_json(STATES_DIR / "rs.json")

    b = find_benefit(data["benefits"], "rs-devolve-icms")
    if b:
        b["shortDescription"] = "Devolução de ICMS para famílias de baixa renda: parcela fixa de R$ 100 + variável de até R$ 473 por trimestre."
        b["estimatedValue"]["min"] = 33
        b["estimatedValue"]["max"] = 191
        b["estimatedValue"]["description"] = "R$ 100 fixo + até R$ 473,82 variável por trimestre (até R$ 2.295/ano)"
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 4863
                rule["description"] = "Renda familiar de até 3 salários mínimos (R$ 4.863) OU receber Bolsa Família"
        changes_log.append("RS: rs-devolve-icms - fixed value (R$100 fixed + variable), renda R$3200→R$4863")

    b = find_benefit(data["benefits"], "rs-todo-jovem-na-escola")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "idade":
                rule["value"] = 14
                rule["description"] = "Estudante do ensino médio estadual (até 21 anos regular, até 29 anos EJA)"
        changes_log.append("RS: rs-todo-jovem-na-escola - fixed age range")

    b = find_benefit(data["benefits"], "rs-qualifica-rs")
    if b:
        b["name"] = "RS Qualificação Recomeçar"
        b["shortDescription"] = "Cursos de qualificação com bolsa de até R$ 1.500 para trabalhadores desempregados ou informais no RS."
        b["estimatedValue"]["min"] = 750
        b["estimatedValue"]["max"] = 1500
        b["estimatedValue"]["description"] = "Bolsa permanência de R$ 750 por 40h de qualificação, até R$ 1.500 total"
        changes_log.append("RS: rs-qualifica-rs - renamed, fixed value R$200→R$750-1500")

    b = find_benefit(data["benefits"], "rs-porta-de-entrada")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 8105
                rule["description"] = "Renda familiar de até 5 salários mínimos (R$ 8.105)"
        changes_log.append("RS: rs-porta-de-entrada - renda R$7060→R$8105 (5 SM 2026)")

    save_json(STATES_DIR / "rs.json", data)

    # === SC (Santa Catarina) ===
    data = load_json(STATES_DIR / "sc.json")

    b = find_benefit(data["benefits"], "sc-programa-catarinense-de-inclusao-social")
    if b:
        b["id"] = "sc-proemprego"
        b["name"] = "ProEmprego SC - Qualificação Profissional"
        b["shortDescription"] = "Cursos gratuitos de qualificação profissional pelo governo de Santa Catarina para quem busca emprego."
        b["estimatedValue"]["description"] = "Cursos gratuitos de qualificação profissional"
        b["sourceUrl"] = "https://www.sas.sc.gov.br/"
        b["category"] = "Qualificação Profissional"
        changes_log.append("SC: sc-programa-catarinense → sc-proemprego (identity fix)")

    b = find_benefit(data["benefits"], "sc-casa-catarina")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 6484
                rule["description"] = "Renda familiar de até 4 salários mínimos (R$ 6.484)"
        changes_log.append("SC: sc-casa-catarina - renda R$5648→R$6484 (4 SM 2026)")

    save_json(STATES_DIR / "sc.json", data)

    # === PI (Piauí) ===
    data = load_json(STATES_DIR / "pi.json")

    b = find_benefit(data["benefits"], "pi-alfabetiza-piaui")
    if b:
        b["estimatedValue"]["type"] = "one_time"
        b["estimatedValue"]["min"] = 600
        b["estimatedValue"]["max"] = 600
        b["estimatedValue"]["description"] = "R$ 600 total em 3 parcelas de R$ 200 (matrícula, após 3 meses, após certificação)"
        changes_log.append("PI: pi-alfabetiza-piaui - fixed type monthly→one_time, clarified R$600 total not monthly")

    b = find_benefit(data["benefits"], "pi-morar-bem")
    if b:
        b["shortDescription"] = "Cheque-moradia de até R$ 10 mil para entrada do financiamento habitacional no Piauí."
        b["estimatedValue"]["min"] = 7000
        b["estimatedValue"]["max"] = 10000
        b["estimatedValue"]["description"] = "Cheque-moradia de R$ 7 mil (Faixa B) a R$ 10 mil (Faixa A) para entrada do financiamento"
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 8000
                rule["description"] = "Renda familiar de até R$ 4.400 (Faixa A) ou R$ 8.000 (Faixa B)"
        b["whereToApply"] = "App Gov.Pi Cidadão ou site da ADH-PI (Agência de Desenvolvimento Habitacional)"
        changes_log.append("PI: pi-morar-bem - fixed value R$30-80k→R$7-10k (cheque-moradia), renda R$2640→R$8000")

    save_json(STATES_DIR / "pi.json", data)

    # === RN (Rio Grande do Norte) ===
    data = load_json(STATES_DIR / "rn.json")

    b = find_benefit(data["benefits"], "rn-minha-casa-rn")
    if b:
        b["id"] = "rn-moradia"
        b["name"] = "RN+ Moradia"
        b["shortDescription"] = "Programa habitacional do governo do RN que facilita o acesso à casa própria para famílias de baixa renda."
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 2850
                rule["description"] = "Renda familiar de até R$ 2.850 (Faixa 1 alinhada ao MCMV)"
        b["sourceUrl"] = "https://opoti.com.br/governo-do-rn-lanca-programa-habitacional-rn-moradia-para-ampliar-acesso-a-casa-propria/"
        changes_log.append("RN: rn-minha-casa-rn → rn-moradia (RN+ Moradia), renda R$4000→R$2850")

    b = find_benefit(data["benefits"], "rn-jovem-potiguar")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "idade":
                rule["value"] = 16
                rule["description"] = "Ter entre 16 e 35 anos"
        b["estimatedValue"]["min"] = 0
        b["estimatedValue"]["max"] = 900
        b["estimatedValue"]["description"] = "Auxílio financeiro de até R$ 900/mês durante a formação + curso gratuito"
        changes_log.append("RN: rn-jovem-potiguar - age 15→16, added value R$900/month")

    b = find_benefit(data["benefits"], "rn-programa-materno-infantil")
    if b:
        b["name"] = "Pré-natal e Parto Seguro RN"
        b["shortDescription"] = "Acompanhamento pré-natal completo e parto pelo SUS nas maternidades estaduais do RN."
        changes_log.append("RN: rn-programa-materno-infantil - renamed to avoid confusion with federal")

    save_json(STATES_DIR / "rn.json", data)

    # === SE (Sergipe) ===
    data = load_json(STATES_DIR / "se.json")

    b = find_benefit(data["benefits"], "se-cartao-mais-inclusao")
    if b:
        b["estimatedValue"]["min"] = 130
        b["estimatedValue"]["max"] = 130
        b["estimatedValue"]["description"] = "R$ 130 por mês (modalidade CMais Cidadania)"
        changes_log.append("SE: se-cartao-mais-inclusao - value R$100-300→R$130")

    b = find_benefit(data["benefits"], "se-casa-sergipana")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 2850
                rule["description"] = "Renda familiar de até R$ 2.850 (Faixa 1 alinhada ao MCMV)"
        b["estimatedValue"]["min"] = 15000
        b["estimatedValue"]["max"] = 20000
        b["estimatedValue"]["description"] = "Subsídio estadual de R$ 15 mil (Faixa 2) a R$ 20 mil (Faixa 1) para entrada do financiamento"
        b["whereToApply"] = "Site casasergipana.se.gov.br"
        changes_log.append("SE: se-casa-sergipana - renda R$2640→R$2850, value R$20-80k→R$15-20k")

    save_json(STATES_DIR / "se.json", data)

    # === DF (Distrito Federal) ===
    data = load_json(STATES_DIR / "df.json")

    b = find_benefit(data["benefits"], "df-cartao-prato-cheio")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal" and rule.get("value") == 3200:
                rule["value"] = 3242
                rule["description"] = "Renda per capita de até meio salário mínimo (R$ 810,50 por pessoa)"
        changes_log.append("DF: df-cartao-prato-cheio - renda R$3200→R$3242")

    b = find_benefit(data["benefits"], "df-df-social")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 3242
                rule["description"] = "Renda per capita de até meio salário mínimo (R$ 810,50 por pessoa)"
        changes_log.append("DF: df-df-social - renda R$2424→R$3242")

    b = find_benefit(data["benefits"], "df-cartao-material-escolar")
    if b:
        b["estimatedValue"]["min"] = 240
        b["estimatedValue"]["description"] = "R$ 240 a R$ 320 por aluno por ano, conforme nível de ensino"
        changes_log.append("DF: df-cartao-material-escolar - value min R$320→R$240")

    b = find_benefit(data["benefits"], "df-bolsa-maternidade")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal" and rule.get("value") == 3200:
                rule["value"] = 3242
                rule["description"] = "Renda per capita de até meio salário mínimo (R$ 810,50 por pessoa)"
        changes_log.append("DF: df-bolsa-maternidade - renda R$3200→R$3242")

    b = find_benefit(data["benefits"], "df-morar-df")
    if b:
        # Add missing renda rule
        has_renda = any(r.get("field") == "rendaFamiliarMensal" for r in b.get("eligibilityRules", []))
        if not has_renda:
            b["eligibilityRules"].append({
                "field": "rendaFamiliarMensal",
                "operator": "lte",
                "value": 8105,
                "description": "Renda familiar bruta de até 5 salários mínimos (R$ 8.105)"
            })
        changes_log.append("DF: df-morar-df - added missing renda rule (5 SM)")

    save_json(STATES_DIR / "df.json", data)

    # === GO (Goiás) ===
    data = load_json(STATES_DIR / "go.json")

    b = find_benefit(data["benefits"], "go-renda-cidada")
    if b:
        b["estimatedValue"]["min"] = 100
        b["estimatedValue"]["description"] = "R$ 100 base + R$ 10/dependente (até 4) + R$ 40 para doenças crônicas/gestantes"
        changes_log.append("GO: go-renda-cidada - value min R$80→R$100")

    b = find_benefit(data["benefits"], "go-goias-por-elas")
    if b:
        b["shortDescription"] = "R$ 300/mês para mulheres vítimas de violência doméstica com medida protetiva ativa em Goiás."
        b["estimatedValue"]["min"] = 300
        b["estimatedValue"]["max"] = 300
        b["estimatedValue"]["description"] = "R$ 300/mês + Bolsa Qualificação de R$ 250/mês (3 parcelas)"
        changes_log.append("GO: go-goias-por-elas - clarified requires domestic violence protective order")

    b = find_benefit(data["benefits"], "go-bolsa-estudo")
    if b:
        b["estimatedValue"]["min"] = 112
        b["estimatedValue"]["max"] = 112
        b["estimatedValue"]["description"] = "R$ 111,92 por mês em 10 parcelas para alunos da rede estadual (9º ano e EM)"
        changes_log.append("GO: go-bolsa-estudo - value R$130-150→R$111.92 (valor vigente)")

    b = find_benefit(data["benefits"], "go-maes-de-goias")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["description"] = "Renda per capita de até R$ 109 (extrema pobreza)"
        changes_log.append("GO: go-maes-de-goias - clarified renda is per capita R$109")

    save_json(STATES_DIR / "go.json", data)

    # === MT (Mato Grosso) ===
    data = load_json(STATES_DIR / "mt.json")

    b = find_benefit(data["benefits"], "mt-ser-familia")
    if b:
        b["estimatedValue"]["min"] = 100
        b["estimatedValue"]["max"] = 100
        b["estimatedValue"]["description"] = "R$ 100 por mês para famílias em extrema pobreza"
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 2161
                rule["description"] = "Renda per capita de até 1/3 do salário mínimo (~R$ 540 por pessoa)"
        changes_log.append("MT: mt-ser-familia - value R$150-300→R$100, renda R$872→R$2161")

    b = find_benefit(data["benefits"], "mt-pra-ter-onde-morar")
    if b:
        b["id"] = "mt-ser-familia-habitacao"
        b["name"] = "SER Família Habitação"
        b["shortDescription"] = "Subsídio de até R$ 35 mil do governo de Mato Grosso para ajudar famílias a comprar a casa própria."
        b["estimatedValue"]["min"] = 10000
        b["estimatedValue"]["max"] = 35000
        b["estimatedValue"]["description"] = "Subsídio de R$ 10 mil a R$ 35 mil conforme a faixa de renda"
        b["sourceUrl"] = "https://www.mtpar.mt.gov.br/serfamiliahabitacao"
        changes_log.append("MT: mt-pra-ter-onde-morar → mt-ser-familia-habitacao (correct name)")

    save_json(STATES_DIR / "mt.json", data)

    # === MS (Mato Grosso do Sul) ===
    data = load_json(STATES_DIR / "ms.json")

    b = find_benefit(data["benefits"], "ms-protecao-gestante")
    if b:
        b["name"] = "Atenção à Gestante MS"
        b["shortDescription"] = "Pré-natal completo e parto seguro pelo SUS para gestantes do Mato Grosso do Sul."
        changes_log.append("MS: ms-protecao-gestante - renamed to be more accurate")

    save_json(STATES_DIR / "ms.json", data)

    # === ES (Espírito Santo) ===
    data = load_json(STATES_DIR / "es.json")

    b = find_benefit(data["benefits"], "es-nossa-bolsa")
    if b:
        b["estimatedValue"]["description"] = "Bolsa integral (100% da mensalidade) em faculdade particular do ES"
        changes_log.append("ES: es-nossa-bolsa - clarified it's full scholarship, not R$300-800")

    b = find_benefit(data["benefits"], "es-nossa-casa")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal" and rule.get("value") == 4000:
                rule["value"] = 4863
                rule["description"] = "Renda familiar de até 3 salários mínimos (R$ 4.863)"
        changes_log.append("ES: es-nossa-casa - renda R$4000→R$4863 (3 SM 2026)")

    save_json(STATES_DIR / "es.json", data)

    # === MG (Minas Gerais) ===
    data = load_json(STATES_DIR / "mg.json")

    b = find_benefit(data["benefits"], "mg-bolsa-merenda")
    if b:
        b["estimatedValue"]["max"] = 50
        b["estimatedValue"]["description"] = "R$ 50 por aluno por período (recesso escolar)"
        changes_log.append("MG: mg-bolsa-merenda - value max R$100→R$50")

    b = find_benefit(data["benefits"], "mg-filhos-de-minas")
    if b:
        b["estimatedValue"]["min"] = 324
        b["estimatedValue"]["max"] = 324
        b["estimatedValue"]["description"] = "Kit com 14 itens de enxoval (valor estimado R$ 324)"
        changes_log.append("MG: mg-filhos-de-minas - value R$200-400→R$324 (kit)")

    save_json(STATES_DIR / "mg.json", data)

    # === RJ (Rio de Janeiro) ===
    data = load_json(STATES_DIR / "rj.json")

    b = find_benefit(data["benefits"], "rj-riocard-social")
    if b:
        b["name"] = "Tarifa Social (Metrô/Trem/BUI)"
        b["shortDescription"] = "Desconto na passagem do metrô, trem e ônibus intermunicipal no RJ para quem ganha pouco."
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "rendaFamiliarMensal":
                rule["value"] = 3205
                rule["description"] = "Renda mensal declarada de até R$ 3.205,20"
        changes_log.append("RJ: rj-riocard-social → Tarifa Social, renda R$3200→R$3205")

    save_json(STATES_DIR / "rj.json", data)

    # === SP (São Paulo) ===
    data = load_json(STATES_DIR / "sp.json")

    b = find_benefit(data["benefits"], "sp-renda-cidada")
    if b:
        b["estimatedValue"]["max"] = 80
        b["estimatedValue"]["description"] = "R$ 80 por mês por família"
        changes_log.append("SP: sp-renda-cidada - value max R$115→R$80")

    b = find_benefit(data["benefits"], "sp-bom-prato")
    if b:
        b["shortDescription"] = "Restaurante do governo com café da manhã a R$ 0,50 e almoço/jantar a R$ 1,00 em São Paulo."
        changes_log.append("SP: sp-bom-prato - fixed jantar price in description")

    save_json(STATES_DIR / "sp.json", data)

    # === PE (Pernambuco) ===
    data = load_json(STATES_DIR / "pe.json")

    b = find_benefit(data["benefits"], "pe-mae-coruja")
    if b:
        b["estimatedValue"]["min"] = 0
        b["estimatedValue"]["max"] = 0
        b["estimatedValue"]["description"] = "Kit bebê com 14 itens de higiene e enxoval (sem valor monetário direto)"
        changes_log.append("PE: pe-mae-coruja - value R$200-400→kit (not monetary)")

    b = find_benefit(data["benefits"], "pe-qualifica-pe")
    if b:
        for rule in b.get("eligibilityRules", []):
            if rule.get("field") == "idade" and rule.get("value") == 16:
                rule["value"] = 18
                rule["description"] = "Ter pelo menos 18 anos"
        changes_log.append("PE: pe-qualifica-pe - age 16→18")

    save_json(STATES_DIR / "pe.json", data)

    # Print summary
    print("=" * 70)
    print("PHASE 3: Individual corrections applied")
    print("=" * 70)
    for change in changes_log:
        print(f"  {change}")
    print(f"\nTotal corrections: {len(changes_log)}")


def validate_all():
    """Validate all JSON files."""
    print("\nValidation:")
    total = 0
    errors = 0
    for fp in sorted(STATES_DIR.glob("*.json")):
        try:
            data = load_json(fp)
            n = len(data.get("benefits", []))
            total += n
            # Check for duplicate IDs
            ids = [b["id"] for b in data["benefits"]]
            if len(ids) != len(set(ids)):
                print(f"  WARNING: {fp.name} has duplicate IDs!")
        except Exception as e:
            print(f"  ERROR: {fp.name}: {e}")
            errors += 1

    print(f"  Total benefits: {total}")
    print(f"  Parse errors: {errors}")
    if errors == 0:
        print("  All files valid JSON.")


if __name__ == "__main__":
    apply_fixes()
    validate_all()

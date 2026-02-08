#!/usr/bin/env python3
"""
Auditoria de campos desconhecidos nos benefícios setoriais.

17 benefícios usam campos que NÃO existem no CitizenProfile.
Estratégia por campo:
- Mapeável → substitui por campo válido
- Setor já filtra → remove regra desconhecida, adiciona disclaimer
- Nicho/emergencial → remove regra, mantém descrição no disclaimer

Uso:
  python scripts/audit_sectoral_fields.py              # aplica
  python scripts/audit_sectoral_fields.py --dry-run    # preview
"""

import json
import sys
from pathlib import Path

SECTORAL_JSON = Path(__file__).parent.parent / "frontend" / "src" / "data" / "benefits" / "sectoral.json"
DRY_RUN = "--dry-run" in sys.argv


def load():
    with open(SECTORAL_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(SECTORAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def find(benefits, bid):
    for b in benefits:
        if b["id"] == bid:
            return b
    return None


def set_disclaimer(b, text):
    if "metadata" not in b:
        b["metadata"] = {}
    existing = b["metadata"].get("disclaimer", "")
    if text not in existing:
        b["metadata"]["disclaimer"] = f"{existing} {text}".strip() if existing else text


def remove_field_rule(b, field_name):
    """Remove eligibility rule with given field, return True if removed."""
    before = len(b["eligibilityRules"])
    b["eligibilityRules"] = [r for r in b["eligibilityRules"] if r.get("field") != field_name]
    return len(b["eligibilityRules"]) < before


def replace_field_rule(b, old_field, new_rule):
    """Replace a rule by field name with a new rule dict."""
    for i, r in enumerate(b["eligibilityRules"]):
        if r.get("field") == old_field:
            b["eligibilityRules"][i] = new_rule
            return True
    return False


def fix_all(benefits):
    changes = []

    # ── servidor_publico (4 benefícios) ──
    # Todos já têm servidorPublico=true como 1ª regra → setor filtra.
    # Regras extras são requisitos administrativos que não podemos avaliar.

    b = find(benefits, "sectoral-servidor-auxilio-alimentacao")
    if b and remove_field_rule(b, "jornadaTrabalho"):
        set_disclaimer(b, "Exige jornada mínima de 30 horas semanais. Verifique com o RH do seu órgão.")
        changes.append("servidor-auxilio-alimentacao: jornadaTrabalho REMOVIDO (disclaimer)")

    b = find(benefits, "sectoral-servidor-auxilio-saude")
    if b and remove_field_rule(b, "planoSaude"):
        set_disclaimer(b, "Necessário estar inscrito em plano de saúde para receber o auxílio.")
        changes.append("servidor-auxilio-saude: planoSaude REMOVIDO (disclaimer)")

    b = find(benefits, "sectoral-servidor-auxilio-transporte")
    if b and remove_field_rule(b, "usaTransportePublico"):
        set_disclaimer(b, "Destinado a servidores que utilizam transporte público no deslocamento residência-trabalho.")
        changes.append("servidor-auxilio-transporte: usaTransportePublico REMOVIDO (disclaimer)")

    b = find(benefits, "sectoral-servidor-licenca-capacitacao")
    if b and remove_field_rule(b, "tempoServico"):
        set_disclaimer(b, "Exige pelo menos 5 anos de efetivo exercício no serviço público federal.")
        changes.append("servidor-licenca-capacitacao: tempoServico REMOVIDO (disclaimer)")

    # ── estudante (1 benefício) ──

    # resideFora → remover (setor + rendaPerCapita já filtram)
    b = find(benefits, "sectoral-estudante-auxilio-moradia")
    if b and remove_field_rule(b, "resideFora"):
        set_disclaimer(b, "Destinado a estudantes que residem fora do município de origem. Cada universidade tem edital próprio.")
        changes.append("estudante-auxilio-moradia: resideFora REMOVIDO (disclaimer)")

    # ── gestante (2 benefícios) ──

    # nascimentoFilho → temGestante (proxy: se é gestante, terá nascimento)
    b = find(benefits, "sectoral-gestante-auxilio-natalidade")
    if b and replace_field_rule(b, "nascimentoFilho", {
        "field": "temGestante",
        "operator": "eq",
        "value": True,
        "description": "Gestante ou ter tido filho recentemente",
        "legalReference": "Art. 196, Lei 8.112/1990"
    }):
        set_disclaimer(b, "Pago por ocasião do nascimento de filho. Servidora ou cônjuge de servidor.")
        changes.append("gestante-auxilio-natalidade: nascimentoFilho→temGestante")

    # contribuinteINSS → trabalhoFormal (proxy: quem contribui geralmente tem vínculo)
    b = find(benefits, "sectoral-gestante-licenca-maternidade")
    if b and replace_field_rule(b, "contribuinteINSS", {
        "field": "trabalhoFormal",
        "operator": "eq",
        "value": True,
        "description": "Contribuinte do INSS (CLT, MEI ou contribuinte individual)",
        "legalReference": "Art. 71, Lei 8.213/1991"
    }):
        set_disclaimer(b, "Exige contribuição ao INSS. MEIs e contribuintes individuais também têm direito.")
        changes.append("gestante-licenca-maternidade: contribuinteINSS→trabalhoFormal (disclaimer MEI)")

    # ── indigena_quilombola (2 benefícios) ──

    # indigena → indigenaOuQuilombola
    b = find(benefits, "sectoral-indigena-sesai")
    if b and replace_field_rule(b, "indigena", {
        "field": "indigenaOuQuilombola",
        "operator": "eq",
        "value": True,
        "description": "Ser indígena (aldeado ou em contexto urbano)"
    }):
        set_disclaimer(b, "Exclusivo para indígenas. Quilombolas acessam o SUS regular.")
        changes.append("indigena-sesai: indigena→indigenaOuQuilombola (disclaimer)")

    # quilombola + certidaoPalmares → indigenaOuQuilombola (simplifica)
    b = find(benefits, "sectoral-indigena-titulacao-terras")
    if b:
        removed_q = remove_field_rule(b, "quilombola")
        removed_c = remove_field_rule(b, "certidaoPalmares")
        if removed_q or removed_c:
            # Adiciona regra válida se não existe
            has_valid = any(r["field"] == "indigenaOuQuilombola" for r in b["eligibilityRules"])
            if not has_valid:
                b["eligibilityRules"].insert(0, {
                    "field": "indigenaOuQuilombola",
                    "operator": "eq",
                    "value": True,
                    "description": "Pertencer a comunidade remanescente de quilombo",
                    "legalReference": "Art. 68, ADCT, CF/88"
                })
            set_disclaimer(b, "Exige certificação da Fundação Cultural Palmares. Processo coletivo da comunidade.")
            changes.append("indigena-titulacao-terras: quilombola+certidaoPalmares→indigenaOuQuilombola (disclaimer)")

    # ── agricultor (2 benefícios) ──

    # rendaBrutaAgro → rendaFamiliarMensal (R$500k/ano ≈ R$41.666/mês)
    b = find(benefits, "sectoral-agricultor-dap-caf")
    if b and replace_field_rule(b, "rendaBrutaAgro", {
        "field": "rendaFamiliarMensal",
        "operator": "lte",
        "value": 41666,
        "description": "Renda bruta anual de até R$ 500 mil (≈ R$ 41.666/mês)",
        "legalReference": "Lei 11.326/2006, Art. 3º"
    }):
        changes.append("agricultor-dap-caf: rendaBrutaAgro→rendaFamiliarMensal (R$500k/12)")

    # tempoOcupacao → remover (setor já filtra + disclamer)
    b = find(benefits, "sectoral-agricultor-terra-legal")
    if b and remove_field_rule(b, "tempoOcupacao"):
        set_disclaimer(b, "Exige ocupação mansa e pacífica da terra por pelo menos 5 anos na Amazônia Legal.")
        changes.append("agricultor-terra-legal: tempoOcupacao REMOVIDO (disclaimer)")

    # ── catador (1 benefício) ──

    # cooperativa → remover (setor já filtra)
    b = find(benefits, "sectoral-catador-pro-catador")
    if b and remove_field_rule(b, "cooperativa"):
        set_disclaimer(b, "Prioridade para catadores organizados em cooperativas ou associações.")
        changes.append("catador-pro-catador: cooperativa REMOVIDO (disclaimer)")

    # ── clt (1 benefício) ──

    # acordoColetivo → temCarteiraAssinada (proxy: PLR exige vínculo CLT)
    b = find(benefits, "sectoral-clt-plr")
    if b and replace_field_rule(b, "acordoColetivo", {
        "field": "temCarteiraAssinada",
        "operator": "eq",
        "value": True,
        "description": "Ter carteira assinada (CLT) com acordo de PLR",
        "legalReference": "Lei 10.101/2000"
    }):
        set_disclaimer(b, "Exige acordo coletivo ou convenção prevendo PLR. Nem todas as empresas oferecem.")
        changes.append("clt-plr: acordoColetivo→temCarteiraAssinada (disclaimer)")

    # ── entregador (1 benefício) ──

    # cadastradoPlataforma → trabalhaAplicativo (mapeamento direto)
    b = find(benefits, "sectoral-entregador-seguro-acidente")
    if b and replace_field_rule(b, "cadastradoPlataforma", {
        "field": "trabalhaAplicativo",
        "operator": "eq",
        "value": True,
        "description": "Cadastrado em plataforma de entrega/transporte por aplicativo"
    }):
        changes.append("entregador-seguro-acidente: cadastradoPlataforma→trabalhaAplicativo")

    # ── motorista_app (1 benefício) ──

    # veiculoRegularizado → remover (setor já filtra)
    b = find(benefits, "sectoral-motorista-dpvat")
    if b and remove_field_rule(b, "veiculoRegularizado"):
        set_disclaimer(b, "Exige veículo com documentação regularizada (CRLV em dia).")
        changes.append("motorista-dpvat: veiculoRegularizado REMOVIDO (disclaimer)")

    # ── pescador (2 benefícios) ──

    # dap → pescadorArtesanal (setor já implica, DAP é documento)
    b = find(benefits, "sectoral-pescador-pronaf-pesca")
    if b and replace_field_rule(b, "dap", {
        "field": "pescadorArtesanal",
        "operator": "eq",
        "value": True,
        "description": "Pescador artesanal com RGP (Registro Geral de Pesca) ativo"
    }):
        set_disclaimer(b, "Exige DAP Pescador Artesanal ou CAF ativa. Procure a colônia de pesca.")
        changes.append("pescador-pronaf-pesca: dap→pescadorArtesanal (disclaimer DAP)")

    # contribuinteINSS → trabalhoFormal (proxy)
    b = find(benefits, "sectoral-pescador-seguro-artesanal")
    if b and replace_field_rule(b, "contribuinteINSS", {
        "field": "trabalhoFormal",
        "operator": "eq",
        "value": True,
        "description": "Contribuinte do INSS como segurado especial (pescador artesanal)",
        "legalReference": "Art. 12, VII, Lei 8.212/1991"
    }):
        set_disclaimer(b, "Exige contribuição ao INSS como segurado especial. Pescador artesanal com RGP ativo.")
        changes.append("pescador-seguro-artesanal: contribuinteINSS→trabalhoFormal (disclaimer)")

    return changes


def main():
    data = load()
    benefits = data["benefits"]

    print("=" * 60)
    print("AUDITORIA SETORIAL — Campos desconhecidos pelo evaluator")
    print("=" * 60)

    changes = fix_all(benefits)
    for c in changes:
        print(f"  ✓ {c}")

    print(f"\nTotal: {len(changes)} correções em {len(benefits)} setoriais")

    if DRY_RUN:
        print("\n⚠️  --dry-run: nenhuma alteração salva.")
    else:
        save(data)
        print(f"\n✅ Salvo em {SECTORAL_JSON}")


if __name__ == "__main__":
    main()

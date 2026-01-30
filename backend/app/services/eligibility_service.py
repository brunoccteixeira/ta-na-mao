"""
Eligibility evaluation service.
Evaluates citizen profiles against benefit eligibility rules.
"""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.benefit import Benefit
from app.schemas.benefit import (
    CitizenProfile,
    BenefitSummary,
    BenefitEligibilityResult,
    EligibilitySummary,
    EligibilityResponse,
    RuleEvaluationResult,
    EstimatedValue,
)


def calculate_renda_per_capita(profile: CitizenProfile) -> float:
    """Calculate per capita income."""
    pessoas = max(profile.pessoas_na_casa, 1)
    return profile.renda_familiar_mensal / pessoas


def get_field_value(profile: CitizenProfile, field: str) -> Any:
    """Get a field value from the profile, including computed fields."""
    # Computed fields
    if field == "rendaPerCapita":
        return calculate_renda_per_capita(profile)

    # Map camelCase fields to snake_case attributes
    field_mapping = {
        "pessoasNaCasa": "pessoas_na_casa",
        "quantidadeFilhos": "quantidade_filhos",
        "temIdoso65Mais": "tem_idoso_65_mais",
        "temGestante": "tem_gestante",
        "temPcd": "tem_pcd",
        "temCrianca0a6": "tem_crianca_0_a_6",
        "rendaFamiliarMensal": "renda_familiar_mensal",
        "trabalhoFormal": "trabalho_formal",
        "temCasaPropria": "tem_casa_propria",
        "moradiaZonaRural": "moradia_zona_rural",
        "cadastradoCadunico": "cadastrado_cadunico",
        "recebeBolsaFamilia": "recebe_bolsa_familia",
        "recebeBpc": "recebe_bpc",
        "trabalhou1971_1988": "trabalhou_1971_1988",
        "temCarteiraAssinada": "tem_carteira_assinada",
        "tempoCarteiraAssinada": "tempo_carteira_assinada",
        "fezSaqueFgts": "fez_saque_fgts",
        "temMei": "tem_mei",
        "trabalhaAplicativo": "trabalha_aplicativo",
        "agricultorFamiliar": "agricultor_familiar",
        "pescadorArtesanal": "pescador_artesanal",
        "catadorReciclavel": "catador_reciclavel",
        "mulherMenstruante": "mulher_menstruante",
        "idadeMulher": "idade_mulher",
        "redePublica": "rede_publica",
        "municipioIbge": "municipio_ibge",
    }

    # Convert camelCase to snake_case if needed
    attr_name = field_mapping.get(field, field)

    return getattr(profile, attr_name, None)


def evaluate_rule(
    profile: CitizenProfile,
    rule: Dict[str, Any]
) -> RuleEvaluationResult:
    """Evaluate a single rule against a profile."""
    field = rule.get("field", "")
    operator = rule.get("operator", "eq")
    expected_value = rule.get("value")
    description = rule.get("description", "")

    field_value = get_field_value(profile, field)

    # If the field is undefined/null, mark as inconclusive
    if field_value is None:
        return RuleEvaluationResult(
            ruleDescription=description,
            passed=False,
            inconclusive=True,
            field=field,
            expectedValue=expected_value,
            actualValue=None,
        )

    passed = False

    if operator == "eq":
        passed = field_value == expected_value
    elif operator == "neq":
        passed = field_value != expected_value
    elif operator == "lt":
        passed = float(field_value) < float(expected_value)
    elif operator == "lte":
        passed = float(field_value) <= float(expected_value)
    elif operator == "gt":
        passed = float(field_value) > float(expected_value)
    elif operator == "gte":
        passed = float(field_value) >= float(expected_value)
    elif operator == "in":
        passed = isinstance(expected_value, list) and field_value in expected_value
    elif operator == "not_in":
        passed = isinstance(expected_value, list) and field_value not in expected_value
    elif operator == "has":
        passed = bool(field_value)
    elif operator == "not_has":
        passed = not field_value

    return RuleEvaluationResult(
        ruleDescription=description,
        passed=passed,
        inconclusive=False,
        field=field,
        expectedValue=expected_value,
        actualValue=field_value,
    )


def matches_geography(profile: CitizenProfile, benefit: Benefit) -> bool:
    """Check if benefit applies to citizen's geographic location."""
    scope = benefit.scope

    # Federal benefits apply everywhere
    if scope == "federal":
        return True

    # State benefits require matching state
    if scope == "state":
        return benefit.state == profile.estado

    # Municipal benefits require matching municipality
    if scope == "municipal":
        return benefit.municipality_ibge == profile.municipio_ibge

    # Sectoral benefits may have geographic restrictions
    if scope == "sectoral":
        if not benefit.state:
            return True
        return benefit.state == profile.estado

    return False


def matches_sector(profile: CitizenProfile, benefit: Benefit) -> bool:
    """Check if benefit applies to citizen's sector/profession."""
    if benefit.scope != "sectoral" or not benefit.sector:
        return True

    sector_map = {
        "pescador": "pescador_artesanal",
        "agricultor": "agricultor_familiar",
        "entregador": "trabalha_aplicativo",
        "motorista_app": "trabalha_aplicativo",
        "catador": "catador_reciclavel",
        "mei": "tem_mei",
        "autonomo": "tem_mei",
        "pcd": "tem_pcd",
    }

    profile_field = sector_map.get(benefit.sector)
    if not profile_field:
        return True

    return bool(getattr(profile, profile_field, False))


def calculate_estimated_value(
    profile: CitizenProfile,
    benefit: Benefit
) -> Optional[float]:
    """Calculate estimated value for a benefit based on profile."""
    if not benefit.estimated_value:
        return None

    est_value = benefit.estimated_value
    min_val = est_value.get("min")
    max_val = est_value.get("max")

    # Specific calculations for known benefits
    if benefit.id == "federal-bolsa-familia":
        valor = 142  # Benefício de Renda de Cidadania
        if profile.tem_crianca_0_a_6:
            valor += 150 * min(profile.quantidade_filhos, 3)
        if profile.quantidade_filhos > 0:
            valor += 50 * profile.quantidade_filhos
        if profile.tem_gestante:
            valor += 50
        return min(valor, max_val or 900)

    if benefit.id == "federal-abono-salarial":
        return max_val or 1412

    # Default to average or min
    if min_val and max_val:
        return round((min_val + max_val) / 2)

    return min_val or max_val


def is_already_receiving(profile: CitizenProfile, benefit: Benefit) -> bool:
    """Check if citizen is already receiving this benefit."""
    if benefit.id == "federal-bolsa-familia" and profile.recebe_bolsa_familia:
        return True
    if benefit.id in ("federal-bpc-idoso", "federal-bpc-pcd") and profile.recebe_bpc:
        return True
    return False


def benefit_to_summary(benefit: Benefit) -> BenefitSummary:
    """Convert Benefit model to BenefitSummary schema."""
    est_value = None
    if benefit.estimated_value:
        est_value = EstimatedValue(
            type=benefit.estimated_value.get("type", "monthly"),
            min=benefit.estimated_value.get("min"),
            max=benefit.estimated_value.get("max"),
            description=benefit.estimated_value.get("description"),
        )

    return BenefitSummary(
        id=benefit.id,
        name=benefit.name,
        shortDescription=benefit.short_description,
        scope=benefit.scope,
        state=benefit.state,
        municipalityIbge=benefit.municipality_ibge,
        estimatedValue=est_value,
        status=benefit.status,
        icon=benefit.icon,
        category=benefit.category,
    )


def evaluate_benefit(
    profile: CitizenProfile,
    benefit: Benefit
) -> BenefitEligibilityResult:
    """Evaluate a single benefit against a citizen profile."""
    benefit_summary = benefit_to_summary(benefit)

    # Check if already receiving
    if is_already_receiving(profile, benefit):
        return BenefitEligibilityResult(
            benefit=benefit_summary,
            status="already_receiving",
            matchedRules=[],
            failedRules=[],
            inconclusiveRules=[],
            reason="Você já recebe este benefício",
        )

    # Check geographic scope
    if not matches_geography(profile, benefit):
        return BenefitEligibilityResult(
            benefit=benefit_summary,
            status="not_applicable",
            matchedRules=[],
            failedRules=[],
            inconclusiveRules=[],
            reason=f"Não disponível em {profile.estado or 'sua região'}",
        )

    # Check sector scope
    if not matches_sector(profile, benefit):
        return BenefitEligibilityResult(
            benefit=benefit_summary,
            status="not_applicable",
            matchedRules=[],
            failedRules=[],
            inconclusiveRules=[],
            reason="Não se aplica à sua profissão",
        )

    # Evaluate all eligibility rules
    matched_rules: List[str] = []
    failed_rules: List[str] = []
    inconclusive_rules: List[str] = []
    rule_details: List[RuleEvaluationResult] = []

    rules = benefit.eligibility_rules or []
    for rule in rules:
        result = evaluate_rule(profile, rule)
        rule_details.append(result)

        if result.inconclusive:
            inconclusive_rules.append(result.rule_description)
        elif result.passed:
            matched_rules.append(result.rule_description)
        else:
            failed_rules.append(result.rule_description)

    # Determine status based on rule results
    if len(failed_rules) == 0 and len(inconclusive_rules) == 0:
        status = "eligible"
        reason = "Você atende a todos os requisitos"
    elif len(failed_rules) == 0 and len(inconclusive_rules) > 0:
        status = "likely_eligible"
        reason = "Provavelmente elegível, verificar presencialmente"
    elif len(failed_rules) <= 1 and len(inconclusive_rules) > 0:
        status = "maybe"
        reason = "Pode ter direito, verificar no CRAS"
    else:
        status = "not_eligible"
        reason = failed_rules[0] if failed_rules else "Não atende aos requisitos"

    estimated_value = None
    if status in ("eligible", "likely_eligible"):
        estimated_value = calculate_estimated_value(profile, benefit)

    return BenefitEligibilityResult(
        benefit=benefit_summary,
        status=status,
        matchedRules=matched_rules,
        failedRules=failed_rules,
        inconclusiveRules=inconclusive_rules,
        estimatedValue=estimated_value,
        reason=reason,
        ruleDetails=rule_details,
    )


async def evaluate_all_benefits(
    db: AsyncSession,
    profile: CitizenProfile,
    scope: Optional[str] = None,
    include_not_applicable: bool = False,
) -> EligibilityResponse:
    """Evaluate all benefits against a citizen profile."""
    # Query benefits from database
    stmt = select(Benefit).where(Benefit.status == "active")

    if scope:
        stmt = stmt.where(Benefit.scope == scope)

    result = await db.execute(stmt)
    benefits = result.scalars().all()

    # Evaluate each benefit
    results: List[BenefitEligibilityResult] = []
    for benefit in benefits:
        eval_result = evaluate_benefit(profile, benefit)
        results.append(eval_result)

    # Group results by status
    eligible = [r for r in results if r.status == "eligible"]
    likely_eligible = [r for r in results if r.status == "likely_eligible"]
    maybe = [r for r in results if r.status == "maybe"]
    not_eligible = [r for r in results if r.status == "not_eligible"]
    not_applicable = [r for r in results if r.status == "not_applicable"]
    already_receiving = [r for r in results if r.status == "already_receiving"]

    # Calculate potential values
    def calculate_total(results_list: List[BenefitEligibilityResult], value_type: str) -> float:
        total = 0.0
        for r in results_list:
            if (r.benefit.estimated_value and
                r.benefit.estimated_value.type == value_type and
                r.estimated_value):
                total += r.estimated_value
        return total

    eligible_and_likely = eligible + likely_eligible
    total_monthly = calculate_total(eligible_and_likely, "monthly")
    total_annual = calculate_total(eligible_and_likely, "annual")
    total_one_time = calculate_total(eligible_and_likely, "one_time")

    # Collect required documents
    documents_needed: Set[str] = set()
    for r in eligible_and_likely:
        # Get documents from the benefit (need to re-query for full info)
        for benefit in benefits:
            if benefit.id == r.benefit.id:
                for doc in benefit.documents_required or []:
                    documents_needed.add(doc)
                break

    # Generate priority steps
    priority_steps: List[str] = []

    # Check if CadUnico is needed
    needs_cadunico = any(
        any(rule.get("field") == "cadastradoCadunico" for rule in (b.eligibility_rules or []))
        for b in benefits
        if any(r.benefit.id == b.id for r in eligible_and_likely)
    )

    if not profile.cadastrado_cadunico and needs_cadunico:
        priority_steps.append("Faça ou atualize seu Cadastro Único no CRAS")

    if eligible:
        top_benefit = eligible[0]
        # Find the full benefit to get whereToApply
        for benefit in benefits:
            if benefit.id == top_benefit.benefit.id:
                priority_steps.append(
                    f"Solicite o {top_benefit.benefit.name} - {benefit.where_to_apply}"
                )
                break

    if likely_eligible:
        priority_steps.append("Vá ao CRAS para verificar outros benefícios possíveis")

    # Build summary
    summary = EligibilitySummary(
        eligible=eligible,
        likelyEligible=likely_eligible,
        maybe=maybe,
        notEligible=not_eligible if include_not_applicable else [],
        notApplicable=not_applicable if include_not_applicable else [],
        alreadyReceiving=already_receiving,
        totalAnalyzed=len(results),
        totalPotentialMonthly=total_monthly,
        totalPotentialAnnual=total_annual,
        totalPotentialOneTime=total_one_time,
        prioritySteps=priority_steps,
        documentsNeeded=list(documents_needed),
    )

    # Profile summary for response
    profile_summary = {
        "estado": profile.estado,
        "municipio": profile.municipio_nome or profile.municipio_ibge,
        "pessoasNaCasa": profile.pessoas_na_casa,
        "rendaFamiliar": profile.renda_familiar_mensal,
        "rendaPerCapita": calculate_renda_per_capita(profile),
        "cadastradoCadunico": profile.cadastrado_cadunico,
    }

    return EligibilityResponse(
        profileSummary=profile_summary,
        summary=summary,
        evaluatedAt=datetime.utcnow().isoformat(),
    )


async def get_benefits_for_location(
    db: AsyncSession,
    state_code: str,
    ibge_code: Optional[str] = None,
) -> List[Benefit]:
    """Get all applicable benefits for a location."""
    # Start with federal benefits
    stmt = select(Benefit).where(
        Benefit.status == "active",
    )

    result = await db.execute(stmt)
    all_benefits = result.scalars().all()

    # Filter by location
    applicable = []
    for benefit in all_benefits:
        if benefit.scope == "federal":
            applicable.append(benefit)
        elif benefit.scope == "state" and benefit.state == state_code:
            applicable.append(benefit)
        elif benefit.scope == "municipal" and ibge_code and benefit.municipality_ibge == ibge_code:
            applicable.append(benefit)
        elif benefit.scope == "sectoral":
            if not benefit.state or benefit.state == state_code:
                applicable.append(benefit)

    return applicable

"""Pydantic schemas for benefits API."""

from datetime import date
from typing import Optional, List, Any, Literal
from pydantic import BaseModel, ConfigDict, Field


# ========== BENEFIT SCHEMAS ==========

class EstimatedValue(BaseModel):
    """Estimated value for a benefit."""
    type: Literal["monthly", "annual", "one_time"]
    min: Optional[float] = None
    max: Optional[float] = None
    description: Optional[str] = None
    estimated: Optional[bool] = None
    estimated_rationale: Optional[str] = Field(None, alias="estimatedRationale")


class EligibilityRule(BaseModel):
    """Single eligibility rule for a benefit."""
    field: str
    operator: Literal["lte", "gte", "lt", "gt", "eq", "neq", "in", "not_in", "has", "not_has"]
    value: Any
    description: str


class BenefitResponse(BaseModel):
    """Benefit response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    short_description: str = Field(alias="shortDescription")
    scope: Literal["federal", "state", "municipal", "sectoral"]
    state: Optional[str] = None
    municipality_ibge: Optional[str] = Field(None, alias="municipalityIbge")
    sector: Optional[str] = None
    estimated_value: Optional[EstimatedValue] = Field(None, alias="estimatedValue")
    eligibility_rules: List[EligibilityRule] = Field(alias="eligibilityRules")
    where_to_apply: str = Field(alias="whereToApply")
    documents_required: List[str] = Field(alias="documentsRequired")
    how_to_apply: Optional[List[str]] = Field(None, alias="howToApply")
    source_url: Optional[str] = Field(None, alias="sourceUrl")
    last_updated: date = Field(alias="lastUpdated")
    status: Literal["active", "suspended", "ended"]
    icon: Optional[str] = None
    category: Optional[str] = None

    # Override to handle alias population from ORM
    @classmethod
    def from_orm_dict(cls, data: dict) -> "BenefitResponse":
        """Create from ORM model.to_dict() output."""
        return cls(**data)


class BenefitSummary(BaseModel):
    """Simplified benefit for list views."""
    id: str
    name: str
    short_description: str = Field(alias="shortDescription")
    scope: str
    state: Optional[str] = None
    municipality_ibge: Optional[str] = Field(None, alias="municipalityIbge")
    estimated_value: Optional[EstimatedValue] = Field(None, alias="estimatedValue")
    status: str
    icon: Optional[str] = None
    category: Optional[str] = None


class BenefitListResponse(BaseModel):
    """Paginated list of benefits."""
    items: List[BenefitSummary]
    total: int
    page: int
    limit: int
    pages: int


class BenefitStatsResponse(BaseModel):
    """Statistics about the benefits catalog."""
    total_benefits: int = Field(alias="totalBenefits")
    by_scope: dict[str, int] = Field(alias="byScope")
    by_category: dict[str, int] = Field(alias="byCategory")
    states_covered: int = Field(alias="statesCovered")
    municipalities_covered: int = Field(alias="municipalitiesCovered")


# ========== CITIZEN PROFILE SCHEMAS ==========

class CitizenProfile(BaseModel):
    """
    Citizen profile for eligibility evaluation.
    Matches the frontend CitizenProfile type.
    """
    # Location
    estado: str = Field(description="UF code (e.g., 'SP', 'RJ')")
    municipio_ibge: Optional[str] = Field(None, alias="municipioIbge", description="IBGE municipality code")
    municipio_nome: Optional[str] = Field(None, alias="municipioNome")

    # Basic info
    idade: Optional[int] = Field(None, ge=0, le=150)
    cpf: Optional[str] = None
    nome: Optional[str] = None
    cep: Optional[str] = None

    # Family
    pessoas_na_casa: int = Field(1, ge=1, alias="pessoasNaCasa")
    quantidade_filhos: int = Field(0, ge=0, alias="quantidadeFilhos")
    tem_idoso_65_mais: bool = Field(False, alias="temIdoso65Mais")
    tem_gestante: bool = Field(False, alias="temGestante")
    tem_pcd: bool = Field(False, alias="temPcd")
    tem_crianca_0_a_6: bool = Field(False, alias="temCrianca0a6")

    # Income
    renda_familiar_mensal: float = Field(0, ge=0, alias="rendaFamiliarMensal")
    trabalho_formal: bool = Field(False, alias="trabalhoFormal")

    # Housing
    tem_casa_propria: bool = Field(False, alias="temCasaPropria")
    moradia_zona_rural: bool = Field(False, alias="moradiaZonaRural")

    # CadUnico and current benefits
    cadastrado_cadunico: bool = Field(False, alias="cadastradoCadunico")
    nis_cadunico: Optional[str] = Field(None, alias="nisCadunico")
    recebe_bolsa_familia: bool = Field(False, alias="recebeBolsaFamilia")
    valor_bolsa_familia: Optional[float] = Field(None, alias="valorBolsaFamilia")
    recebe_bpc: bool = Field(False, alias="recebeBpc")

    # Work history
    trabalhou_1971_1988: Optional[bool] = Field(None, alias="trabalhou1971_1988")
    tem_carteira_assinada: Optional[bool] = Field(None, alias="temCarteiraAssinada")
    tempo_carteira_assinada: Optional[int] = Field(None, alias="tempoCarteiraAssinada", description="Months")
    fez_saque_fgts: Optional[bool] = Field(None, alias="fezSaqueFgts")

    # Sectoral
    profissao: Optional[str] = None
    tem_mei: bool = Field(False, alias="temMei")
    trabalha_aplicativo: bool = Field(False, alias="trabalhaAplicativo")
    agricultor_familiar: bool = Field(False, alias="agricultorFamiliar")
    pescador_artesanal: bool = Field(False, alias="pescadorArtesanal")
    catador_reciclavel: bool = Field(False, alias="catadorReciclavel")

    # Special conditions
    mulher_menstruante: Optional[bool] = Field(None, alias="mulherMenstruante")
    idade_mulher: Optional[int] = Field(None, alias="idadeMulher")

    # Education
    estudante: bool = False
    rede_publica: bool = Field(False, alias="redePublica")

    @property
    def renda_per_capita(self) -> float:
        """Calculate per capita income."""
        if self.pessoas_na_casa <= 0:
            return self.renda_familiar_mensal
        return self.renda_familiar_mensal / self.pessoas_na_casa


# ========== ELIGIBILITY SCHEMAS ==========

class EligibilityRequest(BaseModel):
    """Request to evaluate eligibility."""
    profile: CitizenProfile
    scope: Optional[Literal["federal", "state", "municipal", "sectoral"]] = None
    include_not_applicable: bool = Field(False, alias="includeNotApplicable")


class RuleEvaluationResult(BaseModel):
    """Result of evaluating a single rule."""
    rule_description: str = Field(alias="ruleDescription")
    passed: bool
    inconclusive: bool = False
    field: str
    expected_value: Any = Field(alias="expectedValue")
    actual_value: Any = Field(None, alias="actualValue")


class BenefitEligibilityResult(BaseModel):
    """Eligibility result for a single benefit."""
    benefit: BenefitSummary
    status: Literal["eligible", "likely_eligible", "maybe", "not_eligible", "not_applicable", "already_receiving"]
    matched_rules: List[str] = Field(alias="matchedRules")
    failed_rules: List[str] = Field(alias="failedRules")
    inconclusive_rules: List[str] = Field(alias="inconclusiveRules")
    estimated_value: Optional[float] = Field(None, alias="estimatedValue")
    reason: Optional[str] = None
    rule_details: Optional[List[RuleEvaluationResult]] = Field(None, alias="ruleDetails")


class EligibilitySummary(BaseModel):
    """Summary of eligibility evaluation."""
    eligible: List[BenefitEligibilityResult]
    likely_eligible: List[BenefitEligibilityResult] = Field(alias="likelyEligible")
    maybe: List[BenefitEligibilityResult]
    not_eligible: List[BenefitEligibilityResult] = Field(alias="notEligible")
    not_applicable: List[BenefitEligibilityResult] = Field(alias="notApplicable")
    already_receiving: List[BenefitEligibilityResult] = Field(alias="alreadyReceiving")

    total_analyzed: int = Field(alias="totalAnalyzed")
    total_potential_monthly: float = Field(alias="totalPotentialMonthly")
    total_potential_annual: float = Field(alias="totalPotentialAnnual")
    total_potential_one_time: float = Field(alias="totalPotentialOneTime")

    priority_steps: List[str] = Field(alias="prioritySteps")
    documents_needed: List[str] = Field(alias="documentsNeeded")


class EligibilityResponse(BaseModel):
    """Full eligibility evaluation response."""
    profile_summary: dict = Field(alias="profileSummary")
    summary: EligibilitySummary
    evaluated_at: str = Field(alias="evaluatedAt")

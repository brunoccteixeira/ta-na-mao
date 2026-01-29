"""
Tool de Triagem Universal - Verifica elegibilidade para todos os benefícios.

Esta tool executa a triagem de elegibilidade para todos os programas sociais
disponíveis e retorna uma "Carteira de Direitos" com os benefícios que o
cidadão pode ter acesso.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

from .regras_elegibilidade import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    verificar_bolsa_familia,
    verificar_bpc,
    verificar_farmacia_popular,
    verificar_tsee,
    verificar_auxilio_gas,
    verificar_dignidade_menstrual,
    verificar_mcmv,
    verificar_pis_pasep,
)

logger = logging.getLogger(__name__)


@dataclass
class HabitacaoInfo:
    """Informações específicas de habitação da triagem."""
    faixa_mcmv: Optional[str] = None
    elegivel_aquisicao: bool = False
    elegivel_reforma: bool = False
    subsidio_estimado: float = 0.0
    parcela_estimada: float = 0.0
    encaminhamento: Optional[str] = None
    grupo_prioritario: Optional[str] = None


@dataclass
class TriagemResult:
    """Resultado da triagem universal de elegibilidade."""

    # Benefícios por status
    beneficios_elegiveis: List[EligibilityResult] = field(default_factory=list)
    beneficios_ja_recebe: List[EligibilityResult] = field(default_factory=list)
    beneficios_inelegiveis: List[EligibilityResult] = field(default_factory=list)
    beneficios_inconclusivos: List[EligibilityResult] = field(default_factory=list)

    # Resumo
    total_programas_analisados: int = 0
    valor_potencial_mensal: float = 0.0
    valor_ja_recebe_mensal: float = 0.0

    # Próximos passos consolidados
    proximos_passos_prioritarios: List[str] = field(default_factory=list)

    # Documentos consolidados (sem duplicatas)
    documentos_necessarios: List[str] = field(default_factory=list)

    # Informações de habitação (enriquecido)
    habitacao: Optional[HabitacaoInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        result = {
            "beneficios_elegiveis": [
                self._eligibility_to_dict(b) for b in self.beneficios_elegiveis
            ],
            "beneficios_ja_recebe": [
                self._eligibility_to_dict(b) for b in self.beneficios_ja_recebe
            ],
            "beneficios_inelegiveis": [
                self._eligibility_to_dict(b) for b in self.beneficios_inelegiveis
            ],
            "beneficios_inconclusivos": [
                self._eligibility_to_dict(b) for b in self.beneficios_inconclusivos
            ],
            "total_programas_analisados": self.total_programas_analisados,
            "valor_potencial_mensal": self.valor_potencial_mensal,
            "valor_ja_recebe_mensal": self.valor_ja_recebe_mensal,
            "proximos_passos_prioritarios": self.proximos_passos_prioritarios,
            "documentos_necessarios": self.documentos_necessarios,
        }

        # Adicionar info de habitação se disponível
        if self.habitacao:
            result["habitacao"] = {
                "faixa_mcmv": self.habitacao.faixa_mcmv,
                "elegivel_aquisicao": self.habitacao.elegivel_aquisicao,
                "elegivel_reforma": self.habitacao.elegivel_reforma,
                "subsidio_estimado": self.habitacao.subsidio_estimado,
                "parcela_estimada": self.habitacao.parcela_estimada,
                "encaminhamento": self.habitacao.encaminhamento,
                "grupo_prioritario": self.habitacao.grupo_prioritario,
            }

        return result

    def _eligibility_to_dict(self, e: EligibilityResult) -> Dict[str, Any]:
        return {
            "programa": e.programa,
            "programa_nome": e.programa_nome,
            "status": e.status.value,
            "motivo": e.motivo,
            "valor_estimado": e.valor_estimado,
            "proximos_passos": e.proximos_passos,
            "documentos_necessarios": e.documentos_necessarios,
            "onde_solicitar": e.onde_solicitar,
            "observacoes": e.observacoes,
        }


# Lista de todos os verificadores disponíveis
VERIFICADORES = [
    ("BOLSA_FAMILIA", verificar_bolsa_familia),
    ("BPC", verificar_bpc),
    ("FARMACIA_POPULAR", verificar_farmacia_popular),
    ("TSEE", verificar_tsee),
    ("AUXILIO_GAS", verificar_auxilio_gas),
    ("DIGNIDADE_MENSTRUAL", verificar_dignidade_menstrual),
    ("MCMV", verificar_mcmv),
    ("PIS_PASEP", verificar_pis_pasep),
]


async def triagem_universal(perfil: CitizenProfile) -> TriagemResult:
    """
    Executa triagem de elegibilidade para todos os programas sociais.

    Args:
        perfil: Dados do cidadão (CitizenProfile)

    Returns:
        TriagemResult com todos os resultados consolidados
    """
    resultado = TriagemResult()
    documentos_set = set()

    for programa_id, verificador in VERIFICADORES:
        try:
            elegibilidade = verificador(perfil)
            resultado.total_programas_analisados += 1

            # Classificar por status
            if elegibilidade.status == EligibilityStatus.ELEGIVEL:
                resultado.beneficios_elegiveis.append(elegibilidade)
                if elegibilidade.valor_estimado:
                    resultado.valor_potencial_mensal += elegibilidade.valor_estimado

            elif elegibilidade.status == EligibilityStatus.JA_RECEBE:
                resultado.beneficios_ja_recebe.append(elegibilidade)
                if elegibilidade.valor_estimado:
                    resultado.valor_ja_recebe_mensal += elegibilidade.valor_estimado

            elif elegibilidade.status == EligibilityStatus.INELEGIVEL:
                resultado.beneficios_inelegiveis.append(elegibilidade)

            elif elegibilidade.status == EligibilityStatus.INCONCLUSIVO:
                resultado.beneficios_inconclusivos.append(elegibilidade)

            # Coletar documentos necessários (sem duplicatas)
            if elegibilidade.documentos_necessarios:
                for doc in elegibilidade.documentos_necessarios:
                    documentos_set.add(doc)

            # Enriquecer informações de habitação
            if programa_id == "MCMV":
                resultado.habitacao = _extrair_info_habitacao(elegibilidade, perfil)

        except Exception as e:
            logger.error(f"Erro ao verificar {programa_id}: {e}")

    # Consolidar documentos
    resultado.documentos_necessarios = sorted(list(documentos_set))

    # Gerar próximos passos prioritários
    resultado.proximos_passos_prioritarios = _gerar_proximos_passos(resultado, perfil)

    return resultado


def _extrair_info_habitacao(
    elegibilidade: EligibilityResult,
    perfil: CitizenProfile
) -> HabitacaoInfo:
    """Extrai informações de habitação do resultado MCMV."""
    from .regras_elegibilidade import (
        MCMV_FAIXA_1,
        MCMV_FAIXA_2,
        MCMV_FAIXA_3,
        MCMV_FAIXA_4,
        REFORMA_LIMITE_FAIXA_2,
    )

    renda = perfil.renda_familiar_mensal

    # Determinar faixa
    if renda <= MCMV_FAIXA_1:
        faixa = "Faixa 1"
    elif renda <= MCMV_FAIXA_2:
        faixa = "Faixa 2"
    elif renda <= MCMV_FAIXA_3:
        faixa = "Faixa 3"
    elif renda <= MCMV_FAIXA_4:
        faixa = "Faixa 4"
    else:
        faixa = None

    # Elegibilidade
    elegivel_aquisicao = (
        elegibilidade.status == EligibilityStatus.ELEGIVEL
        and "MCMV" in elegibilidade.programa
        and "REFORMAS" not in elegibilidade.programa
    )

    elegivel_reforma = (
        perfil.tem_casa_propria
        and renda <= REFORMA_LIMITE_FAIXA_2
    )

    # Identificar grupo prioritário
    grupo = None
    if perfil.situacao_rua:
        grupo = "Pessoa em situação de rua"
    elif getattr(perfil, "vitima_violencia_domestica", False):
        grupo = "Vítima de violência doméstica"
    elif getattr(perfil, "em_area_risco", False):
        grupo = "Família em área de risco"
    elif perfil.recebe_bpc or perfil.recebe_bolsa_familia:
        if faixa == "Faixa 1":
            grupo = "Beneficiário BPC/Bolsa Família"
    elif perfil.tem_pcd:
        grupo = "Família com PCD"
    elif perfil.tem_idoso_65_mais:
        grupo = "Família com idoso"

    # Encaminhamento
    if perfil.tem_casa_propria:
        encaminhamento = "CAIXA - Programa de Reformas"
    elif faixa == "Faixa 1":
        if not perfil.cadastrado_cadunico:
            encaminhamento = "CRAS (fazer CadÚnico)"
        else:
            encaminhamento = "Prefeitura - Secretaria de Habitação"
    elif faixa:
        encaminhamento = "CAIXA Econômica Federal"
    else:
        encaminhamento = "Sistema Financeiro de Habitação"

    return HabitacaoInfo(
        faixa_mcmv=faixa,
        elegivel_aquisicao=elegivel_aquisicao,
        elegivel_reforma=elegivel_reforma,
        subsidio_estimado=elegibilidade.valor_estimado or 0,
        parcela_estimada=0,  # Seria necessário chamar simulador
        encaminhamento=encaminhamento,
        grupo_prioritario=grupo,
    )


def _gerar_proximos_passos(resultado: TriagemResult, perfil: CitizenProfile) -> List[str]:
    """
    Gera lista priorizada de próximos passos baseado nos resultados.

    Ordem de prioridade:
    1. CadÚnico (se não tem e precisa)
    2. Benefícios de maior valor
    3. Benefícios de acesso mais fácil
    """
    passos = []

    # 1. CadÚnico é prioridade se não tem
    if not perfil.cadastrado_cadunico:
        programas_que_precisam = [
            b.programa_nome
            for b in resultado.beneficios_elegiveis
            if b.programa not in ["FARMACIA_POPULAR", "PIS_PASEP"]
        ]
        if programas_que_precisam:
            passos.append(
                f"1. PRIORIDADE: Faça o CadÚnico no CRAS - necessário para: {', '.join(programas_que_precisam[:3])}"
            )

    # 2. Ordenar benefícios elegíveis por valor (maior primeiro)
    elegiveis_com_valor = [
        b for b in resultado.beneficios_elegiveis if b.valor_estimado
    ]
    elegiveis_com_valor.sort(key=lambda x: x.valor_estimado or 0, reverse=True)

    # 3. Adicionar passos para benefícios de maior valor
    for i, beneficio in enumerate(elegiveis_com_valor[:3], start=len(passos) + 1):
        if beneficio.proximos_passos:
            passos.append(
                f"{i}. {beneficio.programa_nome} (R$ {beneficio.valor_estimado:.0f}/mês): {beneficio.proximos_passos[0]}"
            )

    # 4. Farmácia Popular (acesso fácil, sempre útil)
    farmacia = next(
        (b for b in resultado.beneficios_elegiveis if b.programa == "FARMACIA_POPULAR"),
        None,
    )
    if farmacia and len(passos) < 5:
        passos.append(
            f"{len(passos) + 1}. Farmácia Popular: Vá a uma farmácia credenciada com receita médica para remédios gratuitos"
        )

    # 5. PIS/PASEP (potencial de valor alto)
    pis = next(
        (b for b in resultado.beneficios_inconclusivos if b.programa == "PIS_PASEP"),
        None,
    )
    if pis and len(passos) < 5:
        passos.append(
            f"{len(passos) + 1}. PIS/PASEP: Consulte na CAIXA ou Banco do Brasil se tem dinheiro esquecido"
        )

    # 6. MCMV - Encaminhamento específico para habitação
    if resultado.habitacao and resultado.habitacao.elegivel_aquisicao:
        encaminhamento = resultado.habitacao.encaminhamento or "CAIXA"
        faixa = resultado.habitacao.faixa_mcmv or ""
        if len(passos) < 6:
            passos.append(
                f"{len(passos) + 1}. Minha Casa Minha Vida ({faixa}): {encaminhamento}"
            )

    return passos


def triagem_para_texto(resultado: TriagemResult) -> str:
    """
    Converte resultado da triagem em texto formatado para o chat.

    Args:
        resultado: TriagemResult da triagem

    Returns:
        Texto formatado em linguagem simples
    """
    linhas = []

    # Cabeçalho
    total_elegiveis = len(resultado.beneficios_elegiveis)
    if total_elegiveis > 0:
        linhas.append(f"🎉 **Boa notícia!** Você pode ter direito a {total_elegiveis} benefício(s)!\n")
    else:
        linhas.append("Analisamos sua situação.\n")

    # Benefícios que já recebe
    if resultado.beneficios_ja_recebe:
        linhas.append("**Benefícios que você já recebe:**")
        for b in resultado.beneficios_ja_recebe:
            valor = f" (R$ {b.valor_estimado:.0f}/mês)" if b.valor_estimado else ""
            linhas.append(f"✅ {b.programa_nome}{valor}")
        linhas.append("")

    # Benefícios elegíveis
    if resultado.beneficios_elegiveis:
        linhas.append("**Benefícios que você pode ter direito:**")
        for b in resultado.beneficios_elegiveis:
            valor = f" - até R$ {b.valor_estimado:.0f}/mês" if b.valor_estimado else ""
            linhas.append(f"💰 **{b.programa_nome}**{valor}")
            linhas.append(f"   {b.motivo[:100]}...")
        linhas.append("")

    # Valor potencial
    if resultado.valor_potencial_mensal > 0:
        linhas.append(
            f"💵 **Valor potencial:** até R$ {resultado.valor_potencial_mensal:.0f}/mês em benefícios\n"
        )

    # Próximos passos
    if resultado.proximos_passos_prioritarios:
        linhas.append("**Próximos passos:**")
        for passo in resultado.proximos_passos_prioritarios:
            linhas.append(f"• {passo}")
        linhas.append("")

    # Documentos
    if resultado.documentos_necessarios:
        linhas.append("**Documentos que você vai precisar:**")
        for doc in resultado.documentos_necessarios[:6]:  # Limitar a 6
            linhas.append(f"📄 {doc}")

    return "\n".join(linhas)


# Função para criar perfil a partir de dados coletados
def criar_perfil_cidadao(
    cpf: Optional[str] = None,
    nome: Optional[str] = None,
    data_nascimento: Optional[str] = None,
    municipio: Optional[str] = None,
    uf: Optional[str] = None,
    pessoas_na_casa: int = 1,
    renda_familiar_mensal: float = 0.0,
    tem_filhos_menores: bool = False,
    quantidade_filhos: int = 0,
    tem_idoso_65_mais: bool = False,
    tem_gestante: bool = False,
    tem_pcd: bool = False,
    recebe_bolsa_familia: bool = False,
    valor_bolsa_familia: float = 0.0,
    recebe_bpc: bool = False,
    cadastrado_cadunico: bool = False,
    tem_casa_propria: bool = False,
    trabalhou_1971_1988: Optional[bool] = None,
    # Novos campos MCMV
    regiao_metropolitana: bool = False,
    tem_imovel_registrado: Optional[bool] = None,
    teve_beneficio_habitacional_federal: Optional[bool] = None,
    tem_financiamento_ativo: Optional[bool] = None,
    em_area_risco: bool = False,
    vitima_violencia_domestica: bool = False,
    situacao_rua: bool = False,
    valor_fgts_disponivel: Optional[float] = None,
    tempo_contribuicao_fgts_meses: Optional[int] = None,
    tem_restricao_credito: Optional[bool] = None,
    **kwargs,
) -> CitizenProfile:
    """
    Cria um CitizenProfile a partir de dados coletados no chat.

    Args:
        Dados coletados do cidadão

    Returns:
        CitizenProfile populado
    """
    return CitizenProfile(
        cpf=cpf,
        nome=nome,
        data_nascimento=data_nascimento,
        municipio=municipio,
        uf=uf,
        pessoas_na_casa=pessoas_na_casa,
        renda_familiar_mensal=renda_familiar_mensal,
        tem_filhos_menores=tem_filhos_menores,
        quantidade_filhos=quantidade_filhos,
        tem_idoso_65_mais=tem_idoso_65_mais,
        tem_gestante=tem_gestante,
        tem_pcd=tem_pcd,
        recebe_bolsa_familia=recebe_bolsa_familia,
        valor_bolsa_familia=valor_bolsa_familia,
        recebe_bpc=recebe_bpc,
        cadastrado_cadunico=cadastrado_cadunico,
        tem_casa_propria=tem_casa_propria,
        trabalhou_1971_1988=trabalhou_1971_1988,
        # Novos campos MCMV
        regiao_metropolitana=regiao_metropolitana,
        tem_imovel_registrado=tem_imovel_registrado,
        teve_beneficio_habitacional_federal=teve_beneficio_habitacional_federal,
        tem_financiamento_ativo=tem_financiamento_ativo,
        em_area_risco=em_area_risco,
        vitima_violencia_domestica=vitima_violencia_domestica,
        situacao_rua=situacao_rua,
        valor_fgts_disponivel=valor_fgts_disponivel,
        tempo_contribuicao_fgts_meses=tempo_contribuicao_fgts_meses,
        tem_restricao_credito=tem_restricao_credito,
    )

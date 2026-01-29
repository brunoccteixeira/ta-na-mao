"""Tool para verificar elegibilidade de cidadaos SEM documentacao.

Esta tool implementa verificacao de elegibilidade baseada em questionario,
para cidadaos que nao tem CPF/RG mas querem saber se tem direito a beneficios.

Baseado nas diretrizes do CadUnico e recomendacoes do Banco Mundial (ID4D)
sobre inclusao de populacoes vulneraveis sem documentacao.

Fato importante: O CadUnico aceita Certidao de Nascimento como documento!
Mesmo sem RG, o cidadao pode se cadastrar.
"""

from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

from app.agent.tools.base import ToolResult, UIHint


class FaixaRenda(str, Enum):
    """Faixas de renda per capita familiar."""
    EXTREMA_POBREZA = "extrema_pobreza"  # Ate R$ 105,00
    POBREZA = "pobreza"  # R$ 105,01 a R$ 218,00
    BAIXA_RENDA = "baixa_renda"  # Ate 1/2 salario minimo
    ACIMA = "acima"  # Acima de 1/2 salario minimo


class SituacaoMoradia(str, Enum):
    """Situacao de moradia do cidadao."""
    PROPRIO = "proprio"
    ALUGADO = "alugado"
    CEDIDO = "cedido"
    RUA = "rua"
    ABRIGO = "abrigo"
    OCUPACAO = "ocupacao"


class ElegibilidadeResult(ToolResult):
    """Resultado de verificacao de elegibilidade."""

    @classmethod
    def elegivel(
        cls,
        programas: List[Dict[str, Any]],
        faixa_renda: FaixaRenda,
        documentos_necessarios: List[str],
        orientacoes: str
    ) -> "ElegibilidadeResult":
        return cls(
            success=True,
            data={
                "elegivel": True,
                "programas_possiveis": programas,
                "faixa_renda": faixa_renda.value,
                "documentos_necessarios": documentos_necessarios,
                "orientacoes": orientacoes,
                "pode_gerar_carta": True
            },
            ui_hint=UIHint.ELIGIBILITY_STATUS
        )

    @classmethod
    def inconclusivo(
        cls,
        motivo: str,
        proximos_passos: str
    ) -> "ElegibilidadeResult":
        return cls(
            success=True,
            data={
                "elegivel": None,
                "motivo": motivo,
                "proximos_passos": proximos_passos,
                "pode_gerar_carta": True  # Mesmo inconclusivo, pode encaminhar
            },
            ui_hint=UIHint.INFO
        )


# Constantes de renda (valores de 2024/2025)
LINHA_EXTREMA_POBREZA = 105.00  # Ate R$ 105 per capita
LINHA_POBREZA = 218.00  # Ate R$ 218 per capita
SALARIO_MINIMO = 1518.00  # Salario minimo 2025
MEIO_SALARIO = SALARIO_MINIMO / 2
QUARTO_SALARIO = SALARIO_MINIMO / 4


def calcular_faixa_renda(
    renda_total_familiar: float,
    qtd_pessoas: int
) -> FaixaRenda:
    """Calcula a faixa de renda per capita da familia.

    Args:
        renda_total_familiar: Renda mensal total da familia
        qtd_pessoas: Quantidade de pessoas na familia

    Returns:
        FaixaRenda correspondente
    """
    if qtd_pessoas <= 0:
        qtd_pessoas = 1

    renda_per_capita = renda_total_familiar / qtd_pessoas

    if renda_per_capita <= LINHA_EXTREMA_POBREZA:
        return FaixaRenda.EXTREMA_POBREZA
    elif renda_per_capita <= LINHA_POBREZA:
        return FaixaRenda.POBREZA
    elif renda_per_capita <= MEIO_SALARIO:
        return FaixaRenda.BAIXA_RENDA
    else:
        return FaixaRenda.ACIMA


def verificar_elegibilidade_sem_docs(
    # Dados basicos
    idade: Optional[int] = None,
    data_nascimento: Optional[str] = None,

    # Composicao familiar
    qtd_pessoas_familia: int = 1,
    tem_criancas_0_6: bool = False,
    tem_criancas_7_17: bool = False,
    tem_gestante: bool = False,
    tem_idoso_65_mais: bool = False,
    tem_pessoa_deficiencia: bool = False,

    # Situacao economica
    renda_total_familiar: float = 0,
    trabalha_formal: bool = False,
    recebe_algum_beneficio: bool = False,

    # Moradia
    situacao_moradia: Optional[str] = None,
    tem_endereco_fixo: bool = True,

    # Documentacao
    tem_certidao_nascimento: bool = False,
    tem_rg: bool = False,
    tem_cpf: bool = False,
    tem_titulo_eleitor: bool = False,
    tem_carteira_trabalho: bool = False
) -> ElegibilidadeResult:
    """Verifica elegibilidade para programas sociais SEM exigir CPF.

    Esta funcao permite verificar elegibilidade baseada em questionario,
    para pessoas que nao tem documentacao completa.

    IMPORTANTE: O CadUnico aceita diversos documentos alternativos ao RG!
    - Certidao de Nascimento
    - Carteira de Trabalho
    - Titulo de Eleitor
    - Carteira Profissional (OAB, CREA, etc)

    Args:
        idade: Idade em anos (ou calcular de data_nascimento)
        data_nascimento: Data de nascimento (YYYY-MM-DD)
        qtd_pessoas_familia: Total de pessoas na familia
        tem_criancas_0_6: Tem criancas de 0 a 6 anos
        tem_criancas_7_17: Tem criancas/adolescentes de 7 a 17 anos
        tem_gestante: Familia tem gestante
        tem_idoso_65_mais: Familia tem idoso 65+
        tem_pessoa_deficiencia: Familia tem PCD
        renda_total_familiar: Renda mensal total da familia
        trabalha_formal: Trabalha com carteira assinada
        recebe_algum_beneficio: Ja recebe algum beneficio
        situacao_moradia: Tipo de moradia
        tem_endereco_fixo: Tem endereco fixo
        tem_certidao_nascimento: Tem certidao de nascimento
        tem_rg: Tem RG
        tem_cpf: Tem CPF
        tem_titulo_eleitor: Tem titulo de eleitor
        tem_carteira_trabalho: Tem carteira de trabalho

    Returns:
        ElegibilidadeResult com programas elegiveis e orientacoes
    """
    # Calcula idade se data_nascimento fornecida
    if data_nascimento and not idade:
        try:
            nasc = date.fromisoformat(data_nascimento)
            hoje = date.today()
            idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        except ValueError:
            pass

    # Calcula faixa de renda
    faixa = calcular_faixa_renda(renda_total_familiar, qtd_pessoas_familia)

    # Lista de programas elegiveis
    programas_elegiveis = []

    # ==========================================================================
    # BOLSA FAMILIA
    # Criterio: Renda per capita ate R$ 218
    # ==========================================================================
    if faixa in [FaixaRenda.EXTREMA_POBREZA, FaixaRenda.POBREZA]:
        programa = {
            "codigo": "BOLSA_FAMILIA",
            "nome": "Bolsa Familia",
            "elegivel": True,
            "valor_estimado": _estimar_valor_bolsa_familia(
                qtd_pessoas_familia,
                tem_criancas_0_6,
                tem_criancas_7_17,
                tem_gestante
            ),
            "motivo": f"Renda familiar de R$ {renda_total_familiar:.2f} para {qtd_pessoas_familia} pessoas "
                     f"(R$ {renda_total_familiar/qtd_pessoas_familia:.2f} per capita) esta dentro do limite.",
            "como_solicitar": "Fazer ou atualizar CadUnico no CRAS"
        }
        programas_elegiveis.append(programa)

    # ==========================================================================
    # BPC/LOAS - Idoso
    # Criterio: 65+ anos, renda per capita ate 1/4 salario minimo
    # ==========================================================================
    if idade and idade >= 65 and renda_total_familiar / qtd_pessoas_familia <= QUARTO_SALARIO:
        programas_elegiveis.append({
            "codigo": "BPC_IDOSO",
            "nome": "BPC/LOAS (Idoso)",
            "elegivel": True,
            "valor_estimado": SALARIO_MINIMO,
            "motivo": f"Idade de {idade} anos e renda per capita de "
                     f"R$ {renda_total_familiar/qtd_pessoas_familia:.2f} (limite: R$ {QUARTO_SALARIO:.2f})",
            "como_solicitar": "Agendar no INSS (135) ou pelo Meu INSS"
        })

    # ==========================================================================
    # BPC/LOAS - PCD
    # Criterio: Pessoa com deficiencia, renda per capita ate 1/4 salario minimo
    # ==========================================================================
    if tem_pessoa_deficiencia and renda_total_familiar / qtd_pessoas_familia <= QUARTO_SALARIO:
        programas_elegiveis.append({
            "codigo": "BPC_PCD",
            "nome": "BPC/LOAS (Pessoa com Deficiencia)",
            "elegivel": True,
            "valor_estimado": SALARIO_MINIMO,
            "motivo": f"Pessoa com deficiencia e renda per capita de "
                     f"R$ {renda_total_familiar/qtd_pessoas_familia:.2f} (limite: R$ {QUARTO_SALARIO:.2f})",
            "como_solicitar": "Agendar pericia no INSS (135) ou pelo Meu INSS"
        })

    # ==========================================================================
    # TARIFA SOCIAL DE ENERGIA
    # Criterio: CadUnico com renda ate 1/2 SM ou receber BPC/BF
    # ==========================================================================
    if faixa in [FaixaRenda.EXTREMA_POBREZA, FaixaRenda.POBREZA, FaixaRenda.BAIXA_RENDA]:
        programas_elegiveis.append({
            "codigo": "TSEE",
            "nome": "Tarifa Social de Energia Eletrica",
            "elegivel": True,
            "valor_estimado": None,  # Desconto de 10% a 65%
            "motivo": "Renda familiar dentro dos limites para desconto na conta de luz",
            "como_solicitar": "Solicitar na concessionaria de energia com CadUnico atualizado"
        })

    # ==========================================================================
    # FARMACIA POPULAR
    # Criterio: Qualquer brasileiro com receita medica
    # ==========================================================================
    programas_elegiveis.append({
        "codigo": "FARMACIA_POPULAR",
        "nome": "Farmacia Popular",
        "elegivel": True,
        "valor_estimado": None,  # Gratuidade ou desconto
        "motivo": "Qualquer brasileiro pode usar. Com CadUnico, pode ter gratuidade total.",
        "como_solicitar": "Ir a farmacia credenciada com CPF e receita medica"
    })

    # ==========================================================================
    # DIGNIDADE MENSTRUAL
    # Criterio: Mulheres inscritas no CadUnico
    # ==========================================================================
    if tem_gestante or tem_criancas_7_17:  # Proxy para ter mulheres na familia
        programas_elegiveis.append({
            "codigo": "DIGNIDADE_MENSTRUAL",
            "nome": "Dignidade Menstrual",
            "elegivel": True,
            "valor_estimado": None,
            "motivo": "Mulheres em idade fertil inscritas no CadUnico tem direito",
            "como_solicitar": "Ir a farmacia credenciada ou UBS com CPF"
        })

    # ==========================================================================
    # AUXILIO GAS
    # Criterio: Familias do CadUnico com renda ate 1/2 SM per capita
    # ==========================================================================
    if faixa in [FaixaRenda.EXTREMA_POBREZA, FaixaRenda.POBREZA, FaixaRenda.BAIXA_RENDA]:
        programas_elegiveis.append({
            "codigo": "AUXILIO_GAS",
            "nome": "Auxilio Gas",
            "elegivel": True,
            "valor_estimado": 104.00,  # Valor 2025 (aprox)
            "motivo": "Familias do CadUnico com renda ate 1/2 salario minimo per capita",
            "como_solicitar": "Automatico para quem esta no CadUnico e Bolsa Familia"
        })

    # ==========================================================================
    # Define documentos necessarios
    # ==========================================================================
    documentos = _definir_documentos_necessarios(
        tem_certidao_nascimento,
        tem_rg,
        tem_cpf,
        tem_titulo_eleitor,
        tem_carteira_trabalho,
        situacao_moradia
    )

    # ==========================================================================
    # Monta orientacoes personalizadas
    # ==========================================================================
    orientacoes = _gerar_orientacoes(
        programas_elegiveis,
        documentos,
        tem_endereco_fixo,
        situacao_moradia
    )

    if programas_elegiveis:
        return ElegibilidadeResult.elegivel(
            programas=programas_elegiveis,
            faixa_renda=faixa,
            documentos_necessarios=documentos,
            orientacoes=orientacoes
        )
    else:
        return ElegibilidadeResult.inconclusivo(
            motivo="Com base nas informacoes, voce pode nao se enquadrar nos criterios principais. "
                   "Mas recomendo ir ao CRAS para uma avaliacao completa!",
            proximos_passos="Procure o CRAS do seu municipio para avaliacao presencial."
        )


def _estimar_valor_bolsa_familia(
    qtd_pessoas: int,
    tem_criancas_0_6: bool,
    tem_criancas_7_17: bool,
    tem_gestante: bool
) -> float:
    """Estima valor do Bolsa Familia (valores 2025).

    Componentes:
    - Beneficio de Renda de Cidadania (BRC): R$ 142 por pessoa
    - Beneficio Complementar: Garante minimo de R$ 600
    - Beneficio Primeira Infancia: R$ 150 por crianca 0-6
    - Beneficio Variavel Familiar: R$ 50 por gestante/crianca 7-17
    """
    # Base: R$ 142 por pessoa
    valor = qtd_pessoas * 142

    # Primeira infancia (0-6): +R$ 150
    if tem_criancas_0_6:
        valor += 150

    # Variavel (7-17 ou gestante): +R$ 50
    if tem_criancas_7_17:
        valor += 50
    if tem_gestante:
        valor += 50

    # Minimo garantido de R$ 600
    if valor < 600:
        valor = 600

    return valor


def _definir_documentos_necessarios(
    tem_certidao: bool,
    tem_rg: bool,
    tem_cpf: bool,
    tem_titulo: bool,
    tem_ctps: bool,
    situacao_moradia: Optional[str]
) -> List[str]:
    """Define lista de documentos necessarios para CadUnico.

    IMPORTANTE: CadUnico aceita varios documentos alternativos ao RG!
    """
    docs = []

    # Documento de identificacao com foto - varios sao aceitos!
    if not tem_rg:
        if tem_ctps:
            docs.append("Carteira de Trabalho (voce ja tem!)")
        elif tem_titulo:
            docs.append("Titulo de Eleitor (voce ja tem!)")
        elif tem_certidao:
            docs.append("Certidao de Nascimento (voce ja tem! O CRAS pode aceitar)")
        else:
            docs.append("DOCUMENTO DE IDENTIFICACAO - Opcoes aceitas:")
            docs.append("  - Certidao de Nascimento (gratuita no cartorio)")
            docs.append("  - Carteira de Trabalho")
            docs.append("  - Titulo de Eleitor")
            docs.append("  - Carteira Profissional (OAB, CREA, etc)")
            docs.append("  - RG (se conseguir tirar)")

    # CPF
    if not tem_cpf:
        docs.append("CPF - Pode tirar gratuitamente:")
        docs.append("  - Nos Correios")
        docs.append("  - Na Receita Federal")
        docs.append("  - No proprio CRAS (alguns fazem)")

    # Comprovante de endereco
    if situacao_moradia == "rua":
        docs.append("COMPROVANTE DE ENDERECO:")
        docs.append("  - Declaracao de organizacao (abrigo, ONG)")
        docs.append("  - Declaracao de terceiro que te conhece")
        docs.append("  - O CRAS pode fazer declaracao especial")
    elif situacao_moradia in ["cedido", "ocupacao"]:
        docs.append("COMPROVANTE DE ENDERECO:")
        docs.append("  - Declaracao do proprietario/responsavel")
        docs.append("  - Conta de luz/agua em nome de quem mora junto")
    else:
        docs.append("Comprovante de endereco (conta de luz, agua, etc)")

    return docs


def _gerar_orientacoes(
    programas: List[Dict],
    documentos: List[str],
    tem_endereco: bool,
    situacao_moradia: Optional[str]
) -> str:
    """Gera orientacoes personalizadas."""
    partes = []

    # Programas elegiveis
    if programas:
        partes.append("VOCE PODE TER DIREITO A:")
        for p in programas[:3]:  # Limita a 3 principais
            valor = f" (estimado R$ {p['valor_estimado']:.2f})" if p.get('valor_estimado') else ""
            partes.append(f"  - {p['nome']}{valor}")

    # Situacao especial: pessoa em situacao de rua
    if situacao_moradia == "rua":
        partes.append("")
        partes.append("ATENCAO - VOCE ESTA EM SITUACAO DE RUA:")
        partes.append("  - O CRAS tem atendimento especial para voce")
        partes.append("  - Nao precisa de comprovante de endereco tradicional")
        partes.append("  - Pode usar endereco de referencia (abrigo, CRAS)")
        partes.append("  - Pergunte sobre o Centro POP (Centro de Referencia Especializado)")

    # Mutiroes de documentacao
    partes.append("")
    partes.append("DICA IMPORTANTE:")
    partes.append("  O CNJ realiza mutiroes 'Registre-se!' com emissao gratuita de documentos.")
    partes.append("  Pergunte no CRAS sobre os proximos mutiroes na sua cidade!")

    return "\n".join(partes)


# =============================================================================
# Funcao auxiliar para o agente
# =============================================================================

def coletar_dados_elegibilidade() -> Dict[str, Any]:
    """Retorna estrutura de dados para coletar via questionario.

    O agente usa esta funcao para saber quais perguntas fazer.
    """
    return {
        "perguntas": [
            {
                "campo": "qtd_pessoas_familia",
                "pergunta": "Quantas pessoas moram na sua casa?",
                "tipo": "numero",
                "obrigatorio": True
            },
            {
                "campo": "renda_total_familiar",
                "pergunta": "Qual a renda total da familia por mes? (some tudo que entra)",
                "tipo": "numero",
                "obrigatorio": True
            },
            {
                "campo": "tem_criancas_0_6",
                "pergunta": "Tem criancas de 0 a 6 anos na familia?",
                "tipo": "sim_nao",
                "obrigatorio": False
            },
            {
                "campo": "tem_criancas_7_17",
                "pergunta": "Tem criancas ou adolescentes de 7 a 17 anos?",
                "tipo": "sim_nao",
                "obrigatorio": False
            },
            {
                "campo": "tem_gestante",
                "pergunta": "Tem alguma gestante na familia?",
                "tipo": "sim_nao",
                "obrigatorio": False
            },
            {
                "campo": "tem_idoso_65_mais",
                "pergunta": "Tem algum idoso com 65 anos ou mais?",
                "tipo": "sim_nao",
                "obrigatorio": False
            },
            {
                "campo": "tem_pessoa_deficiencia",
                "pergunta": "Tem alguma pessoa com deficiencia na familia?",
                "tipo": "sim_nao",
                "obrigatorio": False
            },
            {
                "campo": "situacao_moradia",
                "pergunta": "Qual sua situacao de moradia?",
                "tipo": "opcoes",
                "opcoes": ["proprio", "alugado", "cedido", "rua", "abrigo", "ocupacao"],
                "obrigatorio": False
            },
            {
                "campo": "tem_certidao_nascimento",
                "pergunta": "Voce tem Certidao de Nascimento?",
                "tipo": "sim_nao",
                "obrigatorio": True
            },
            {
                "campo": "tem_cpf",
                "pergunta": "Voce tem CPF?",
                "tipo": "sim_nao",
                "obrigatorio": True
            }
        ]
    }

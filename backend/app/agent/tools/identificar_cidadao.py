"""Tool para identificacao multimodal de cidadaos.

Permite identificar cidadaos usando multiplos metodos:
1. CPF (primario)
2. NIS (secundario)
3. Nome + Municipio (fuzzy match)
4. Sem identificacao (coleta de dados para encaminhamento)

Inspirado no sistema de Introdutores do Aadhaar (India) e
recomendacoes do ID4D do Banco Mundial.
"""

import re
from typing import Optional, List, Dict, Any
from enum import Enum

from app.database import SessionLocal
from app.models.beneficiario import Beneficiario
from app.agent.tools.base import ToolResult, UIHint


class MetodoIdentificacao(str, Enum):
    """Metodos de identificacao suportados."""
    CPF = "cpf"
    NIS = "nis"
    NOME_MUNICIPIO = "nome_municipio"
    SEM_IDENTIFICACAO = "sem_identificacao"


class IdentificacaoResult(ToolResult):
    """Resultado de identificacao de cidadao."""

    @classmethod
    def identificado(
        cls,
        metodo: MetodoIdentificacao,
        beneficiario_data: Dict[str, Any],
        confianca: str = "alta"
    ) -> "IdentificacaoResult":
        """Cidadao identificado com sucesso."""
        return cls(
            success=True,
            data={
                "identificado": True,
                "metodo": metodo.value,
                "confianca": confianca,
                "beneficiario": beneficiario_data
            },
            ui_hint=UIHint.BENEFIT_LIST,
            context_updates={
                "cidadao_identificado": True,
                "metodo_identificacao": metodo.value
            }
        )

    @classmethod
    def multiplos_resultados(
        cls,
        candidatos: List[Dict[str, Any]],
        metodo: MetodoIdentificacao
    ) -> "IdentificacaoResult":
        """Multiplos candidatos encontrados - precisa confirmacao."""
        return cls(
            success=True,
            data={
                "identificado": False,
                "multiplos": True,
                "candidatos": candidatos,
                "metodo": metodo.value,
                "mensagem": "Encontrei algumas pessoas com esse nome. Qual e voce?"
            },
            ui_hint=UIHint.INFO
        )

    @classmethod
    def nao_identificado(
        cls,
        motivo: str,
        pode_continuar: bool = True
    ) -> "IdentificacaoResult":
        """Cidadao nao identificado na base."""
        return cls(
            success=True,
            data={
                "identificado": False,
                "multiplos": False,
                "motivo": motivo,
                "pode_continuar": pode_continuar,
                "proximos_passos": (
                    "Mesmo sem estar na base, posso ajudar voce! "
                    "Vou verificar se voce pode ter direito a beneficios "
                    "e te orientar sobre como se cadastrar."
                ) if pode_continuar else motivo
            },
            ui_hint=UIHint.INFO
        )


def identificar_por_cpf(cpf: str) -> IdentificacaoResult:
    """Identifica cidadao por CPF.

    Args:
        cpf: CPF com 11 digitos (com ou sem formatacao)

    Returns:
        IdentificacaoResult com dados do beneficiario ou nao encontrado
    """
    # Limpa CPF
    cpf_limpo = re.sub(r'\D', '', cpf)

    # Valida tamanho
    if len(cpf_limpo) != 11:
        return IdentificacaoResult.nao_identificado(
            f"CPF invalido: deve ter 11 digitos, voce informou {len(cpf_limpo)}.",
            pode_continuar=False
        )

    # Valida digitos iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return IdentificacaoResult.nao_identificado(
            "CPF invalido: todos os digitos sao iguais.",
            pode_continuar=False
        )

    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_cpf(db, cpf_limpo)

        if beneficiario:
            return IdentificacaoResult.identificado(
                metodo=MetodoIdentificacao.CPF,
                beneficiario_data=beneficiario.to_dict(),
                confianca="alta"
            )
        else:
            return IdentificacaoResult.nao_identificado(
                "CPF nao encontrado na base de beneficiarios. "
                "Isso pode significar que voce ainda nao esta cadastrado "
                "no CadUnico ou nao recebe beneficios federais."
            )
    finally:
        db.close()


def identificar_por_nis(nis: str) -> IdentificacaoResult:
    """Identifica cidadao por NIS (Numero de Identificacao Social).

    O NIS e atribuido quando a pessoa se cadastra no CadUnico.
    E uma alternativa ao CPF para pessoas que nao lembram o CPF.

    Args:
        nis: NIS com 11 digitos

    Returns:
        IdentificacaoResult com dados do beneficiario ou nao encontrado
    """
    # Limpa NIS
    nis_limpo = re.sub(r'\D', '', nis)

    # Valida tamanho
    if len(nis_limpo) != 11:
        return IdentificacaoResult.nao_identificado(
            f"NIS invalido: deve ter 11 digitos, voce informou {len(nis_limpo)}.",
            pode_continuar=False
        )

    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_nis(db, nis_limpo)

        if beneficiario:
            return IdentificacaoResult.identificado(
                metodo=MetodoIdentificacao.NIS,
                beneficiario_data=beneficiario.to_dict(),
                confianca="alta"
            )
        else:
            return IdentificacaoResult.nao_identificado(
                "NIS nao encontrado na base. "
                "O NIS esta no cartao do Bolsa Familia ou no comprovante do CadUnico."
            )
    finally:
        db.close()


def identificar_por_nome(
    nome: str,
    municipio: Optional[str] = None,
    uf: Optional[str] = None,
    ibge_code: Optional[str] = None
) -> IdentificacaoResult:
    """Identifica cidadao por nome e municipio (busca fuzzy).

    Metodo de menor confianca - retorna multiplos candidatos
    para confirmacao pelo usuario.

    Args:
        nome: Nome completo ou parcial
        municipio: Nome do municipio (para contexto)
        uf: UF do estado
        ibge_code: Codigo IBGE do municipio

    Returns:
        IdentificacaoResult com candidatos ou nao encontrado
    """
    if not nome or len(nome.strip()) < 3:
        return IdentificacaoResult.nao_identificado(
            "Por favor, informe seu nome completo para que eu possa buscar.",
            pode_continuar=False
        )

    db = SessionLocal()
    try:
        beneficiarios = Beneficiario.buscar_por_nome_municipio(
            db,
            nome=nome,
            ibge_code=ibge_code,
            uf=uf,
            limite=5
        )

        if not beneficiarios:
            return IdentificacaoResult.nao_identificado(
                f"Nao encontrei ninguem com o nome '{nome}' na base. "
                "Isso pode significar que voce ainda nao esta cadastrado."
            )

        if len(beneficiarios) == 1:
            # Unico resultado - mas pede confirmacao
            b = beneficiarios[0]
            return IdentificacaoResult.multiplos_resultados(
                candidatos=[{
                    "nome": b.nome,
                    "cpf_masked": b.cpf_masked,
                    "uf": b.uf,
                    "beneficios_resumo": b.gerar_resumo_texto()
                }],
                metodo=MetodoIdentificacao.NOME_MUNICIPIO
            )

        # Multiplos resultados - usuario precisa confirmar
        candidatos = []
        for b in beneficiarios:
            candidatos.append({
                "nome": b.nome,
                "cpf_masked": b.cpf_masked,
                "uf": b.uf,
                "beneficios_resumo": b.gerar_resumo_texto()
            })

        return IdentificacaoResult.multiplos_resultados(
            candidatos=candidatos,
            metodo=MetodoIdentificacao.NOME_MUNICIPIO
        )
    finally:
        db.close()


def identificar_cidadao(
    cpf: Optional[str] = None,
    nis: Optional[str] = None,
    nome: Optional[str] = None,
    municipio: Optional[str] = None,
    uf: Optional[str] = None,
    ibge_code: Optional[str] = None
) -> IdentificacaoResult:
    """Orquestrador de identificacao multimodal.

    Tenta identificar o cidadao usando os dados disponiveis,
    na seguinte ordem de prioridade:
    1. CPF (mais confiavel)
    2. NIS (confiavel)
    3. Nome + Municipio (menos confiavel, requer confirmacao)
    4. Sem identificacao (continua com coleta de dados)

    Esta funcao implementa o conceito de "identificacao progressiva"
    inspirado nas recomendacoes do ID4D do Banco Mundial.

    Args:
        cpf: CPF do cidadao (opcional)
        nis: NIS do cidadao (opcional)
        nome: Nome do cidadao (opcional)
        municipio: Nome do municipio (opcional)
        uf: UF do estado (opcional)
        ibge_code: Codigo IBGE (opcional)

    Returns:
        IdentificacaoResult com resultado da identificacao
    """
    # Tentativa 1: CPF
    if cpf:
        resultado = identificar_por_cpf(cpf)
        if resultado.data.get("identificado"):
            return resultado
        # Se CPF invalido, continua tentando outros metodos
        if not resultado.data.get("pode_continuar", True):
            return resultado

    # Tentativa 2: NIS
    if nis:
        resultado = identificar_por_nis(nis)
        if resultado.data.get("identificado"):
            return resultado

    # Tentativa 3: Nome + Municipio
    if nome:
        resultado = identificar_por_nome(
            nome=nome,
            municipio=municipio,
            uf=uf,
            ibge_code=ibge_code
        )
        if resultado.data.get("identificado") or resultado.data.get("multiplos"):
            return resultado

    # Tentativa 4: Sem identificacao - mas podemos continuar!
    return IdentificacaoResult.nao_identificado(
        "Nao consegui te identificar na base de beneficiarios, "
        "mas isso NAO significa que voce nao tem direito a beneficios! "
        "Vou te ajudar a verificar sua elegibilidade e orientar o cadastro.",
        pode_continuar=True
    )


def confirmar_identidade(
    candidato_index: int,
    candidatos: List[Dict[str, Any]]
) -> IdentificacaoResult:
    """Confirma identidade apos usuario escolher entre multiplos candidatos.

    Args:
        candidato_index: Indice do candidato escolhido (0-based)
        candidatos: Lista de candidatos retornada anteriormente

    Returns:
        IdentificacaoResult com dados do candidato confirmado
    """
    if candidato_index < 0 or candidato_index >= len(candidatos):
        return IdentificacaoResult.nao_identificado(
            f"Opcao invalida. Escolha um numero entre 1 e {len(candidatos)}.",
            pode_continuar=False
        )

    candidato = candidatos[candidato_index]
    return IdentificacaoResult.identificado(
        metodo=MetodoIdentificacao.NOME_MUNICIPIO,
        beneficiario_data=candidato,
        confianca="media"  # Confirmado pelo usuario, mas nao por documento
    )


# Aliases para uso no agente
consultar_por_nis = identificar_por_nis
buscar_por_nome = identificar_por_nome

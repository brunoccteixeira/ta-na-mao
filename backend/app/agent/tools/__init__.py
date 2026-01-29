"""Tools disponiveis para o agente Ta na Mao."""

from app.agent.tools.validar_cpf import validar_cpf
from app.agent.tools.buscar_cep import buscar_cep
from app.agent.tools.consultar_api import consultar_beneficios
from app.agent.tools.checklist import gerar_checklist, listar_beneficios
from app.agent.tools.buscar_cras import buscar_cras, buscar_cras_sync, buscar_cras_por_coordenadas
from app.agent.tools.buscar_farmacia import buscar_farmacia, buscar_farmacia_sync, buscar_farmacia_por_coordenadas

# Novas tools para inclusao de cidadaos sem documentacao
from app.agent.tools.identificar_cidadao import (
    identificar_cidadao,
    identificar_por_cpf,
    identificar_por_nis,
    identificar_por_nome,
    confirmar_identidade,
    consultar_por_nis,
    buscar_por_nome,
)
from app.agent.tools.verificar_elegibilidade_sem_docs import (
    verificar_elegibilidade_sem_docs,
    calcular_faixa_renda,
    coletar_dados_elegibilidade,
)
from app.agent.tools.gerar_carta_encaminhamento import (
    gerar_carta_encaminhamento,
    salvar_carta_arquivo,
)
from app.agent.tools.buscar_mutirao import (
    buscar_mutirao,
    formatar_mutirao_texto,
    carregar_mutiroes,
)

__all__ = [
    # Tools existentes
    "validar_cpf",
    "buscar_cep",
    "consultar_beneficios",
    "gerar_checklist",
    "listar_beneficios",
    "buscar_cras",
    "buscar_cras_sync",
    "buscar_cras_por_coordenadas",
    "buscar_farmacia",
    "buscar_farmacia_sync",
    "buscar_farmacia_por_coordenadas",

    # Novas tools - Identificacao Multimodal
    "identificar_cidadao",
    "identificar_por_cpf",
    "identificar_por_nis",
    "identificar_por_nome",
    "confirmar_identidade",
    "consultar_por_nis",
    "buscar_por_nome",

    # Novas tools - Elegibilidade sem documentos
    "verificar_elegibilidade_sem_docs",
    "calcular_faixa_renda",
    "coletar_dados_elegibilidade",

    # Novas tools - Carta de Encaminhamento
    "gerar_carta_encaminhamento",
    "salvar_carta_arquivo",

    # Novas tools - Mutiroes de Documentacao
    "buscar_mutirao",
    "formatar_mutirao_texto",
    "carregar_mutiroes",
]

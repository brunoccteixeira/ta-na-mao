"""Tool para gerar checklist de documentos por benefício."""

import json
import os
from typing import Optional

# Carrega base de conhecimento
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "data", "documentos_por_beneficio.json"
)

_DOCUMENTOS_CACHE = None


def _carregar_documentos() -> dict:
    """Carrega a base de documentos do JSON."""
    global _DOCUMENTOS_CACHE
    if _DOCUMENTOS_CACHE is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _DOCUMENTOS_CACHE = json.load(f)
    return _DOCUMENTOS_CACHE


def gerar_checklist(
    beneficio: str,
    situacao: Optional[dict] = None
) -> dict:
    """Gera checklist personalizado de documentos para um benefício.

    Esta tool cria uma lista de documentos necessários para solicitar
    um benefício social, personalizada conforme a situação do cidadão.

    Args:
        beneficio: Código do benefício. Valores aceitos:
            - "CADASTRO_UNICO" ou "CADUNICO"
            - "BOLSA_FAMILIA"
            - "BPC_LOAS" ou "BPC"
            - "TARIFA_SOCIAL_ENERGIA" ou "TSEE"
            - "FARMACIA_POPULAR"
            - "DIGNIDADE_MENSTRUAL"
        situacao: Dicionário com situação do cidadão para personalizar:
            - "tem_filhos": bool - Se tem filhos menores
            - "idoso": bool - Se tem 65 anos ou mais
            - "gestante": bool - Se está grávida
            - "deficiencia": bool - Se tem deficiência
            - "trabalha_formal": bool - Se tem carteira assinada
            - "autonomo": bool - Se trabalha por conta própria

    Returns:
        dict: {
            "beneficio": "Nome do benefício",
            "descricao": "Descrição breve",
            "requisito": "Requisito principal",
            "documentos_obrigatorios": [
                {"nome": "CPF", "dica": "...", "aceita_digital": True}
            ],
            "documentos_opcionais": [...],
            "documentos_condicionais": [...],
            "onde_fazer": "Local para solicitar",
            "valor_ou_desconto": "Valor do benefício",
            "checklist_texto": "Texto formatado para enviar"
        }

    Examples:
        >>> gerar_checklist("BOLSA_FAMILIA", {"tem_filhos": True})
        >>> gerar_checklist("BPC", {"idoso": True})
        >>> gerar_checklist("CADUNICO")
    """
    if situacao is None:
        situacao = {}

    # Normaliza código do benefício
    beneficio_upper = beneficio.upper().replace(" ", "_")
    mapeamento = {
        "CADUNICO": "CADASTRO_UNICO",
        "BPC": "BPC_LOAS",
        "TSEE": "TARIFA_SOCIAL_ENERGIA",
        "FARMACIA": "FARMACIA_POPULAR",
        "DIGNIDADE": "DIGNIDADE_MENSTRUAL",
    }
    beneficio_key = mapeamento.get(beneficio_upper, beneficio_upper)

    # Carrega dados
    dados = _carregar_documentos()
    if beneficio_key not in dados:
        return {
            "erro": True,
            "mensagem": f"Benefício '{beneficio}' não encontrado.",
            "beneficios_disponiveis": list(dados.keys())
        }

    info = dados[beneficio_key]

    # Coleta documentos
    obrigatorios = []
    opcionais = []
    condicionais = []

    for categoria, docs in info.get("documentos", {}).items():
        for doc in docs:
            doc_info = {
                "nome": doc["nome"],
                "dica": doc.get("dica", ""),
                "aceita_digital": doc.get("aceita_digital", False),
                "categoria": categoria
            }

            # Verifica condições
            condicao = doc.get("condicao")
            if condicao:
                # Verifica se a condição se aplica
                aplica = False
                if "filhos" in condicao.lower() and situacao.get("tem_filhos"):
                    aplica = True
                elif "grávida" in condicao.lower() and situacao.get("gestante"):
                    aplica = True
                elif "gestante" in condicao.lower() and situacao.get("gestante"):
                    aplica = True
                elif "carteira" in condicao.lower() and situacao.get("trabalha_formal"):
                    aplica = True
                elif "autônomo" in condicao.lower() and situacao.get("autonomo"):
                    aplica = True
                elif "renda formal" in condicao.lower() and situacao.get("trabalha_formal"):
                    aplica = True

                doc_info["condicao"] = condicao
                if aplica:
                    condicionais.append(doc_info)
                continue

            # Documentos específicos para idoso/PCD
            if categoria == "idoso" and not situacao.get("idoso"):
                continue
            if categoria == "pessoa_com_deficiencia" and not situacao.get("deficiencia"):
                continue

            if doc.get("obrigatorio", False):
                obrigatorios.append(doc_info)
            else:
                opcionais.append(doc_info)

    # Gera texto formatado para enviar
    texto_linhas = [
        f"📋 DOCUMENTOS PARA {info['nome'].upper()}",
        "",
        "✅ OBRIGATÓRIOS:"
    ]
    for i, doc in enumerate(obrigatorios, 1):
        emoji = "📱" if doc["aceita_digital"] else "📄"
        texto_linhas.append(f"   {i}. {emoji} {doc['nome']}")
        if doc["dica"]:
            texto_linhas.append(f"      💡 {doc['dica']}")

    if condicionais:
        texto_linhas.append("")
        texto_linhas.append("📌 SE APLICA A VOCÊ:")
        for doc in condicionais:
            texto_linhas.append(f"   • {doc['nome']}")
            if doc.get("condicao"):
                texto_linhas.append(f"     ({doc['condicao']})")

    if opcionais:
        texto_linhas.append("")
        texto_linhas.append("➕ OPCIONAIS (se tiver):")
        for doc in opcionais:
            texto_linhas.append(f"   • {doc['nome']}")

    texto_linhas.extend([
        "",
        f"📍 ONDE FAZER: {info.get('onde_fazer', 'Consulte o CRAS')}",
    ])

    if info.get("valor_medio"):
        texto_linhas.append(f"💰 VALOR: {info['valor_medio']}")
    elif info.get("valor"):
        texto_linhas.append(f"💰 VALOR: {info['valor']}")
    elif info.get("desconto"):
        texto_linhas.append(f"💰 DESCONTO: {info['desconto']}")

    return {
        "beneficio": info["nome"],
        "descricao": info.get("descricao", ""),
        "requisito": info.get("requisito_principal", ""),
        "documentos_obrigatorios": obrigatorios,
        "documentos_opcionais": opcionais,
        "documentos_condicionais": condicionais,
        "total_documentos": len(obrigatorios) + len(condicionais),
        "onde_fazer": info.get("onde_fazer", ""),
        "valor_ou_desconto": info.get("valor_medio") or info.get("valor") or info.get("desconto", ""),
        "checklist_texto": "\n".join(texto_linhas),
        "prazo_atualizacao": info.get("prazo_atualizacao", "")
    }


def listar_beneficios() -> dict:
    """Lista todos os benefícios disponíveis com resumo.

    Returns:
        dict: Lista de benefícios com nome e descrição
    """
    dados = _carregar_documentos()
    beneficios = []
    for codigo, info in dados.items():
        beneficios.append({
            "codigo": codigo,
            "nome": info["nome"],
            "descricao": info.get("descricao", ""),
            "requisito": info.get("requisito_principal", ""),
            "onde_fazer": info.get("onde_fazer", "")
        })
    return {"beneficios": beneficios, "total": len(beneficios)}

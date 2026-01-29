"""Tool para processar receita medica e extrair medicamentos.

Usa MCP PDF/OCR como fonte primaria, com fallback para Gemini Vision.
Aceita texto digitado como alternativa.
Valida medicamentos contra lista do Farmacia Popular.
"""

import json
import os
import base64
import re
import logging
from typing import Optional, List, Dict

import google.generativeai as genai

from app.agent.mcp import mcp_manager, PDFOcrMCP
from app.agent.data.medicamentos_farmacia_popular import (
    buscar_medicamento
)

logger = logging.getLogger(__name__)


def _validar_medicamento(nome: str) -> Dict:
    """Verifica se medicamento esta na lista do Farmacia Popular.

    Usa a nova base de dados com busca fuzzy.

    Returns:
        {
            "encontrado": bool,
            "nome_oficial": str,
            "categoria": str,
            "gratuito": bool,
            "dosagens": list
        }
    """
    resultado = buscar_medicamento(nome)

    if resultado["encontrado"]:
        return {
            "encontrado": True,
            "nome_oficial": resultado["nome"],
            "categoria": resultado["categoria"],
            "gratuito": resultado["gratuito"],
            "desconto": None,  # Desde 2025, todos são 100% gratuitos
            "dosagens": resultado["dosagens"] or []
        }

    return {"encontrado": False}


def _extrair_dosagem(texto: str) -> Optional[str]:
    """Extrai dosagem de uma string (ex: '50mg', '100UI/ml')."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|mcg|ml|ui|g|%|UI/ml)', texto, re.IGNORECASE)
    if match:
        return f"{match.group(1)}{match.group(2).lower()}"
    return None


def _extrair_quantidade(texto: str) -> Optional[int]:
    """Extrai quantidade (ex: '30 comprimidos', '60 capsulas')."""
    match = re.search(r'(\d+)\s*(comp|caps|unid|cp|cps|dias)', texto, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


async def _processar_imagem_mcp(imagem_base64: str) -> List[Dict] | None:
    """Tenta processar receita via MCP PDF/OCR.

    Args:
        imagem_base64: Imagem da receita em base64

    Returns:
        Lista de medicamentos ou None se MCP falhar
    """
    try:
        wrapper = mcp_manager.get_wrapper("pdf-ocr")
        if not wrapper or not isinstance(wrapper, PDFOcrMCP):
            logger.debug("pdf-ocr MCP not available")
            return None

        resultado = await wrapper.processar_receita_base64(imagem_base64)
        if not resultado:
            return None

        # Converte ReceitaExtraida para lista de medicamentos
        medicamentos = []
        for med in resultado.medicamentos:
            medicamentos.append({
                "nome": med.nome,
                "dosagem": med.dosagem,
                "quantidade": med.quantidade,
                "confianca_ocr": med.confianca,
                "fonte": "pdf-ocr-mcp"
            })

        if medicamentos:
            logger.info(f"MCP OCR found {len(medicamentos)} medications")

        return medicamentos if medicamentos else None

    except Exception as e:
        logger.warning(f"MCP processar_receita failed: {e}")
        return None


def _processar_imagem_gemini(imagem_base64: Optional[str], imagem_url: Optional[str]) -> List[Dict]:
    """Fallback para Gemini Vision quando MCP não disponível."""

    # Configurar Gemini
    try:
        from app.config import settings
        api_key = settings.GOOGLE_API_KEY
    except ImportError:
        api_key = os.getenv("GOOGLE_API_KEY", "")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY nao configurada")

    genai.configure(api_key=api_key)

    # Preparar imagem
    if imagem_base64:
        # Decodificar base64
        image_data = base64.b64decode(imagem_base64)
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        ]
    elif imagem_url:
        # Para URL, o Gemini pode acessar diretamente em alguns casos
        # Mas para maior compatibilidade, seria melhor baixar a imagem
        image_parts = [{"url": imagem_url}]
    else:
        return []

    # Prompt para extrair medicamentos
    prompt = """Analise esta receita medica e extraia TODOS os medicamentos prescritos.

Para cada medicamento, identifique:
1. Nome do medicamento (generico ou comercial)
2. Dosagem (ex: 50mg, 100mg, 850mg)
3. Quantidade (se indicada)
4. Frequencia (se indicada)

Responda APENAS em formato JSON assim:
{
    "medicamentos": [
        {"nome": "Losartana", "dosagem": "50mg", "quantidade": 30},
        {"nome": "Metformina", "dosagem": "850mg", "quantidade": 60}
    ]
}

Se nao conseguir ler a receita, responda:
{"medicamentos": [], "erro": "motivo"}
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content([prompt, image_parts[0]])

        # Extrair JSON da resposta
        texto = response.text
        # Encontrar o JSON na resposta
        match = re.search(r'\{[\s\S]*\}', texto)
        if match:
            dados = json.loads(match.group())
            medicamentos = dados.get("medicamentos", [])
            # Adiciona fonte
            for med in medicamentos:
                med["fonte"] = "gemini-vision"
            return medicamentos

    except Exception as e:
        logger.error(f"Erro ao processar imagem com Gemini: {e}")

    return []


def _processar_texto(texto: str) -> List[Dict]:
    """Parseia texto digitado para extrair medicamentos."""
    medicamentos = []

    # Normalizar texto
    texto = texto.strip()

    # Separadores possiveis: virgula, quebra de linha, ponto e virgula, numeros
    # Exemplo: "1. Losartana 50mg 2. Metformina 850mg"
    # Exemplo: "Losartana 50mg, Metformina 850mg"

    # Remover numeracao
    texto = re.sub(r'^\d+[\.\)\-]\s*', '', texto, flags=re.MULTILINE)

    # Dividir por separadores
    partes = re.split(r'[,;\n]+', texto)

    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue

        # Tentar extrair nome, dosagem e quantidade
        med = {"nome": "", "dosagem": None, "quantidade": None, "fonte": "texto"}

        # Extrair dosagem
        med["dosagem"] = _extrair_dosagem(parte)

        # Extrair quantidade
        med["quantidade"] = _extrair_quantidade(parte)

        # O resto eh o nome
        nome = re.sub(r'\d+\s*(mg|mcg|ml|ui|g|%|comp|caps|unid|dias|cp|cps|UI/ml)[\s\d]*', '', parte, flags=re.IGNORECASE)
        nome = nome.strip(' -,.')
        if nome:
            med["nome"] = nome
            medicamentos.append(med)

    return medicamentos


def processar_receita(
    imagem_base64: Optional[str] = None,
    imagem_url: Optional[str] = None,
    texto: Optional[str] = None
) -> dict:
    """Extrai medicamentos da receita medica.

    Esta tool processa receita medica de duas formas:
    1. Foto da receita: usa MCP PDF/OCR ou Gemini Vision para extrair medicamentos
    2. Texto digitado: parseia nomes de medicamentos

    Apos extrair, valida contra lista do Farmacia Popular.

    Args:
        imagem_base64: Imagem da receita em base64
        imagem_url: URL da imagem da receita
        texto: Texto digitado com nomes dos medicamentos
            Formatos aceitos:
            - "Losartana 50mg, Metformina 850mg"
            - "Losartana 50mg\\nMetformina 850mg"
            - "1. Losartana 50mg 2. Metformina 850mg"

    Returns:
        dict: {
            "sucesso": True/False,
            "medicamentos": [
                {
                    "nome": "Losartana",
                    "dosagem": "50mg",
                    "quantidade": 30,
                    "disponivel_farmacia_popular": True,
                    "gratuito": True,
                    "categoria": "Hipertensao"
                }
            ],
            "todos_disponiveis": True/False,
            "alertas": ["Medicamento X nao esta no Farmacia Popular"],
            "texto_resumo": "Voce precisa de 2 medicamentos..."
        }
    """
    import asyncio

    medicamentos = []
    alertas = []

    try:
        # Processar imagem com MCP ou Gemini Vision
        if imagem_base64 or imagem_url:
            # Tenta MCP primeiro (async)
            if imagem_base64:
                try:
                    asyncio.get_running_loop()
                    # Estamos em contexto async
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            _processar_imagem_mcp(imagem_base64)
                        )
                        medicamentos = future.result()
                except RuntimeError:
                    # Não há loop rodando
                    medicamentos = asyncio.run(_processar_imagem_mcp(imagem_base64))

            # Fallback para Gemini
            if not medicamentos:
                logger.debug("Falling back to Gemini Vision")
                medicamentos = _processar_imagem_gemini(imagem_base64, imagem_url)

        # Processar texto digitado
        elif texto:
            medicamentos = _processar_texto(texto)

        else:
            return {
                "sucesso": False,
                "erro": "Envie uma foto da receita ou digite o nome dos medicamentos.",
                "medicamentos": []
            }

        if not medicamentos:
            return {
                "sucesso": False,
                "erro": "Nao consegui identificar medicamentos. Tente digitar o nome.",
                "medicamentos": []
            }

        # Validar cada medicamento contra Farmacia Popular
        for med in medicamentos:
            validacao = _validar_medicamento(med["nome"])
            med["disponivel_farmacia_popular"] = validacao["encontrado"]

            if validacao["encontrado"]:
                med["nome_oficial"] = validacao["nome_oficial"]
                med["categoria"] = validacao["categoria"]
                med["gratuito"] = validacao["gratuito"]
                med["desconto"] = validacao.get("desconto")
                if not med.get("dosagem") and validacao.get("dosagens"):
                    med["dosagens_disponiveis"] = validacao["dosagens"]
            else:
                alertas.append(f"'{med['nome']}' nao esta na lista do Farmacia Popular")

        # Verificar se todos estao disponiveis
        todos_disponiveis = all(m.get("disponivel_farmacia_popular") for m in medicamentos)

        # Gerar resumo
        qtd = len(medicamentos)
        gratuitos = sum(1 for m in medicamentos if m.get("gratuito"))
        texto_resumo = f"Identifiquei {qtd} medicamento(s)"
        if gratuitos == qtd:
            texto_resumo += " - todos gratuitos pelo Farmacia Popular!"
        elif gratuitos > 0:
            texto_resumo += f" - {gratuitos} gratuito(s)"

        # Identificar fonte usada
        fontes = set(m.get("fonte", "unknown") for m in medicamentos)
        fonte_principal = fontes.pop() if len(fontes) == 1 else "mixed"

        return {
            "sucesso": True,
            "medicamentos": medicamentos,
            "total": len(medicamentos),
            "todos_disponiveis": todos_disponiveis,
            "alertas": alertas,
            "texto_resumo": texto_resumo,
            "fonte": fonte_principal
        }

    except Exception as e:
        logger.error(f"Erro ao processar receita: {e}")
        return {
            "sucesso": False,
            "erro": f"Erro ao processar: {str(e)}",
            "medicamentos": []
        }


async def processar_receita_async(
    imagem_base64: Optional[str] = None,
    imagem_url: Optional[str] = None,
    texto: Optional[str] = None
) -> dict:
    """Versão assíncrona de processar_receita.

    Usa MCP PDF/OCR como fonte primária, com fallback para Gemini Vision.
    """
    medicamentos = []
    alertas = []

    try:
        # Processar imagem
        if imagem_base64 or imagem_url:
            # Tenta MCP primeiro
            if imagem_base64:
                medicamentos = await _processar_imagem_mcp(imagem_base64)

            # Fallback para Gemini
            if not medicamentos:
                logger.debug("Falling back to Gemini Vision")
                medicamentos = _processar_imagem_gemini(imagem_base64, imagem_url)

        # Processar texto digitado
        elif texto:
            medicamentos = _processar_texto(texto)

        else:
            return {
                "sucesso": False,
                "erro": "Envie uma foto da receita ou digite o nome dos medicamentos.",
                "medicamentos": []
            }

        if not medicamentos:
            return {
                "sucesso": False,
                "erro": "Nao consegui identificar medicamentos. Tente digitar o nome.",
                "medicamentos": []
            }

        # Validar cada medicamento contra Farmacia Popular
        for med in medicamentos:
            validacao = _validar_medicamento(med["nome"])
            med["disponivel_farmacia_popular"] = validacao["encontrado"]

            if validacao["encontrado"]:
                med["nome_oficial"] = validacao["nome_oficial"]
                med["categoria"] = validacao["categoria"]
                med["gratuito"] = validacao["gratuito"]
                med["desconto"] = validacao.get("desconto")
                if not med.get("dosagem") and validacao.get("dosagens"):
                    med["dosagens_disponiveis"] = validacao["dosagens"]
            else:
                alertas.append(f"'{med['nome']}' nao esta na lista do Farmacia Popular")

        # Verificar se todos estao disponiveis
        todos_disponiveis = all(m.get("disponivel_farmacia_popular") for m in medicamentos)

        # Gerar resumo
        qtd = len(medicamentos)
        gratuitos = sum(1 for m in medicamentos if m.get("gratuito"))
        texto_resumo = f"Identifiquei {qtd} medicamento(s)"
        if gratuitos == qtd:
            texto_resumo += " - todos gratuitos pelo Farmacia Popular!"
        elif gratuitos > 0:
            texto_resumo += f" - {gratuitos} gratuito(s)"

        # Identificar fonte usada
        fontes = set(m.get("fonte", "unknown") for m in medicamentos)
        fonte_principal = fontes.pop() if len(fontes) == 1 else "mixed"

        return {
            "sucesso": True,
            "medicamentos": medicamentos,
            "total": len(medicamentos),
            "todos_disponiveis": todos_disponiveis,
            "alertas": alertas,
            "texto_resumo": texto_resumo,
            "fonte": fonte_principal
        }

    except Exception as e:
        logger.error(f"Erro ao processar receita: {e}")
        return {
            "sucesso": False,
            "erro": f"Erro ao processar: {str(e)}",
            "medicamentos": []
        }


def processar_receita_sync(
    imagem_base64: Optional[str] = None,
    imagem_url: Optional[str] = None,
    texto: Optional[str] = None
) -> dict:
    """Versao sincrona para uso com o agente."""
    return processar_receita(
        imagem_base64=imagem_base64,
        imagem_url=imagem_url,
        texto=texto
    )

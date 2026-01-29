"""Root Agent para o assistente Tá na Mão.

Este módulo implementa o agente principal usando Google Generative AI (Gemini).
Pode ser executado via CLI do ADK ou integrado ao FastAPI.
"""

import os
import uuid
import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from app.agent.prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, ERROR_MESSAGE
from app.agent.tools.validar_cpf import validar_cpf
from app.agent.tools.buscar_cep import buscar_cep_sync
from app.agent.tools.consultar_api import consultar_beneficios
from app.agent.tools.checklist import gerar_checklist, listar_beneficios
from app.agent.tools.buscar_cras import buscar_cras_sync
from app.agent.tools.buscar_farmacia import buscar_farmacia_sync
from app.agent.tools.processar_receita import processar_receita_sync
from app.agent.tools.preparar_pedido import preparar_pedido, consultar_pedido, listar_pedidos_cidadao
from app.agent.tools.consultar_beneficio import consultar_beneficio, verificar_elegibilidade
from app.agent.tools.beneficios_setoriais import (
    consultar_beneficios_agricultores,
    consultar_beneficios_entregadores,
    consultar_beneficios_servidor
)
from app.agent.tools.dinheiro_esquecido import (
    consultar_dinheiro_esquecido,
    guia_pis_pasep,
    guia_svr,
    guia_fgts,
    verificar_dinheiro_por_perfil
)
from app.agent.tools.meus_dados import (
    meus_dados,
    gerar_alertas_beneficios
)
from app.agent.tools.pre_atendimento_cras import (
    preparar_pre_atendimento_cras,
    gerar_formulario_pre_cras
)

logger = logging.getLogger(__name__)

# Configurar API key (preferência: config > env var)
try:
    from app.config import settings
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")
    AGENT_MODEL = settings.AGENT_MODEL
except ImportError:
    # Fallback para execução standalone
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.0-flash-exp")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Definição das funções como Tools para o Gemini
TOOL_DECLARATIONS = [
    FunctionDeclaration(
        name="validar_cpf",
        description="Valida um CPF brasileiro usando os dígitos verificadores. Use sempre que o cidadão informar um CPF.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF com 11 dígitos numéricos (pode conter pontos e traços)"
                }
            },
            "required": ["cpf"]
        }
    ),
    FunctionDeclaration(
        name="buscar_cep",
        description="Busca endereço completo pelo CEP usando a API ViaCEP. Use quando precisar confirmar ou coletar endereço.",
        parameters={
            "type": "object",
            "properties": {
                "cep": {
                    "type": "string",
                    "description": "CEP com 8 dígitos (pode conter traço)"
                }
            },
            "required": ["cep"]
        }
    ),
    FunctionDeclaration(
        name="consultar_beneficios",
        description="Consulta benefícios sociais disponíveis. Pode listar todos os programas ou buscar por município específico.",
        parameters={
            "type": "object",
            "properties": {
                "ibge_code": {
                    "type": "string",
                    "description": "Código IBGE do município (7 dígitos). Obtido via buscar_cep."
                },
                "listar_todos": {
                    "type": "boolean",
                    "description": "Se True, lista todos os programas disponíveis no sistema."
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="gerar_checklist",
        description="Gera checklist de documentos necessários para solicitar um benefício. USE SEMPRE que o cidadão quiser saber quais documentos precisa. Retorna lista formatada pronta para enviar.",
        parameters={
            "type": "object",
            "properties": {
                "beneficio": {
                    "type": "string",
                    "description": "Código do benefício: CADASTRO_UNICO, BOLSA_FAMILIA, BPC_LOAS, TARIFA_SOCIAL_ENERGIA, FARMACIA_POPULAR, DIGNIDADE_MENSTRUAL"
                },
                "situacao": {
                    "type": "object",
                    "description": "Situação do cidadão para personalizar a lista",
                    "properties": {
                        "tem_filhos": {"type": "boolean", "description": "Se tem filhos menores de 18 anos"},
                        "idoso": {"type": "boolean", "description": "Se tem 65 anos ou mais"},
                        "gestante": {"type": "boolean", "description": "Se está grávida"},
                        "deficiencia": {"type": "boolean", "description": "Se tem deficiência"},
                        "trabalha_formal": {"type": "boolean", "description": "Se trabalha com carteira assinada"},
                        "autonomo": {"type": "boolean", "description": "Se trabalha por conta própria"}
                    }
                }
            },
            "required": ["beneficio"]
        }
    ),
    FunctionDeclaration(
        name="listar_beneficios",
        description="Lista todos os beneficios sociais disponiveis no sistema com descricao e requisitos.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    FunctionDeclaration(
        name="buscar_cras",
        description="Busca CRAS (Centro de Referencia de Assistencia Social) mais proximos do cidadao. USE para beneficios que exigem atendimento presencial no CRAS: CadUnico, Bolsa Familia, BPC/LOAS, Tarifa Social.",
        parameters={
            "type": "object",
            "properties": {
                "cep": {
                    "type": "string",
                    "description": "CEP do cidadao (8 digitos). Obtemos o municipio automaticamente."
                },
                "ibge_code": {
                    "type": "string",
                    "description": "Codigo IBGE do municipio (7 digitos). Alternativa ao CEP."
                },
                "limite": {
                    "type": "integer",
                    "description": "Numero maximo de CRAS a retornar (padrao: 3)"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="buscar_farmacia",
        description="Busca farmacias credenciadas no Farmacia Popular. USE para Farmacia Popular e Dignidade Menstrual. NAO precisa ir ao CRAS - o cidadao vai direto na farmacia com CPF e receita.",
        parameters={
            "type": "object",
            "properties": {
                "cep": {
                    "type": "string",
                    "description": "CEP do cidadao (8 digitos). Obtemos o municipio automaticamente."
                },
                "ibge_code": {
                    "type": "string",
                    "description": "Codigo IBGE do municipio (7 digitos). Alternativa ao CEP."
                },
                "programa": {
                    "type": "string",
                    "description": "Filtrar por programa: FARMACIA_POPULAR ou DIGNIDADE_MENSTRUAL"
                },
                "limite": {
                    "type": "integer",
                    "description": "Numero maximo de farmacias a retornar (padrao: 5)"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="processar_receita",
        description="Extrai medicamentos de uma receita medica. Aceita foto (base64 ou URL) ou texto digitado. Use quando cidadao quiser pedir medicamentos no Farmacia Popular.",
        parameters={
            "type": "object",
            "properties": {
                "imagem_base64": {
                    "type": "string",
                    "description": "Foto da receita em base64"
                },
                "imagem_url": {
                    "type": "string",
                    "description": "URL da foto da receita"
                },
                "texto": {
                    "type": "string",
                    "description": "Texto digitado com nomes dos medicamentos. Ex: 'Losartana 50mg, Metformina 850mg'"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="preparar_pedido",
        description="Cria pedido de medicamentos e envia para farmacia via WhatsApp. A farmacia prepara os remedios e o cidadao retira quando estiver pronto (estilo iFood). USE apos processar_receita e cidadao escolher farmacia.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao (11 digitos, sem formatacao)"
                },
                "nome": {
                    "type": "string",
                    "description": "Nome completo do cidadao"
                },
                "telefone": {
                    "type": "string",
                    "description": "WhatsApp do cidadao para notificacoes"
                },
                "medicamentos": {
                    "type": "array",
                    "description": "Lista de medicamentos",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nome": {"type": "string"},
                            "dosagem": {"type": "string"},
                            "quantidade": {"type": "integer"}
                        }
                    }
                },
                "farmacia_id": {
                    "type": "string",
                    "description": "ID da farmacia escolhida (obtido de buscar_farmacia)"
                },
                "ibge_code": {
                    "type": "string",
                    "description": "Codigo IBGE do municipio"
                },
                "receita_url": {
                    "type": "string",
                    "description": "URL da foto da receita (opcional)"
                }
            },
            "required": ["cpf", "nome", "telefone", "medicamentos", "farmacia_id", "ibge_code"]
        }
    ),
    FunctionDeclaration(
        name="consultar_pedido",
        description="Consulta status de um pedido de medicamentos. Use quando cidadao perguntar sobre um pedido ja feito.",
        parameters={
            "type": "object",
            "properties": {
                "pedido_numero": {
                    "type": "string",
                    "description": "Numero do pedido (ex: PED-12345)"
                },
                "pedido_id": {
                    "type": "string",
                    "description": "UUID do pedido (alternativa ao numero)"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="listar_pedidos_cidadao",
        description="Lista todos os pedidos de um cidadao. Use quando cidadao quiser ver seus pedidos.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao"
                },
                "apenas_ativos": {
                    "type": "boolean",
                    "description": "Se True, mostra apenas pedidos pendentes/confirmados/prontos (padrao: True)"
                }
            },
            "required": ["cpf"]
        }
    ),
    FunctionDeclaration(
        name="consultar_beneficio",
        description="Consulta beneficios que o cidadao JA RECEBE por CPF. Busca no banco de dados indexado do Portal da Transparencia. USE quando cidadao perguntar 'meu bolsa familia ta vindo?', 'quanto eu recebo?', 'to cadastrado?'. Retorna Bolsa Familia, BPC e CadUnico.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao (11 digitos, com ou sem formatacao)"
                }
            },
            "required": ["cpf"]
        }
    ),
    FunctionDeclaration(
        name="verificar_elegibilidade",
        description="Verifica se cidadao e elegivel para um programa especifico. USE quando cidadao perguntar 'tenho direito a...?', 'posso pedir...?'. Consulta dados do cidadao e retorna se ja recebe ou pode ser elegivel.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao"
                },
                "programa": {
                    "type": "string",
                    "description": "Codigo do programa: BOLSA_FAMILIA, BPC, FARMACIA_POPULAR, DIGNIDADE_MENSTRUAL, TSEE, CADUNICO"
                }
            },
            "required": ["cpf", "programa"]
        }
    ),
    # Tools de orientação setorial
    FunctionDeclaration(
        name="consultar_beneficios_agricultores",
        description="Orienta sobre beneficios para AGRICULTORES FAMILIARES. USE quando cidadao mencionar: agricultura, plantacao, roça, lavoura, pecuaria, pesca, DAP, CAF, PRONAF, Garantia-Safra. Retorna informacoes sobre credito rural, seguro safra, venda para governo (PAA/PNAE).",
        parameters={
            "type": "object",
            "properties": {
                "regiao": {
                    "type": "string",
                    "description": "Regiao do agricultor: SEMIARIDO, NORDESTE, NORTE, SUDESTE, SUL, CENTRO_OESTE"
                },
                "atividade": {
                    "type": "string",
                    "description": "Tipo de atividade: CULTIVO, PESCA, PECUARIA, EXTRATIVISMO"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="consultar_beneficios_entregadores",
        description="Orienta sobre beneficios para ENTREGADORES DE APP e TRABALHADORES INFORMAIS. USE quando cidadao mencionar: entregador, iFood, Rappi, Uber, 99, motorista de app, autonomo, informal, MEI, INSS, aposentadoria. Explica como se formalizar e contribuir para INSS.",
        parameters={
            "type": "object",
            "properties": {
                "tipo_trabalho": {
                    "type": "string",
                    "description": "Tipo de trabalho: ENTREGADOR, MOTORISTA, AUTONOMO, MEI"
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="consultar_beneficios_servidor",
        description="Orienta sobre beneficios para FUNCIONARIOS PUBLICOS. USE quando cidadao mencionar: servidor publico, funcionario publico, prefeitura, estado, federal, vale-alimentacao, auxilio-saude, auxilio-creche. Informa sobre beneficios de servidores.",
        parameters={
            "type": "object",
            "properties": {
                "esfera": {
                    "type": "string",
                    "description": "Esfera do servidor: FEDERAL, ESTADUAL, MUNICIPAL"
                },
                "cargo": {
                    "type": "string",
                    "description": "Tipo de cargo: EFETIVO, COMISSIONADO, TEMPORARIO"
                }
            },
            "required": []
        }
    ),
    # Tools de Dinheiro Esquecido (Pilar 1)
    FunctionDeclaration(
        name="consultar_dinheiro_esquecido",
        description="Mostra informacoes sobre DINHEIRO ESQUECIDO que o cidadao pode ter direito. USE quando cidadao mencionar: dinheiro esquecido, PIS, PASEP, valores a receber, FGTS, conta antiga, dinheiro parado, grana esquecida. Total disponivel: R$ 42 bilhoes!",
        parameters={
            "type": "object",
            "properties": {
                "tipo": {
                    "type": "string",
                    "description": "Tipo especifico: pis_pasep, svr, fgts. Se nao informado, mostra todos."
                }
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="guia_pis_pasep",
        description="Guia COMPLETO passo-a-passo para consultar e sacar PIS/PASEP esquecido. R$ 26 BILHOES disponiveis para 10,5 milhoes de pessoas. USE quando cidadao quiser saber como consultar ou sacar PIS/PASEP.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    FunctionDeclaration(
        name="guia_svr",
        description="Guia COMPLETO passo-a-passo para consultar Valores a Receber (SVR) no Banco Central. R$ 8-10 BILHOES disponiveis para 48 milhoes de pessoas. USE quando cidadao quiser consultar valores a receber, dinheiro em banco, conta antiga.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    FunctionDeclaration(
        name="guia_fgts",
        description="Guia COMPLETO passo-a-passo para consultar e sacar FGTS. R$ 7,8 BILHOES retidos de 14 milhoes de trabalhadores. URGENTE: Prazo 30/12/2025 para Saque-Aniversario! USE quando cidadao mencionar FGTS, saque-aniversario, fundo de garantia.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    FunctionDeclaration(
        name="verificar_dinheiro_por_perfil",
        description="Verifica quais tipos de DINHEIRO ESQUECIDO o cidadao pode ter direito baseado no perfil. USE para fazer triagem inicial e recomendar o que consultar.",
        parameters={
            "type": "object",
            "properties": {
                "trabalhou_antes_1988": {
                    "type": "boolean",
                    "description": "Se trabalhou com carteira assinada entre 1971 e 1988"
                },
                "teve_carteira_assinada": {
                    "type": "boolean",
                    "description": "Se ja trabalhou com carteira assinada em qualquer epoca"
                },
                "teve_conta_banco": {
                    "type": "boolean",
                    "description": "Se ja teve conta em banco"
                },
                "idade": {
                    "type": "integer",
                    "description": "Idade do cidadao"
                }
            },
            "required": []
        }
    ),
    # Tools de Meus Dados (Pilar 2)
    FunctionDeclaration(
        name="meus_dados",
        description="Mostra TODOS OS DADOS do cidadao em um so lugar: beneficios ativos, valores, alertas e sugestoes. USE quando cidadao perguntar 'quais meus dados?', 'o que eu recebo?', 'quanto eu recebo?', 'meus beneficios'. Retorna visao consolidada completa.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao (11 digitos, com ou sem formatacao)"
                }
            },
            "required": ["cpf"]
        }
    ),
    FunctionDeclaration(
        name="gerar_alertas_beneficios",
        description="Gera ALERTAS proativos sobre beneficios do cidadao: CadUnico desatualizado, beneficios proximos de expirar, oportunidades. USE para verificar se tem algo que o cidadao precisa fazer.",
        parameters={
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao (11 digitos)"
                }
            },
            "required": ["cpf"]
        }
    ),
    # Tools de Pre-Atendimento CRAS (Pilar 3)
    FunctionDeclaration(
        name="preparar_pre_atendimento_cras",
        description="Prepara TUDO para ida ao CRAS: gera checklist de documentos personalizada, tempo estimado, dicas. USE quando cidadao quiser ir ao CRAS, fazer CadUnico, Bolsa Familia, BPC. Reduz tempo de atendimento de 2h para 30min!",
        parameters={
            "type": "object",
            "properties": {
                "programa": {
                    "type": "string",
                    "description": "Programa desejado: CADUNICO, BOLSA_FAMILIA, BPC, TSEE"
                },
                "nome": {
                    "type": "string",
                    "description": "Nome do cidadao"
                },
                "cpf": {
                    "type": "string",
                    "description": "CPF do cidadao"
                },
                "composicao_familiar": {
                    "type": "integer",
                    "description": "Numero de pessoas na familia"
                },
                "tem_filhos": {
                    "type": "boolean",
                    "description": "Se tem filhos menores de 18 anos"
                },
                "tem_filhos_pequenos": {
                    "type": "boolean",
                    "description": "Se tem filhos ate 7 anos"
                },
                "idoso": {
                    "type": "boolean",
                    "description": "Se tem 65 anos ou mais"
                },
                "gestante": {
                    "type": "boolean",
                    "description": "Se esta gravida"
                },
                "deficiencia": {
                    "type": "boolean",
                    "description": "Se tem deficiencia"
                },
                "trabalha_formal": {
                    "type": "boolean",
                    "description": "Se trabalha com carteira assinada"
                },
                "autonomo": {
                    "type": "boolean",
                    "description": "Se trabalha por conta propria"
                },
                "desempregado": {
                    "type": "boolean",
                    "description": "Se esta desempregado"
                }
            },
            "required": ["programa"]
        }
    ),
    FunctionDeclaration(
        name="gerar_formulario_pre_cras",
        description="Gera formulario PRE-PREENCHIDO para levar ao CRAS. Cidadao chega com tudo pronto, so assina. USE apos coletar dados do cidadao.",
        parameters={
            "type": "object",
            "properties": {
                "nome": {
                    "type": "string",
                    "description": "Nome completo do responsavel familiar"
                },
                "cpf": {
                    "type": "string",
                    "description": "CPF do responsavel"
                },
                "data_nascimento": {
                    "type": "string",
                    "description": "Data de nascimento (DD/MM/AAAA)"
                },
                "telefone": {
                    "type": "string",
                    "description": "Telefone para contato"
                },
                "endereco": {
                    "type": "string",
                    "description": "Endereco completo"
                },
                "composicao_familiar": {
                    "type": "array",
                    "description": "Lista de membros da familia",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nome": {"type": "string"},
                            "parentesco": {"type": "string"},
                            "data_nascimento": {"type": "string"}
                        }
                    }
                },
                "renda_familiar": {
                    "type": "number",
                    "description": "Renda total da familia em reais"
                },
                "situacao_moradia": {
                    "type": "string",
                    "description": "PROPRIA, ALUGADA, CEDIDA, OCUPACAO"
                },
                "programa": {
                    "type": "string",
                    "description": "Programa desejado: CADUNICO, BOLSA_FAMILIA, BPC"
                }
            },
            "required": ["nome", "cpf", "data_nascimento", "telefone", "endereco", "composicao_familiar", "renda_familiar"]
        }
    ),
]

# Mapeamento de funcoes para execucao
TOOL_FUNCTIONS = {
    "validar_cpf": validar_cpf,
    "buscar_cep": buscar_cep_sync,
    "consultar_beneficios": consultar_beneficios,
    "gerar_checklist": gerar_checklist,
    "listar_beneficios": listar_beneficios,
    "buscar_cras": buscar_cras_sync,
    "buscar_farmacia": buscar_farmacia_sync,
    "processar_receita": processar_receita_sync,
    "preparar_pedido": preparar_pedido,
    "consultar_pedido": consultar_pedido,
    "listar_pedidos_cidadao": listar_pedidos_cidadao,
    "consultar_beneficio": consultar_beneficio,
    "verificar_elegibilidade": verificar_elegibilidade,
    # Tools de orientação setorial
    "consultar_beneficios_agricultores": consultar_beneficios_agricultores,
    "consultar_beneficios_entregadores": consultar_beneficios_entregadores,
    "consultar_beneficios_servidor": consultar_beneficios_servidor,
    # Tools de Dinheiro Esquecido (Pilar 1)
    "consultar_dinheiro_esquecido": consultar_dinheiro_esquecido,
    "guia_pis_pasep": guia_pis_pasep,
    "guia_svr": guia_svr,
    "guia_fgts": guia_fgts,
    "verificar_dinheiro_por_perfil": verificar_dinheiro_por_perfil,
    # Tools de Meus Dados (Pilar 2)
    "meus_dados": meus_dados,
    "gerar_alertas_beneficios": gerar_alertas_beneficios,
    # Tools de Pre-Atendimento CRAS (Pilar 3)
    "preparar_pre_atendimento_cras": preparar_pre_atendimento_cras,
    "gerar_formulario_pre_cras": gerar_formulario_pre_cras,
}


class TaNaMaoAgent:
    """Agente conversacional Tá na Mão usando Gemini Flash."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        model_name: str = None,
        api_base_url: str = "http://localhost:8000"
    ):
        """Inicializa o agente.

        Args:
            session_id: ID da sessão. Se não fornecido, gera um novo.
            model_name: Nome do modelo Gemini a usar.
            api_base_url: URL base da API Tá na Mão para consultas.
        """
        # Usa modelo da config se não especificado
        if model_name is None:
            model_name = AGENT_MODEL
        self.session_id = session_id or str(uuid.uuid4())
        self.model_name = model_name
        self.api_base_url = api_base_url
        self.history = []
        self.tools_used = []

        # Configura o modelo com as tools
        self.tools = Tool(function_declarations=TOOL_DECLARATIONS)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=[self.tools],
            system_instruction=SYSTEM_PROMPT,
        )

        # Inicia chat com histórico
        self.chat = self.model.start_chat(history=self.history)

    def _execute_function(self, function_call) -> dict:
        """Executa uma função chamada pelo modelo.

        Args:
            function_call: Objeto FunctionCall do Gemini.

        Returns:
            dict: Resultado da execução da função.
        """
        function_name = function_call.name
        function_args = dict(function_call.args)

        logger.info(f"Executando tool: {function_name} com args: {function_args}")

        if function_name not in TOOL_FUNCTIONS:
            return {"error": f"Função {function_name} não encontrada"}

        # Adiciona api_base_url para consultar_beneficios
        if function_name == "consultar_beneficios":
            function_args["api_base_url"] = self.api_base_url

        try:
            result = TOOL_FUNCTIONS[function_name](**function_args)
            self.tools_used.append(function_name)
            return result
        except Exception as e:
            logger.error(f"Erro ao executar {function_name}: {e}")
            return {"error": str(e)}

    def process_message(self, user_message: str) -> str:
        """Processa uma mensagem do usuário e retorna a resposta.

        Args:
            user_message: Mensagem enviada pelo usuário.

        Returns:
            str: Resposta do agente.
        """
        try:
            # Envia mensagem para o modelo
            response = self.chat.send_message(user_message)

            # Processa function calls se houver
            while response.candidates[0].content.parts:
                # Verifica se há function calls
                function_calls = [
                    part.function_call
                    for part in response.candidates[0].content.parts
                    if hasattr(part, 'function_call') and part.function_call.name
                ]

                if not function_calls:
                    # Não há function calls, retorna o texto
                    break

                # Executa as funções e coleta resultados
                function_responses = []
                for fc in function_calls:
                    result = self._execute_function(fc)
                    function_responses.append({
                        "name": fc.name,
                        "response": result
                    })

                # Envia os resultados de volta ao modelo
                response = self.chat.send_message(
                    [
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fr["name"],
                                response={"result": fr["response"]}
                            )
                        )
                        for fr in function_responses
                    ]
                )

            # Extrai texto da resposta
            text_parts = [
                part.text
                for part in response.candidates[0].content.parts
                if hasattr(part, 'text') and part.text
            ]

            return " ".join(text_parts) if text_parts else "Desculpe, não consegui processar sua solicitação."

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return ERROR_MESSAGE

    def get_welcome_message(self) -> str:
        """Retorna a mensagem de boas-vindas."""
        return WELCOME_MESSAGE

    def reset(self):
        """Reinicia a conversa."""
        self.history = []
        self.tools_used = []
        self.chat = self.model.start_chat(history=self.history)


# Instância global para uso com ADK CLI
root_agent = None


def create_agent(session_id: Optional[str] = None) -> TaNaMaoAgent:
    """Factory function para criar agentes.

    Args:
        session_id: ID da sessão (opcional).

    Returns:
        TaNaMaoAgent: Nova instância do agente.
    """
    return TaNaMaoAgent(session_id=session_id)


# Para compatibilidade com adk run
if __name__ == "__main__":
    import sys

    # Verifica se API key está configurada
    if not GOOGLE_API_KEY:
        print("Erro: GOOGLE_API_KEY não configurada.")
        print("Configure a variável de ambiente: export GOOGLE_API_KEY='sua-chave'")
        sys.exit(1)

    # Modo interativo
    print("=" * 60)
    print("Tá na Mão - Assistente de Benefícios Sociais")
    print("=" * 60)

    agent = create_agent()
    print(agent.get_welcome_message())
    print()

    while True:
        try:
            user_input = input("Você: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\nAté mais! Espero ter ajudado.")
                break

            response = agent.process_message(user_input)
            print(f"\nAssistente: {response}\n")

        except KeyboardInterrupt:
            print("\n\nAté mais!")
            break

"""
Sub-agente especializado em documentação e localização de CRAS.

Gerencia o workflow de orientação sobre documentos necessários:
1. Identificar qual programa o cidadão quer
2. Gerar checklist de documentos personalizado
3. Coletar situação familiar para personalizar lista
4. Buscar CRAS mais próximo
5. Orientar sobre como fazer o cadastro

Usa máquina de estados para manter contexto entre mensagens.
"""

import re
import logging
from typing import Optional, Dict

from ..context import (
    ConversationContext,
    DocumentacaoFlowData,
    DocumentacaoState
)
from ..response_types import (
    AgentResponse,
    UIComponent,
    Action,
    ChecklistData,
    ChecklistItem,
    CrasCardData,
    AlertData
)
from ..tools.checklist import gerar_checklist, listar_beneficios
from ..tools.buscar_cras import buscar_cras
from ..tools.buscar_cep import buscar_cep

logger = logging.getLogger(__name__)


class DocumentacaoSubAgent:
    """
    Sub-agente para documentação e localização de CRAS.

    Implementa máquina de estados para guiar o cidadão através da
    preparação de documentos e localização do CRAS.
    """

    # Programas disponíveis para checklist
    PROGRAMAS = {
        "cadunico": ("CADASTRO_UNICO", "CadÚnico"),
        "cadastro_unico": ("CADASTRO_UNICO", "CadÚnico"),
        "bolsa_familia": ("BOLSA_FAMILIA", "Bolsa Família"),
        "bpc": ("BPC_LOAS", "BPC/LOAS"),
        "bpc_loas": ("BPC_LOAS", "BPC/LOAS"),
        "loas": ("BPC_LOAS", "BPC/LOAS"),
        "tarifa_social": ("TARIFA_SOCIAL_ENERGIA", "Tarifa Social de Energia"),
        "tsee": ("TARIFA_SOCIAL_ENERGIA", "Tarifa Social de Energia"),
        "farmacia_popular": ("FARMACIA_POPULAR", "Farmácia Popular"),
        "dignidade_menstrual": ("DIGNIDADE_MENSTRUAL", "Dignidade Menstrual"),
    }

    def __init__(self, context: ConversationContext):
        """
        Inicializa o sub-agente com contexto compartilhado.

        Args:
            context: Contexto da conversa (compartilhado com orquestrador)
        """
        self.context = context
        self.flow = context.get_documentacao_flow()

    async def process(self, message: str, image_base64: Optional[str] = None) -> AgentResponse:
        """
        Processa mensagem do usuário no fluxo de documentação.

        Args:
            message: Texto enviado pelo usuário
            image_base64: Imagem anexada (não usado neste fluxo)

        Returns:
            AgentResponse estruturado com texto, componentes UI e ações
        """
        state = self.flow.state
        logger.info(f"DocumentacaoAgent processando: state={state}, message={message[:50]}...")

        # Verificar comandos especiais
        if self._is_cancel_command(message):
            return self._handle_cancel()

        # Dispatch por estado
        handlers = {
            DocumentacaoState.INICIO: self._handle_inicio,
            DocumentacaoState.PROGRAMA: self._handle_programa,
            DocumentacaoState.CHECKLIST: self._handle_checklist,
            DocumentacaoState.LOCALIZACAO: self._handle_localizacao,
            DocumentacaoState.CRAS: self._handle_cras,
        }

        handler = handlers.get(state, self._handle_inicio)
        response = await handler(message)

        # Salvar estado atualizado
        self.context.set_documentacao_flow(self.flow)

        return response

    # =========================================================================
    # Handlers por Estado
    # =========================================================================

    async def _handle_inicio(self, message: str) -> AgentResponse:
        """Estado inicial: identifica programa ou pede qual quer."""

        # Verificar se quer buscar CRAS diretamente
        if self._wants_cras(message):
            # Verificar se já tem localização
            if self.context.citizen.cep or self.context.citizen.ibge_code:
                return await self._search_cras()

            self.flow.state = DocumentacaoState.LOCALIZACAO
            return self._ask_location()

        # Verificar se mencionou programa específico
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_selecionado = programa
            return await self._generate_checklist(programa)

        # Verificar se quer lista de programas
        if self._wants_list(message):
            return self._list_programs()

        # Pedir qual programa
        self.flow.state = DocumentacaoState.PROGRAMA
        return AgentResponse(
            text="Posso te ajudar com documentos para programas sociais!\n\n"
                 "Qual programa você precisa?\n"
                 "- **CadÚnico** - Cadastro Único\n"
                 "- **Bolsa Família**\n"
                 "- **BPC/LOAS** - Benefício para idosos/PCD\n"
                 "- **Tarifa Social** - Desconto na luz\n\n"
                 "Ou quer saber **onde é o CRAS**?",
            suggested_actions=[
                Action.send_message("CadÚnico", "documentos cadunico", primary=True),
                Action.send_message("Bolsa Família", "documentos bolsa familia"),
                Action.send_message("BPC/LOAS", "documentos bpc"),
                Action.send_message("Onde é o CRAS?", "onde fica o cras")
            ],
            flow_state="documentacao:inicio"
        )

    async def _handle_programa(self, message: str) -> AgentResponse:
        """Estado PROGRAMA: aguarda escolha do programa."""

        # Verificar se quer CRAS
        if self._wants_cras(message):
            if self.context.citizen.cep or self.context.citizen.ibge_code:
                return await self._search_cras()

            self.flow.state = DocumentacaoState.LOCALIZACAO
            return self._ask_location()

        # Tentar extrair programa
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_selecionado = programa
            return await self._generate_checklist(programa)

        # Não entendeu
        return AgentResponse(
            text="Não entendi qual programa você precisa.\n\n"
                 "Escolhe uma opção:",
            suggested_actions=[
                Action.send_message("CadÚnico", "documentos cadunico"),
                Action.send_message("Bolsa Família", "documentos bolsa familia"),
                Action.send_message("BPC/LOAS", "documentos bpc"),
                Action.send_message("Ver todos", "listar programas")
            ],
            flow_state="documentacao:programa"
        )

    async def _handle_checklist(self, message: str) -> AgentResponse:
        """Estado CHECKLIST: mostra checklist e oferece opções."""

        message_lower = message.lower()

        # Quer buscar CRAS
        if self._wants_cras(message):
            if self.context.citizen.cep or self.context.citizen.ibge_code:
                return await self._search_cras()

            self.flow.state = DocumentacaoState.LOCALIZACAO
            return self._ask_location()

        # Quer outro programa
        programa = self._extract_programa(message)
        if programa and programa != self.flow.programa_selecionado:
            self.flow.programa_selecionado = programa
            return await self._generate_checklist(programa)

        # Informou situação familiar
        situacao = self._extract_situacao(message)
        if situacao:
            # Atualizar contexto e regenerar checklist
            self._update_citizen_situacao(situacao)
            programa = self.flow.programa_selecionado or "CADASTRO_UNICO"
            return await self._generate_checklist(programa, with_situacao=True)

        # Perguntas sobre documentos específicos
        if any(word in message_lower for word in ["qual", "onde", "como", "consigo"]):
            return self._answer_document_question(message)

        # Quer saber onde ir
        if any(word in message_lower for word in ["onde ir", "endereço", "endereco", "local"]):
            self.flow.state = DocumentacaoState.LOCALIZACAO
            return self._ask_location()

        # Não entendeu
        return AgentResponse(
            text="Posso te ajudar com mais alguma coisa?\n\n"
                 "- Buscar o **CRAS mais próximo**\n"
                 "- Ver documentos de **outro programa**\n"
                 "- Tirar **dúvidas** sobre algum documento",
            suggested_actions=[
                Action.send_message("Onde é o CRAS?", "onde fica o cras", primary=True),
                Action.send_message("Outro programa", "ver outros programas"),
                Action.send_message("Tenho filhos", "tenho filhos menores")
            ],
            flow_state="documentacao:checklist"
        )

    async def _handle_localizacao(self, message: str) -> AgentResponse:
        """Estado LOCALIZACAO: coleta CEP para buscar CRAS."""

        # Tentar extrair CEP
        cep = self._extract_cep(message)

        if cep:
            # Buscar endereço
            resultado = await buscar_cep(cep)

            if resultado.get("encontrado"):
                # Atualizar contexto
                self.context.citizen.update_from_cep_result(resultado)
                return await self._search_cras()

            return AgentResponse(
                text=f"Não encontrei o CEP {cep}. Confere se digitou certo?\n\n"
                     "Digita só os 8 números: 01310100",
                flow_state="documentacao:localizacao"
            )

        # Não sabe o CEP
        if "não sei" in message.lower() or "nao sei" in message.lower():
            return AgentResponse(
                text="Sem problema! Você pode encontrar o CRAS de outra forma:\n\n"
                     "- Ligue para o **Disque Social: 121** (gratuito)\n"
                     "- Ou acesse: aplicacoes.mds.gov.br/sagi/miv/miv.php\n\n"
                     "Quer ver os documentos que precisa levar?",
                suggested_actions=[
                    Action.send_message("Ver documentos do CadÚnico", "documentos cadunico"),
                    Action.open_url("Buscar CRAS online", "https://aplicacoes.mds.gov.br/sagi/miv/miv.php")
                ],
                flow_state="documentacao:localizacao"
            )

        # Pede CEP
        return AgentResponse(
            text="Digita seu CEP pra eu achar o CRAS perto de você.\n\n"
                 "Só os 8 números: 01310100",
            suggested_actions=[
                Action.send_message("Não sei meu CEP", "não sei o cep")
            ],
            flow_state="documentacao:localizacao"
        )

    async def _handle_cras(self, message: str) -> AgentResponse:
        """Estado CRAS: mostra CRAS e oferece opções."""

        message_lower = message.lower()

        # Quer ver documentos
        if any(word in message_lower for word in ["documento", "checklist", "preciso levar"]):
            programa = self.flow.programa_selecionado or "CADASTRO_UNICO"
            return await self._generate_checklist(programa)

        # Quer outro CRAS ou CEP
        cep = self._extract_cep(message)
        if cep:
            resultado = buscar_cep(cep)
            if resultado.get("encontrado"):
                self.context.citizen.update_from_cep_result(resultado)
                return await self._search_cras()

        # Quer outro programa
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_selecionado = programa
            return await self._generate_checklist(programa)

        # Finaliza
        return AgentResponse(
            text="Mais alguma coisa que posso ajudar?",
            suggested_actions=[
                Action.send_message("Ver documentos", "que documentos preciso"),
                Action.send_message("Outro CEP", "buscar outro cep"),
                Action.send_message("Pedir remédios", "quero pedir remédios")
            ],
            flow_state="documentacao:cras"
        )

    # =========================================================================
    # Métodos de Geração de Checklist
    # =========================================================================

    async def _generate_checklist(
        self,
        programa: str,
        with_situacao: bool = False
    ) -> AgentResponse:
        """Gera checklist de documentos para o programa."""

        # Mapear para código
        codigo, nome = self.PROGRAMAS.get(programa, (programa.upper(), programa))

        # Situação do cidadão para personalizar
        situacao = {}
        if with_situacao or self._has_situacao():
            situacao = {
                "tem_filhos": self.context.citizen.tem_filhos,
                "idoso": self.context.citizen.idoso,
                "gestante": self.context.citizen.gestante,
                "deficiencia": self.context.citizen.deficiencia,
            }

        self.context.add_tool_usage("gerar_checklist")
        resultado = gerar_checklist(codigo, situacao)

        if resultado.get("erro"):
            return AgentResponse(
                text=f"Não encontrei informações sobre '{programa}'.\n"
                     "Veja os programas disponíveis:",
                suggested_actions=[
                    Action.send_message("Ver programas", "listar programas")
                ],
                flow_state="documentacao:programa"
            )

        self.flow.checklist_gerado = resultado
        self.flow.state = DocumentacaoState.CHECKLIST

        # Montar items do checklist
        items = []
        for doc in resultado.get("documentos_obrigatorios", []):
            items.append(ChecklistItem(
                text=doc["nome"],
                required=True,
                note=doc.get("dica")
            ))

        for doc in resultado.get("documentos_condicionais", []):
            items.append(ChecklistItem(
                text=doc["nome"],
                required=False,
                note=doc.get("condicao")
            ))

        for doc in resultado.get("documentos_opcionais", []):
            items.append(ChecklistItem(
                text=doc["nome"],
                required=False
            ))

        # Texto formatado
        texto = resultado.get("checklist_texto", "")

        # Se não perguntou sobre situação familiar ainda, perguntar
        if not with_situacao and not self._has_situacao():
            texto += "\n\n**Tem filhos menores de 18 anos?** Me conta que eu personalizo a lista!"

        # Determinar ações baseado no programa (farmácia vs CRAS)
        programas_farmacia = ["FARMACIA_POPULAR", "DIGNIDADE_MENSTRUAL"]
        if codigo in programas_farmacia:
            actions = [
                Action.send_message("Encontrar Farmácia", "onde tem farmácia popular perto de mim", primary=True),
                Action.send_message("Enviar receita", "quero enviar foto da receita")
            ]
        else:
            actions = [
                Action.send_message("Onde é o CRAS?", "onde fica o cras", primary=True),
                Action.send_message("Tenho filhos", "tenho filhos menores"),
                Action.send_message("Outro programa", "ver outros programas")
            ]

        return AgentResponse(
            text=texto,
            ui_components=[
                UIComponent.checklist(ChecklistData(
                    title=f"Documentos para {resultado['beneficio']}",
                    items=items,
                    program=codigo,
                    total_required=len(resultado.get("documentos_obrigatorios", [])),
                    total_optional=len(resultado.get("documentos_opcionais", []))
                ))
            ],
            suggested_actions=actions,
            flow_state="documentacao:checklist"
        )

    def _list_programs(self) -> AgentResponse:
        """Lista programas disponíveis para checklist."""

        self.context.add_tool_usage("listar_beneficios")
        resultado = listar_beneficios()

        texto = "**Programas que você pode solicitar:**\n\n"

        for b in resultado.get("beneficios", []):
            texto += f"**{b['nome']}**\n"
            texto += f"{b.get('descricao', '')}\n"
            texto += f"📍 {b.get('onde_fazer', '')}\n\n"

        texto += "Qual você precisa?"

        return AgentResponse(
            text=texto,
            suggested_actions=[
                Action.send_message("CadÚnico", "documentos cadunico"),
                Action.send_message("Bolsa Família", "documentos bolsa familia"),
                Action.send_message("BPC/LOAS", "documentos bpc")
            ],
            flow_state="documentacao:programa"
        )

    def _answer_document_question(self, message: str) -> AgentResponse:
        """Responde dúvidas sobre documentos específicos."""

        message_lower = message.lower()

        # Dúvidas comuns
        if "comprovante de renda" in message_lower or "comprovar renda" in message_lower:
            return AgentResponse(
                text="**Sobre comprovante de renda:**\n\n"
                     "Se você **trabalha com carteira assinada**:\n"
                     "- Último contracheque ou holerite\n\n"
                     "Se é **autônomo ou informal**:\n"
                     "- Declaração de próprio punho informando quanto ganha\n"
                     "- Não precisa de assinatura de terceiros\n\n"
                     "Se **não tem renda**:\n"
                     "- Declaração de que não tem renda\n\n"
                     "O CRAS aceita declaração escrita à mão!",
                flow_state="documentacao:checklist"
            )

        if "certidão de nascimento" in message_lower or "certidao" in message_lower:
            return AgentResponse(
                text="**Sobre Certidão de Nascimento:**\n\n"
                     "- Pode ser a original ou cópia\n"
                     "- Se perdeu, pode tirar segunda via no cartório\n"
                     "- Em alguns casos, o RG substitui\n\n"
                     "Precisa para cada membro da família!",
                flow_state="documentacao:checklist"
            )

        if "comprovante de residência" in message_lower or "endereço" in message_lower:
            return AgentResponse(
                text="**Sobre comprovante de residência:**\n\n"
                     "Pode ser:\n"
                     "- Conta de luz, água ou telefone (últimos 3 meses)\n"
                     "- Contrato de aluguel\n"
                     "- Declaração do proprietário\n\n"
                     "**Se mora de favor ou não tem conta no nome:**\n"
                     "- Declaração do dono do imóvel\n"
                     "- Ou declaração de próprio punho",
                flow_state="documentacao:checklist"
            )

        # Resposta genérica
        return AgentResponse(
            text="Se tiver dúvida sobre algum documento específico, "
                 "o CRAS pode orientar quando você chegar lá.\n\n"
                 "O importante é levar o que você tem. "
                 "Se faltar algo, eles informam!",
            suggested_actions=[
                Action.send_message("Onde é o CRAS?", "onde fica o cras")
            ],
            flow_state="documentacao:checklist"
        )

    # =========================================================================
    # Métodos de Busca de CRAS
    # =========================================================================

    async def _search_cras(self) -> AgentResponse:
        """Busca CRAS mais próximos."""

        self.context.add_tool_usage("buscar_cras")

        resultado = buscar_cras(
            cep=self.context.citizen.cep,
            ibge_code=self.context.citizen.ibge_code,
            limite=3
        )

        cras_list = resultado.get("cras", [])

        if not cras_list:
            # Não encontrou CRAS na base
            return AgentResponse(
                text=resultado.get("texto_formatado", "Não encontrei CRAS na região."),
                ui_components=[
                    UIComponent.alert(AlertData(
                        type="info",
                        title="CRAS não encontrado na base",
                        message="Ligue para o Disque Social: 121",
                        dismissable=True
                    ))
                ],
                suggested_actions=[
                    Action.call_phone("Ligar Disque Social", "121"),
                    Action.open_url("Buscar online", "https://aplicacoes.mds.gov.br/sagi/miv/miv.php"),
                    Action.send_message("Ver documentos", "que documentos preciso")
                ],
                flow_state="documentacao:cras"
            )

        # Salvar CRAS encontrados
        self.flow.cras_encontrados = cras_list
        self.flow.state = DocumentacaoState.CRAS

        # Montar cards de CRAS
        cras_cards = []
        texto = f"Encontrei {len(cras_list)} CRAS perto de você:\n\n"

        for i, cras in enumerate(cras_list, 1):
            texto += f"**{i}. {cras['nome']}**\n"
            texto += f"📍 {cras['endereco']}"
            if cras.get("bairro"):
                texto += f", {cras['bairro']}"
            texto += "\n"
            if cras.get("telefone"):
                texto += f"📞 {cras['telefone']}\n"
            if cras.get("horario"):
                texto += f"🕐 {cras['horario']}\n"
            texto += "\n"

            cras_cards.append(UIComponent.cras_card(CrasCardData(
                name=cras["nome"],
                address=cras["endereco"],
                neighborhood=cras.get("bairro"),
                city=cras.get("cidade"),
                phone=cras.get("telefone"),
                hours=cras.get("horario"),
                services=cras.get("servicos", [])
            )))

        texto += "Leve os documentos e vá ao CRAS mais perto de você!"

        # Ações
        actions = []
        if cras_list[0].get("telefone"):
            actions.append(Action.call_phone(
                f"Ligar {cras_list[0]['nome'][:15]}",
                cras_list[0]["telefone"]
            ))
        actions.append(Action.send_message("Ver documentos necessários", "que documentos preciso"))
        if cras_list[0].get("endereco"):
            actions.append(Action.open_map("Ver no mapa", cras_list[0]["endereco"]))

        return AgentResponse(
            text=texto,
            ui_components=cras_cards,
            suggested_actions=actions,
            flow_state="documentacao:cras"
        )

    def _ask_location(self) -> AgentResponse:
        """Pede localização para buscar CRAS."""

        return AgentResponse(
            text="Para encontrar o CRAS mais perto de você, "
                 "me passa seu CEP.\n\n"
                 "Digita os 8 números: 01310100",
            suggested_actions=[
                Action.send_message("Não sei meu CEP", "não sei o cep")
            ],
            flow_state="documentacao:localizacao"
        )

    # =========================================================================
    # Métodos Auxiliares
    # =========================================================================

    def _extract_programa(self, text: str) -> Optional[str]:
        """Extrai programa mencionado no texto."""

        text_lower = text.lower()

        # Mapeamento de keywords para programas
        keywords = {
            "cadunico": ["cadunico", "cadúnico", "cadastro único", "cadastro unico", "cad único"],
            "bolsa_familia": ["bolsa família", "bolsa familia", "bf"],
            "bpc": ["bpc", "loas", "bpc/loas", "benefício de prestação", "idoso", "deficiência"],
            "tarifa_social": ["tarifa social", "desconto luz", "tsee", "energia", "conta de luz"],
            "farmacia_popular": ["farmácia popular", "farmacia popular"],
            "dignidade_menstrual": ["dignidade menstrual", "absorvente"],
        }

        for programa, kws in keywords.items():
            if any(kw in text_lower for kw in kws):
                return programa

        return None

    def _extract_cep(self, text: str) -> Optional[str]:
        """Extrai CEP do texto."""
        numeros = re.sub(r'\D', '', text)
        if len(numeros) == 8:
            return numeros
        match = re.search(r'\d{5}-?\d{3}', text)
        if match:
            return re.sub(r'\D', '', match.group())
        return None

    def _extract_situacao(self, text: str) -> Optional[Dict[str, bool]]:
        """Extrai situação familiar do texto."""

        text_lower = text.lower()
        situacao = {}

        if any(word in text_lower for word in ["filho", "filhos", "criança", "criancas", "menor"]):
            situacao["tem_filhos"] = True

        if any(word in text_lower for word in ["grávida", "gravida", "gestante", "gravidez"]):
            situacao["gestante"] = True

        if any(word in text_lower for word in ["idoso", "65 anos", "terceira idade"]):
            situacao["idoso"] = True

        if any(word in text_lower for word in ["deficiência", "deficiencia", "pcd", "cadeirante"]):
            situacao["deficiencia"] = True

        return situacao if situacao else None

    def _update_citizen_situacao(self, situacao: Dict[str, bool]) -> None:
        """Atualiza situação do cidadão no contexto."""
        if situacao.get("tem_filhos"):
            self.context.citizen.tem_filhos = True
        if situacao.get("gestante"):
            self.context.citizen.gestante = True
        if situacao.get("idoso"):
            self.context.citizen.idoso = True
        if situacao.get("deficiencia"):
            self.context.citizen.deficiencia = True

    def _has_situacao(self) -> bool:
        """Verifica se já tem informações de situação familiar."""
        c = self.context.citizen
        return c.tem_filhos or c.gestante or c.idoso or c.deficiencia

    def _wants_cras(self, message: str) -> bool:
        """Verifica se quer buscar CRAS."""
        keywords = ["cras", "onde ir", "onde fica", "endereço", "endereco", "local", "unidade"]
        return any(kw in message.lower() for kw in keywords)

    def _wants_list(self, message: str) -> bool:
        """Verifica se quer listar programas."""
        keywords = ["listar", "todos", "quais programas", "ver programas", "disponíveis"]
        return any(kw in message.lower() for kw in keywords)

    def _is_cancel_command(self, message: str) -> bool:
        """Verifica se é comando de cancelamento."""
        return any(word in message.lower() for word in ["cancelar", "sair", "voltar"])

    def _handle_cancel(self) -> AgentResponse:
        """Cancela o fluxo atual."""

        self.flow = DocumentacaoFlowData()
        self.context.set_documentacao_flow(self.flow)
        self.context.end_flow()

        return AgentResponse(
            text="Tudo bem! Posso ajudar com outra coisa?",
            suggested_actions=[
                Action.send_message("Ver documentos", "que documentos preciso"),
                Action.send_message("Consultar benefícios", "consultar benefícios"),
                Action.send_message("Pedir remédios", "quero pedir remédios")
            ],
            flow_state=None
        )

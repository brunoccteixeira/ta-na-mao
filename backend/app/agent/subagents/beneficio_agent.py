"""
Sub-agente especializado em consulta de benefícios sociais.

Gerencia o workflow de consulta e orientação sobre benefícios:
1. Coletar CPF do cidadão
2. Consultar benefícios ativos (Bolsa Família, BPC, CadÚnico)
3. Mostrar resultados estruturados
4. Verificar elegibilidade para outros programas
5. Orientar sobre próximos passos

Usa máquina de estados para manter contexto entre mensagens.
"""

import re
import logging
from typing import Optional, Dict, Any

from ..context import (
    ConversationContext,
    BeneficioFlowData,
    BeneficioState
)
from ..response_types import (
    AgentResponse,
    UIComponent,
    Action,
    BenefitCardData,
    ChecklistData,
    ChecklistItem,
    AlertData
)
from ..tools.consultar_beneficio import consultar_beneficio, verificar_elegibilidade
from ..tools.checklist import gerar_checklist, listar_beneficios
from ..tools.validar_cpf import validar_cpf

logger = logging.getLogger(__name__)


class BeneficioSubAgent:
    """
    Sub-agente para consulta de benefícios sociais.

    Implementa máquina de estados para guiar o cidadão através da
    consulta de benefícios e orientação sobre elegibilidade.
    """

    # Programas suportados para verificação de elegibilidade
    PROGRAMAS = {
        "bolsa_familia": "Bolsa Família",
        "bpc": "BPC/LOAS",
        "farmacia_popular": "Farmácia Popular",
        "tarifa_social": "Tarifa Social de Energia",
        "dignidade_menstrual": "Dignidade Menstrual",
        "cadunico": "CadÚnico"
    }

    def __init__(self, context: ConversationContext):
        """
        Inicializa o sub-agente com contexto compartilhado.

        Args:
            context: Contexto da conversa (compartilhado com orquestrador)
        """
        self.context = context
        self.flow = context.get_beneficio_flow()

    async def process(self, message: str, image_base64: Optional[str] = None) -> AgentResponse:
        """
        Processa mensagem do usuário no fluxo de benefícios.

        Args:
            message: Texto enviado pelo usuário
            image_base64: Imagem anexada (não usado neste fluxo)

        Returns:
            AgentResponse estruturado com texto, componentes UI e ações
        """
        state = self.flow.state
        logger.info(f"BeneficioAgent processando: state={state}, message={message[:50]}...")

        # Verificar comandos especiais
        if self._is_cancel_command(message):
            return self._handle_cancel()

        # Dispatch por estado
        handlers = {
            BeneficioState.INICIO: self._handle_inicio,
            BeneficioState.CONSULTA_CPF: self._handle_consulta_cpf,
            BeneficioState.RESULTADO: self._handle_resultado,
            BeneficioState.ELEGIBILIDADE: self._handle_elegibilidade,
            BeneficioState.ORIENTACAO: self._handle_orientacao,
        }

        handler = handlers.get(state, self._handle_inicio)
        response = await handler(message)

        # Salvar estado atualizado
        self.context.set_beneficio_flow(self.flow)

        return response

    # =========================================================================
    # Handlers por Estado
    # =========================================================================

    async def _handle_inicio(self, message: str) -> AgentResponse:
        """Estado inicial: identifica intenção e pede CPF se necessário."""

        # Verificar se já tem CPF no contexto
        if self.context.citizen.cpf:
            return await self._consultar_e_mostrar_beneficios()

        # Verificar se a mensagem contém CPF
        cpf = self._extract_cpf(message)
        if cpf:
            return await self._process_cpf(cpf)

        # Verificar se quer listar benefícios disponíveis
        if self._wants_list_benefits(message):
            return self._list_available_benefits()

        # Verificar se quer saber sobre programa específico
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_consultado = programa
            self.flow.state = BeneficioState.ELEGIBILIDADE
            return self._ask_cpf_for_eligibility(programa)

        # Pede CPF para consulta
        self.flow.state = BeneficioState.CONSULTA_CPF
        return AgentResponse(
            text="Posso te ajudar com benefícios sociais!\n\n"
                 "O que você precisa?\n"
                 "- **Consultar seus benefícios**: me passa seu CPF\n"
                 "- **Ver benefícios disponíveis**: lista de programas\n"
                 "- **Saber se tem direito**: me fala qual programa",
            suggested_actions=[
                Action.send_message("Consultar meus benefícios", "quero consultar", primary=True),
                Action.send_message("Ver programas disponíveis", "listar programas"),
                Action.send_message("Bolsa Família", "tenho direito ao bolsa família?")
            ],
            flow_state="beneficio:inicio"
        )

    async def _handle_consulta_cpf(self, message: str) -> AgentResponse:
        """Estado CONSULTA_CPF: aguarda CPF do cidadão."""

        # Tentar extrair CPF
        cpf = self._extract_cpf(message)

        if cpf:
            return await self._process_cpf(cpf)

        # Verificar se quer listar benefícios
        if self._wants_list_benefits(message):
            return self._list_available_benefits()

        # Não encontrou CPF
        return AgentResponse(
            text="Não consegui identificar o CPF.\n\n"
                 "Digita os 11 números do seu CPF.\n"
                 "Exemplo: 12345678900 ou 123.456.789-00",
            suggested_actions=[
                Action.send_message("Ver programas disponíveis", "listar programas")
            ],
            flow_state="beneficio:consulta_cpf"
        )

    async def _handle_resultado(self, message: str) -> AgentResponse:
        """Estado RESULTADO: mostra resultado e oferece opções."""

        message_lower = message.lower()

        # Quer ver outro programa
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_consultado = programa
            return await self._check_eligibility(programa)

        # Quer ver checklist
        if any(word in message_lower for word in ["documento", "checklist", "preciso"]):
            programa = self.flow.programa_consultado or "CADASTRO_UNICO"
            return self._show_checklist(programa)

        # Quer consultar outro CPF
        cpf = self._extract_cpf(message)
        if cpf:
            return await self._process_cpf(cpf)

        # Quer saber mais
        if any(word in message_lower for word in ["mais", "outro", "demais"]):
            return self._list_available_benefits()

        # Não entendeu
        return AgentResponse(
            text="Posso te ajudar com mais alguma coisa?\n\n"
                 "- Ver **documentos necessários** para algum programa\n"
                 "- Verificar **elegibilidade** para outro benefício\n"
                 "- **Consultar outro CPF**",
            suggested_actions=[
                Action.send_message("Ver documentos do CadÚnico", "documentos cadunico"),
                Action.send_message("Tenho direito ao BPC?", "tenho direito ao bpc"),
                Action.send_message("Consultar outro CPF", "consultar outro cpf")
            ],
            flow_state="beneficio:resultado"
        )

    async def _handle_elegibilidade(self, message: str) -> AgentResponse:
        """Estado ELEGIBILIDADE: verifica direito a programa específico."""

        # Verificar se enviou CPF
        cpf = self._extract_cpf(message)
        if cpf:
            # Validar e salvar CPF
            resultado = validar_cpf(cpf)
            if resultado.get("valido"):
                self.context.citizen.cpf = resultado.get("cpf_numerico")
                self.context.citizen.cpf_masked = resultado.get("cpf_formatado")

                # Verificar elegibilidade
                programa = self.flow.programa_consultado or "BOLSA_FAMILIA"
                return await self._check_eligibility(programa)
            else:
                return AgentResponse(
                    text=f"CPF inválido: {resultado.get('mensagem', 'verifique os números')}\n\n"
                         "Digita novamente os 11 números.",
                    flow_state="beneficio:elegibilidade"
                )

        # Verificar se quer ver sem CPF
        if any(word in message.lower() for word in ["sem cpf", "não tenho", "nao tenho", "geral"]):
            programa = self.flow.programa_consultado or "CADASTRO_UNICO"
            return self._show_program_info(programa)

        # Pede CPF
        return AgentResponse(
            text="Para verificar se você tem direito, preciso do seu CPF.\n\n"
                 "Digita os 11 números:",
            suggested_actions=[
                Action.send_message("Ver informações gerais", "informações gerais")
            ],
            flow_state="beneficio:elegibilidade"
        )

    async def _handle_orientacao(self, message: str) -> AgentResponse:
        """Estado ORIENTACAO: fornece orientação detalhada."""

        message_lower = message.lower()

        # Quer ver checklist
        if any(word in message_lower for word in ["documento", "checklist", "lista"]):
            programa = self.flow.programa_consultado or "CADASTRO_UNICO"
            return self._show_checklist(programa)

        # Quer saber onde ir
        if any(word in message_lower for word in ["onde", "cras", "endereço", "endereco"]):
            self.context.end_flow()
            return AgentResponse(
                text="Para saber onde é o CRAS mais próximo, me fala seu CEP!",
                suggested_actions=[
                    Action.send_message("Buscar CRAS", "onde fica o cras")
                ],
                flow_state=None
            )

        # Quer outro benefício
        programa = self._extract_programa(message)
        if programa:
            self.flow.programa_consultado = programa
            return await self._check_eligibility(programa)

        # Finaliza
        return AgentResponse(
            text="Quer saber mais alguma coisa?",
            suggested_actions=[
                Action.send_message("Ver documentos", "que documentos preciso"),
                Action.send_message("Buscar CRAS", "onde fica o cras"),
                Action.send_message("Outro benefício", "outros benefícios")
            ],
            flow_state="beneficio:orientacao"
        )

    # =========================================================================
    # Métodos de Consulta
    # =========================================================================

    async def _process_cpf(self, cpf: str) -> AgentResponse:
        """Processa CPF e consulta benefícios."""

        # Validar CPF
        resultado_validacao = validar_cpf(cpf)

        if not resultado_validacao.get("valido"):
            return AgentResponse(
                text=f"CPF inválido: {resultado_validacao.get('mensagem', 'verifique os números')}\n\n"
                     "Digita novamente os 11 números do CPF:",
                flow_state="beneficio:consulta_cpf"
            )

        # Salvar CPF no contexto
        cpf_numerico = resultado_validacao.get("cpf_numerico")
        self.context.citizen.cpf = cpf_numerico
        self.context.citizen.cpf_masked = resultado_validacao.get("cpf_formatado")
        self.context.add_tool_usage("validar_cpf")

        return await self._consultar_e_mostrar_beneficios()

    async def _consultar_e_mostrar_beneficios(self) -> AgentResponse:
        """Consulta benefícios e monta resposta estruturada."""

        cpf = self.context.citizen.cpf
        if not cpf:
            self.flow.state = BeneficioState.CONSULTA_CPF
            return AgentResponse(
                text="Preciso do seu CPF para consultar. Me passa?",
                flow_state="beneficio:consulta_cpf"
            )

        # Consultar benefícios
        self.context.add_tool_usage("consultar_beneficio")
        resultado = consultar_beneficio(cpf)

        # Salvar resultado
        self.flow.resultado_consulta = resultado
        self.flow.state = BeneficioState.RESULTADO

        if not resultado.get("encontrado"):
            return self._handle_not_found(resultado)

        # Atualizar perfil do cidadão
        if resultado.get("nome"):
            self.context.citizen.nome = resultado.get("nome")
        if resultado.get("uf"):
            self.context.citizen.uf = resultado.get("uf")
        if resultado.get("beneficios"):
            self.context.citizen.update_from_beneficio_result(resultado.get("beneficios"))

        return self._build_benefit_response(resultado)

    def _build_benefit_response(self, resultado: Dict[str, Any]) -> AgentResponse:
        """Monta resposta com cards de benefícios."""

        beneficios = resultado.get("beneficios", {})
        nome = resultado.get("nome", "")
        cpf_masked = resultado.get("cpf_masked", "")

        # Montar texto
        texto = f"Encontrei os dados de **{nome}**\n"
        texto += f"CPF: {cpf_masked}\n\n"

        # Cards de benefícios
        ui_components = []
        beneficios_ativos = []

        # Bolsa Família
        bf = beneficios.get("bolsa_familia", {})
        if bf:
            status = "receiving" if bf.get("ativo") else "not_eligible"
            valor = bf.get("valor", 0)
            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else None

            ui_components.append(UIComponent.benefit_card(BenefitCardData(
                code="BOLSA_FAMILIA",
                name="Bolsa Família",
                status=status,
                value=valor,
                value_formatted=valor_fmt,
                last_payment=bf.get("parcela_mes"),
                description="Transferência de renda para famílias"
            )))

            if bf.get("ativo"):
                beneficios_ativos.append(f"**Bolsa Família**: {valor_fmt}")

        # BPC
        bpc = beneficios.get("bpc", {})
        if bpc:
            status = "receiving" if bpc.get("ativo") else "not_eligible"
            valor = bpc.get("valor", 0)
            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else None
            tipo = bpc.get("tipo", "")

            ui_components.append(UIComponent.benefit_card(BenefitCardData(
                code="BPC",
                name=f"BPC/LOAS {tipo}".strip(),
                status=status,
                value=valor,
                value_formatted=valor_fmt,
                description="Benefício para idosos e pessoas com deficiência"
            )))

            if bpc.get("ativo"):
                beneficios_ativos.append(f"**BPC {tipo}**: {valor_fmt}")

        # CadÚnico
        cadunico = beneficios.get("cadunico", {})
        if cadunico:
            status = "receiving" if cadunico.get("ativo") else "not_eligible"
            faixa = cadunico.get("faixa_renda", "")

            ui_components.append(UIComponent.benefit_card(BenefitCardData(
                code="CADUNICO",
                name="CadÚnico",
                status=status,
                description=f"Faixa: {faixa}" if faixa else "Cadastro Único"
            )))

            if cadunico.get("ativo"):
                beneficios_ativos.append(f"**CadÚnico** ativo (faixa: {faixa})")

        # Resumo no texto
        if beneficios_ativos:
            texto += "**Benefícios ativos:**\n"
            for b in beneficios_ativos:
                texto += f"- {b}\n"
        else:
            texto += "Nenhum benefício ativo no momento.\n"

        texto += "\nQuer saber se tem direito a outros programas?"

        # Ações sugeridas
        actions = []
        if not bf.get("ativo"):
            actions.append(Action.send_message("Tenho direito ao Bolsa Família?", "tenho direito bolsa familia"))
        if not bpc.get("ativo"):
            actions.append(Action.send_message("Tenho direito ao BPC?", "tenho direito bpc"))
        actions.append(Action.send_message("Ver outros programas", "listar programas"))

        return AgentResponse(
            text=texto,
            ui_components=ui_components,
            suggested_actions=actions[:3],
            flow_state="beneficio:resultado"
        )

    def _handle_not_found(self, resultado: Dict[str, Any]) -> AgentResponse:
        """Trata caso de CPF não encontrado."""

        cpf_masked = resultado.get("cpf_masked", "")

        return AgentResponse(
            text=f"Não encontrei benefícios para o CPF {cpf_masked}.\n\n"
                 "Isso pode significar:\n"
                 "- Você não recebe Bolsa Família ou BPC atualmente\n"
                 "- Os dados ainda não foram atualizados\n"
                 "- O CPF informado está incorreto\n\n"
                 "Quer saber como solicitar um benefício?",
            ui_components=[
                UIComponent.alert(AlertData(
                    type="info",
                    title="CPF não encontrado",
                    message="Você ainda pode ter direito a benefícios!",
                    dismissable=True
                ))
            ],
            suggested_actions=[
                Action.send_message("Como solicitar Bolsa Família", "como solicitar bolsa familia"),
                Action.send_message("Como solicitar BPC", "como solicitar bpc"),
                Action.send_message("Fazer CadÚnico", "como fazer cadunico")
            ],
            flow_state="beneficio:resultado"
        )

    async def _check_eligibility(self, programa: str) -> AgentResponse:
        """Verifica elegibilidade para programa específico."""

        cpf = self.context.citizen.cpf
        if not cpf:
            self.flow.programa_consultado = programa
            self.flow.state = BeneficioState.ELEGIBILIDADE
            return self._ask_cpf_for_eligibility(programa)

        # Mapear para código
        codigo_map = {
            "bolsa_familia": "BOLSA_FAMILIA",
            "bpc": "BPC",
            "farmacia_popular": "FARMACIA_POPULAR",
            "tarifa_social": "TSEE",
            "dignidade_menstrual": "DIGNIDADE_MENSTRUAL",
            "cadunico": "CADUNICO"
        }
        codigo = codigo_map.get(programa, programa.upper())

        # Verificar elegibilidade
        self.context.add_tool_usage("verificar_elegibilidade")
        resultado = verificar_elegibilidade(cpf, codigo)

        self.flow.state = BeneficioState.ORIENTACAO

        # Montar resposta
        nome_programa = self.PROGRAMAS.get(programa, programa)

        if resultado.get("ja_recebe"):
            return AgentResponse(
                text=f"Você **já recebe** {nome_programa}!\n\n"
                     f"{resultado.get('motivo', '')}\n\n"
                     f"**Próximos passos:**\n{resultado.get('proximos_passos', '')}",
                ui_components=[
                    UIComponent.benefit_card(BenefitCardData(
                        code=codigo,
                        name=nome_programa,
                        status="receiving",
                        description=resultado.get('motivo', '')
                    ))
                ],
                suggested_actions=[
                    Action.send_message("Ver outros programas", "outros programas"),
                    Action.send_message("Documentos necessários", f"documentos {programa}")
                ],
                flow_state="beneficio:orientacao"
            )

        elif resultado.get("elegivel") is True:
            return AgentResponse(
                text=f"Você **pode ter direito** ao {nome_programa}!\n\n"
                     f"{resultado.get('motivo', '')}\n\n"
                     f"**Como solicitar:**\n{resultado.get('proximos_passos', '')}",
                ui_components=[
                    UIComponent.benefit_card(BenefitCardData(
                        code=codigo,
                        name=nome_programa,
                        status="eligible",
                        description="Você pode ter direito!"
                    ))
                ],
                suggested_actions=[
                    Action.send_message("Ver documentos necessários", f"documentos {programa}", primary=True),
                    Action.send_message("Onde ir (CRAS)", "onde fica o cras")
                ],
                flow_state="beneficio:orientacao"
            )

        else:
            return AgentResponse(
                text=f"Sobre o **{nome_programa}**:\n\n"
                     f"{resultado.get('motivo', 'Não foi possível determinar elegibilidade.')}\n\n"
                     f"**Orientação:**\n{resultado.get('proximos_passos', '')}",
                ui_components=[
                    UIComponent.benefit_card(BenefitCardData(
                        code=codigo,
                        name=nome_programa,
                        status="pending",
                        description="Verifique no CRAS"
                    ))
                ],
                suggested_actions=[
                    Action.send_message("Ver documentos", f"documentos {programa}"),
                    Action.send_message("Buscar CRAS", "onde fica o cras"),
                    Action.send_message("Outros programas", "listar programas")
                ],
                flow_state="beneficio:orientacao"
            )

    def _ask_cpf_for_eligibility(self, programa: str) -> AgentResponse:
        """Pede CPF para verificar elegibilidade."""

        nome_programa = self.PROGRAMAS.get(programa, programa)

        return AgentResponse(
            text=f"Para verificar se você tem direito ao **{nome_programa}**, "
                 f"preciso consultar seus dados.\n\n"
                 f"Me passa seu CPF (11 números):",
            suggested_actions=[
                Action.send_message("Ver informações gerais", f"informações {programa}")
            ],
            flow_state="beneficio:elegibilidade"
        )

    # =========================================================================
    # Métodos de Listagem e Checklist
    # =========================================================================

    def _list_available_benefits(self) -> AgentResponse:
        """Lista benefícios disponíveis."""

        self.context.add_tool_usage("listar_beneficios")
        resultado = listar_beneficios()

        texto = "**Programas sociais disponíveis:**\n\n"

        for b in resultado.get("beneficios", []):
            texto += f"**{b['nome']}**\n"
            texto += f"{b.get('descricao', '')}\n"
            texto += f"📍 {b.get('onde_fazer', '')}\n\n"

        texto += "Qual programa você quer saber mais?"

        return AgentResponse(
            text=texto,
            suggested_actions=[
                Action.send_message("Bolsa Família", "saber mais bolsa familia"),
                Action.send_message("BPC/LOAS", "saber mais bpc"),
                Action.send_message("CadÚnico", "saber mais cadunico")
            ],
            flow_state="beneficio:inicio"
        )

    def _show_program_info(self, programa: str) -> AgentResponse:
        """Mostra informações gerais de um programa."""

        # Mapear para código
        codigo_map = {
            "bolsa_familia": "BOLSA_FAMILIA",
            "bpc": "BPC_LOAS",
            "farmacia_popular": "FARMACIA_POPULAR",
            "tarifa_social": "TARIFA_SOCIAL_ENERGIA",
            "dignidade_menstrual": "DIGNIDADE_MENSTRUAL",
            "cadunico": "CADASTRO_UNICO"
        }
        codigo = codigo_map.get(programa, programa.upper())

        # Gerar checklist (tem info do programa)
        resultado = gerar_checklist(codigo)

        if resultado.get("erro"):
            return AgentResponse(
                text=f"Não encontrei informações sobre '{programa}'.\n"
                     "Veja os programas disponíveis:",
                suggested_actions=[
                    Action.send_message("Ver programas", "listar programas")
                ],
                flow_state="beneficio:inicio"
            )

        texto = f"**{resultado['beneficio']}**\n\n"
        texto += f"{resultado.get('descricao', '')}\n\n"
        texto += f"**Requisito principal:** {resultado.get('requisito', '')}\n\n"
        texto += f"**Onde solicitar:** {resultado.get('onde_fazer', '')}\n\n"

        if resultado.get("valor_ou_desconto"):
            texto += f"**Valor/Desconto:** {resultado['valor_ou_desconto']}\n\n"

        texto += "Quer ver os documentos necessários?"

        return AgentResponse(
            text=texto,
            suggested_actions=[
                Action.send_message("Ver documentos", f"documentos {programa}", primary=True),
                Action.send_message("Verificar se tenho direito", f"tenho direito {programa}")
            ],
            flow_state="beneficio:orientacao"
        )

    def _show_checklist(self, programa: str) -> AgentResponse:
        """Mostra checklist de documentos."""

        # Mapear para código
        codigo_map = {
            "bolsa_familia": "BOLSA_FAMILIA",
            "bpc": "BPC_LOAS",
            "farmacia_popular": "FARMACIA_POPULAR",
            "tarifa_social": "TARIFA_SOCIAL_ENERGIA",
            "dignidade_menstrual": "DIGNIDADE_MENSTRUAL",
            "cadunico": "CADASTRO_UNICO"
        }
        codigo = codigo_map.get(programa, programa.upper())

        # Situação do cidadão
        situacao = {
            "tem_filhos": self.context.citizen.tem_filhos,
            "idoso": self.context.citizen.idoso,
            "gestante": self.context.citizen.gestante,
            "deficiencia": self.context.citizen.deficiencia
        }

        self.context.add_tool_usage("gerar_checklist")
        resultado = gerar_checklist(codigo, situacao)

        if resultado.get("erro"):
            return AgentResponse(
                text=f"Não encontrei checklist para '{programa}'.",
                flow_state="beneficio:orientacao"
            )

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

        # Usar texto formatado da tool
        texto = resultado.get("checklist_texto", "")

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
                Action.send_message("Outros programas", "listar programas")
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
            flow_state="beneficio:orientacao"
        )

    # =========================================================================
    # Métodos Auxiliares
    # =========================================================================

    def _extract_cpf(self, text: str) -> Optional[str]:
        """Extrai CPF do texto."""
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', text)
        if len(numeros) == 11:
            return numeros

        # Padrão XXX.XXX.XXX-XX
        match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', text)
        if match:
            return re.sub(r'\D', '', match.group())

        return None

    def _extract_programa(self, text: str) -> Optional[str]:
        """Extrai programa mencionado no texto."""

        text_lower = text.lower()

        # Mapeamento de keywords para programas
        keywords = {
            "bolsa_familia": ["bolsa família", "bolsa familia", "bf"],
            "bpc": ["bpc", "loas", "benefício de prestação", "beneficio de prestacao"],
            "farmacia_popular": ["farmácia popular", "farmacia popular", "remédio grátis"],
            "tarifa_social": ["tarifa social", "desconto luz", "tsee", "energia"],
            "dignidade_menstrual": ["dignidade menstrual", "absorvente"],
            "cadunico": ["cadunico", "cadúnico", "cadastro único", "cadastro unico"]
        }

        for programa, kws in keywords.items():
            if any(kw in text_lower for kw in kws):
                return programa

        return None

    def _wants_list_benefits(self, message: str) -> bool:
        """Verifica se quer listar benefícios."""
        keywords = ["listar", "quais programas", "quais benefícios", "ver programas",
                    "todos", "disponíveis", "disponiveis"]
        return any(kw in message.lower() for kw in keywords)

    def _is_cancel_command(self, message: str) -> bool:
        """Verifica se é comando de cancelamento."""
        return any(word in message.lower() for word in ["cancelar", "sair", "voltar"])

    def _handle_cancel(self) -> AgentResponse:
        """Cancela o fluxo atual."""

        self.flow = BeneficioFlowData()
        self.context.set_beneficio_flow(self.flow)
        self.context.end_flow()

        return AgentResponse(
            text="Tudo bem! Posso ajudar com outra coisa?",
            suggested_actions=[
                Action.send_message("Consultar benefícios", "consultar benefícios"),
                Action.send_message("Pedir remédios", "quero pedir remédios")
            ],
            flow_state=None
        )

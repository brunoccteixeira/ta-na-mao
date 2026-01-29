"""
Sub-agente especializado no fluxo de Farmácia Popular.

Gerencia o workflow completo de pedido de medicamentos:
1. Receber receita (foto ou texto)
2. Processar e validar medicamentos
3. Buscar farmácias próximas
4. Coletar dados do cidadão
5. Enviar pedido via WhatsApp
6. Acompanhar status

Usa máquina de estados para manter contexto entre mensagens.
"""

import re
import logging
from typing import Optional

from ..context import (
    ConversationContext,
    FarmaciaFlowData,
    FarmaciaState
)
from ..response_types import (
    AgentResponse,
    UIComponent,
    Action,
    MedicationItem,
    MedicationListData,
    PharmacyCardData,
    OrderStatusData,
    OrderStep,
    AlertData
)
from ..tools.processar_receita import processar_receita
from ..tools.buscar_farmacia import buscar_farmacia
from ..tools.buscar_cep import buscar_cep
from ..tools.preparar_pedido import preparar_pedido, consultar_pedido
from ..tools.validar_cpf import validar_cpf

logger = logging.getLogger(__name__)


class FarmaciaSubAgent:
    """
    Sub-agente para fluxo de Farmácia Popular.

    Implementa máquina de estados para guiar o cidadão através do processo
    de pedido de medicamentos, do processamento da receita até a retirada.
    """

    def __init__(self, context: ConversationContext):
        """
        Inicializa o sub-agente com contexto compartilhado.

        Args:
            context: Contexto da conversa (compartilhado com orquestrador)
        """
        self.context = context
        self.flow = context.get_farmacia_flow()

    async def process(self, message: str, image_base64: Optional[str] = None) -> AgentResponse:
        """
        Processa mensagem do usuário no fluxo de farmácia.

        Args:
            message: Texto enviado pelo usuário
            image_base64: Imagem anexada (receita médica)

        Returns:
            AgentResponse estruturado com texto, componentes UI e ações
        """
        state = self.flow.state
        logger.info(f"FarmaciaAgent processando: state={state}, message={message[:50]}...")

        # Verificar comandos de escape
        if self._is_cancel_command(message):
            return self._handle_cancel()

        if self._is_status_query(message):
            return await self._handle_status_query(message)

        # Dispatch por estado
        handlers = {
            FarmaciaState.INICIO: self._handle_inicio,
            FarmaciaState.RECEITA: self._handle_receita,
            FarmaciaState.MEDICAMENTOS: self._handle_medicamentos,
            FarmaciaState.LOCALIZACAO: self._handle_localizacao,
            FarmaciaState.FARMACIA: self._handle_farmacia,
            FarmaciaState.DADOS_CIDADAO: self._handle_dados_cidadao,
            FarmaciaState.CONFIRMACAO: self._handle_confirmacao,
            FarmaciaState.PEDIDO_ENVIADO: self._handle_pedido_enviado,
        }

        handler = handlers.get(state, self._handle_inicio)
        response = await handler(message, image_base64)

        # Salvar estado atualizado
        self.context.set_farmacia_flow(self.flow)

        return response

    # =========================================================================
    # Handlers por Estado
    # =========================================================================

    async def _handle_inicio(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado inicial: pede receita ou processa se já enviou."""

        # Se já mandou imagem ou texto de medicamentos
        if image_base64:
            return await self._process_prescription(image_base64=image_base64)

        if self._looks_like_medication_text(message):
            return await self._process_prescription(texto=message)

        # Pede a receita
        self.flow.state = FarmaciaState.RECEITA
        return AgentResponse(
            text="Pra pedir seus remédios, preciso ver a RECEITA MÉDICA.\n\n"
                 "Pode mandar de duas formas:\n"
                 "- Tirar uma FOTO da receita\n"
                 "- Ou DIGITAR o nome dos remédios",
            ui_components=[],
            suggested_actions=[
                Action.open_camera("Tirar foto da receita"),
                Action.send_message("Digitar remédios", "quero digitar", primary=False)
            ],
            flow_state="farmacia:receita"
        )

    async def _handle_receita(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado RECEITA: aguarda foto ou texto de medicamentos."""

        if image_base64:
            return await self._process_prescription(image_base64=image_base64)

        if self._looks_like_medication_text(message):
            return await self._process_prescription(texto=message)

        # Se digitou algo que não parece medicamento
        if "digitar" in message.lower() or "escrever" in message.lower():
            return AgentResponse(
                text="Beleza! Digita o nome dos remédios.\n\n"
                     "Exemplo: Losartana 50mg, Metformina 850mg",
                suggested_actions=[],
                flow_state="farmacia:receita"
            )

        return AgentResponse(
            text="Não entendi. Manda a foto da receita ou digita o nome dos remédios.\n\n"
                 "Exemplo: Losartana 50mg, Metformina 850mg",
            suggested_actions=[
                Action.open_camera("Tirar foto"),
            ],
            flow_state="farmacia:receita"
        )

    async def _handle_medicamentos(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado MEDICAMENTOS: confirma lista de medicamentos."""

        message_lower = message.lower()

        # Confirmou os medicamentos
        if any(word in message_lower for word in ["sim", "certo", "ok", "isso", "confirmo", "tá certo"]):
            # Verificar se já tem localização
            if self.context.citizen.cep or self.context.citizen.ibge_code:
                return await self._search_pharmacies()

            # Pedir localização
            self.flow.state = FarmaciaState.LOCALIZACAO
            return AgentResponse(
                text="Perfeito! Agora preciso saber onde você está.\n\n"
                     "Me passa seu CEP pra eu achar as farmácias mais perto de você.",
                suggested_actions=[
                    Action.send_message("Não sei meu CEP", "não sei o cep")
                ],
                flow_state="farmacia:localizacao"
            )

        # Quer corrigir
        if any(word in message_lower for word in ["não", "errado", "corrigir", "mudar", "falta"]):
            self.flow.state = FarmaciaState.RECEITA
            self.flow.medicamentos = []
            return AgentResponse(
                text="Tudo bem! Manda de novo a receita ou digita os remédios corretos.",
                suggested_actions=[
                    Action.open_camera("Nova foto"),
                    Action.send_message("Digitar", "quero digitar")
                ],
                flow_state="farmacia:receita"
            )

        # Não entendeu
        return AgentResponse(
            text="Os remédios estão certos? Responde SIM pra continuar ou NÃO pra corrigir.",
            suggested_actions=[
                Action.send_message("Sim, estão certos", "sim", primary=True),
                Action.send_message("Não, corrigir", "corrigir")
            ],
            flow_state="farmacia:medicamentos"
        )

    async def _handle_localizacao(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado LOCALIZACAO: coleta CEP do cidadão."""

        # Extrair CEP do texto
        cep = self._extract_cep(message)

        if cep:
            # Buscar endereço
            resultado = buscar_cep(cep)

            if resultado.get("encontrado"):
                # Atualizar contexto
                self.context.citizen.update_from_cep_result(resultado)

                # Buscar farmácias
                return await self._search_pharmacies()

            return AgentResponse(
                text=f"Não encontrei o CEP {cep}. Confere se digitou certo?\n\n"
                     "Pode digitar só os números: 01310100",
                flow_state="farmacia:localizacao"
            )

        # Não sabe o CEP
        if "não sei" in message.lower() or "nao sei" in message.lower():
            return AgentResponse(
                text="Sem problema! Me fala qual a sua CIDADE e BAIRRO?\n\n"
                     "Exemplo: Vila Mariana, São Paulo",
                flow_state="farmacia:localizacao"
            )

        # Pode ser cidade/bairro
        if len(message) > 3 and not message.isdigit():
            # Por enquanto, pede CEP novamente (futuramente pode buscar por cidade)
            return AgentResponse(
                text="Não consegui identificar a localização.\n\n"
                     "Por favor, me passa o CEP (só os números).\n"
                     "Exemplo: 01310100",
                flow_state="farmacia:localizacao"
            )

        return AgentResponse(
            text="Digita seu CEP pra eu achar as farmácias perto de você.\n"
                 "Só os números: 01310100",
            flow_state="farmacia:localizacao"
        )

    async def _handle_farmacia(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado FARMACIA: cidadão escolhe qual farmácia."""

        farmacias = self.flow.farmacias_encontradas

        # Tentar extrair número da escolha
        numero = self._extract_number(message)

        if numero and 1 <= numero <= len(farmacias):
            farmacia_escolhida = farmacias[numero - 1]
            self.flow.farmacia_selecionada = farmacia_escolhida

            # Verificar se já tem dados do cidadão
            if self._has_citizen_data():
                self.flow.state = FarmaciaState.CONFIRMACAO
                return self._build_confirmation_response()

            # Coletar dados
            self.flow.state = FarmaciaState.DADOS_CIDADAO
            return self._ask_citizen_data()

        # Escolha inválida
        opcoes = "\n".join([f"{i+1}. {f['nome']}" for i, f in enumerate(farmacias)])
        return AgentResponse(
            text=f"Não entendi. Escolhe o número da farmácia:\n\n{opcoes}",
            suggested_actions=[
                Action.send_message(f"{i+1}", str(i+1))
                for i in range(min(3, len(farmacias)))
            ],
            flow_state="farmacia:farmacia"
        )

    async def _handle_dados_cidadao(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado DADOS_CIDADAO: coleta nome, CPF, telefone."""

        # Tentar extrair dados do texto
        cpf = self._extract_cpf(message)
        telefone = self._extract_phone(message)
        nome = self._extract_name(message)

        # Atualizar o que encontrou
        if cpf:
            resultado = validar_cpf(cpf)
            if resultado.get("valido"):
                self.context.citizen.cpf = resultado.get("cpf_numerico")
                self.context.citizen.cpf_masked = resultado.get("cpf_formatado")

        if telefone:
            self.context.citizen.telefone = telefone
            self.context.citizen.whatsapp = telefone

        if nome:
            self.context.citizen.nome = nome

        # Verificar o que falta
        if self._has_citizen_data():
            self.flow.state = FarmaciaState.CONFIRMACAO
            return self._build_confirmation_response()

        # Pedir o que falta
        return self._ask_missing_data()

    async def _handle_confirmacao(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado CONFIRMACAO: confirma pedido antes de enviar."""

        message_lower = message.lower()

        # Confirmou
        if any(word in message_lower for word in ["sim", "confirmo", "enviar", "manda", "ok"]):
            return await self._submit_order()

        # Cancelou
        if any(word in message_lower for word in ["não", "cancelar", "voltar"]):
            return self._handle_cancel()

        # Quer corrigir algo
        if any(word in message_lower for word in ["corrigir", "mudar", "alterar"]):
            self.flow.state = FarmaciaState.DADOS_CIDADAO
            return AgentResponse(
                text="O que você quer corrigir?\n\n"
                     "Me manda os dados atualizados.",
                flow_state="farmacia:dados_cidadao"
            )

        return AgentResponse(
            text="Confirma o envio do pedido?",
            suggested_actions=[
                Action.send_message("Sim, enviar!", "confirmo", primary=True),
                Action.send_message("Cancelar", "cancelar")
            ],
            flow_state="farmacia:confirmacao"
        )

    async def _handle_pedido_enviado(
        self,
        message: str,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """Estado PEDIDO_ENVIADO: pedido foi criado, acompanha status."""

        # Consulta status
        if self.flow.pedido_numero:
            return await self._check_order_status()

        # Permite fazer novo pedido
        if any(word in message.lower() for word in ["novo", "outro", "mais"]):
            self.flow = FarmaciaFlowData()
            self.flow.state = FarmaciaState.INICIO
            return await self._handle_inicio(message, image_base64)

        return AgentResponse(
            text="Seu pedido já foi enviado!\n\n"
                 "Quer ver o status ou fazer outro pedido?",
            suggested_actions=[
                Action.send_message("Ver status", f"status {self.flow.pedido_numero}"),
                Action.send_message("Novo pedido", "novo pedido")
            ],
            flow_state="farmacia:pedido_enviado"
        )

    # =========================================================================
    # Métodos Auxiliares
    # =========================================================================

    async def _process_prescription(
        self,
        image_base64: Optional[str] = None,
        texto: Optional[str] = None
    ) -> AgentResponse:
        """Processa receita e mostra medicamentos encontrados."""

        self.context.add_tool_usage("processar_receita")

        resultado = processar_receita(
            imagem_base64=image_base64,
            texto=texto
        )

        if not resultado.get("sucesso"):
            return AgentResponse(
                text=f"Não consegui ler a receita: {resultado.get('erro', 'erro desconhecido')}\n\n"
                     "Tenta de novo ou digita o nome dos remédios.",
                ui_components=[
                    UIComponent.alert(AlertData(
                        type="warning",
                        title="Não consegui ler",
                        message=resultado.get('erro', 'Tente novamente'),
                        dismissable=True
                    ))
                ],
                suggested_actions=[
                    Action.open_camera("Nova foto"),
                    Action.send_message("Digitar", "quero digitar")
                ],
                flow_state="farmacia:receita"
            )

        medicamentos = resultado.get("medicamentos", [])
        if not medicamentos:
            return AgentResponse(
                text="Não encontrei medicamentos. Digita o nome dos remédios.\n\n"
                     "Exemplo: Losartana 50mg, Metformina 850mg",
                flow_state="farmacia:receita"
            )

        # Salvar no flow
        self.flow.medicamentos = medicamentos
        self.flow.state = FarmaciaState.MEDICAMENTOS

        # Montar lista de medicamentos
        med_items = [
            MedicationItem(
                name=m.get("nome_oficial", m.get("nome")),
                dosage=m.get("dosagem"),
                quantity=m.get("quantidade"),
                free=m.get("gratuito", False)
            )
            for m in medicamentos
        ]

        todos_gratuitos = all(m.free for m in med_items)

        # Resposta
        texto_base = f"Encontrei {len(medicamentos)} remédio(s):\n\n"
        for m in med_items:
            status = "GRATUITO" if m.free else "com desconto"
            texto_base += f"- {m.name}"
            if m.dosage:
                texto_base += f" {m.dosage}"
            texto_base += f" ({status})\n"

        if todos_gratuitos:
            texto_base += "\nTODOS são GRATUITOS pelo Farmácia Popular!"
        else:
            texto_base += "\nAlguns têm desconto de até 90%."

        texto_base += "\n\nEstá certo?"

        return AgentResponse(
            text=texto_base,
            ui_components=[
                UIComponent.medication_list(MedicationListData(
                    medications=med_items,
                    all_free=todos_gratuitos,
                    needs_prescription=True
                ))
            ],
            suggested_actions=[
                Action.send_message("Sim, está certo", "sim", primary=True),
                Action.send_message("Não, corrigir", "corrigir")
            ],
            flow_state="farmacia:medicamentos"
        )

    async def _search_pharmacies(self) -> AgentResponse:
        """Busca farmácias e apresenta opções."""

        self.context.add_tool_usage("buscar_farmacia")

        resultado = buscar_farmacia(
            cep=self.context.citizen.cep,
            ibge_code=self.context.citizen.ibge_code,
            programa="FARMACIA_POPULAR",
            limite=5
        )

        farmacias = resultado.get("farmacias", [])

        if not farmacias:
            # Sem farmácias específicas, mostra redes nacionais
            redes = resultado.get("redes_nacionais", [])
            texto = "Não encontrei farmácias específicas na sua região.\n\n"
            texto += "Mas você pode ir em qualquer uma dessas redes:\n"
            texto += "\n".join([f"- {r}" for r in redes])
            texto += "\n\nTodas participam do Farmácia Popular!"

            return AgentResponse(
                text=texto,
                ui_components=[
                    UIComponent.alert(AlertData(
                        type="info",
                        title="Redes credenciadas",
                        message="Drogasil, Droga Raia, Pague Menos participam",
                        dismissable=True
                    ))
                ],
                flow_state="farmacia:farmacia"
            )

        # Salvar farmácias encontradas
        self.flow.farmacias_encontradas = farmacias
        self.flow.state = FarmaciaState.FARMACIA

        # Montar cards
        pharmacy_cards = []
        texto = f"Achei {len(farmacias)} farmácia(s) perto de você:\n\n"

        for i, f in enumerate(farmacias, 1):
            texto += f"{i}. {f['nome']}\n"
            texto += f"   {f['endereco']}\n"
            if f.get("horario"):
                texto += f"   {f['horario']}\n"
            texto += "\n"

            pharmacy_cards.append(UIComponent.pharmacy_card(PharmacyCardData(
                id=f.get("id", str(i)),
                name=f["nome"],
                address=f["endereco"],
                neighborhood=f.get("bairro"),
                city=f.get("cidade"),
                phone=f.get("telefone"),
                whatsapp=f.get("whatsapp"),
                distance=f.get("distancia"),
                hours=f.get("horario"),
                has_whatsapp=bool(f.get("whatsapp")),
                programs=f.get("programas", [])
            )))

        texto += "Qual você escolhe? Me manda o número."

        actions = [
            Action.send_message(f"{i+1}. {farmacias[i]['nome'][:20]}", str(i+1))
            for i in range(min(3, len(farmacias)))
        ]

        return AgentResponse(
            text=texto,
            ui_components=pharmacy_cards,
            suggested_actions=actions,
            flow_state="farmacia:farmacia"
        )

    def _ask_citizen_data(self) -> AgentResponse:
        """Pede dados do cidadão para criar pedido."""

        return AgentResponse(
            text="Agora preciso dos seus dados para criar o pedido:\n\n"
                 "Me manda:\n"
                 "- Seu nome completo\n"
                 "- Seu CPF\n"
                 "- Seu WhatsApp (pra avisar quando estiver pronto)\n\n"
                 "Pode mandar tudo junto!",
            flow_state="farmacia:dados_cidadao"
        )

    def _ask_missing_data(self) -> AgentResponse:
        """Pede dados que ainda faltam."""

        faltando = []
        if not self.context.citizen.nome:
            faltando.append("nome completo")
        if not self.context.citizen.cpf:
            faltando.append("CPF")
        if not self.context.citizen.telefone:
            faltando.append("WhatsApp")

        texto = f"Ainda falta: {', '.join(faltando)}\n\nMe manda?"
        return AgentResponse(
            text=texto,
            flow_state="farmacia:dados_cidadao"
        )

    def _build_confirmation_response(self) -> AgentResponse:
        """Monta resposta de confirmação do pedido."""

        farmacia = self.flow.farmacia_selecionada
        meds = self.flow.medicamentos
        citizen = self.context.citizen

        texto = "CONFIRMA O PEDIDO?\n\n"
        texto += f"Nome: {citizen.nome}\n"
        texto += f"CPF: {citizen.cpf_masked or citizen.cpf}\n"
        texto += f"WhatsApp: {citizen.telefone}\n\n"
        texto += f"Farmácia: {farmacia['nome']}\n"
        texto += f"Endereço: {farmacia['endereco']}\n\n"
        texto += "Remédios:\n"
        for m in meds:
            texto += f"- {m.get('nome_oficial', m.get('nome'))}"
            if m.get("dosagem"):
                texto += f" {m['dosagem']}"
            texto += "\n"

        texto += "\n Vou mandar pra farmácia preparar!"

        return AgentResponse(
            text=texto,
            suggested_actions=[
                Action.send_message("ENVIAR PEDIDO", "confirmo", primary=True),
                Action.send_message("Cancelar", "cancelar")
            ],
            flow_state="farmacia:confirmacao"
        )

    async def _submit_order(self) -> AgentResponse:
        """Envia o pedido para a farmácia."""

        self.context.add_tool_usage("preparar_pedido")

        farmacia = self.flow.farmacia_selecionada
        citizen = self.context.citizen

        resultado = preparar_pedido(
            cpf=citizen.cpf,
            nome=citizen.nome,
            telefone=citizen.telefone,
            medicamentos=self.flow.medicamentos,
            farmacia_id=farmacia.get("id", farmacia["nome"]),
            ibge_code=citizen.ibge_code,
            receita_url=self.flow.receita_url
        )

        if not resultado.get("sucesso"):
            return AgentResponse(
                text=f"Ops! Não consegui enviar: {resultado.get('erro')}\n\n"
                     "Quer tentar outra farmácia?",
                ui_components=[
                    UIComponent.alert(AlertData(
                        type="error",
                        title="Erro ao enviar",
                        message=resultado.get('erro', 'Tente novamente'),
                        dismissable=True
                    ))
                ],
                suggested_actions=[
                    Action.send_message("Outra farmácia", "outra farmacia"),
                    Action.send_message("Cancelar", "cancelar")
                ],
                flow_state="farmacia:farmacia"
            )

        # Sucesso!
        self.flow.pedido_numero = resultado.get("pedido_numero")
        self.flow.pedido_id = resultado.get("pedido_id")
        self.flow.state = FarmaciaState.PEDIDO_ENVIADO

        farmacia_info = resultado.get("farmacia", {})

        texto = "PEDIDO ENVIADO!\n\n"
        texto += f"Número: {self.flow.pedido_numero}\n"
        texto += f"Farmácia: {farmacia_info.get('nome')}\n"
        texto += f"Endereço: {farmacia_info.get('endereco')}\n\n"
        texto += "A farmácia vai confirmar em até 30 minutos.\n"
        texto += "Você vai receber uma mensagem quando estiver pronto!\n\n"
        texto += "LEMBRE: leve documento com foto e receita médica."

        # Order status component
        order_component = UIComponent.order_status(OrderStatusData(
            order_number=self.flow.pedido_numero,
            status="pending",
            pharmacy_name=farmacia_info.get("nome", ""),
            pharmacy_address=farmacia_info.get("endereco"),
            estimated_ready="30 minutos",
            steps=[
                OrderStep(label="Pedido enviado", done=True),
                OrderStep(label="Farmácia confirmou", done=False),
                OrderStep(label="Separando", done=False),
                OrderStep(label="Pronto para retirar", done=False),
            ],
            can_cancel=True
        ))

        return AgentResponse(
            text=texto,
            ui_components=[order_component],
            suggested_actions=[
                Action.send_message("Ver status", f"status {self.flow.pedido_numero}"),
                Action.open_map("Ver no mapa", farmacia_info.get("endereco", "")),
            ],
            flow_state="farmacia:pedido_enviado"
        )

    async def _check_order_status(self) -> AgentResponse:
        """Consulta status do pedido."""

        self.context.add_tool_usage("consultar_pedido")

        resultado = consultar_pedido(pedido_numero=self.flow.pedido_numero)

        if not resultado.get("encontrado"):
            return AgentResponse(
                text="Não encontrei esse pedido. Confere o número?",
                flow_state="farmacia:pedido_enviado"
            )

        pedido = resultado.get("pedido", {})
        status_texto = resultado.get("status_texto", "")

        # Mapear status
        status_map = {
            "PENDENTE": "pending",
            "CONFIRMADO": "confirmed",
            "PRONTO": "ready",
            "RETIRADO": "picked_up",
            "CANCELADO": "cancelled"
        }

        steps = [
            OrderStep(label="Pedido enviado", done=True),
            OrderStep(label="Farmácia confirmou", done=pedido["status"] in ["CONFIRMADO", "PRONTO", "RETIRADO"]),
            OrderStep(label="Separando", done=pedido["status"] in ["PRONTO", "RETIRADO"]),
            OrderStep(label="Pronto para retirar", done=pedido["status"] == "RETIRADO"),
        ]

        return AgentResponse(
            text=f"Pedido {pedido['numero']}\n\n{status_texto}",
            ui_components=[
                UIComponent.order_status(OrderStatusData(
                    order_number=pedido["numero"],
                    status=status_map.get(pedido["status"], "pending"),
                    pharmacy_name=pedido.get("farmacia", ""),
                    steps=steps,
                    can_cancel=pedido["status"] in ["PENDENTE", "CONFIRMADO"]
                ))
            ],
            flow_state="farmacia:pedido_enviado"
        )

    async def _handle_status_query(self, message: str) -> AgentResponse:
        """Trata consulta de status de pedido."""

        # Extrair número do pedido
        match = re.search(r'PED-\d+', message.upper())
        if match:
            numero = match.group()
            resultado = consultar_pedido(pedido_numero=numero)
            if resultado.get("encontrado"):
                self.flow.pedido_numero = numero
                return await self._check_order_status()

        # Se tem pedido no flow, mostra esse
        if self.flow.pedido_numero:
            return await self._check_order_status()

        return AgentResponse(
            text="Qual o número do pedido?\n\nExemplo: PED-12345",
            flow_state="farmacia:pedido_enviado"
        )

    def _handle_cancel(self) -> AgentResponse:
        """Cancela o fluxo atual."""

        self.flow = FarmaciaFlowData()
        self.context.set_farmacia_flow(self.flow)
        self.context.end_flow()

        return AgentResponse(
            text="Tudo bem, cancelei.\n\nPosso ajudar com outra coisa?",
            suggested_actions=[
                Action.send_message("Pedir remédios", "quero pedir remédios"),
                Action.send_message("Ver benefícios", "quais benefícios tenho")
            ],
            flow_state=None
        )

    # =========================================================================
    # Extratores
    # =========================================================================

    def _extract_cep(self, text: str) -> Optional[str]:
        """Extrai CEP do texto."""
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', text)
        if len(numeros) == 8:
            return numeros
        # Tenta encontrar padrão XXXXX-XXX
        match = re.search(r'\d{5}-?\d{3}', text)
        if match:
            return re.sub(r'\D', '', match.group())
        return None

    def _extract_cpf(self, text: str) -> Optional[str]:
        """Extrai CPF do texto."""
        numeros = re.sub(r'\D', '', text)
        if len(numeros) == 11:
            return numeros
        # Padrão XXX.XXX.XXX-XX
        match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', text)
        if match:
            return re.sub(r'\D', '', match.group())
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extrai telefone do texto."""
        numeros = re.sub(r'\D', '', text)
        # Celular com DDD: 11 dígitos
        if len(numeros) in [10, 11]:
            return numeros
        # Buscar padrão
        match = re.search(r'\(?\d{2}\)?\s*9?\d{4}-?\d{4}', text)
        if match:
            return re.sub(r'\D', '', match.group())
        return None

    def _extract_name(self, text: str) -> Optional[str]:
        """Extrai nome do texto (heurística simples)."""
        # Remove CPF e telefone
        clean = re.sub(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', '', text)
        clean = re.sub(r'\(?\d{2}\)?\s*9?\d{4}-?\d{4}', '', clean)
        clean = re.sub(r'\d+', '', clean)
        clean = clean.strip(' ,.-')

        # Se sobrou algo com pelo menos 2 palavras
        palavras = clean.split()
        if len(palavras) >= 2:
            return ' '.join(palavras)

        return None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extrai número de escolha do texto."""
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())
        return None

    def _looks_like_medication_text(self, text: str) -> bool:
        """Verifica se texto parece lista de medicamentos."""
        # Palavras comuns em medicamentos
        keywords = ["mg", "mcg", "comprimido", "capsul", "losartan", "metformin",
                    "atenolol", "omeprazol", "sinvastatina", "hidroclorotiazida"]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    def _has_citizen_data(self) -> bool:
        """Verifica se tem dados suficientes do cidadão."""
        c = self.context.citizen
        return bool(c.nome and c.cpf and c.telefone)

    def _is_cancel_command(self, message: str) -> bool:
        """Verifica se é comando de cancelamento."""
        return any(word in message.lower() for word in ["cancelar", "sair", "parar", "desistir"])

    def _is_status_query(self, message: str) -> bool:
        """Verifica se é consulta de status."""
        return any(word in message.lower() for word in ["status", "meu pedido", "como está", "ped-"])

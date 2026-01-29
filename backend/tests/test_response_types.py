"""
Testes para os tipos de resposta do agente.

Testa AgentResponse, UIComponent, Action, etc.
"""

import pytest


class TestUIComponentType:
    """Testes para UIComponentType enum."""

    def test_component_types_exist(self):
        """Deve ter todos os tipos de componente."""
        from app.agent.response_types import UIComponentType

        assert UIComponentType.PHARMACY_CARD is not None
        assert UIComponentType.MEDICATION_LIST is not None
        assert UIComponentType.CHECKLIST is not None
        assert UIComponentType.BENEFIT_CARD is not None
        assert UIComponentType.CRAS_CARD is not None


class TestActionType:
    """Testes para ActionType enum."""

    def test_action_types_exist(self):
        """Deve ter todos os tipos de acao."""
        from app.agent.response_types import ActionType

        assert ActionType.SEND_MESSAGE is not None
        assert ActionType.CAMERA is not None
        assert ActionType.CALL_PHONE is not None
        assert ActionType.OPEN_URL is not None
        assert ActionType.OPEN_WHATSAPP is not None


class TestUIComponent:
    """Testes para UIComponent."""

    def test_create_medication_list_component(self):
        """Deve criar componente de lista de medicamentos."""
        from app.agent.response_types import (
            UIComponent, UIComponentType, MedicationListData, MedicationItem
        )

        data = MedicationListData(
            medications=[
                MedicationItem(name="Losartana", dosage="50mg", free=True)
            ],
            all_free=True
        )
        component = UIComponent.medication_list(data)

        assert component.type == UIComponentType.MEDICATION_LIST
        assert component.data["all_free"] is True

    def test_create_checklist_component(self):
        """Deve criar componente de checklist."""
        from app.agent.response_types import (
            UIComponent, UIComponentType, ChecklistData, ChecklistItem
        )

        data = ChecklistData(
            title="Documentos",
            items=[
                ChecklistItem(text="RG", required=True),
                ChecklistItem(text="CPF", required=True)
            ]
        )
        component = UIComponent.checklist(data)

        assert component.type == UIComponentType.CHECKLIST
        assert component.data["title"] == "Documentos"

    def test_create_alert_component(self):
        """Deve criar componente de alerta."""
        from app.agent.response_types import UIComponent, UIComponentType, AlertData

        data = AlertData(
            type="warning",
            title="Atencao",
            message="Verifique os documentos"
        )
        component = UIComponent.alert(data)

        assert component.type == UIComponentType.ALERT
        assert component.data["type"] == "warning"


class TestAction:
    """Testes para Action."""

    def test_create_send_message_action(self):
        """Deve criar acao de enviar mensagem."""
        from app.agent.response_types import Action, ActionType

        action = Action.send_message("Confirmar", "sim")

        assert action.label == "Confirmar"
        assert action.action_type == ActionType.SEND_MESSAGE
        assert action.payload == "sim"

    def test_create_camera_action(self):
        """Deve criar acao de camera."""
        from app.agent.response_types import Action, ActionType

        action = Action.open_camera()

        assert action.label == "Tirar foto"
        assert action.action_type == ActionType.CAMERA
        assert action.icon == "camera"

    def test_create_call_phone_action(self):
        """Deve criar acao de ligar."""
        from app.agent.response_types import Action, ActionType

        action = Action.call_phone("Ligar", "11999999999")

        assert action.action_type == ActionType.CALL_PHONE
        assert action.payload == "11999999999"

    def test_create_whatsapp_action(self):
        """Deve criar acao de WhatsApp."""
        from app.agent.response_types import Action, ActionType

        action = Action.open_whatsapp("WhatsApp", "11999999999", "Ola")

        assert action.action_type == ActionType.OPEN_WHATSAPP
        assert "11999999999" in action.payload

    def test_create_map_action(self):
        """Deve criar acao de mapa."""
        from app.agent.response_types import Action, ActionType

        action = Action.open_map("Ver no mapa", "Av. Paulista, 1000")

        assert action.action_type == ActionType.OPEN_MAP
        assert action.payload == "Av. Paulista, 1000"


class TestAgentResponse:
    """Testes para AgentResponse."""

    def test_create_simple_response(self):
        """Deve criar resposta simples."""
        from app.agent.response_types import AgentResponse

        response = AgentResponse(text="Ola!")

        assert response.text == "Ola!"
        assert response.ui_components == []
        assert response.suggested_actions == []

    def test_create_response_with_components(self):
        """Deve criar resposta com componentes."""
        from app.agent.response_types import (
            AgentResponse, UIComponent, UIComponentType, AlertData
        )

        alert = AlertData(type="info", title="Info", message="Test")
        component = UIComponent.alert(alert)

        response = AgentResponse(
            text="Resposta",
            ui_components=[component]
        )

        assert response.text == "Resposta"
        assert len(response.ui_components) == 1
        assert response.ui_components[0].type == UIComponentType.ALERT

    def test_create_response_with_actions(self):
        """Deve criar resposta com acoes sugeridas."""
        from app.agent.response_types import AgentResponse, Action

        action = Action.send_message("Sim", "sim", primary=True)

        response = AgentResponse(
            text="Confirmar?",
            suggested_actions=[action]
        )

        assert len(response.suggested_actions) == 1
        assert response.suggested_actions[0].label == "Sim"

    def test_create_response_with_flow_state(self):
        """Deve criar resposta com estado do fluxo."""
        from app.agent.response_types import AgentResponse

        response = AgentResponse(
            text="Resposta",
            flow_state="farmacia:medicamentos"
        )

        assert response.flow_state == "farmacia:medicamentos"

    def test_with_component_fluent_interface(self):
        """Deve suportar fluent interface para adicionar componente."""
        from app.agent.response_types import (
            AgentResponse, UIComponent, AlertData
        )

        alert = AlertData(type="info", title="Info", message="Test")
        component = UIComponent.alert(alert)

        response = AgentResponse(text="Teste").with_component(component)

        assert len(response.ui_components) == 1

    def test_with_action_fluent_interface(self):
        """Deve suportar fluent interface para adicionar acao."""
        from app.agent.response_types import AgentResponse, Action

        action = Action.send_message("Sim", "sim")

        response = AgentResponse(text="Teste").with_action(action)

        assert len(response.suggested_actions) == 1


class TestMedicationItem:
    """Testes para MedicationItem."""

    def test_create_medication_item(self):
        """Deve criar item de medicamento."""
        from app.agent.response_types import MedicationItem

        item = MedicationItem(
            name="Losartana",
            dosage="50mg",
            quantity=30,
            free=True
        )

        assert item.name == "Losartana"
        assert item.dosage == "50mg"
        assert item.quantity == 30
        assert item.free is True


class TestChecklistItem:
    """Testes para ChecklistItem."""

    def test_create_checklist_item(self):
        """Deve criar item de checklist."""
        from app.agent.response_types import ChecklistItem

        item = ChecklistItem(
            text="RG ou CNH",
            required=True,
            checked=False,
            note="Original e copia"
        )

        assert item.text == "RG ou CNH"
        assert item.required is True
        assert item.checked is False
        assert item.note == "Original e copia"

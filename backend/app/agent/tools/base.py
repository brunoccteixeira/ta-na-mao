"""
Tipos base para tools do agente.

Define ToolResult como estrutura padrão de retorno para todas as tools,
permitindo tratamento uniforme e hints de renderização.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class UIHint(str, Enum):
    """Dicas de renderização para o frontend."""

    # Validação
    VALIDATION_SUCCESS = "validation_success"
    VALIDATION_ERROR = "validation_error"

    # Listas
    MEDICATION_LIST = "medication_list"
    PHARMACY_LIST = "pharmacy_list"
    CRAS_LIST = "cras_list"
    BENEFIT_LIST = "benefit_list"

    # Cards
    PHARMACY_CARD = "pharmacy_card"
    CRAS_CARD = "cras_card"
    BENEFIT_CARD = "benefit_card"
    ORDER_CARD = "order_card"

    # Status
    ORDER_STATUS = "order_status"
    ELIGIBILITY_STATUS = "eligibility_status"

    # Documentos
    CHECKLIST = "checklist"

    # Mapas
    MAP_LOCATION = "map_location"
    MAP_MULTIPLE = "map_multiple"

    # Genéricos
    TEXT = "text"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ToolResult(BaseModel):
    """
    Resultado padronizado de uma tool.

    Todas as tools devem retornar esta estrutura para tratamento uniforme
    pelo orquestrador e sub-agentes.
    """

    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dados retornados pela tool"
    )
    error: Optional[str] = Field(
        None,
        description="Mensagem de erro se success=False"
    )
    error_code: Optional[str] = Field(
        None,
        description="Código de erro para tratamento programático"
    )
    ui_hint: Optional[UIHint] = Field(
        None,
        description="Dica de renderização para o frontend"
    )
    context_updates: Dict[str, Any] = Field(
        default_factory=dict,
        description="Atualizações para o contexto da conversa"
    )

    @classmethod
    def ok(
        cls,
        data: Dict[str, Any],
        ui_hint: Optional[UIHint] = None,
        context_updates: Optional[Dict[str, Any]] = None
    ) -> "ToolResult":
        """Cria resultado de sucesso."""
        return cls(
            success=True,
            data=data,
            ui_hint=ui_hint,
            context_updates=context_updates or {}
        )

    @classmethod
    def fail(
        cls,
        error: str,
        error_code: Optional[str] = None,
        ui_hint: UIHint = UIHint.ERROR
    ) -> "ToolResult":
        """Cria resultado de falha."""
        return cls(
            success=False,
            data={},
            error=error,
            error_code=error_code,
            ui_hint=ui_hint
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Acessa dado pelo nome."""
        return self.data.get(key, default)


# =============================================================================
# Tipos específicos de resultado
# =============================================================================

class CPFValidationResult(ToolResult):
    """Resultado de validação de CPF."""

    @classmethod
    def valid(cls, cpf_formatado: str, cpf_numerico: str) -> "CPFValidationResult":
        return cls(
            success=True,
            data={
                "valido": True,
                "cpf_formatado": cpf_formatado,
                "cpf_numerico": cpf_numerico
            },
            ui_hint=UIHint.VALIDATION_SUCCESS,
            context_updates={"cpf": cpf_numerico}
        )

    @classmethod
    def invalid(cls, mensagem: str) -> "CPFValidationResult":
        return cls(
            success=True,  # A operação funcionou, o CPF é que é inválido
            data={"valido": False, "mensagem": mensagem},
            ui_hint=UIHint.VALIDATION_ERROR
        )


class CEPResult(ToolResult):
    """Resultado de busca de CEP."""

    @classmethod
    def found(
        cls,
        cep: str,
        logradouro: str,
        bairro: str,
        cidade: str,
        uf: str,
        ibge: str
    ) -> "CEPResult":
        return cls(
            success=True,
            data={
                "cep": cep,
                "logradouro": logradouro,
                "bairro": bairro,
                "localidade": cidade,
                "uf": uf,
                "ibge": ibge
            },
            ui_hint=UIHint.VALIDATION_SUCCESS,
            context_updates={
                "cep": cep,
                "ibge_code": ibge,
                "cidade": cidade,
                "uf": uf
            }
        )

    @classmethod
    def not_found(cls, cep: str) -> "CEPResult":
        return cls(
            success=False,
            data={},
            error=f"CEP {cep} não encontrado",
            error_code="CEP_NOT_FOUND",
            ui_hint=UIHint.VALIDATION_ERROR
        )


class PharmacySearchResult(ToolResult):
    """Resultado de busca de farmácias."""

    @classmethod
    def found(
        cls,
        farmacias: List[Dict[str, Any]],
        total: int
    ) -> "PharmacySearchResult":
        return cls(
            success=True,
            data={
                "farmacias": farmacias,
                "total": total,
                "encontradas": len(farmacias)
            },
            ui_hint=UIHint.PHARMACY_LIST
        )

    @classmethod
    def none_found(cls, cep: str) -> "PharmacySearchResult":
        return cls(
            success=True,
            data={"farmacias": [], "total": 0, "encontradas": 0},
            error=f"Nenhuma farmácia credenciada encontrada perto do CEP {cep}",
            ui_hint=UIHint.WARNING
        )


class CRASSearchResult(ToolResult):
    """Resultado de busca de CRAS."""

    @classmethod
    def found(
        cls,
        cras_list: List[Dict[str, Any]],
        total: int
    ) -> "CRASSearchResult":
        return cls(
            success=True,
            data={
                "cras": cras_list,
                "total": total,
                "encontrados": len(cras_list)
            },
            ui_hint=UIHint.CRAS_LIST
        )


class MedicationProcessResult(ToolResult):
    """Resultado de processamento de receita."""

    @classmethod
    def processed(
        cls,
        medicamentos: List[Dict[str, Any]],
        todos_disponiveis: bool
    ) -> "MedicationProcessResult":
        return cls(
            success=True,
            data={
                "medicamentos": medicamentos,
                "todos_disponiveis": todos_disponiveis,
                "total": len(medicamentos)
            },
            ui_hint=UIHint.MEDICATION_LIST
        )


class OrderResult(ToolResult):
    """Resultado de criação/consulta de pedido."""

    @classmethod
    def created(
        cls,
        pedido_numero: str,
        pedido_id: str,
        farmacia_nome: str,
        status: str = "PENDENTE"
    ) -> "OrderResult":
        return cls(
            success=True,
            data={
                "pedido_numero": pedido_numero,
                "pedido_id": pedido_id,
                "farmacia_nome": farmacia_nome,
                "status": status
            },
            ui_hint=UIHint.ORDER_STATUS,
            context_updates={
                "pedido_numero": pedido_numero,
                "pedido_id": pedido_id
            }
        )


class BenefitQueryResult(ToolResult):
    """Resultado de consulta de benefícios."""

    @classmethod
    def found(
        cls,
        beneficios: Dict[str, Any],
        nome: Optional[str] = None,
        cpf_masked: Optional[str] = None
    ) -> "BenefitQueryResult":
        return cls(
            success=True,
            data={
                "encontrado": True,
                "beneficios": beneficios,
                "nome": nome,
                "cpf_masked": cpf_masked
            },
            ui_hint=UIHint.BENEFIT_LIST,
            context_updates={"beneficios": beneficios}
        )

    @classmethod
    def not_found(cls, cpf_masked: str) -> "BenefitQueryResult":
        return cls(
            success=True,
            data={
                "encontrado": False,
                "cpf_masked": cpf_masked
            },
            ui_hint=UIHint.INFO
        )


class ChecklistResult(ToolResult):
    """Resultado de geração de checklist."""

    @classmethod
    def generated(
        cls,
        programa: str,
        documentos: List[Dict[str, Any]],
        total_obrigatorios: int,
        total_opcionais: int
    ) -> "ChecklistResult":
        return cls(
            success=True,
            data={
                "programa": programa,
                "documentos": documentos,
                "total_obrigatorios": total_obrigatorios,
                "total_opcionais": total_opcionais
            },
            ui_hint=UIHint.CHECKLIST
        )

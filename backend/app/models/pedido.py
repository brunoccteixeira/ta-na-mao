"""Modelo de Pedido para preparacao de medicamentos."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class StatusPedido(str, Enum):
    """Status possiveis de um pedido."""
    PENDENTE = "PENDENTE"           # Aguardando confirmacao da farmacia
    CONFIRMADO = "CONFIRMADO"       # Farmacia confirmou, preparando
    PRONTO = "PRONTO"               # Remedio pronto para retirada
    RETIRADO = "RETIRADO"           # Cidadao retirou
    CANCELADO = "CANCELADO"         # Cancelado por qualquer motivo
    EXPIRADO = "EXPIRADO"           # Nao retirado no prazo


class Pedido(Base):
    """Pedido de medicamento para Farmacia Popular.

    Representa o fluxo:
    1. Cidadao pede remedio via agente
    2. Agente envia WhatsApp para farmacia
    3. Farmacia confirma
    4. Cidadao eh notificado e retira
    """

    __tablename__ = "pedidos"

    id = Column(String(36), primary_key=True)  # UUID
    numero = Column(String(10), unique=True, index=True)  # Numero curto: PED-12345

    # Dados do cidadao
    cpf_cidadao = Column(String(11), nullable=False, index=True)
    nome_cidadao = Column(String(200))
    telefone_cidadao = Column(String(15))  # WhatsApp do cidadao

    # Dados da farmacia
    farmacia_id = Column(String(50), nullable=False)
    farmacia_nome = Column(String(200))
    farmacia_whatsapp = Column(String(15))

    # Medicamentos (JSON array)
    # [{"nome": "Losartana", "dosagem": "50mg", "quantidade": 30}]
    medicamentos = Column(JSONB, nullable=False)

    # Receita (URL da imagem se enviada)
    receita_url = Column(Text)

    # Status
    status = Column(String(20), default=StatusPedido.PENDENTE.value, index=True)

    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmado_em = Column(DateTime)  # Quando farmacia confirmou
    pronto_em = Column(DateTime)      # Quando ficou pronto
    retirado_em = Column(DateTime)    # Quando cidadao retirou

    # Mensagens Twilio (para tracking)
    twilio_sid_farmacia = Column(String(50))   # SID da mensagem enviada para farmacia
    twilio_sid_cidadao = Column(String(50))    # SID da notificacao para cidadao

    # Observacoes
    observacoes = Column(Text)

    def __repr__(self):
        return f"<Pedido {self.numero} - {self.status}>"

    @property
    def medicamentos_texto(self) -> str:
        """Retorna lista de medicamentos como texto."""
        if not self.medicamentos:
            return ""
        linhas = []
        for med in self.medicamentos:
            nome = med.get("nome", "")
            dosagem = med.get("dosagem", "")
            qtd = med.get("quantidade", "")
            linha = f"- {nome}"
            if dosagem:
                linha += f" {dosagem}"
            if qtd:
                linha += f" ({qtd} unidades)"
            linhas.append(linha)
        return "\n".join(linhas)

    @property
    def cpf_mascarado(self) -> str:
        """Retorna CPF com mascara parcial: ***456789**"""
        if not self.cpf_cidadao or len(self.cpf_cidadao) != 11:
            return "***"
        return f"***{self.cpf_cidadao[3:9]}**"

    def atualizar_status(self, novo_status: StatusPedido):
        """Atualiza status e timestamps correspondentes."""
        self.status = novo_status.value
        self.atualizado_em = datetime.utcnow()

        if novo_status == StatusPedido.CONFIRMADO:
            self.confirmado_em = datetime.utcnow()
        elif novo_status == StatusPedido.PRONTO:
            self.pronto_em = datetime.utcnow()
        elif novo_status == StatusPedido.RETIRADO:
            self.retirado_em = datetime.utcnow()

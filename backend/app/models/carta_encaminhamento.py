"""Modelo de Carta de Encaminhamento para CRAS."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class StatusCarta(str, Enum):
    """Status possíveis de uma carta de encaminhamento."""
    ATIVA = "ATIVA"           # Carta válida, pode ser usada
    UTILIZADA = "UTILIZADA"   # Carta já foi validada por um atendente
    EXPIRADA = "EXPIRADA"     # Carta passou da validade (30 dias)
    CANCELADA = "CANCELADA"   # Cancelada pelo cidadão ou sistema


class CartaEncaminhamento(Base):
    """Carta de Encaminhamento para atendimento no CRAS.

    Representa o fluxo:
    1. Cidadão faz triagem no Tá na Mão
    2. Sistema gera carta com dados pré-preenchidos
    3. Cidadão leva ao CRAS (impresso ou celular)
    4. Atendente valida pelo código/QR Code
    5. Atendimento é agilizado
    """

    __tablename__ = "cartas_encaminhamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_validacao = Column(String(20), unique=True, index=True, nullable=False)  # TNM-2026-ABC123

    # Dados do cidadão (hash do CPF para privacidade)
    cpf_hash = Column(String(64), index=True)  # SHA256 do CPF
    cpf_masked = Column(String(15))  # ***456.789-**
    nome = Column(String(200))
    municipio = Column(String(100))
    uf = Column(String(2))

    # Dados da triagem (JSON)
    dados_cidadao = Column(JSONB, nullable=False)
    # {
    #   "renda_familiar": 800.0,
    #   "renda_per_capita": 200.0,
    #   "pessoas_na_casa": 4,
    #   "tem_filhos": True,
    #   "tem_idoso": False,
    #   "tem_pcd": False,
    # }

    # Benefícios solicitados (JSON array)
    beneficios = Column(JSONB, nullable=False)
    # ["BOLSA_FAMILIA", "TSEE", "FARMACIA_POPULAR"]

    # Documentos apresentados (JSON array)
    documentos_checklist = Column(JSONB)
    # [{"nome": "CPF", "apresentado": True}, {"nome": "RG", "apresentado": False}]

    # CRAS sugerido
    cras_nome = Column(String(200))
    cras_endereco = Column(Text)
    cras_telefone = Column(String(20))

    # Status e timestamps
    status = Column(String(20), default=StatusCarta.ATIVA.value, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    validade = Column(DateTime, nullable=False)  # Expira em 30 dias
    utilizado_em = Column(DateTime)  # Quando foi validada pelo atendente

    # Validação (quem validou)
    validado_por = Column(String(100))  # Nome/ID do atendente que validou
    cras_atendimento = Column(String(200))  # CRAS onde foi atendido

    # Conteúdo gerado
    html_content = Column(Text)  # HTML da carta
    pdf_base64 = Column(Text)    # PDF em base64 (pode ser grande)

    def __repr__(self):
        return f"<CartaEncaminhamento {self.codigo_validacao} - {self.status}>"

    @property
    def esta_valida(self) -> bool:
        """Verifica se a carta ainda é válida."""
        if self.status != StatusCarta.ATIVA.value:
            return False
        if self.validade and datetime.utcnow() > self.validade:
            return False
        return True

    @property
    def beneficios_texto(self) -> str:
        """Retorna lista de benefícios como texto."""
        if not self.beneficios:
            return ""
        return ", ".join(self.beneficios)

    def marcar_utilizada(self, atendente: str, cras: str):
        """Marca a carta como utilizada pelo atendente."""
        self.status = StatusCarta.UTILIZADA.value
        self.utilizado_em = datetime.utcnow()
        self.validado_por = atendente
        self.cras_atendimento = cras

    def marcar_expirada(self):
        """Marca a carta como expirada."""
        self.status = StatusCarta.EXPIRADA.value

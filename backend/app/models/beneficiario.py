"""Modelo de Beneficiario para consultas individuais por CPF.

Armazena dados de beneficiarios indexados dos CSVs do Portal da Transparencia.
CPF e armazenado como hash SHA256 para privacidade.
"""

import hashlib
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, DateTime, ForeignKey, Index

from app.database import Base


def hash_cpf(cpf: str) -> str:
    """Gera hash SHA256 do CPF.

    Args:
        cpf: CPF com 11 digitos (sem formatacao)

    Returns:
        Hash SHA256 em hexadecimal (64 caracteres)
    """
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    return hashlib.sha256(cpf_limpo.encode()).hexdigest()


def mask_cpf(cpf: str) -> str:
    """Mascara CPF para exibicao.

    Args:
        cpf: CPF com 11 digitos

    Returns:
        CPF mascarado: ***456.789-**
    """
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    if len(cpf_limpo) != 11:
        return "***"
    return f"***{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-**"


class Beneficiario(Base):
    """Beneficiario de programas sociais.

    Dados indexados dos CSVs do Portal da Transparencia.
    Permite consulta individual por CPF (via hash).
    """

    __tablename__ = "beneficiarios"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacao (CPF hashificado para privacidade)
    cpf_hash = Column(String(64), nullable=False, unique=True)
    cpf_masked = Column(String(14))  # ***456.789-**
    nis = Column(String(11))  # NIS do beneficiario
    nome = Column(String(200))

    # Municipio
    ibge_code = Column(String(7), ForeignKey("municipalities.ibge_code"))
    uf = Column(String(2))

    # Bolsa Familia
    bf_ativo = Column(Boolean, default=False)
    bf_valor = Column(Numeric(10, 2))
    bf_parcela_mes = Column(String(7))  # YYYY-MM
    bf_data_referencia = Column(Date)

    # BPC/LOAS
    bpc_ativo = Column(Boolean, default=False)
    bpc_valor = Column(Numeric(10, 2))
    bpc_tipo = Column(String(20))  # IDOSO, PCD_LEVE, PCD_MODERADA, PCD_GRAVE
    bpc_data_referencia = Column(Date)

    # CadUnico (se disponivel)
    cadunico_ativo = Column(Boolean, default=False)
    cadunico_data_atualizacao = Column(Date)
    cadunico_faixa_renda = Column(String(50))  # EXTREMA_POBREZA, POBREZA, BAIXA_RENDA

    # Metadata
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fonte = Column(String(50))  # PORTAL_TRANSPARENCIA, DATASUS, etc.

    # Indices para busca rapida
    __table_args__ = (
        Index("ix_beneficiarios_cpf_hash", "cpf_hash"),
        Index("ix_beneficiarios_nis", "nis"),
        Index("ix_beneficiarios_ibge", "ibge_code"),
        Index("ix_beneficiarios_bf_ativo", "bf_ativo"),
        Index("ix_beneficiarios_bpc_ativo", "bpc_ativo"),
    )

    def __repr__(self):
        return f"<Beneficiario {self.cpf_masked} - BF:{self.bf_ativo} BPC:{self.bpc_ativo}>"

    @classmethod
    def buscar_por_cpf(cls, db_session, cpf: str) -> Optional["Beneficiario"]:
        """Busca beneficiario por CPF.

        Args:
            db_session: Sessao do SQLAlchemy
            cpf: CPF (com ou sem formatacao)

        Returns:
            Beneficiario ou None
        """
        cpf_hash_busca = hash_cpf(cpf)
        return db_session.query(cls).filter(cls.cpf_hash == cpf_hash_busca).first()

    @classmethod
    def buscar_por_nis(cls, db_session, nis: str) -> Optional["Beneficiario"]:
        """Busca beneficiario por NIS (Numero de Identificacao Social).

        Args:
            db_session: Sessao do SQLAlchemy
            nis: NIS com 11 digitos

        Returns:
            Beneficiario ou None
        """
        nis_limpo = "".join(c for c in nis if c.isdigit())
        if len(nis_limpo) != 11:
            return None
        return db_session.query(cls).filter(cls.nis == nis_limpo).first()

    @classmethod
    def buscar_por_nome_municipio(
        cls,
        db_session,
        nome: str,
        ibge_code: Optional[str] = None,
        uf: Optional[str] = None,
        limite: int = 5
    ) -> list["Beneficiario"]:
        """Busca beneficiarios por nome e municipio (busca fuzzy).

        Usado para identificar cidadaos que nao tem CPF mas sabem o nome.
        Retorna multiplos resultados para confirmacao.

        Args:
            db_session: Sessao do SQLAlchemy
            nome: Nome completo ou parcial do beneficiario
            ibge_code: Codigo IBGE do municipio (opcional)
            uf: UF para filtro (opcional)
            limite: Maximo de resultados

        Returns:
            Lista de beneficiarios que batem com os criterios
        """
        from sqlalchemy import func

        # Normaliza nome para busca
        nome_normalizado = nome.upper().strip()

        # Query base - busca por LIKE no nome
        query = db_session.query(cls).filter(
            func.upper(cls.nome).like(f"%{nome_normalizado}%")
        )

        # Filtra por municipio se informado
        if ibge_code:
            query = query.filter(cls.ibge_code == ibge_code)
        elif uf:
            query = query.filter(cls.uf == uf.upper())

        # Limita resultados e ordena por nome
        return query.order_by(cls.nome).limit(limite).all()

    def to_dict(self) -> dict:
        """Converte para dicionario (para API)."""
        return {
            "cpf_masked": self.cpf_masked,
            "nome": self.nome,
            "uf": self.uf,
            "beneficios": {
                "bolsa_familia": {
                    "ativo": self.bf_ativo,
                    "valor": float(self.bf_valor) if self.bf_valor else None,
                    "parcela_mes": self.bf_parcela_mes,
                    "data_referencia": self.bf_data_referencia.isoformat() if self.bf_data_referencia else None
                } if self.bf_ativo else {"ativo": False},
                "bpc": {
                    "ativo": self.bpc_ativo,
                    "valor": float(self.bpc_valor) if self.bpc_valor else None,
                    "tipo": self.bpc_tipo,
                    "data_referencia": self.bpc_data_referencia.isoformat() if self.bpc_data_referencia else None
                } if self.bpc_ativo else {"ativo": False},
                "cadunico": {
                    "ativo": self.cadunico_ativo,
                    "faixa_renda": self.cadunico_faixa_renda,
                    "ultima_atualizacao": self.cadunico_data_atualizacao.isoformat() if self.cadunico_data_atualizacao else None
                } if self.cadunico_ativo else {"ativo": False}
            },
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None
        }

    def gerar_resumo_texto(self) -> str:
        """Gera resumo em texto amigavel para o agente."""
        partes = []

        if self.bf_ativo and self.bf_valor:
            valor_fmt = f"R$ {self.bf_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            partes.append(f"BOLSA FAMILIA: {valor_fmt}")
            if self.bf_parcela_mes:
                partes.append(f"  Parcela: {self.bf_parcela_mes}")

        if self.bpc_ativo and self.bpc_valor:
            valor_fmt = f"R$ {self.bpc_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tipo = self.bpc_tipo or "BPC"
            partes.append(f"BPC ({tipo}): {valor_fmt}")

        if self.cadunico_ativo:
            faixa = self.cadunico_faixa_renda or "Cadastrado"
            partes.append(f"CADUNICO: {faixa}")
            if self.cadunico_data_atualizacao:
                partes.append(f"  Atualizado: {self.cadunico_data_atualizacao.strftime('%d/%m/%Y')}")

        if not partes:
            return "Nenhum beneficio encontrado para este CPF."

        return "\n".join(partes)

"""Program model for social benefit programs."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Program(Base):
    """Social benefit program model."""

    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    data_source_url = Column(String(500))
    update_frequency = Column(String(50))  # MONTHLY, QUARTERLY, YEARLY
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    beneficiary_data = relationship("BeneficiaryData", back_populates="program")

    def __repr__(self):
        return f"<Program {self.code} - {self.name}>"


# Program codes constants
class ProgramCode:
    """Program code constants."""

    BOLSA_FAMILIA = "BOLSA_FAMILIA"
    BPC = "BPC"
    TSEE = "TSEE"
    FARMACIA_POPULAR = "FARMACIA_POPULAR"
    DIGNIDADE_MENSTRUAL = "DIGNIDADE_MENSTRUAL"
    PIS_PASEP = "PIS_PASEP"
    CADUNICO = "CADUNICO"
    # New programs
    AUXILIO_GAS = "AUXILIO_GAS"
    SEGURO_DEFESO = "SEGURO_DEFESO"
    AUXILIO_INCLUSAO = "AUXILIO_INCLUSAO"
    # Agricultural programs
    GARANTIA_SAFRA = "GARANTIA_SAFRA"
    PNAE = "PNAE"
    PAA = "PAA"


# Program metadata for initialization
PROGRAMS_METADATA = [
    {
        "code": ProgramCode.BOLSA_FAMILIA,
        "name": "Bolsa Família",
        "description": "Principal programa de transferência de renda do Brasil para famílias em situação de pobreza e extrema pobreza",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.BPC,
        "name": "Benefício de Prestação Continuada (BPC/LOAS)",
        "description": "Benefício assistencial de um salário mínimo para idosos e pessoas com deficiência de baixa renda",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/bpc",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.TSEE,
        "name": "Tarifa Social de Energia Elétrica",
        "description": "Desconto na conta de luz para famílias de baixa renda inscritas no CadÚnico",
        "data_source_url": "https://dadosabertos.aneel.gov.br/",
        "update_frequency": "QUARTERLY",
    },
    {
        "code": ProgramCode.FARMACIA_POPULAR,
        "name": "Farmácia Popular do Brasil",
        "description": "Medicamentos gratuitos ou com desconto para tratamento de hipertensão, diabetes e asma",
        "data_source_url": "https://dados.gov.br/dataset/farmacia_popular_estabelecimento",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.DIGNIDADE_MENSTRUAL,
        "name": "Programa Dignidade Menstrual",
        "description": "Distribuição gratuita de absorventes para mulheres em situação de vulnerabilidade",
        "data_source_url": "https://www.gov.br/saude/",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.PIS_PASEP,
        "name": "Cotas do PIS/PASEP",
        "description": "Resgate de cotas antigas do PIS/PASEP para trabalhadores cadastrados entre 1971-1988",
        "data_source_url": "http://repiscidadao.fazenda.gov.br/",
        "update_frequency": "YEARLY",
    },
    {
        "code": ProgramCode.CADUNICO,
        "name": "Cadastro Único",
        "description": "Base de dados para identificação de famílias de baixa renda para programas sociais",
        "data_source_url": "https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.AUXILIO_GAS,
        "name": "Auxílio Gás",
        "description": "Auxílio financeiro para compra de botijão de gás de cozinha para famílias de baixa renda inscritas no CadÚnico",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/auxilio-gas",
        "update_frequency": "BIMONTHLY",
    },
    {
        "code": ProgramCode.SEGURO_DEFESO,
        "name": "Seguro Defeso",
        "description": "Benefício de um salário mínimo para pescadores artesanais durante o período de defeso (reprodução das espécies)",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/seguro-defeso",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.AUXILIO_INCLUSAO,
        "name": "Auxílio Inclusão",
        "description": "Benefício para pessoas com deficiência que ingressam no mercado de trabalho formal, substituindo o BPC",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/auxilio-inclusao",
        "update_frequency": "MONTHLY",
    },
    # Agricultural programs
    {
        "code": ProgramCode.GARANTIA_SAFRA,
        "name": "Garantia-Safra",
        "description": "Benefício de R$ 1.200 para agricultores familiares do semiárido que perdem safra por seca ou excesso de chuvas",
        "data_source_url": "https://portaldatransparencia.gov.br/download-de-dados/garantia-safra",
        "update_frequency": "YEARLY",
    },
    {
        "code": ProgramCode.PNAE,
        "name": "Programa Nacional de Alimentação Escolar",
        "description": "Repasses federais para alimentação escolar. Municípios devem comprar 30% da agricultura familiar",
        "data_source_url": "https://dados.gov.br/dados/conjuntos-dados/programa-nacional-de-alimentacao-escolar-pnae",
        "update_frequency": "MONTHLY",
    },
    {
        "code": ProgramCode.PAA,
        "name": "Programa de Aquisição de Alimentos",
        "description": "Governo compra alimentos da agricultura familiar para distribuir em programas sociais",
        "data_source_url": "https://www.gov.br/cidadania/pt-br/acoes-e-programas/inclusao-produtiva-rural/paa",
        "update_frequency": "MONTHLY",
    },
]

"""
Módulo de regras de elegibilidade para benefícios sociais.

Cada arquivo exporta uma função verificar_elegibilidade(perfil) que retorna
um EligibilityResult com o status de elegibilidade do cidadão.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class EligibilityStatus(Enum):
    """Status de elegibilidade para um benefício."""
    ELEGIVEL = "elegivel"
    JA_RECEBE = "ja_recebe"
    INELEGIVEL = "inelegivel"
    INCONCLUSIVO = "inconclusivo"  # Faltam dados para determinar


@dataclass
class EligibilityResult:
    """Resultado da verificação de elegibilidade."""
    programa: str
    programa_nome: str
    status: EligibilityStatus
    motivo: str
    valor_estimado: Optional[float] = None
    proximos_passos: Optional[List[str]] = None
    documentos_necessarios: Optional[List[str]] = None
    onde_solicitar: Optional[str] = None
    observacoes: Optional[str] = None


@dataclass
class CitizenProfile:
    """Perfil do cidadão para verificação de elegibilidade."""
    # Identificação (opcional)
    cpf: Optional[str] = None
    nome: Optional[str] = None
    data_nascimento: Optional[str] = None  # YYYY-MM-DD

    # Localização
    municipio: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    regiao_metropolitana: bool = False
    populacao_municipio: Optional[int] = None

    # Composição familiar
    pessoas_na_casa: int = 1
    tem_filhos_menores: bool = False
    quantidade_filhos: int = 0
    tem_idoso_65_mais: bool = False
    tem_gestante: bool = False
    tem_pcd: bool = False  # Pessoa com deficiência
    estado_civil: Optional[str] = None
    idade_conjuge: Optional[int] = None

    # Renda
    renda_familiar_mensal: float = 0.0
    trabalha_formal: bool = False
    trabalha_informal: bool = False
    autonomo: bool = False
    desempregado: bool = False

    # Benefícios atuais (se conhecidos via consulta CPF)
    recebe_bolsa_familia: bool = False
    valor_bolsa_familia: float = 0.0
    recebe_bpc: bool = False
    valor_bpc: float = 0.0
    cadastrado_cadunico: bool = False
    faixa_cadunico: Optional[int] = None  # 1, 2 ou 3

    # Habitação - Situação atual
    tem_casa_propria: bool = False
    mora_aluguel: bool = False
    mora_cedido: bool = False
    situacao_rua: bool = False

    # Habitação - Critérios MCMV
    tem_imovel_registrado: Optional[bool] = None
    teve_beneficio_habitacional_federal: Optional[bool] = None
    tem_financiamento_ativo: Optional[bool] = None

    # Grupos Prioritários MCMV
    em_area_risco: bool = False
    vitima_violencia_domestica: bool = False

    # Dados para Simulação MCMV
    valor_fgts_disponivel: Optional[float] = None
    tempo_contribuicao_fgts_meses: Optional[int] = None

    # Score de Crédito
    tem_restricao_credito: Optional[bool] = None

    # Trabalho histórico (para PIS/PASEP)
    trabalhou_1971_1988: Optional[bool] = None
    tem_fgts: Optional[bool] = None

    @property
    def renda_per_capita(self) -> float:
        """Calcula renda per capita da família."""
        if self.pessoas_na_casa <= 0:
            return self.renda_familiar_mensal
        return self.renda_familiar_mensal / self.pessoas_na_casa

    @property
    def idade(self) -> Optional[int]:
        """Calcula idade a partir da data de nascimento."""
        if not self.data_nascimento:
            return None
        from datetime import datetime, date
        try:
            nasc = datetime.strptime(self.data_nascimento, "%Y-%m-%d").date()
            hoje = date.today()
            idade = hoje.year - nasc.year
            if (hoje.month, hoje.day) < (nasc.month, nasc.day):
                idade -= 1
            return idade
        except ValueError:
            return None


# Constantes de referência (valores 2024/2025)
SALARIO_MINIMO = 1412.00  # R$ 1.412,00 em 2024
LIMITE_EXTREMA_POBREZA = 105.00  # R$ 105,00 per capita
LIMITE_POBREZA = 218.00  # R$ 218,00 per capita
LIMITE_BAIXA_RENDA = SALARIO_MINIMO / 2  # R$ 706,00 per capita

# Faixas MCMV 2026 (atualizadas)
MCMV_FAIXA_1 = 2850.00
MCMV_FAIXA_2 = 4700.00
MCMV_FAIXA_3 = 8600.00
MCMV_FAIXA_4 = 12000.00  # Nova Faixa 4 (antiga "Classe Média")
MCMV_CLASSE_MEDIA = MCMV_FAIXA_4  # Alias para compatibilidade

# Tetos de valor do imóvel MCMV 2026
MCMV_TETO_RM_GRANDE = 270000.00  # Regiões metropolitanas >750 mil hab
MCMV_TETO_DEMAIS = 255000.00     # Demais regiões
MCMV_TETO_FAIXA_3 = 350000.00    # Faixa 3
MCMV_TETO_FAIXA_4 = 500000.00    # Faixa 4

# Subsídios MCMV 2026
MCMV_SUBSIDIO_FAIXA_1 = 65000.00
MCMV_SUBSIDIO_FAIXA_2 = 55000.00

# Taxas de juros MCMV 2026 (ao ano)
MCMV_JUROS_FAIXA_1_MIN = 4.00
MCMV_JUROS_FAIXA_1_MAX = 4.25
MCMV_JUROS_FAIXA_2_MIN = 4.25
MCMV_JUROS_FAIXA_2_MAX = 7.00
MCMV_JUROS_FAIXA_3_MIN = 7.00
MCMV_JUROS_FAIXA_3_MAX = 8.16
MCMV_JUROS_FAIXA_4 = 10.00

# Programa Reforma Casa Brasil 2026
REFORMA_LIMITE_FAIXA_1 = 3200.00
REFORMA_LIMITE_FAIXA_2 = 9600.00
REFORMA_CREDITO_MIN = 5000.00
REFORMA_CREDITO_MAX = 30000.00
REFORMA_JUROS_FAIXA_1 = 1.17  # ao mês
REFORMA_JUROS_FAIXA_2 = 1.95  # ao mês


# Importar verificadores de cada programa
from .bolsa_familia import verificar_elegibilidade as verificar_bolsa_familia
from .bpc import verificar_elegibilidade as verificar_bpc
from .farmacia_popular import verificar_elegibilidade as verificar_farmacia_popular
from .tsee import verificar_elegibilidade as verificar_tsee
from .auxilio_gas import verificar_elegibilidade as verificar_auxilio_gas
from .dignidade_menstrual import verificar_elegibilidade as verificar_dignidade_menstrual
from .mcmv import verificar_elegibilidade as verificar_mcmv
from .pis_pasep import verificar_elegibilidade as verificar_pis_pasep


__all__ = [
    "EligibilityStatus",
    "EligibilityResult",
    "CitizenProfile",
    "SALARIO_MINIMO",
    "LIMITE_EXTREMA_POBREZA",
    "LIMITE_POBREZA",
    "LIMITE_BAIXA_RENDA",
    # MCMV Faixas
    "MCMV_FAIXA_1",
    "MCMV_FAIXA_2",
    "MCMV_FAIXA_3",
    "MCMV_FAIXA_4",
    "MCMV_CLASSE_MEDIA",
    # MCMV Tetos
    "MCMV_TETO_RM_GRANDE",
    "MCMV_TETO_DEMAIS",
    "MCMV_TETO_FAIXA_3",
    "MCMV_TETO_FAIXA_4",
    # MCMV Subsídios
    "MCMV_SUBSIDIO_FAIXA_1",
    "MCMV_SUBSIDIO_FAIXA_2",
    # MCMV Juros
    "MCMV_JUROS_FAIXA_1_MIN",
    "MCMV_JUROS_FAIXA_1_MAX",
    "MCMV_JUROS_FAIXA_2_MIN",
    "MCMV_JUROS_FAIXA_2_MAX",
    "MCMV_JUROS_FAIXA_3_MIN",
    "MCMV_JUROS_FAIXA_3_MAX",
    "MCMV_JUROS_FAIXA_4",
    # Programa Reformas
    "REFORMA_LIMITE_FAIXA_1",
    "REFORMA_LIMITE_FAIXA_2",
    "REFORMA_CREDITO_MIN",
    "REFORMA_CREDITO_MAX",
    "REFORMA_JUROS_FAIXA_1",
    "REFORMA_JUROS_FAIXA_2",
    # Verificadores
    "verificar_bolsa_familia",
    "verificar_bpc",
    "verificar_farmacia_popular",
    "verificar_tsee",
    "verificar_auxilio_gas",
    "verificar_dignidade_menstrual",
    "verificar_mcmv",
    "verificar_pis_pasep",
]

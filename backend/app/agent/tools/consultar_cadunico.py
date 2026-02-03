"""
Tools de consulta ao CadUnico (Cadastro Unico).

Implementa consulta por CPF e verificacao de atualizacao do cadastro.

Quando CADUNICO_API_URL esta configurado, consulta a API real.
Quando vazio, usa mock realista para desenvolvimento/testes.

SEGURANCA: CPF eh hasheado para logs, nunca armazenado em texto.
"""

import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

# Timeout para chamadas HTTP (segundos)
_HTTP_TIMEOUT = 15.0
_HTTP_RETRIES = 2


# =============================================================================
# Helpers
# =============================================================================

def _hash_cpf(cpf: str) -> str:
    """Gera hash do CPF para logs seguros."""
    return hashlib.sha256(cpf.encode()).hexdigest()[:12]


def _limpar_cpf(cpf: str) -> str:
    """Remove formatacao do CPF."""
    return re.sub(r'\D', '', cpf)


def _mascarar_cpf(cpf: str) -> str:
    """Mascara CPF para exibicao: ***.456.789-**"""
    cpf = _limpar_cpf(cpf)
    if len(cpf) != 11:
        return "***.***.***-**"
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"


def _get_api_config() -> tuple[str, str]:
    """Retorna (api_url, api_key) do settings. Vazio se nao configurado."""
    try:
        from app.config import settings
        return settings.CADUNICO_API_URL, settings.CADUNICO_API_KEY
    except Exception:
        return "", ""


def _is_api_configured() -> bool:
    """Verifica se a API real esta configurada."""
    url, _ = _get_api_config()
    return bool(url)


# =============================================================================
# Cliente HTTP para API real do CadUnico
# =============================================================================

def _consultar_api(cpf_limpo: str) -> Optional[Dict[str, Any]]:
    """Consulta a API real do CadUnico.

    Args:
        cpf_limpo: CPF com 11 digitos, sem formatacao

    Returns:
        dict com dados brutos da API, ou None se falhou/nao encontrado
    """
    api_url, api_key = _get_api_config()
    cpf_hash = _hash_cpf(cpf_limpo)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = f"{api_url.rstrip('/')}/consulta/cpf"

    last_error = None
    for attempt in range(1, _HTTP_RETRIES + 1):
        try:
            logger.info(
                f"CadUnico API request: hash={cpf_hash}, "
                f"attempt={attempt}/{_HTTP_RETRIES}"
            )
            with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
                response = client.post(
                    url,
                    json={"cpf": cpf_limpo},
                    headers=headers,
                )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"CadUnico API: encontrado hash={cpf_hash}")
                return data

            if response.status_code == 404:
                logger.info(f"CadUnico API: nao encontrado hash={cpf_hash}")
                return None

            if response.status_code == 401:
                logger.error("CadUnico API: chave de acesso invalida (401)")
                return None

            if response.status_code == 429:
                logger.warning("CadUnico API: rate limit (429), tentando novamente...")
                continue

            logger.warning(
                f"CadUnico API: status inesperado {response.status_code} "
                f"para hash={cpf_hash}"
            )
            last_error = f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            logger.warning(
                f"CadUnico API: timeout attempt={attempt} hash={cpf_hash}"
            )
            last_error = "timeout"

        except httpx.ConnectError as e:
            logger.error(f"CadUnico API: erro de conexao: {e}")
            last_error = "connection_error"
            break  # Nao faz sentido retry em erro de conexao

        except Exception as e:
            logger.error(f"CadUnico API: erro inesperado: {e}")
            last_error = str(e)
            break

    logger.error(
        f"CadUnico API: falha apos {_HTTP_RETRIES} tentativas "
        f"hash={cpf_hash} ultimo_erro={last_error}"
    )
    return None


def _normalizar_resposta_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza resposta da API real para o formato interno.

    A API pode retornar campos com nomes diferentes do mock.
    Este metodo mapeia para a estrutura padrao.

    Args:
        data: Resposta bruta da API

    Returns:
        dict no formato padrao (mesmo que o mock retorna)
    """
    # A API real pode usar nomes diferentes. Este mapeamento
    # adapta para a estrutura interna usada pelo agente.
    # Campos que ja estiverem no formato correto passam direto.

    cadastro = {}

    # Codigo familiar
    cadastro["codigo_familiar"] = data.get(
        "codigo_familiar",
        data.get("cd_familiar_fam", "")
    )

    # Responsavel familiar
    resp_raw = data.get("responsavel_familiar", data.get("responsavel", {}))
    cadastro["responsavel_familiar"] = {
        "nome": resp_raw.get("nome", resp_raw.get("no_pessoa", "")),
        "nis": resp_raw.get("nis", resp_raw.get("nu_nis_pessoa", "")),
        "data_nascimento": resp_raw.get("data_nascimento", resp_raw.get("dt_nasc_pessoa", "")),
        "sexo": resp_raw.get("sexo", resp_raw.get("co_sexo_pessoa", "")),
        "estado_civil": resp_raw.get("estado_civil", ""),
        "escolaridade": resp_raw.get("escolaridade", ""),
    }

    # Composicao familiar
    membros_raw = data.get(
        "composicao_familiar",
        data.get("membros", data.get("componentes_familiares", []))
    )
    cadastro["composicao_familiar"] = []
    for m in membros_raw:
        membro = {
            "nome": m.get("nome", m.get("no_pessoa", "")),
            "parentesco": m.get("parentesco", m.get("co_parentesco", "MEMBRO")),
            "data_nascimento": m.get("data_nascimento", m.get("dt_nasc_pessoa", "")),
            "idade": m.get("idade", 0),
            "nis": m.get("nis", m.get("nu_nis_pessoa", "")),
        }
        # Calcular idade se nao veio
        if membro["idade"] == 0 and membro["data_nascimento"]:
            try:
                for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(membro["data_nascimento"], fmt)
                        membro["idade"] = (datetime.now() - dt).days // 365
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        cadastro["composicao_familiar"].append(membro)

    # Endereco
    end_raw = data.get("endereco", {})
    cadastro["endereco"] = {
        "logradouro": end_raw.get("logradouro", end_raw.get("no_localidade_fam", "")),
        "numero": end_raw.get("numero", end_raw.get("nu_logradouro_fam", "")),
        "bairro": end_raw.get("bairro", ""),
        "cidade": end_raw.get("cidade", end_raw.get("no_municipio", "")),
        "uf": end_raw.get("uf", end_raw.get("sg_uf", "")),
        "cep": end_raw.get("cep", end_raw.get("nu_cep_logradouro_fam", "")),
    }

    # Renda
    renda_raw = data.get("renda", {})
    renda_total = renda_raw.get(
        "renda_familiar_total",
        renda_raw.get("vl_renda_total_fam", 0)
    )
    renda_pc = renda_raw.get(
        "renda_per_capita",
        renda_raw.get("vl_renda_per_capita_fam", 0)
    )
    faixa = renda_raw.get("faixa", "")
    if not faixa:
        # Inferir faixa pela renda per capita
        if renda_pc <= 105:
            faixa = "EXTREMA_POBREZA"
        elif renda_pc <= 218:
            faixa = "POBREZA"
        elif renda_pc <= 706:  # Meio salario minimo aprox
            faixa = "BAIXA_RENDA"
        else:
            faixa = "ACIMA_MEIO_SM"
    cadastro["renda"] = {
        "renda_familiar_total": float(renda_total),
        "renda_per_capita": float(renda_pc),
        "faixa": faixa,
    }

    # Programas vinculados
    programas_raw = data.get(
        "programas_vinculados",
        data.get("programas", data.get("beneficios", []))
    )
    cadastro["programas_vinculados"] = []
    for p in programas_raw:
        cadastro["programas_vinculados"].append({
            "codigo": p.get("codigo", p.get("cd_programa", "")),
            "nome": p.get("nome", p.get("no_programa", "")),
            "ativo": p.get("ativo", p.get("in_ativo", True)),
            "valor_mensal": p.get("valor_mensal", p.get("vl_beneficio", None)),
        })

    # Datas
    cadastro["data_cadastro"] = data.get(
        "data_cadastro",
        data.get("dt_cadastro_fam", "")
    )
    cadastro["data_ultima_atualizacao"] = data.get(
        "data_ultima_atualizacao",
        data.get("dt_atualizacao_fam", "")
    )
    cadastro["situacao_cadastral"] = data.get(
        "situacao_cadastral",
        data.get("co_situacao_cadastral", "CADASTRADO")
    )

    return cadastro


# =============================================================================
# Mock de dados CadUnico (estrutura realista)
# =============================================================================

# CPFs de teste com dados ficticios
_MOCK_CADASTROS: Dict[str, Dict[str, Any]] = {
    "52998224725": {
        "codigo_familiar": "1234567890123",
        "responsavel_familiar": {
            "nome": "MARIA DA SILVA SANTOS",
            "nis": "12345678901",
            "data_nascimento": "15/03/1985",
            "sexo": "F",
            "estado_civil": "SOLTEIRA",
            "escolaridade": "FUNDAMENTAL_INCOMPLETO",
        },
        "composicao_familiar": [
            {
                "nome": "MARIA DA SILVA SANTOS",
                "parentesco": "RESPONSAVEL",
                "data_nascimento": "15/03/1985",
                "idade": 40,
                "nis": "12345678901",
            },
            {
                "nome": "JOAO PEDRO SANTOS",
                "parentesco": "FILHO",
                "data_nascimento": "10/08/2012",
                "idade": 13,
                "nis": "12345678902",
            },
            {
                "nome": "ANA CLARA SANTOS",
                "parentesco": "FILHA",
                "data_nascimento": "22/01/2016",
                "idade": 9,
                "nis": "12345678903",
            },
        ],
        "endereco": {
            "logradouro": "RUA DAS FLORES",
            "numero": "123",
            "bairro": "CENTRO",
            "cidade": "SAO PAULO",
            "uf": "SP",
            "cep": "01001000",
        },
        "renda": {
            "renda_familiar_total": 800.00,
            "renda_per_capita": 266.67,
            "faixa": "POBREZA",
        },
        "programas_vinculados": [
            {
                "codigo": "BOLSA_FAMILIA",
                "nome": "Bolsa Familia",
                "ativo": True,
                "valor_mensal": 600.00,
            },
            {
                "codigo": "TSEE",
                "nome": "Tarifa Social de Energia Eletrica",
                "ativo": True,
                "valor_mensal": None,
            },
        ],
        "data_cadastro": "2019-05-10",
        "data_ultima_atualizacao": "2024-11-15",
        "situacao_cadastral": "CADASTRADO",
    },
    "11144477735": {
        "codigo_familiar": "9876543210123",
        "responsavel_familiar": {
            "nome": "JOSE CARLOS OLIVEIRA",
            "nis": "98765432101",
            "data_nascimento": "20/07/1958",
            "sexo": "M",
            "estado_civil": "VIUVO",
            "escolaridade": "NAO_ALFABETIZADO",
        },
        "composicao_familiar": [
            {
                "nome": "JOSE CARLOS OLIVEIRA",
                "parentesco": "RESPONSAVEL",
                "data_nascimento": "20/07/1958",
                "idade": 67,
                "nis": "98765432101",
            },
        ],
        "endereco": {
            "logradouro": "TRAVESSA BOA ESPERANCA",
            "numero": "45",
            "bairro": "PERIFERIA",
            "cidade": "RECIFE",
            "uf": "PE",
            "cep": "50000000",
        },
        "renda": {
            "renda_familiar_total": 0.00,
            "renda_per_capita": 0.00,
            "faixa": "EXTREMA_POBREZA",
        },
        "programas_vinculados": [
            {
                "codigo": "BPC",
                "nome": "Beneficio de Prestacao Continuada",
                "ativo": True,
                "valor_mensal": 1412.00,
            },
        ],
        "data_cadastro": "2015-03-22",
        "data_ultima_atualizacao": "2023-06-10",
        "situacao_cadastral": "CADASTRADO",
    },
    "12345678909": {
        "codigo_familiar": "5555666677778",
        "responsavel_familiar": {
            "nome": "ANA PAULA FERREIRA",
            "nis": "55566677788",
            "data_nascimento": "08/12/1990",
            "sexo": "F",
            "estado_civil": "CASADA",
            "escolaridade": "MEDIO_COMPLETO",
        },
        "composicao_familiar": [
            {
                "nome": "ANA PAULA FERREIRA",
                "parentesco": "RESPONSAVEL",
                "data_nascimento": "08/12/1990",
                "idade": 35,
                "nis": "55566677788",
            },
            {
                "nome": "CARLOS FERREIRA LIMA",
                "parentesco": "CONJUGE",
                "data_nascimento": "14/04/1988",
                "idade": 37,
                "nis": "55566677789",
            },
            {
                "nome": "LUCAS FERREIRA LIMA",
                "parentesco": "FILHO",
                "data_nascimento": "30/06/2020",
                "idade": 5,
                "nis": "55566677790",
            },
        ],
        "endereco": {
            "logradouro": "AV BRASIL",
            "numero": "500",
            "bairro": "COPACABANA",
            "cidade": "RIO DE JANEIRO",
            "uf": "RJ",
            "cep": "22041080",
        },
        "renda": {
            "renda_familiar_total": 1500.00,
            "renda_per_capita": 500.00,
            "faixa": "BAIXA_RENDA",
        },
        "programas_vinculados": [
            {
                "codigo": "BOLSA_FAMILIA",
                "nome": "Bolsa Familia",
                "ativo": True,
                "valor_mensal": 600.00,
            },
        ],
        "data_cadastro": "2021-01-20",
        "data_ultima_atualizacao": "2025-01-08",
        "situacao_cadastral": "CADASTRADO",
    },
}


# =============================================================================
# Tools
# =============================================================================

def _buscar_cadastro(cpf_limpo: str) -> Optional[Dict[str, Any]]:
    """Busca cadastro na API real ou no mock, conforme configuracao.

    Args:
        cpf_limpo: CPF com 11 digitos, sem formatacao

    Returns:
        dict com dados do cadastro no formato interno, ou None
    """
    if _is_api_configured():
        api_data = _consultar_api(cpf_limpo)
        if api_data is None:
            return None
        return _normalizar_resposta_api(api_data)

    # Fallback para mock
    return _MOCK_CADASTROS.get(cpf_limpo)


def consultar_cadunico(cpf: str) -> dict:
    """Consulta dados do CadUnico por CPF.

    Usa API real quando CADUNICO_API_URL esta configurado,
    caso contrario usa mock para desenvolvimento/testes.

    Retorna composicao familiar, renda per capita, programas vinculados
    e situacao cadastral.

    Args:
        cpf: CPF do cidadao (11 digitos, com ou sem formatacao)

    Returns:
        dict com dados do CadUnico ou mensagem de nao encontrado
    """
    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)
    fonte = "API" if _is_api_configured() else "mock"

    logger.info(f"Consultando CadUnico para CPF hash={cpf_hash} via {fonte}")

    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "erro": "CPF invalido. Precisa ter 11 digitos.",
            "cpf_masked": "***.***.***-**",
        }

    cadastro = _buscar_cadastro(cpf_limpo)

    if not cadastro:
        logger.info(f"CPF hash={cpf_hash} nao encontrado no CadUnico ({fonte})")
        return {
            "encontrado": False,
            "cpf_masked": _mascarar_cpf(cpf_limpo),
            "mensagem": (
                "Nao encontrei seu cadastro no CadUnico. "
                "Isso pode significar que voce ainda nao fez o cadastro. "
                "Quer que eu te ajude a se cadastrar?"
            ),
            "sugestao": "Para se cadastrar, voce precisa ir ao CRAS mais perto de voce.",
        }

    cpf_masked = _mascarar_cpf(cpf_limpo)
    resp = cadastro["responsavel_familiar"]
    renda = cadastro["renda"]
    membros = cadastro["composicao_familiar"]
    programas = cadastro["programas_vinculados"]

    logger.info(
        f"CadUnico encontrado para CPF hash={cpf_hash}: "
        f"{len(membros)} membros, renda_pc={renda['renda_per_capita']} ({fonte})"
    )

    return {
        "encontrado": True,
        "cpf_masked": cpf_masked,
        "responsavel": resp["nome"],
        "codigo_familiar": cadastro["codigo_familiar"],
        "composicao_familiar": {
            "total_membros": len(membros),
            "membros": [
                {
                    "nome": m["nome"],
                    "parentesco": m["parentesco"],
                    "idade": m["idade"],
                }
                for m in membros
            ],
        },
        "renda": {
            "renda_familiar_total": renda["renda_familiar_total"],
            "renda_per_capita": renda["renda_per_capita"],
            "faixa": renda["faixa"],
            "faixa_descricao": _descrever_faixa(renda["faixa"]),
        },
        "programas_vinculados": [
            {
                "nome": p["nome"],
                "ativo": p["ativo"],
                "valor_mensal": p.get("valor_mensal"),
            }
            for p in programas
        ],
        "data_ultima_atualizacao": cadastro["data_ultima_atualizacao"],
        "situacao_cadastral": cadastro["situacao_cadastral"],
    }


def verificar_atualizacao_cadunico(cpf: str) -> dict:
    """Verifica se o cadastro do CadUnico esta atualizado.

    O CadUnico precisa ser atualizado a cada 2 anos.
    Cadastro desatualizado pode causar bloqueio de beneficios.

    Usa API real quando CADUNICO_API_URL esta configurado,
    caso contrario usa mock para desenvolvimento/testes.

    Args:
        cpf: CPF do cidadao (11 digitos, com ou sem formatacao)

    Returns:
        dict com status de atualizacao e orientacoes
    """
    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)
    fonte = "API" if _is_api_configured() else "mock"

    logger.info(f"Verificando atualizacao CadUnico para CPF hash={cpf_hash} via {fonte}")

    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "erro": "CPF invalido. Precisa ter 11 digitos.",
        }

    cadastro = _buscar_cadastro(cpf_limpo)

    if not cadastro:
        return {
            "encontrado": False,
            "cpf_masked": _mascarar_cpf(cpf_limpo),
            "mensagem": "Nao encontrei cadastro no CadUnico para este CPF.",
            "sugestao": "Voce precisa fazer o cadastro no CRAS.",
        }

    data_atualizacao = datetime.strptime(
        cadastro["data_ultima_atualizacao"], "%Y-%m-%d"
    )
    hoje = datetime.now()
    dias_desde_atualizacao = (hoje - data_atualizacao).days
    limite_dias = 730  # 2 anos

    atualizado = dias_desde_atualizacao <= limite_dias
    dias_restantes = max(0, limite_dias - dias_desde_atualizacao)

    cpf_masked = _mascarar_cpf(cpf_limpo)

    if atualizado:
        if dias_restantes <= 90:
            # Cadastro perto de vencer
            urgencia = "ATENCAO"
            mensagem = (
                f"Seu cadastro ainda esta em dia, mas vai vencer em {dias_restantes} dias. "
                "Recomendo atualizar logo para nao perder nenhum beneficio."
            )
        else:
            urgencia = "OK"
            mensagem = (
                f"Seu cadastro esta em dia! "
                f"Foi atualizado em {data_atualizacao.strftime('%d/%m/%Y')}. "
                f"Proxima atualizacao obrigatoria em {dias_restantes} dias."
            )
    else:
        urgencia = "URGENTE"
        dias_atraso = dias_desde_atualizacao - limite_dias
        mensagem = (
            f"Seu cadastro esta DESATUALIZADO ha {dias_atraso} dias! "
            "Isso pode bloquear seus beneficios. "
            "Voce precisa ir ao CRAS o mais rapido possivel para atualizar."
        )

    programas_em_risco = []
    if not atualizado:
        for p in cadastro["programas_vinculados"]:
            if p["ativo"]:
                programas_em_risco.append(p["nome"])

    logger.info(
        f"Atualizacao CadUnico hash={cpf_hash}: "
        f"atualizado={atualizado}, dias={dias_desde_atualizacao}, urgencia={urgencia}"
    )

    return {
        "encontrado": True,
        "cpf_masked": cpf_masked,
        "atualizado": atualizado,
        "urgencia": urgencia,
        "data_ultima_atualizacao": data_atualizacao.strftime("%d/%m/%Y"),
        "dias_desde_atualizacao": dias_desde_atualizacao,
        "dias_restantes": dias_restantes if atualizado else 0,
        "mensagem": mensagem,
        "programas_em_risco": programas_em_risco,
        "orientacao": (
            "Leve RG e CPF de todos da familia ao CRAS para atualizar."
            if not atualizado
            else ""
        ),
    }


# =============================================================================
# Helpers
# =============================================================================

def _descrever_faixa(faixa: str) -> str:
    """Retorna descricao simples da faixa de renda."""
    descricoes = {
        "EXTREMA_POBREZA": "Renda muito baixa (ate R$ 105 por pessoa)",
        "POBREZA": "Renda baixa (entre R$ 105 e R$ 218 por pessoa)",
        "BAIXA_RENDA": "Renda ate meio salario minimo por pessoa",
    }
    return descricoes.get(faixa, "Faixa nao identificada")

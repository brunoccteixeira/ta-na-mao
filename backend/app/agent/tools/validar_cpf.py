"""Tool para validação de CPF brasileiro."""

import re


def validar_cpf(cpf: str) -> dict:
    """Valida um CPF brasileiro usando os dígitos verificadores.

    Args:
        cpf: CPF com 11 dígitos numéricos (pode conter pontos e traços)

    Returns:
        dict: {"valido": bool, "cpf_formatado": str, "mensagem": str}
    """
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', cpf)

    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return {
            "valido": False,
            "cpf_formatado": None,
            "mensagem": f"CPF deve ter 11 dígitos. Você informou {len(cpf_limpo)} dígitos."
        }

    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf_limpo == cpf_limpo[0] * 11:
        return {
            "valido": False,
            "cpf_formatado": None,
            "mensagem": "CPF inválido: todos os dígitos são iguais."
        }

    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf_limpo[9]) != digito1:
        return {
            "valido": False,
            "cpf_formatado": None,
            "mensagem": "CPF inválido: primeiro dígito verificador não confere."
        }

    # Calcula o segundo dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf_limpo[10]) != digito2:
        return {
            "valido": False,
            "cpf_formatado": None,
            "mensagem": "CPF inválido: segundo dígito verificador não confere."
        }

    # CPF válido - formata com pontos e traço
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

    return {
        "valido": True,
        "cpf_formatado": cpf_formatado,
        "cpf_numerico": cpf_limpo,
        "mensagem": "CPF válido!"
    }

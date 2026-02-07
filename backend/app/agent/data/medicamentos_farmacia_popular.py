"""
Base de dados dos medicamentos gratuitos do Programa Farmácia Popular.
Atualizado em: Fevereiro 2025 (100% gratuidade)

Fonte: https://www.gov.br/saude/pt-br/composicao/sectics/farmacia-popular
"""

from typing import Dict, List, Optional
from difflib import SequenceMatcher


MEDICAMENTOS_FARMACIA_POPULAR: Dict[str, List[Dict]] = {
    "hipertensao": [
        {"nome": "Losartana", "principio_ativo": "losartana potassica", "dosagens": ["50mg"], "gratuito": True},
        {"nome": "Captopril", "principio_ativo": "captopril", "dosagens": ["25mg"], "gratuito": True},
        {"nome": "Atenolol", "principio_ativo": "atenolol", "dosagens": ["25mg"], "gratuito": True},
        {"nome": "Hidroclorotiazida", "principio_ativo": "hidroclorotiazida", "dosagens": ["25mg"], "gratuito": True},
        {"nome": "Enalapril", "principio_ativo": "maleato de enalapril", "dosagens": ["10mg"], "gratuito": True},
        {"nome": "Propranolol", "principio_ativo": "cloridrato de propranolol", "dosagens": ["40mg"], "gratuito": True},
        {"nome": "Anlodipino", "principio_ativo": "besilato de anlodipino", "dosagens": ["5mg"], "gratuito": True},
        {"nome": "Espironolactona", "principio_ativo": "espironolactona", "dosagens": ["25mg"], "gratuito": True},
        {"nome": "Furosemida", "principio_ativo": "furosemida", "dosagens": ["40mg"], "gratuito": True},
    ],
    "diabetes": [
        {"nome": "Metformina", "principio_ativo": "cloridrato de metformina", "dosagens": ["500mg", "850mg"], "gratuito": True},
        {"nome": "Glibenclamida", "principio_ativo": "glibenclamida", "dosagens": ["5mg"], "gratuito": True},
        {"nome": "Insulina NPH", "principio_ativo": "insulina humana nph", "dosagens": ["100ui/ml"], "gratuito": True},
        {"nome": "Insulina Regular", "principio_ativo": "insulina humana regular", "dosagens": ["100ui/ml"], "gratuito": True},
        {"nome": "Dapagliflozina", "principio_ativo": "dapagliflozina", "dosagens": ["10mg"], "gratuito": True},
    ],
    "asma": [
        {"nome": "Salbutamol", "principio_ativo": "sulfato de salbutamol", "dosagens": ["100mcg", "5mg/ml"], "gratuito": True},
        {"nome": "Beclometasona", "principio_ativo": "dipropionato de beclometasona", "dosagens": ["50mcg", "200mcg", "250mcg"], "gratuito": True},
        {"nome": "Ipratrópio", "principio_ativo": "brometo de ipratropio", "dosagens": ["0.02mg", "0.25mg"], "gratuito": True},
    ],
    "osteoporose": [
        {"nome": "Alendronato", "principio_ativo": "alendronato de sodio", "dosagens": ["70mg"], "gratuito": True},
    ],
    "parkinson": [
        {"nome": "Levodopa + Carbidopa", "principio_ativo": "levodopa + carbidopa", "dosagens": ["250mg+25mg"], "gratuito": True},
        {"nome": "Levodopa + Benserazida", "principio_ativo": "levodopa + benserazida", "dosagens": ["200mg+50mg"], "gratuito": True},
    ],
    "glaucoma": [
        {"nome": "Timolol", "principio_ativo": "maleato de timolol", "dosagens": ["0.25%", "0.5%"], "gratuito": True},
    ],
    "dislipidemia": [
        {"nome": "Sinvastatina", "principio_ativo": "sinvastatina", "dosagens": ["10mg", "20mg", "40mg"], "gratuito": True},
    ],
    "rinite": [
        {"nome": "Budesonida", "principio_ativo": "budesonida", "dosagens": ["32mcg", "50mcg"], "gratuito": True},
    ],
    "contraceptivos": [
        {"nome": "Etinilestradiol + Levonorgestrel", "principio_ativo": "etinilestradiol + levonorgestrel", "dosagens": ["0.03mg+0.15mg"], "gratuito": True},
        {"nome": "Noretisterona + Etinilestradiol", "principio_ativo": "noretisterona + etinilestradiol", "dosagens": ["0.5mg+0.035mg"], "gratuito": True},
        {"nome": "Medroxiprogesterona", "principio_ativo": "acetato de medroxiprogesterona", "dosagens": ["150mg/ml"], "gratuito": True},
    ],
    "incontinencia": [
        {"nome": "Fralda Geriátrica", "principio_ativo": "fralda descartavel", "dosagens": ["P", "M", "G", "EG"], "gratuito": False, "desconto": "40%"},
    ],
}

# Aliases e nomes comerciais comuns
ALIASES_MEDICAMENTOS = {
    # Hipertensão
    "losartan": "losartana",
    "cozaar": "losartana",
    "aradois": "losartana",
    "capoten": "captopril",
    "capotril": "captopril",
    "angipress": "atenolol",
    "ablok": "atenolol",
    "clorana": "hidroclorotiazida",
    "diurix": "hidroclorotiazida",
    "hidroclor": "hidroclorotiazida",
    "renitec": "enalapril",
    "vasopril": "enalapril",
    "inderal": "propranolol",
    "norvasc": "anlodipino",
    "pressat": "anlodipino",
    "aldactone": "espironolactona",
    "lasix": "furosemida",

    # Diabetes
    "glifage": "metformina",
    "glucoformin": "metformina",
    "daonil": "glibenclamida",
    "euglucon": "glibenclamida",
    "insulina": "insulina nph",
    "humulin": "insulina nph",
    "novolin": "insulina nph",
    "forxiga": "dapagliflozina",

    # Asma
    "aerolin": "salbutamol",
    "ventolin": "salbutamol",
    "aerojet": "salbutamol",
    "clenil": "beclometasona",
    "beclosol": "beclometasona",
    "atrovent": "ipratrópio",

    # Outros
    "fosamax": "alendronato",
    "zocor": "sinvastatina",
    "busonid": "budesonida",
}


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos e convertendo para minúsculas."""
    import unicodedata
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto


def similarity(a: str, b: str) -> float:
    """Calcula similaridade entre duas strings."""
    return SequenceMatcher(None, normalizar_texto(a), normalizar_texto(b)).ratio()


def buscar_medicamento(nome: str) -> Optional[Dict]:
    """
    Busca um medicamento na base do Farmácia Popular.

    Retorna:
        Dict com informações do medicamento se encontrado, None caso contrário.
        {
            "encontrado": True/False,
            "nome": "Nome do medicamento",
            "principio_ativo": "principio ativo",
            "categoria": "hipertensao",
            "dosagens": ["50mg"],
            "gratuito": True,
            "similaridade": 0.95
        }
    """
    nome_normalizado = normalizar_texto(nome)

    # Verifica aliases primeiro
    for alias, med_real in ALIASES_MEDICAMENTOS.items():
        if alias in nome_normalizado or similarity(alias, nome_normalizado) > 0.85:
            nome_normalizado = normalizar_texto(med_real)
            break

    melhor_match = None
    melhor_similaridade = 0.0

    for categoria, medicamentos in MEDICAMENTOS_FARMACIA_POPULAR.items():
        for med in medicamentos:
            # Compara com nome
            sim_nome = similarity(med["nome"], nome_normalizado)
            # Compara com princípio ativo
            sim_principio = similarity(med["principio_ativo"], nome_normalizado)

            max_sim = max(sim_nome, sim_principio)

            # Verifica se o nome está contido
            nome_med_norm = normalizar_texto(med["nome"])
            principio_norm = normalizar_texto(med["principio_ativo"])

            if nome_med_norm in nome_normalizado or nome_normalizado in nome_med_norm:
                max_sim = max(max_sim, 0.9)
            if principio_norm in nome_normalizado or nome_normalizado in principio_norm:
                max_sim = max(max_sim, 0.9)

            if max_sim > melhor_similaridade:
                melhor_similaridade = max_sim
                melhor_match = {
                    "encontrado": True,
                    "nome": med["nome"],
                    "principio_ativo": med["principio_ativo"],
                    "categoria": categoria,
                    "dosagens": med["dosagens"],
                    "gratuito": med["gratuito"],
                    "desconto": med.get("desconto"),
                    "similaridade": max_sim
                }

    # Considera encontrado se similaridade >= 70%
    if melhor_match and melhor_similaridade >= 0.7:
        return melhor_match

    return {
        "encontrado": False,
        "nome": nome,
        "principio_ativo": None,
        "categoria": None,
        "dosagens": None,
        "gratuito": False,
        "similaridade": melhor_similaridade if melhor_match else 0.0
    }


def verificar_cobertura_receita(medicamentos: List[str]) -> Dict:
    """
    Verifica quais medicamentos de uma receita são cobertos pelo Farmácia Popular.

    Args:
        medicamentos: Lista de nomes de medicamentos

    Returns:
        Dict com medicamentos cobertos e não cobertos
    """
    gratuitos = []
    com_desconto = []
    nao_cobertos = []

    for med in medicamentos:
        resultado = buscar_medicamento(med)
        if resultado["encontrado"] and resultado["gratuito"]:
            gratuitos.append({
                "nome_receita": med,
                "nome_programa": resultado["nome"],
                "categoria": resultado["categoria"],
                "dosagens_disponiveis": resultado["dosagens"]
            })
        elif resultado["encontrado"] and resultado.get("desconto"):
            com_desconto.append({
                "nome_receita": med,
                "nome_programa": resultado["nome"],
                "categoria": resultado["categoria"],
                "dosagens_disponiveis": resultado["dosagens"],
                "desconto": resultado["desconto"]
            })
        else:
            nao_cobertos.append({
                "nome_receita": med,
                "motivo": "Medicamento não está na lista do Farmácia Popular",
                "sugestao": f"Medicamento similar encontrado: {resultado['nome']}" if resultado.get("similaridade", 0) > 0.5 else None
            })

    return {
        "total_medicamentos": len(medicamentos),
        "cobertos": len(gratuitos),
        "com_desconto": len(com_desconto),
        "nao_cobertos": len(nao_cobertos),
        "medicamentos_cobertos": gratuitos,
        "medicamentos_com_desconto": com_desconto,
        "medicamentos_nao_cobertos": nao_cobertos,
        "todos_cobertos": len(nao_cobertos) == 0 and len(com_desconto) == 0,
        "texto_resumo": _gerar_texto_resumo(gratuitos, com_desconto, nao_cobertos)
    }


def _gerar_texto_resumo(gratuitos: List[Dict], com_desconto: List[Dict], nao_cobertos: List[Dict]) -> str:
    """Gera texto de resumo da verificação de cobertura."""
    linhas = []

    if gratuitos:
        linhas.append("✅ **MEDICAMENTOS GRATUITOS no Farmácia Popular:**")
        for med in gratuitos:
            dosagens = ", ".join(med["dosagens_disponiveis"])
            linhas.append(f"   • {med['nome_programa']} ({dosagens})")
        linhas.append("")

    if com_desconto:
        linhas.append("💰 **COM DESCONTO no Farmácia Popular:**")
        for med in com_desconto:
            dosagens = ", ".join(med["dosagens_disponiveis"])
            linhas.append(f"   • {med['nome_programa']} ({dosagens}) — desconto de {med['desconto']}")
        linhas.append("")

    if nao_cobertos:
        linhas.append("❌ **Medicamentos NÃO cobertos pelo programa:**")
        for med in nao_cobertos:
            linhas.append(f"   • {med['nome_receita']}")
            if med.get("sugestao"):
                linhas.append(f"     💡 {med['sugestao']}")
        linhas.append("")

    if gratuitos and not nao_cobertos and not com_desconto:
        linhas.append("🎉 **Todos os medicamentos são gratuitos!**")
        linhas.append("Leve sua receita e documento com CPF a qualquer farmácia credenciada.")
    elif gratuitos or com_desconto:
        linhas.append("📋 Leve a receita para retirar os medicamentos na farmácia credenciada.")
        if nao_cobertos:
            linhas.append("Os demais precisam ser comprados normalmente.")
    else:
        linhas.append("😔 Nenhum medicamento desta receita está no Farmácia Popular.")

    return "\n".join(linhas)


def listar_categorias() -> List[str]:
    """Lista todas as categorias de medicamentos."""
    return list(MEDICAMENTOS_FARMACIA_POPULAR.keys())


def listar_medicamentos_por_categoria(categoria: str) -> List[Dict]:
    """Lista medicamentos de uma categoria específica."""
    return MEDICAMENTOS_FARMACIA_POPULAR.get(categoria.lower(), [])


def get_total_medicamentos() -> int:
    """Retorna o total de medicamentos no programa."""
    total = 0
    for meds in MEDICAMENTOS_FARMACIA_POPULAR.values():
        total += len(meds)
    return total

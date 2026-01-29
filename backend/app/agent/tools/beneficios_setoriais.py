"""Tools para orientação sobre benefícios setoriais.

Fornece informações sobre benefícios para grupos específicos:
- Agricultores familiares (PRONAF, Garantia-Safra, PAA, PNAE)
- Trabalhadores informais / Entregadores de app (MEI, INSS)
- Funcionários públicos (Vale-alimentação, auxílio-saúde)
"""

from typing import Optional


def consultar_beneficios_agricultores(
    regiao: Optional[str] = None,
    atividade: Optional[str] = None
) -> dict:
    """Orienta sobre benefícios para agricultores familiares.

    Args:
        regiao: Região do agricultor (SEMIARIDO, NORTE, NORDESTE, etc.)
        atividade: Tipo de atividade (CULTIVO, PESCA, PECUARIA, etc.)

    Returns:
        dict: Informações sobre benefícios disponíveis
    """
    beneficios = []

    # PRONAF - Programa Nacional de Fortalecimento da Agricultura Familiar
    beneficios.append({
        "codigo": "PRONAF",
        "nome": "Programa Nacional de Fortalecimento da Agricultura Familiar",
        "descricao": "Crédito rural com juros baixos (0,5% a 6% ao ano) para custeio e investimento",
        "valor": "Até R$ 500 mil por ano safra, dependendo da linha",
        "requisitos": [
            "Possuir DAP (Declaração de Aptidão ao PRONAF) ou CAF (Cadastro Nacional da Agricultura Familiar)",
            "Renda bruta anual de até R$ 500 mil",
            "Explorar área de até 4 módulos fiscais",
            "Mão de obra predominantemente familiar"
        ],
        "linhas_credito": [
            {"nome": "Pronaf Custeio", "juros": "3% a 4%", "prazo": "Até 2 anos"},
            {"nome": "Pronaf Mais Alimentos", "juros": "4%", "prazo": "Até 10 anos"},
            {"nome": "Pronaf Mulher", "juros": "3%", "prazo": "Até 10 anos"},
            {"nome": "Pronaf Jovem", "juros": "3%", "prazo": "Até 10 anos"},
            {"nome": "Pronaf Agroecologia", "juros": "3%", "prazo": "Até 10 anos"},
            {"nome": "Pronaf Bioeconomia", "juros": "3%", "prazo": "Até 12 anos"},
        ],
        "onde_solicitar": "Bancos credenciados (Banco do Brasil, Caixa, cooperativas de crédito rural)",
        "documentos": ["DAP/CAF", "CPF", "RG", "Comprovante de residência", "Projeto de crédito"],
        "link": "https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/pronaf"
    })

    # Garantia-Safra - Específico para semiárido
    if regiao in [None, "SEMIARIDO", "NORDESTE", "NORTE_MG", "NORTE_ES"]:
        beneficios.append({
            "codigo": "GARANTIA_SAFRA",
            "nome": "Garantia-Safra",
            "descricao": "Benefício para agricultores que perdem safra por seca ou excesso de chuvas",
            "valor": "R$ 1.200,00 (parcela única)",
            "requisitos": [
                "Agricultura familiar no semiárido (área da SUDENE)",
                "Área cultivada de 0,6 a 5 hectares",
                "Cultivo de feijão, milho, arroz, algodão ou mandioca",
                "Renda familiar mensal de até 1,5 salário mínimo",
                "Adesão do município ao programa"
            ],
            "quando_recebe": "Quando há perda de pelo menos 50% da safra por seca ou excesso hídrico",
            "onde_solicitar": "Sindicato dos Trabalhadores Rurais ou Secretaria de Agricultura do município",
            "documentos": ["DAP/CAF", "CPF", "RG", "Comprovante de residência"],
            "periodo_adesao": "Geralmente de maio a agosto de cada ano",
            "link": "https://www.gov.br/mda/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/programa-garantia-safra"
        })

    # PAA - Programa de Aquisição de Alimentos
    beneficios.append({
        "codigo": "PAA",
        "nome": "Programa de Aquisição de Alimentos",
        "descricao": "Governo compra alimentos da agricultura familiar para programas sociais",
        "valor": "Até R$ 12.000/ano por agricultor (modalidade CDS)",
        "requisitos": [
            "DAP/CAF ativa",
            "Produção própria (não pode ser atravessador)",
            "Regularidade fiscal"
        ],
        "modalidades": [
            {"nome": "Compra com Doação Simultânea (CDS)", "limite": "R$ 12.000/ano"},
            {"nome": "Compra Institucional", "limite": "R$ 20.000/ano"},
            {"nome": "Apoio à Formação de Estoques", "limite": "R$ 8.000"},
        ],
        "onde_vender": "CONAB, prefeituras, estados e órgãos federais",
        "documentos": ["DAP/CAF", "CPF", "RG", "Nota fiscal"],
        "link": "https://www.gov.br/cidadania/pt-br/acoes-e-programas/inclusao-produtiva-rural/paa"
    })

    # PNAE - Venda para alimentação escolar
    beneficios.append({
        "codigo": "PNAE",
        "nome": "Programa Nacional de Alimentação Escolar",
        "descricao": "Venda de alimentos para escolas públicas (30% das compras devem ser da agricultura familiar)",
        "valor": "Até R$ 40.000/ano por agricultor (via organização) ou R$ 20.000 (individual)",
        "requisitos": [
            "DAP/CAF ativa",
            "Produção própria",
            "Prioridade: assentados, quilombolas, indígenas, mulheres"
        ],
        "prioridades": [
            "1º Assentados da reforma agrária, comunidades indígenas e quilombolas",
            "2º Grupos formais (cooperativas e associações)",
            "3º Grupos informais e produtores individuais"
        ],
        "novidade_2024": "50% do valor de compras individuais deve ser no nome de mulheres",
        "onde_vender": "Chamadas públicas das prefeituras e secretarias estaduais de educação",
        "documentos": ["DAP/CAF", "CPF", "RG", "Certidões negativas", "Proposta de venda"],
        "link": "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae"
    })

    # Seguro Defeso - Para pescadores
    if atividade in [None, "PESCA"]:
        beneficios.append({
            "codigo": "SEGURO_DEFESO",
            "nome": "Seguro-Defeso (Pescador Artesanal)",
            "descricao": "Benefício de 1 salário mínimo durante o período de defeso (reprodução dos peixes)",
            "valor": "1 salário mínimo por mês de defeso",
            "requisitos": [
                "Pescador artesanal profissional",
                "Registro Geral de Pesca (RGP) ativo há pelo menos 1 ano",
                "Exclusividade na atividade pesqueira artesanal",
                "Não receber outro benefício (exceto pensão por morte ou auxílio-acidente)"
            ],
            "periodo": "Varia conforme espécie e região (geralmente 3-5 meses)",
            "onde_solicitar": "INSS ou Meu INSS (app/site)",
            "documentos": ["RGP", "CPF", "RG", "Comprovante de residência", "Atestado da colônia de pescadores"],
            "link": "https://www.gov.br/inss/pt-br/assuntos/seguro-defeso"
        })

    # Gerar texto resumido
    texto_linhas = [
        "🌾 BENEFÍCIOS PARA AGRICULTORES FAMILIARES",
        "",
    ]

    for b in beneficios:
        texto_linhas.extend([
            f"📌 {b['nome']}",
            f"   💰 {b['valor']}",
            f"   📋 {b['descricao'][:80]}...",
            ""
        ])

    texto_linhas.extend([
        "💡 DICA: O DAP/CAF é o documento mais importante!",
        "   Emita gratuitamente em: sindicato rural, EMATER ou secretaria de agricultura"
    ])

    return {
        "beneficios": beneficios,
        "total": len(beneficios),
        "resumo_texto": "\n".join(texto_linhas),
        "documento_principal": "DAP/CAF (Cadastro Nacional da Agricultura Familiar)",
        "onde_emitir_dap": "Sindicato de Trabalhadores Rurais, EMATER ou Secretaria de Agricultura do município"
    }


def consultar_beneficios_entregadores(
    tipo_trabalho: Optional[str] = None
) -> dict:
    """Orienta sobre benefícios e direitos para entregadores de app e trabalhadores informais.

    Args:
        tipo_trabalho: Tipo de trabalho (ENTREGADOR, MOTORISTA, AUTONOMO, MEI)

    Returns:
        dict: Informações sobre formalização e benefícios
    """
    beneficios = []

    # MEI - Microempreendedor Individual
    beneficios.append({
        "codigo": "MEI",
        "nome": "Microempreendedor Individual (MEI)",
        "descricao": "Formalização com CNPJ, notas fiscais e acesso a benefícios INSS",
        "custo_mensal": "R$ 75,60 (entregador/serviços) ou R$ 76,60 (comércio)",
        "composicao_das": {
            "INSS": "R$ 70,60 (5% do salário mínimo)",
            "ISS": "R$ 5,00 (serviços)",
            "ICMS": "R$ 1,00 (comércio, se houver)"
        },
        "beneficios_inss": [
            "Aposentadoria por idade (65 anos homem, 62 mulher)",
            "Auxílio por incapacidade temporária (antigo auxílio-doença)",
            "Auxílio por incapacidade permanente (aposentadoria por invalidez)",
            "Salário-maternidade (120 dias, após 10 meses de contribuição)",
            "Auxílio-reclusão (para dependentes)",
            "Pensão por morte (para dependentes)"
        ],
        "limite_faturamento": "R$ 81.000/ano (R$ 6.750/mês em média)",
        "pode_ter_funcionario": "Sim, 1 funcionário com salário mínimo ou piso da categoria",
        "cnae_entregador": "5320-2/02 - Serviços de entrega rápida",
        "onde_abrir": "Portal do Empreendedor (gov.br/mei)",
        "tempo_abertura": "Imediato (online, gratuito)",
        "link": "https://www.gov.br/empresas-e-negocios/pt-br/empreendedor"
    })

    # Contribuinte Individual (sem MEI)
    beneficios.append({
        "codigo": "CONTRIBUINTE_INDIVIDUAL",
        "nome": "Contribuinte Individual INSS",
        "descricao": "Contribuição ao INSS sem abrir empresa (não precisa ser MEI)",
        "opcoes_contribuicao": [
            {
                "plano": "Normal (20%)",
                "codigo_gps": "1007",
                "valor_minimo": f"R$ {1412 * 0.20:.2f} (20% do salário mínimo)",
                "valor_maximo": f"R$ {7786.02 * 0.20:.2f} (20% do teto INSS)",
                "beneficios": "Todos os benefícios + aposentadoria por tempo de contribuição"
            },
            {
                "plano": "Simplificado (11%)",
                "codigo_gps": "1163",
                "valor": f"R$ {1412 * 0.11:.2f} (11% do salário mínimo)",
                "beneficios": "Aposentadoria por idade, auxílio-doença, maternidade",
                "restricao": "NÃO conta para aposentadoria por tempo de contribuição"
            }
        ],
        "como_pagar": "Gerar GPS no site da Receita Federal ou app Meu INSS",
        "vencimento": "Dia 15 do mês seguinte",
        "carencia": {
            "auxilio_doenca": "12 meses",
            "salario_maternidade": "10 meses",
            "aposentadoria_idade": "180 meses (15 anos)"
        },
        "link": "https://www.gov.br/inss/pt-br"
    })

    # Projeto de Lei de Regulamentação (informativo)
    beneficios.append({
        "codigo": "PLP_12_2024",
        "nome": "Regulamentação de Motoristas de App (PLP 12/2024)",
        "descricao": "Projeto de lei para regulamentar motoristas de aplicativo (em tramitação)",
        "status": "Em tramitação no Congresso Nacional",
        "principais_pontos": [
            "Jornada máxima de 12 horas/dia",
            "Remuneração mínima de R$ 32,10/hora trabalhada",
            "Contribuição previdenciária: 7,5% do trabalhador + 20% da empresa",
            "IMPORTANTE: Ainda NÃO inclui entregadores de delivery (iFood, Rappi, etc.)"
        ],
        "observacao": "Entregadores de comida ainda não estão incluídos nesta regulamentação"
    })

    # Gerar texto resumido
    texto_linhas = [
        "🛵 BENEFÍCIOS PARA ENTREGADORES E TRABALHADORES INFORMAIS",
        "",
        "💡 VOCÊ TEM DUAS OPÇÕES PARA CONTRIBUIR AO INSS:",
        "",
        "1️⃣ ABRIR MEI (Recomendado)",
        "   • Custo: R$ 75,60/mês (já inclui INSS)",
        "   • Vantagens: CNPJ, notas fiscais, conta PJ, empréstimos",
        "   • Abertura: Grátis e imediata em gov.br/mei",
        "",
        "2️⃣ CONTRIBUINTE INDIVIDUAL (sem empresa)",
        f"   • Plano Simplificado: R$ {1412 * 0.11:.2f}/mês (11%)",
        f"   • Plano Completo: R$ {1412 * 0.20:.2f}/mês (20%)",
        "   • Pagar via GPS (carnê INSS)",
        "",
        "⚠️ IMPORTANTE:",
        "• Sem contribuição = SEM aposentadoria, auxílio-doença ou maternidade",
        "• Após 10 meses contribuindo = Salário-maternidade",
        "• Após 12 meses = Auxílio por incapacidade (auxílio-doença)",
        "",
        "📲 Consulte seu CNIS (histórico de contribuições):",
        "   App Meu INSS ou site meu.inss.gov.br"
    ]

    return {
        "beneficios": beneficios,
        "total": len(beneficios),
        "resumo_texto": "\n".join(texto_linhas),
        "recomendacao": "MEI é a opção mais vantajosa para entregadores",
        "custo_mei_mensal": "R$ 75,60",
        "link_mei": "https://www.gov.br/empresas-e-negocios/pt-br/empreendedor"
    }


def consultar_beneficios_servidor(
    esfera: Optional[str] = None,
    cargo: Optional[str] = None
) -> dict:
    """Orienta sobre benefícios para funcionários públicos.

    Args:
        esfera: Esfera do servidor (FEDERAL, ESTADUAL, MUNICIPAL)
        cargo: Tipo de cargo (EFETIVO, COMISSIONADO, TEMPORARIO)

    Returns:
        dict: Informações sobre benefícios de servidores
    """
    beneficios = []

    # Benefícios Federais (referência)
    beneficios.append({
        "codigo": "AUXILIO_ALIMENTACAO",
        "nome": "Auxílio-Alimentação/Refeição",
        "descricao": "Valor mensal para custeio de alimentação",
        "valores": {
            "federal_2024": "R$ 1.000,00/mês",
            "estadual": "Varia por estado (R$ 500 a R$ 1.500)",
            "municipal": "Varia por município"
        },
        "quem_recebe": "Servidores ativos em exercício",
        "base_legal_federal": "Lei nº 8.460/1992 e decretos regulamentadores",
        "observacao": "Benefício pecuniário, não integra remuneração para cálculos"
    })

    beneficios.append({
        "codigo": "AUXILIO_SAUDE",
        "nome": "Auxílio-Saúde / Assistência à Saúde Suplementar",
        "descricao": "Ressarcimento parcial de plano de saúde",
        "valores": {
            "federal_2024": "R$ 143 a R$ 287/mês (varia por faixa etária e salarial)",
            "estadual": "Varia por estado",
            "municipal": "Varia por município"
        },
        "requisitos": "Comprovar pagamento de plano de saúde",
        "beneficiarios": "Servidor + dependentes (cônjuge/filhos)",
        "base_legal_federal": "Portaria MGI nº 1.125/2024"
    })

    beneficios.append({
        "codigo": "AUXILIO_CRECHE",
        "nome": "Auxílio Pré-Escolar (Creche)",
        "descricao": "Auxílio para custear creche ou pré-escola de dependentes",
        "valores": {
            "federal_2024": "R$ 484,90/mês por dependente",
            "estadual": "Varia por estado",
            "municipal": "Varia por município"
        },
        "idade_limite": "Até 5 anos de idade (antes da educação fundamental)",
        "requisitos": "Comprovante de matrícula e pagamento da instituição",
        "base_legal_federal": "Decreto nº 977/1993"
    })

    beneficios.append({
        "codigo": "AUXILIO_TRANSPORTE",
        "nome": "Auxílio-Transporte",
        "descricao": "Valor para custear deslocamento residência-trabalho",
        "calculo": "Valor gasto - 6% da remuneração",
        "observacao": "Não é pago para quem usa veículo próprio ou transporte institucional",
        "requisitos": "Declarar trajeto e meio de transporte utilizado"
    })

    beneficios.append({
        "codigo": "AUXILIO_NATALIDADE",
        "nome": "Auxílio-Natalidade",
        "descricao": "Valor pago por ocasião do nascimento de filho",
        "valor_federal": "Menor remuneração do serviço público (1 SM)",
        "quem_recebe": "Servidor (se cônjuge também for servidor, só um recebe)",
        "prazo": "Solicitar em até 60 dias após o nascimento"
    })

    # Informações importantes
    observacoes = [
        "Benefícios municipais variam MUITO entre prefeituras",
        "Consulte sempre o RH ou portal do seu órgão",
        "Servidores temporários podem ter benefícios reduzidos",
        "Comissionados (cargos em comissão) têm os mesmos direitos dos efetivos"
    ]

    # Gerar texto resumido
    texto_linhas = [
        "👔 BENEFÍCIOS PARA SERVIDORES PÚBLICOS",
        "",
        "📋 PRINCIPAIS BENEFÍCIOS (valores federais 2024):",
        "",
        "🍽️ Auxílio-Alimentação: R$ 1.000/mês",
        "🏥 Auxílio-Saúde: R$ 143 a R$ 287/mês",
        "👶 Auxílio Pré-Escolar: R$ 484,90/mês por filho",
        "🚌 Auxílio-Transporte: Valor gasto - 6% da remuneração",
        "👣 Auxílio-Natalidade: 1 salário mínimo por nascimento",
        "",
        "⚠️ ATENÇÃO:",
        "• Valores ESTADUAIS e MUNICIPAIS podem ser diferentes",
        "• Consulte sempre o RH do seu órgão",
        "• Benefícios não integram base de cálculo de aposentadoria",
        "",
        "📍 ONDE CONSULTAR:",
        "• Federal: SIGEPE (gov.br/sigepe)",
        "• Estadual: Portal do servidor do seu estado",
        "• Municipal: RH da prefeitura ou portal de transparência"
    ]

    return {
        "beneficios": beneficios,
        "total": len(beneficios),
        "resumo_texto": "\n".join(texto_linhas),
        "observacoes": observacoes,
        "aviso": "Valores de referência federal. Estaduais e municipais podem variar.",
        "onde_consultar": {
            "federal": "SIGEPE (gov.br/sigepe)",
            "estadual": "Portal do servidor do seu estado",
            "municipal": "RH da prefeitura"
        }
    }

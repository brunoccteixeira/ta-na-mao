# Skill: Guia de Direitos Trabalhistas

Orientação sobre direitos trabalhistas por tipo de vínculo, com calculadoras e encaminhamento.

## Contexto

- Maioria do público-alvo trabalha informalmente ou em vínculos precários
- Desconhecimento de direitos básicos é generalizado
- Medo de "perder benefício" impede formalização
- Prazos legais são críticos (90 dias para seguro-desemprego, 2 anos para reclamar)

## Direitos por Tipo de Vínculo

### CLT (Carteira Assinada)
```
Direitos:
├── 13º salário (proporcional ou integral)
├── Férias + 1/3 constitucional
├── FGTS (8% do salário/mês)
├── Seguro-desemprego (se demitido sem justa causa)
├── Aviso prévio (30 dias + 3 por ano trabalhado)
├── Horas extras (50% dia útil, 100% domingo/feriado)
├── Vale-transporte (desconto máximo 6% do salário)
├── Licença-maternidade (120 dias)
├── Licença-paternidade (5 dias)
└── Estabilidade (gestante, acidentado, CIPA)
```

### Trabalho Doméstico (LC 150/2015)
```
Mesmos direitos da CLT, mais:
├── Jornada máxima: 8h/dia, 44h/semana
├── FGTS obrigatório (8%)
├── Seguro contra acidentes
├── Salário mínimo garantido
└── eSocial Doméstico (DAE mensal)
```

### MEI (Microempreendedor Individual)
```
Direitos previdenciários (após carência):
├── Aposentadoria por idade (15 anos de contribuição)
├── Auxílio-doença (12 meses de contribuição)
├── Salário-maternidade (10 meses de contribuição)
├── Auxílio-reclusão (para dependentes)
└── Pensão por morte (para dependentes)

Obrigações:
├── DAS mensal (~R$75 em 2025)
└── DASN-SIMEI anual (até 31/maio)
```

### Informal (Sem Carteira)
```
Direitos mesmo sem carteira:
├── Pode reclamar na Justiça do Trabalho (até 2 anos após sair)
├── Provas aceitas: mensagens, fotos, testemunhas, PIX
├── Todos os direitos da CLT se comprovado vínculo
└── Defensoria Pública atende de graça

Atenção:
├── Prazo: 2 anos para entrar com ação
├── Prescrição: pode cobrar últimos 5 anos
└── Não precisa de advogado (até 20 salários mínimos)
```

### Trabalhador Rural
```
Direitos específicos:
├── Seguro-Safra (seca/enchente)
├── Garantia-Safra (agricultura familiar)
├── PRONAF (crédito rural)
├── PAA (venda para o governo)
├── Aposentadoria rural (idade reduzida: 55 mulher, 60 homem)
└── Registro no SETR (Serviço Eletrônico de Trabalho Rural)
```

### Pescador Artesanal
```
Direitos específicos:
├── Seguro-Defeso (período de proibição de pesca)
├── Registro Geral de Pesca (RGP)
├── Aposentadoria especial (segurado especial)
└── Benefícios do PRONAF Pesca
```

## Calculadoras

### Rescisão Trabalhista
```python
# backend/app/agent/tools/calcular_rescisao.py
def calcular_rescisao(
    salario: float,
    meses_trabalhados: int,
    tipo_demissao: str,  # "sem_justa_causa", "justa_causa", "pedido"
    ferias_vencidas: bool = False,
) -> dict:
    resultado = {"itens": [], "total": 0}

    # Saldo de salário (dias trabalhados no mês)
    saldo = salario  # simplificado
    resultado["itens"].append({"nome": "Saldo de salário", "valor": saldo})

    # 13º proporcional
    decimo_terceiro = (salario / 12) * (meses_trabalhados % 12)
    resultado["itens"].append({"nome": "13º proporcional", "valor": decimo_terceiro})

    # Férias proporcionais + 1/3
    ferias_prop = (salario / 12) * (meses_trabalhados % 12)
    terco = ferias_prop / 3
    resultado["itens"].append({"nome": "Férias proporcionais + 1/3", "valor": ferias_prop + terco})

    if ferias_vencidas:
        ferias_venc = salario + (salario / 3)
        resultado["itens"].append({"nome": "Férias vencidas + 1/3", "valor": ferias_venc})

    if tipo_demissao == "sem_justa_causa":
        # Multa FGTS 40%
        fgts_total = salario * 0.08 * meses_trabalhados
        multa = fgts_total * 0.4
        resultado["itens"].append({"nome": "Multa FGTS (40%)", "valor": multa})

        # Aviso prévio
        dias_aviso = 30 + (3 * (meses_trabalhados // 12))
        aviso = (salario / 30) * min(dias_aviso, 90)
        resultado["itens"].append({"nome": f"Aviso prévio ({dias_aviso} dias)", "valor": aviso})

    resultado["total"] = sum(item["valor"] for item in resultado["itens"])
    return resultado
```

### Seguro-Desemprego
```python
def calcular_seguro_desemprego(
    salario_medio: float,
    meses_trabalhados: int,
    vezes_solicitado: int,  # 1ª, 2ª, 3ª+ vez
) -> dict:
    # Número de parcelas
    if vezes_solicitado == 1:
        parcelas = 4 if meses_trabalhados >= 12 else 0
    elif vezes_solicitado == 2:
        parcelas = 3 if meses_trabalhados >= 9 else 0
    else:
        parcelas = 3 if meses_trabalhados >= 6 else 0

    if meses_trabalhados >= 24:
        parcelas = 5

    # Valor da parcela (faixas 2025)
    if salario_medio <= 2041.39:
        valor = salario_medio * 0.8
    elif salario_medio <= 3402.65:
        valor = 1633.11 + (salario_medio - 2041.39) * 0.5
        valor = max(valor, 1633.11)
    else:
        valor = 2313.74  # teto

    valor = max(valor, 1412.00)  # piso = salário mínimo

    return {
        "valor_parcela": round(valor, 2),
        "parcelas": parcelas,
        "total": round(valor * parcelas, 2),
        "prazo_solicitar": "Até 120 dias após a demissão",
        "onde": "Posto do SINE, agência da Caixa ou pelo app Carteira Digital",
    }
```

## Fluxograma de Orientação
```
"Tenho problema no trabalho"
├── "Fui demitido"
│   ├── Sem justa causa → Calcular rescisão + seguro-desemprego + FGTS
│   ├── Com justa causa → Explicar direitos que mantém
│   └── Pedi demissão → Calcular rescisão (sem multa/seguro)
│
├── "Trabalho sem carteira"
│   └── → Orientar sobre provas + prazo 2 anos + Defensoria Pública
│
├── "Não recebo direitos"
│   ├── Horas extras → Explicar + orientar registro
│   ├── Férias → Explicar prazo + adicional
│   └── 13º → Explicar parcelas (nov/dez)
│
├── "Quero virar MEI"
│   └── → Skill mei-simplificado (impacto nos benefícios)
│
└── "Sofro assédio/discriminação"
    └── → Disque 100 + MPT + Defensoria + CREAS
```

## Mensagens (Linguagem Simples)

### Demissão sem Justa Causa
```
Você foi mandado embora sem justa causa. Você tem direito a receber:

💰 Saldo de salário: R$ {{saldo}}
💰 13º proporcional: R$ {{decimo_terceiro}}
💰 Férias + 1/3: R$ {{ferias}}
💰 Multa do FGTS (40%): R$ {{multa}}
💰 Aviso prévio: R$ {{aviso}}

📋 Total estimado: R$ {{total}}

⏰ Importante:
- Você tem até 120 dias para pedir o seguro-desemprego
- Pode sacar o FGTS na Caixa
- Se não receber tudo, procure a Defensoria Pública (é de graça)
```

## Arquivos Relacionados
- `backend/app/agent/tools/calcular_rescisao.py` - Calculadora de rescisão
- `backend/app/agent/tools/calcular_seguro.py` - Calculadora seguro-desemprego
- `backend/app/agent/tools/direitos_trabalhistas.py` - Guia por vínculo
- `frontend/src/data/benefits/sectoral.json` - Benefícios setoriais

## Referências
- CLT: https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
- LC 150/2015 (doméstico): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp150.htm
- Seguro-desemprego: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/seguro-desemprego

---
name: jornada-cidadao
description: Mapear jornada completa do cidadão para cada benefício social
---

Mapeia o caminho COMPLETO que um cidadão percorre para acessar cada benefício, pensando em quem tem baixa escolaridade, sem internet, sem documentos.

## Quando Usar

- Ao implementar ou revisar uma feature de benefício
- Para identificar barreiras de acesso que o sistema não cobre
- Para validar que nossas instruções são completas e realistas
- Para criar conteúdo acessível sobre como acessar um benefício

## Template de Jornada (7 Etapas)

### Etapa 1: DESCOBRE
> Como o cidadão fica sabendo que o benefício existe?

- App Tá na Mão / chat com agente
- CRAS / assistente social
- UBS / agente comunitário de saúde
- Boca a boca (vizinho, familiar, igreja)
- Rádio comunitária, TV
- Programa de busca ativa (equipes volantes)

### Etapa 2: VERIFICA
> Como sabe se tem direito?

- Simulador no app (motor de elegibilidade)
- Conversa com agente IA
- Atendimento no CRAS
- Consulta no Meu SUS Digital / Meu INSS
- Telefone: Disque 136 (SUS), 121 (INSS), 111 (CadÚnico)

### Etapa 3: PREPARA
> Quais documentos precisa? Onde tirar os que não tem?

```markdown
| Documento | Onde conseguir | Custo | Prazo |
|-----------|---------------|-------|-------|
| CPF | Correios, Receita Federal, Banco do Brasil | Grátis | Imediato |
| RG | Poupa Tempo, Secretaria de Segurança | Grátis (1ª via) | 7-30 dias |
| Comprovante de residência | Conta de luz/água ou declaração do CRAS | Grátis | Imediato |
| CadÚnico | CRAS | Grátis | 7-45 dias |
| Receita médica | UBS/SUS | Grátis | Depende da consulta |
```

### Etapa 4: AUTORIZA
> Pré-requisitos obrigatórios antes de acessar

- Cadastro no CadÚnico (se obrigatório)
- Autorização via Meu SUS Digital ou UBS (para programas de saúde)
- Inscrição no programa específico
- Entrevista social no CRAS (para benefícios assistenciais)

### Etapa 5: ACESSA
> Onde ir? Com alternativas para diferentes perfis.

```markdown
| Canal | Endereço/Como | Horário | Observação |
|-------|--------------|---------|------------|
| Farmácia credenciada | Buscar no app ou site | Comercial | Nem toda farmácia participa |
| UBS | Mais próxima | 7h-17h | Pode precisar de agendamento |
| CRAS | Buscar por CEP | 8h-17h | Levar documentos |
| App | Meu SUS Digital, Meu CadÚnico | 24h | Precisa de celular + internet |
| Telefone | 136, 121, 111 | Comercial | Alternativa sem internet |
```

### Etapa 6: RECEBE
> O que acontece no local? Frequência? Quantidade?

- O que exatamente recebe (medicamento, benefício, valor)
- Quantidade por vez
- Frequência (mensal, a cada 56 dias, etc.)
- Se tem limite de vezes
- Como conferir se recebeu corretamente

### Etapa 7: RENOVA
> Quando e como renovar?

- Validade da autorização/receita
- Periodicidade de renovação do CadÚnico (a cada 2 anos)
- Recadastramento do programa específico
- O que acontece se perder o prazo

## Paths Alternativos (Obrigatórios)

Para CADA benefício mapeado, verificar estes 5 cenários:

### Sem celular/internet
```
- Pode ir direto ao CRAS/UBS?
- Tem telefone como alternativa? Qual número?
- Agente comunitário pode ajudar?
- Existe posto de atendimento presencial?
```

### Sem documentos
```
- O CRAS pode ajudar a tirar documentos?
- Existe atendimento itinerante?
- Declaração de residência substitui comprovante?
- Para pessoa em situação de rua: qual a alternativa?
```

### Menor de idade
```
- Precisa de responsável legal?
- Quem pode ser representante?
- Escola pode intermediar?
- Conselho Tutelar pode ajudar?
```

### Pessoa em situação de rua
```
- Centro POP como referência
- CREAS para atendimento especializado
- Não precisa de comprovante de residência (usa declaração do CRAS)
- Abordagem social pode iniciar o processo
```

### Zona rural / sem transporte
```
- Equipe volante do CRAS atende?
- Busca ativa da Estratégia Saúde da Família
- Transporte municipal para saúde?
- Agente comunitário pode levar formulários?
```

## Armadilhas Comuns

Lista de erros que cidadãos cometem frequentemente:

| Armadilha | Benefício | O que acontece |
|-----------|-----------|----------------|
| Ir à farmácia sem autorização prévia | Farmácia Popular / Dignidade Menstrual | Farmácia recusa; cidadão perde a viagem |
| Achar que qualquer farmácia serve | Farmácia Popular | Só farmácias credenciadas aceitam |
| Não levar receita médica válida | Farmácia Popular | Receita do SUS tem validade (120/365 dias) |
| Achar que CadÚnico é opcional | Vários | Perde acesso a múltiplos benefícios |
| Não atualizar CadÚnico | Bolsa Família | Pode ter benefício bloqueado |
| Ir ao CRAS sem documentos | CadÚnico | Não consegue se cadastrar |
| Confundir BPC com aposentadoria | BPC/LOAS | Não solicita porque acha que precisa ter contribuído |

## Canais de Suporte

| Canal | Número/Endereço | Horário | Para quê |
|-------|-----------------|---------|----------|
| Disque 136 | 136 | 24h | SUS, Farmácia Popular, saúde |
| Ligue 121 | 121 | 7h-22h (seg-sáb) | INSS, aposentadoria, BPC |
| Ligue 111 | 111 | 7h-19h (seg-sex) | CadÚnico, Bolsa Família |
| Ligue 180 | 180 | 24h | Violência contra mulher |
| Disque 100 | 100 | 24h | Direitos humanos, idoso, PcD |
| CRAS | Buscar por CEP no app | 8h-17h (seg-sex) | Assistência social geral |
| UBS | Buscar por CEP | 7h-17h (seg-sex) | Saúde, receitas, autorizações |
| Defensoria Pública | Buscar por estado | Comercial | Quando direito é negado |

## Formato de Saída

```markdown
# Jornada: [Nome do Benefício]
**Público**: [Quem tem direito]
**Complexidade**: [Baixa/Média/Alta — quantas etapas obrigatórias]

## Caminho Principal
1. **Descobre**: [como]
2. **Verifica**: [como]
3. **Prepara**: [documentos]
4. **Autoriza**: [pré-requisitos]
5. **Acessa**: [onde]
6. **Recebe**: [o quê, quanto, quando]
7. **Renova**: [quando, como]

## Caminhos Alternativos
- Sem celular: [...]
- Sem documentos: [...]
- Menor de idade: [...]

## Armadilhas
- ⚠️ [armadilha 1]
- ⚠️ [armadilha 2]

## Suporte
- 📞 [telefone relevante]
- 🏢 [local presencial]
```

## Regras

- **NUNCA** assumir que cidadão tem smartphone, internet ou documentos
- **SEMPRE** incluir alternativa presencial/telefone
- **SEMPRE** listar documentos com onde conseguir (não só quais)
- **SEMPRE** alertar sobre armadilhas comuns
- Linguagem simples (5ª série) em todo conteúdo voltado ao cidadão
- Verificar cada etapa contra `/auditor-beneficios` para precisão legal

---
name: auditor-beneficios
description: Auditar features de benefícios contra legislação vigente
---

Skill de auditoria para garantir que cada feature de benefício no sistema está conforme a legislação vigente. **Cada dado errado é um cidadão que perde acesso a um direito.**

## Quando Usar

- Antes de considerar qualquer feature de benefício como "pronta"
- Após adicionar/modificar dados de um benefício no catálogo
- Periodicamente para revisar dados já publicados
- Quando legislação muda (nova Portaria, Decreto, etc.)

## Checklist Obrigatório (12 itens)

Toda feature de benefício DEVE passar por estes 12 pontos:

| # | Item | Verificação |
|---|------|-------------|
| 1 | **Base legal** | Lei/Decreto/Portaria identificada com número e data |
| 2 | **Elegibilidade** | Critérios verificados contra TEXTO DA LEI (não interpretação) |
| 3 | **Faixa etária** | Limites de idade documentados, se aplicável |
| 4 | **CadÚnico** | Requisito verificado (obrigatório/opcional/dispensado, para quais grupos) |
| 5 | **Documentos** | Lista completa, diferenciada por grupo (idoso, PcD, estudante, etc.) |
| 6 | **Valores/quantidades** | Com fonte oficial (valor exato, % desconto, quantidade, periodicidade) |
| 7 | **Canais de acesso** | TODOS os canais: app, UBS, CRAS, farmácia, presencial, telefone |
| 8 | **Prazos e validades** | Receita, autorização, renovação, vigência do benefício |
| 9 | **Restrições geográficas** | Cobertura: nacional, estadual, municipal; limitações documentadas |
| 10 | **Dados hardcoded** | Frontend conferido contra backend E legislação |
| 11 | **Disclaimers** | Onde dados são simplificados ou incompletos, há aviso claro |
| 12 | **Data de verificação** | Última auditoria registrada no código ou docs |

## Protocolo de Auditoria

### Passo 1: Identificar o que dizemos
```
1. Ler o catálogo de benefícios no código (src/data/benefits*.ts, backend/data/)
2. Ler as views/componentes que exibem o benefício
3. Ler as tools do agente que respondem sobre o benefício
4. Listar TODAS as claims que fazemos (valores, requisitos, prazos, etc.)
```

### Passo 2: Buscar o que a lei diz
```
1. WebSearch: "[nome do programa] site:gov.br"
2. WebSearch: "[nome do programa] lei decreto portaria site:planalto.gov.br"
3. WebFetch na página oficial do programa em gov.br
4. WebFetch no texto da lei/decreto no Planalto
5. Buscar Portarias atualizadoras mais recentes
```

### Passo 3: Cruzar e relatar gaps
```
Para cada claim no código, verificar:
- É exatamente o que a lei diz? → ✅ Conforme
- Está simplificado mas correto? → ⚠️ Simplificado (adicionar disclaimer)
- Está errado? → ❌ Incorreto (corrigir imediatamente)
- Falta informação importante? → 🔴 Incompleto (adicionar)
```

## Formato do Relatório

```markdown
# Auditoria: [Nome do Benefício]
**Data**: YYYY-MM-DD
**Legislação base**: [Lei/Decreto com número]

| Claim no sistema | O que a lei diz | Status | Ação |
|------------------|-----------------|--------|------|
| "100% grátis" | Art. X: 90% desconto | ❌ Incorreto | Corrigir valor |
| "CadÚnico opcional" | Art. Y: obrigatório | ❌ Incorreto | Corrigir texto |
| "Faixa etária: todos" | Art. Z: 10-49 anos | 🔴 Incompleto | Adicionar faixa |
| "27 medicamentos" | RENAME: 100+ itens | ⚠️ Simplificado | Disclaimer |

## Gaps Encontrados
1. [Descrição do gap + impacto no cidadão]

## Ações Corretivas
1. [Arquivo + linha + o que corrigir]

## Fontes Consultadas
- [Lei X - URL]
- [Portaria Y - URL]
- [Página gov.br - URL]
```

## Fontes Obrigatórias por Área

### Saúde
- gov.br/saude
- Portarias GM/MS (Gabinete do Ministro / Ministério da Saúde)
- DataSUS (datasus.saude.gov.br)
- RENAME (Relação Nacional de Medicamentos)
- Farmácia Popular: gov.br/saude/farmacia-popular

### Assistência Social
- gov.br/mds (Ministério do Desenvolvimento Social)
- SAGI (Secretaria de Avaliação de Informação)
- SUAS (Sistema Único de Assistência Social)
- CadÚnico: Decreto 11.016/2022

### Previdência
- gov.br/inss
- Decreto 3.048/1999 (Regulamento da Previdência)
- Lei 8.213/1991 (Planos de Benefícios)

### Habitação
- gov.br/cidades
- Caixa Econômica Federal
- Minha Casa Minha Vida: Lei 14.620/2023

### Educação
- gov.br/mec
- FNDE (Fundo Nacional de Desenvolvimento da Educação)

## Exemplos de Erros Críticos Já Encontrados

| Benefício | Erro | Impacto |
|-----------|------|---------|
| Farmácia Popular | Fraldas marcadas como 100% grátis | São 40% desconto — cidadão vai à farmácia e descobre que tem que pagar |
| Dignidade Menstrual | Quantidade "varia" | São 40 absorventes a cada 56 dias — cidadã não sabe o que pedir |
| Dignidade Menstrual | Faixa etária ausente | Lei define 10-49 anos — sem filtro, informamos errado |
| Dignidade Menstrual | Falta etapa de autorização | Obrigatório via Meu SUS Digital ou UBS — cidadã vai à farmácia sem |
| Catálogo geral | FAQ diz CadÚnico opcional p/ estudantes | É obrigatório para todos — estudante deixa de se cadastrar |

## Regras

- **NUNCA** marcar feature como pronta sem rodar o checklist de 12 itens
- **NUNCA** usar porcentagens/valores sem fonte legal citada no código
- **SEMPRE** diferenciar "grátis" (100% subsidiado) de "com desconto" (subsidiado parcialmente)
- **SEMPRE** registrar data da última auditoria em comentário no código
- Se dados são simplificados, DEVE haver disclaimer visível ao cidadão

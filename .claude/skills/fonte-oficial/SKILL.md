---
name: fonte-oficial
description: Catálogo de fontes oficiais e protocolo de validação de dados
---

Catálogo de fontes oficiais brasileiras e protocolo para validar qualquer dado antes de incluir no sistema. Nenhum dado entra sem fonte verificável.

## Quando Usar

- Antes de adicionar qualquer dado novo ao sistema (valor, requisito, prazo)
- Para validar uma claim existente no código
- Para resolver conflito entre fontes
- Para atualizar dados após mudança legislativa

## Hierarquia de Fontes

Fontes listadas em ordem de autoridade. Em caso de conflito, a fonte de nível mais alto prevalece.

| Nível | Tipo | Exemplo | Confiabilidade |
|-------|------|---------|----------------|
| 1 | **Texto da Lei/Decreto/Portaria** | planalto.gov.br, DOU | Definitiva |
| 2 | **Página oficial do programa** | gov.br/saude/farmacia-popular | Muito alta |
| 3 | **Cartilha/manual oficial** | Manual do CadÚnico, Guia SUAS | Alta |
| 4 | **Dados abertos governamentais** | dados.gov.br, SAGI, DataSUS | Alta |
| 5 | **API oficial** | Conecta Gov.br, IBGE API | Alta |
| 6 | **Notícia de agência oficial** | Agência Brasil, Agência Gov | Média-alta |
| 7 | ❌ **Notícia de portal privado** | G1, Folha, UOL | NÃO usar como fonte primária |

### Regra de ouro
> Se não encontrou em fonte de nível 1-3, a informação NÃO entra no sistema como fato. Pode entrar como "informação não confirmada" com disclaimer.

## Catálogo de Fontes por Programa

### Farmácia Popular
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei de criação | Lei 10.858/2004 | Base legal do programa |
| Programa atual | Decreto 11.798/2023 | Regras vigentes, expansão |
| Portaria de medicamentos | Portarias GM/MS (atualizar anualmente) | Lista de medicamentos e descontos |
| RENAME | Relação Nacional de Medicamentos Essenciais | Lista completa de medicamentos SUS |
| Página oficial | gov.br/saude/farmacia-popular | Informações ao cidadão |
| Lista de farmácias | Consulta no app Meu SUS Digital | Farmácias credenciadas por CEP |

### Dignidade Menstrual
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 14.214/2021 | Instituiu o Programa |
| Decreto regulamentador | Decreto 11.432/2023 | Regulamentação |
| Portaria operacional | Portaria GM/MS 3.076/2024 | Regras de distribuição, quantidades |
| Página oficial | gov.br/saude (buscar dignidade menstrual) | Informações ao cidadão |
| Público-alvo | Lei 14.214, Art. 1º | Pessoas de 10-49 anos, CadÚnico |

### Bolsa Família
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 14.601/2023 | Recriação do programa |
| Decreto | Decreto 11.901/2024 | Regulamentação, valores |
| Página oficial | gov.br/mds/bolsa-familia | Informações ao cidadão |
| SAGI | aplicacoes.mds.gov.br/sagi | Dados e relatórios |
| Calendário | Caixa Econômica Federal | Datas de pagamento |

### BPC (Benefício de Prestação Continuada)
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 8.742/1993 (LOAS) | Base legal |
| Decreto | Decreto 6.214/2007 | Regulamentação |
| Atualizações | Decretos atualizadores (verificar vigência) | Renda per capita, critérios |
| INSS | gov.br/inss | Solicitação e acompanhamento |
| Valores | Vinculado ao salário mínimo | 1 salário mínimo vigente |

### Tarifa Social de Energia Elétrica
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 12.212/2010 | Base legal |
| Regulação | Resolução Normativa ANEEL | Descontos e critérios |
| Página oficial | gov.br (buscar tarifa social) | Informações ao cidadão |
| Distribuidoras | Sites das distribuidoras locais | Solicitação |

### CadÚnico
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Decreto | Decreto 11.016/2022 | Regulamentação atual |
| Manual | Manual de Gestão do CadÚnico (MDS) | Procedimentos operacionais |
| CECAD | cecad.cidadania.gov.br | Consulta pública de dados |
| Página oficial | gov.br/mds/cadunico | Informações ao cidadão |

### Minha Casa Minha Vida
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 14.620/2023 | Base legal (nova versão) |
| Caixa | caixa.gov.br/minha-casa-minha-vida | Faixas, valores, simulador |
| Página oficial | gov.br/cidades | Informações ao cidadão |

### Benefícios Previdenciários (INSS)
| Fonte | URL/Referência | O que contém |
|-------|---------------|--------------|
| Lei | Lei 8.213/1991 | Planos de benefícios |
| Regulamento | Decreto 3.048/1999 | Regulamento da Previdência |
| Meu INSS | meu.inss.gov.br | Solicitação e consulta |
| Tabela de valores | INSS (atualização anual) | Teto, mínimo, alíquotas |

## Protocolo de Validação (4 Passos)

### Passo 1: Buscar texto legal original
```
1. WebSearch: "[nome programa] lei decreto site:planalto.gov.br"
2. WebFetch no resultado para ler o texto da lei
3. Identificar artigos relevantes para a claim
4. Anotar: número da lei, artigo, parágrafo, inciso
```

### Passo 2: Verificar vigência
```
1. Verificar se a lei/decreto não foi revogada
2. Buscar: "[número da lei] revogada alterada site:planalto.gov.br"
3. Verificar Portarias atualizadoras (especialmente para valores e listas)
4. Checar data: legislação anterior a 2023 pode ter sido atualizada
```

### Passo 3: Cruzar com fonte adicional
```
1. Buscar a página oficial do programa em gov.br
2. WebFetch na página oficial
3. Comparar: o que a lei diz vs. o que gov.br diz
4. Se divergem: a lei prevalece (mas reportar divergência)
```

### Passo 4: Registrar
```
Dado: [o que estamos afirmando]
Fonte primária: [Lei X, Art. Y]
Fonte secundária: [URL gov.br]
Data de consulta: [YYYY-MM-DD]
Próxima verificação: [quando revisar — ex: a cada Portaria anual]
```

## Template de Citação no Código

Para dados hardcoded ou constantes no sistema:

```typescript
// Fonte: Lei 14.214/2021, Art. 1º, §2º
// Verificado em: 2026-02-07
// Próxima verificação: quando houver nova Portaria GM/MS
const DIGNIDADE_MENSTRUAL_FAIXA_ETARIA = { min: 10, max: 49 };

// Fonte: Portaria GM/MS 3.076/2024
// Verificado em: 2026-02-07
const DIGNIDADE_MENSTRUAL_QUANTIDADE = {
  absorventes: 40,
  periodicidade_dias: 56,
};
```

```python
# Fonte: Decreto 11.798/2023
# Verificado em: 2026-02-07
FARMACIA_POPULAR_DESCONTO_FRALDAS = 0.40  # 40% de desconto, NÃO é grátis

# Fonte: Lei 14.601/2023, Art. 3º
# Verificado em: 2026-02-07
BOLSA_FAMILIA_RENDA_PER_CAPITA_LIMITE = 218.00  # R$ 218,00/pessoa
```

## Fontes Gerais de Referência

| Tipo | Fonte | URL | Uso |
|------|-------|-----|-----|
| Legislação federal | Planalto | planalto.gov.br | Leis, Decretos, MPs |
| Diário Oficial | DOU | in.gov.br | Portarias, resoluções |
| Busca legislativa | LexML | lexml.gov.br | Busca consolidada |
| Dados abertos | Portal de Dados | dados.gov.br | Datasets governamentais |
| Dados sociais | SAGI/MDS | aplicacoes.mds.gov.br/sagi | Relatórios e painéis |
| Saúde | DataSUS | datasus.saude.gov.br | Dados de saúde |
| Demografia | IBGE | ibge.gov.br | Censo, pesquisas |
| Notícias oficiais | Agência Brasil | agenciabrasil.ebc.com.br | Notícias governamentais |
| Notícias do governo | Agência Gov | gov.br/noticias | Comunicados oficiais |

## Formato de Saída (Validação de Claim)

```markdown
# Validação: [claim a ser verificada]

## Claim
> "[texto exato que está no sistema]"
> Arquivo: [caminho:linha]

## Fontes Consultadas
1. **[Fonte primária]**: [o que diz]
2. **[Fonte secundária]**: [o que diz]

## Veredito
- [ ] ✅ Conforme — dado está correto e atualizado
- [ ] ⚠️ Parcialmente correto — [o que falta/precisa ajustar]
- [ ] ❌ Incorreto — [o que está errado e como corrigir]
- [ ] 🔴 Sem fonte — não encontrou base legal (NÃO publicar)

## Citação para o Código
// Fonte: [Lei/Decreto/Portaria]
// Verificado em: [data]
```

## Regras

- **NUNCA** incluir dado sem fonte de nível 1-5
- **NUNCA** usar portal privado como fonte primária
- **SEMPRE** verificar vigência da lei antes de citar
- **SEMPRE** cruzar com pelo menos 1 fonte adicional
- **SEMPRE** registrar data de consulta
- Se fonte conflita com outra: o texto legal (nível 1) prevalece
- Se dado não tem fonte verificável: NÃO entra no sistema como fato
- Atualizar catálogo quando novos programas forem adicionados

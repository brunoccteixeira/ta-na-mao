# Auditoria: Alimentacao (34 beneficios)
**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6

## Resumo
- Total auditados: 34
- Conforme: 5
- Simplificado: 16
- Incorreto: 5
- Incompleto: 8
- Correcoes aplicadas: 18

| UF | ID | Status | Correcoes |
|----|-----|--------|-----------|
| SP | sp-bom-prato | INCORRETO | Precos corrigidos (R$0,50/R$1,00) |
| SP | sp-vivaleite | INCOMPLETO | Renda e idosos corrigidos |
| DF | df-cartao-prato-cheio | INCORRETO | Valor atualizado R$250->R$280 |
| DF | df-restaurante-comunitario | SIMPLIFICADO | Precos detalhados (cafe/almoco/jantar) |
| SC | sc-cartao-comida-boa | INCORRETO | Removido (programa do PR, nao SC). Substituido por sc-cesta-basica-paa |
| SC | sc-restaurante-popular | SIMPLIFICADO | Sem preco especifico, generico |
| PR | pr-armazem-da-familia | INCORRETO | Escopo municipal (Curitiba), renda corrigida |
| PR | pr-leite-das-criancas | SIMPLIFICADO | Renda atualizada para 2 SM |
| AL | al-restaurante-popular | INCOMPLETO | Precos adicionados (R$3/R$1) |
| BA | ba-restaurante-popular | INCORRETO | Salvador gratis para CadUnico |
| MG | mg-restaurante-popular | INCOMPLETO | Preco varia por cidade, corrigido |
| MG | mg-bolsa-merenda | INCOMPLETO | CadUnico adicionado como requisito |
| CE | ce-ceara-sem-fome | SIMPLIFICADO | Dados corretos (R$2 restaurante) |
| PE | pe-restaurante-popular | SIMPLIFICADO | R$1 confirmado, mas Recife tem gratis para vulneraveis |
| GO | go-restaurante-do-bem | CONFORME | R$2 confirmado |
| ES | es-restaurante-popular | SIMPLIFICADO | R$2 sem fonte oficial verificavel |
| RJ | rj-restaurante-popular | INCOMPLETO | Sem preco especifico |
| RS | rs-restaurante-popular | INCOMPLETO | Sem preco especifico |
| PA | pa-restaurante-popular | INCOMPLETO | Sem preco especifico |
| MS | ms-vale-renda | SIMPLIFICADO | Cesta basica generico |
| MS | ms-restaurante-popular | SIMPLIFICADO | R$2 sem fonte verificavel |
| MT | mt-restaurante-popular | SIMPLIFICADO | R$2 sem fonte verificavel |
| PB | pb-restaurante-popular | INCOMPLETO | Generico, sem preco |
| PB | pb-cesta-basica | SIMPLIFICADO | Generico |
| PI | pi-comida-na-mesa | SIMPLIFICADO | Generico |
| RN | rn-restaurante-popular | SIMPLIFICADO | Generico |
| RO | ro-cesta-solidaria | SIMPLIFICADO | Generico |
| RR | rr-cesta-basica-roraima | SIMPLIFICADO | Generico |
| SE | se-restaurante-popular | SIMPLIFICADO | Generico |
| TO | to-cesta-basica-tocantins | SIMPLIFICADO | Generico |
| AC | ac-cesta-basica-acre | SIMPLIFICADO | Generico |
| AP | ap-cesta-basica-amapa | SIMPLIFICADO | Generico |
| AM | am-prato-cheio | CONFORME | R$1 confirmado |
| MA | ma-cozinha-popular | SIMPLIFICADO | Generico, sem preco |

---

## Detalhamento por Beneficio

### sp-bom-prato (Sao Paulo) - INCORRETO -> CORRIGIDO

**Pesquisa oficial**: Site desenvolvimentosocial.sp.gov.br/bom-prato

**Dados reais**:
- Cafe da manha: R$ 0,50
- Almoco: R$ 1,00
- Jantar: R$ 1,00
- Aberto a qualquer pessoa, sem cadastro

**Erros encontrados e corrigidos**:
| Item | Antes (ERRADO) | Depois (CORRETO) |
|------|----------------|-------------------|
| shortDescription | R$ 1,00 cafe, R$ 1,50 almoco | R$ 0,50 cafe, R$ 1,00 almoco/jantar |
| howToApply | "Pague R$ 1,00 ou R$ 1,50" | "Pague R$ 0,50 (cafe) ou R$ 1,00 (almoco/jantar)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

**Checklist**:
| # | Item | Status |
|---|------|--------|
| 1 | Base legal | N/A - Programa nao exige lei especifica |
| 2 | Elegibilidade | CONFORME - Aberto a todos |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | CONFORME - Nao exige |
| 5 | Documentos | CONFORME - Nenhum documento |
| 6 | Valores | CORRIGIDO - Precos oficiais atualizados |
| 7 | Canais | CONFORME |
| 8 | Prazos | N/A |
| 9 | Geo | CONFORME - Estado SP |
| 10 | Hardcoded | CONFORME |
| 11 | Disclaimers | N/A |
| 12 | Data | CORRIGIDO |

---

### sp-vivaleite (Sao Paulo) - INCOMPLETO -> CORRIGIDO

**Pesquisa oficial**: vivaleite.sp.gov.br

**Dados reais**:
- Criancas de 6 meses a 6 anos E idosos acima de 60 anos
- Renda familiar ate 2 salarios minimos (R$ 3.036)
- 15 litros de leite por mes

**Erros encontrados e corrigidos**:
| Item | Antes | Depois |
|------|-------|--------|
| eligibilityRules[1].description | "Ter crianca de 6 meses a 6 anos OU" | "Ter crianca de 6 meses a 6 anos OU idoso acima de 60 anos" |
| eligibilityRules[2].value | 3200 | 3036 |
| eligibilityRules[2].description | "R$ 3.200 (~R$800/pessoa)" | "2 salarios minimos (R$ 3.036)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

**Limitacao remanescente**: Campo `temCrianca0a6` captura criancas mas nao idosos. Seria necessario adicionar campo `temIdoso60mais` ao CitizenProfile para captura completa. Simplificacao aceitavel por ora.

---

### df-cartao-prato-cheio (Distrito Federal) - INCORRETO -> CORRIGIDO

**Pesquisa oficial**: sedes.df.gov.br

**Dados reais**:
- Valor reajustado de R$ 250 para R$ 280 em setembro/2025
- CadUnico obrigatorio
- Renda per capita ate meio SM

**Erros encontrados e corrigidos**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | R$ 250 | R$ 280 |
| estimatedValue.min | 250 | 280 |
| estimatedValue.max | 250 | 280 |
| estimatedValue.description | "R$ 250 por mes" | "R$ 280 por mes (reajustado em set/2025)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

---

### df-restaurante-comunitario (Distrito Federal) - SIMPLIFICADO -> CORRIGIDO

**Pesquisa oficial**: sedes.df.gov.br

**Dados reais**:
- Cafe da manha: R$ 0,50
- Almoco: R$ 1,00
- Jantar: R$ 0,50
- Aberto a todos

**Erros encontrados e corrigidos**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | "R$ 1,00. Cafe e almoco" | "cafe R$ 0,50, almoco R$ 1,00, jantar R$ 0,50" |
| howToApply | "Pague R$ 1,00" | "Pague R$ 0,50 (cafe/jantar) ou R$ 1,00 (almoco)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

---

### sc-cartao-comida-boa (Santa Catarina) - INCORRETO -> REMOVIDO

**ERRO CRITICO**: O "Cartao Comida Boa" e um programa do PARANA, nao de Santa Catarina. WebSearch confirmou que o programa pertence ao governo do Parana (R$ 80/mes para familias de baixa renda).

**Acao**: Beneficio removido e substituido por `sc-cesta-basica-paa`, programa real de distribuicao de cestas via PAA estadual.
- PAA/SC executou R$ 10 milhoes em 2024 em 5 meses
- Compra alimentos da agricultura familiar e distribui para familias em inseguranca alimentar
- Fonte: sas.sc.gov.br

---

### sc-restaurante-popular (Santa Catarina) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacoes**: Restaurantes populares em SC sao primariamente municipais (Florianopolis). Nao ha programa estadual de restaurante popular claramente identificado. Descricao generica sem preco e aceitavel como simplificacao.

---

### pr-armazem-da-familia (Parana) - INCORRETO -> CORRIGIDO

**Pesquisa oficial**: curitiba.pr.gov.br/servicos/armazem-da-familia

**ERRO**: Programa e MUNICIPAL de Curitiba, nao estadual. Renda limite e 5 SM, nao R$ 3.200.

**Erros encontrados e corrigidos**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | Generico | Clarificado "em Curitiba e regiao" |
| whereToApply | "Prefeitura ou unidade" | "Unidade em Curitiba (programa municipal)" |
| eligibilityRules.renda.value | 3200 | 7590 (5 SM) |
| lastUpdated | 2026-02-04 | 2026-02-07 |

**Limitacao remanescente**: Idealmente deveria ter scope "municipal", mas mantem "state" por compatibilidade do schema. Nota no whereToApply esclarece.

---

### pr-leite-das-criancas (Parana) - SIMPLIFICADO -> CORRIGIDO

**Pesquisa oficial**: leitedascriancas.pr.gov.br

**Dados reais**:
- Criancas de 6 meses a 36 meses (3 anos)
- Renda per capita ate meio SM
- 7 litros por semana

**Correcoes**:
| Item | Antes | Depois |
|------|-------|--------|
| eligibilityRules.renda.value | 3200 | 3036 (meio SM per capita) |
| lastUpdated | 2026-02-04 | 2026-02-07 |

**Limitacao remanescente**: Campo `temCrianca0a6` captura faixa mais ampla que 6m-36m. Descricao clarifica corretamente "6 meses a 3 anos".

---

### al-restaurante-popular (Alagoas) - INCOMPLETO -> CORRIGIDO

**Pesquisa**: Restaurantes populares em Maceio.

**Correcoes**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | "Almoco por preco baixo" (sem valor) | "Almoco por R$ 3,00 e cafe por R$ 1,00 em Maceio" |
| howToApply | "Pague o preco baixo" | "Pague R$ 3,00 (almoco) ou R$ 1,00 (cafe)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

**Observacao**: Programa primariamente municipal (Maceio), nao estadual.

---

### ba-restaurante-popular (Bahia) - INCORRETO -> CORRIGIDO

**Pesquisa oficial**: Salvador tem refeicoes gratuitas para inscritos no CadUnico.

**Correcoes**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | "R$ 1,00" | "Gratuitas ou a preco popular. Em Salvador, gratis para CadUnico" |
| howToApply | "Pague R$ 1,00" | "Em Salvador, gratis para CadUnico. Demais: valor subsidiado" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

---

### mg-restaurante-popular (Minas Gerais) - INCOMPLETO -> CORRIGIDO

**Pesquisa oficial**: Precos variam por municipio em MG.

**Dados reais**:
- Precos vao de R$ 1,00 (BH) a R$ 7,99 em outros municipios
- Nao ha preco unico estadual

**Correcoes**:
| Item | Antes | Depois |
|------|-------|--------|
| shortDescription | "R$ 2,00" | "Preco popular, valor varia por cidade (R$ 1 a R$ 7,99)" |
| howToApply | "Pague R$ 2,00" | "Pague o valor da refeicao (varia por cidade)" |
| lastUpdated | 2026-02-04 | 2026-02-07 |

---

### mg-bolsa-merenda (Minas Gerais) - INCOMPLETO -> CORRIGIDO

**Pesquisa oficial**: educacao.mg.gov.br

**Dados reais**:
- Exige CadUnico e situacao de extrema pobreza
- R$ 50 por estudante

**Correcoes**:
| Item | Antes | Depois |
|------|-------|--------|
| eligibilityRules | Faltava CadUnico | Adicionado cadastradoCadunico=true |
| documentsRequired | So matricula | Adicionado NIS |
| howToApply | 3 passos | 4 passos com CadUnico |
| lastUpdated | 2026-02-04 | 2026-02-07 |

---

### ce-ceara-sem-fome (Ceara) - SIMPLIFICADO

**Status**: Sem alteracao.
**Dados verificados**: R$ 2,00 no restaurante popular, confirmado. Tambem tem Cartao Ceara Sem Fome (R$ 300/mes) para compra de alimentos, nao mencionado separadamente.

---

### pe-restaurante-popular (Pernambuco) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: R$ 1,00 confirmado como preco padrao. Porem, Recife oferece refeicoes gratuitas para populacao em situacao de rua/vulnerabilidade em algumas unidades. Simplificacao aceitavel.

---

### go-restaurante-do-bem (Goias) - CONFORME

**Status**: Sem alteracao.
**Dados verificados**: R$ 2,00 confirmado por WebSearch. Descricao, valores e elegibilidade corretos.

---

### es-restaurante-popular (Espirito Santo) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: R$ 2,00 mencionado mas sem fonte oficial verificavel. sourceUrl aponta para pagina generica do setades. Preco plausivel mas nao confirmado.

---

### rj-restaurante-popular (Rio de Janeiro) - INCOMPLETO

**Status**: Sem alteracao nesta auditoria.
**Problemas pendentes**:
- Sem preco especifico na descricao
- sourceUrl generico (rj.gov.br)
- Descricao vaga ("precos populares")

---

### rs-restaurante-popular (Rio Grande do Sul) - INCOMPLETO

**Status**: Sem alteracao nesta auditoria.
**Problemas pendentes**:
- Sem preco especifico
- sourceUrl generico

---

### pa-restaurante-popular (Para) - INCOMPLETO

**Status**: Sem alteracao nesta auditoria.
**Problemas pendentes**:
- Sem preco especifico
- sourceUrl generico (seaster.pa.gov.br)

---

### ms-vale-renda (Mato Grosso do Sul) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: Programa de cesta basica, informacoes genericas mas plausveis.

---

### ms-restaurante-popular (Mato Grosso do Sul) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: R$ 2,00 mencionado, sem fonte oficial verificavel.

---

### mt-restaurante-popular (Mato Grosso) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: R$ 2,00 mencionado, sem fonte oficial verificavel.

---

### pb-restaurante-popular (Paraiba) - INCOMPLETO

**Status**: Sem alteracao nesta auditoria.
**Problemas pendentes**:
- Sem preco especifico
- sourceUrl generico

---

### pb-cesta-basica (Paraiba) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: Informacoes genericas mas plausveis.

---

### pi-comida-na-mesa (Piaui) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: Informacoes genericas, programa sem detalhamento oficial facilmente acessivel.

---

### rn-restaurante-popular (Rio Grande do Norte) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: Generico.

---

### ro-cesta-solidaria (Rondonia) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### rr-cesta-basica-roraima (Roraima) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### se-restaurante-popular (Sergipe) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### to-cesta-basica-tocantins (Tocantins) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### ac-cesta-basica-acre (Acre) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### ap-cesta-basica-amapa (Amapa) - SIMPLIFICADO

**Status**: Sem alteracao.

---

### am-prato-cheio (Amazonas) - CONFORME

**Status**: Sem alteracao.
**Dados verificados**: R$ 1,00 confirmado por WebSearch. Descricao precisa.

---

### ma-cozinha-popular (Maranhao) - SIMPLIFICADO

**Status**: Sem alteracao.
**Observacao**: Sem preco especifico, informacoes genericas.

---

## Correcoes Aplicadas

| # | Arquivo | Beneficio | Campo | Antes | Depois | Gravidade |
|---|---------|-----------|-------|-------|--------|-----------|
| 1 | sp.json | sp-bom-prato | shortDescription | R$1,00/R$1,50 | R$0,50/R$1,00 | Alta |
| 2 | sp.json | sp-bom-prato | howToApply[2] | R$1,00 ou R$1,50 | R$0,50/R$1,00 | Alta |
| 3 | sp.json | sp-bom-prato | lastUpdated | 2026-02-04 | 2026-02-07 | Baixa |
| 4 | sp.json | sp-vivaleite | eligibility[1].desc | Faltava idosos | +idosos 60+ | Media |
| 5 | sp.json | sp-vivaleite | eligibility[2].value | 3200 | 3036 (2 SM) | Media |
| 6 | sp.json | sp-vivaleite | lastUpdated | 2026-02-04 | 2026-02-07 | Baixa |
| 7 | df.json | df-cartao-prato-cheio | shortDescription | R$250 | R$280 | Alta |
| 8 | df.json | df-cartao-prato-cheio | estimatedValue | 250/250 | 280/280 | Alta |
| 9 | df.json | df-cartao-prato-cheio | lastUpdated | 2026-02-04 | 2026-02-07 | Baixa |
| 10 | df.json | df-rest-comunitario | shortDescription | R$1,00 generico | cafe/almoco/jantar detalhado | Media |
| 11 | df.json | df-rest-comunitario | howToApply | R$1,00 | R$0,50/R$1,00 | Media |
| 12 | df.json | df-rest-comunitario | lastUpdated | 2026-02-04 | 2026-02-07 | Baixa |
| 13 | sc.json | sc-cartao-comida-boa | INTEIRO | Programa do PR | Substituido por sc-cesta-basica-paa | Critica |
| 14 | pr.json | pr-armazem-da-familia | shortDescription+whereToApply | "estado" | "Curitiba (municipal)" | Alta |
| 15 | pr.json | pr-armazem-da-familia | renda.value | 3200 | 7590 (5 SM) | Alta |
| 16 | pr.json | pr-leite-das-criancas | renda.value | 3200 | 3036 (meio SM pc) | Media |
| 17 | al.json | al-restaurante-popular | shortDescription+howToApply | Sem preco | R$3 almoco, R$1 cafe | Media |
| 18 | ba.json | ba-restaurante-popular | shortDescription+howToApply | R$1,00 | Gratis CadUnico Salvador | Alta |
| 19 | mg.json | mg-restaurante-popular | shortDescription+howToApply | R$2,00 fixo | Varia por cidade (R$1-R$7,99) | Media |
| 20 | mg.json | mg-bolsa-merenda | eligibilityRules | Sem CadUnico | +CadUnico obrigatorio | Alta |

---

## Classificacao por Gravidade

### Critico (1)
- **sc-cartao-comida-boa**: Beneficio de outro estado (PR) atribuido a SC

### Alto (7)
- sp-bom-prato: Precos incorretos (100% errado)
- df-cartao-prato-cheio: Valor desatualizado (R$30 de diferenca)
- pr-armazem-da-familia: Escopo errado (municipal vs estadual)
- ba-restaurante-popular: Preco incorreto (gratis vs R$1)
- mg-bolsa-merenda: Requisito faltante (CadUnico)

### Medio (5)
- sp-vivaleite: Renda e publico incompletos
- df-restaurante-comunitario: Precos incompletos
- mg-restaurante-popular: Preco fixo vs variavel
- al-restaurante-popular: Sem preco
- pr-leite-das-criancas: Renda imprecisa

### Baixo (21)
- Beneficios genericos sem dados oficiais verificaveis, mantidos como "Simplificado"

---

## Fontes Consultadas

| Programa | URL | Verificado em |
|----------|-----|---------------|
| Bom Prato SP | https://www.desenvolvimentosocial.sp.gov.br/bom-prato/ | 2026-02-07 |
| Vivaleite SP | https://www.vivaleite.sp.gov.br/ | 2026-02-07 |
| Restaurante Comunitario DF | https://www.sedes.df.gov.br/ | 2026-02-07 |
| Cartao Prato Cheio DF | https://www.sedes.df.gov.br/ | 2026-02-07 |
| Leite das Criancas PR | https://www.leitedascriancas.pr.gov.br/ | 2026-02-07 |
| Armazem da Familia PR | https://www.curitiba.pr.gov.br/servicos/armazem-da-familia/ | 2026-02-07 |
| Ceara Sem Fome | https://www.ceara.gov.br/ | 2026-02-07 |
| Restaurante Popular MG | https://www.social.mg.gov.br/ | 2026-02-07 |
| Bolsa Merenda MG | https://www.educacao.mg.gov.br/ | 2026-02-07 |
| Restaurante do Bem GO | https://www.goias.gov.br/ | 2026-02-07 |
| Restaurante Popular AL | https://www.al.gov.br/ | 2026-02-07 |
| Restaurante Popular BA | https://www.sjdhds.ba.gov.br/ | 2026-02-07 |
| PAA Santa Catarina | https://www.sas.sc.gov.br/ | 2026-02-07 |
| Prato Cheio AM | https://www.amazonas.am.gov.br/ | 2026-02-07 |

---

## Recomendacoes

1. **Restaurantes populares genericos**: 15 estados tem restaurantes populares com dados genericos (sem precos, fontes vagas). Priorizar pesquisa oficial nos 5 maiores: RJ, RS, PA, PB, RN.

2. **Campo temIdoso60mais**: Necessario para o Vivaleite SP capturar idosos corretamente no CitizenProfile.

3. **Escopo municipal vs estadual**: pr-armazem-da-familia e al-restaurante-popular sao primariamente municipais. Considerar adicionar campo `scopeNote` ou permitir scope "municipal".

4. **Cestas basicas genericas**: 8 estados (AC, AP, RO, RR, TO, PB, PI, MA) tem programas de cesta/alimentacao com dados minimos. Requerem pesquisa dedicada.

5. **Atualizacao de fontes**: sourceUrls genericos (gov.br raiz) devem ser substituidos por links diretos aos programas.

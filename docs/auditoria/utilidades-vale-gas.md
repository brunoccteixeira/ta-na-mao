# Auditoria: Utilidades / Vale Gas (16 beneficios estaduais)

**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6
**Skill**: /auditor-beneficios

## Resumo

| Status | Quantidade |
|--------|-----------|
| Conforme | 0 |
| Simplificado | 10 |
| Incorreto | 6 |
| Incompleto | 0 |

**Achado principal**: Dos 16 "vale gas" estaduais auditados, apenas **6 estados** possuem programa estadual proprio confirmado (SP, CE, ES, MA, PA, TO). Os outros **10 estados** (AC, AM, AP, GO, MS, MT, PR, RO, RR, SC) nao possuem programa estadual especifico de vale gas -- o beneficio disponivel e o **programa federal Gas do Povo** (antigo Auxilio Gas), que opera em todo o territorio nacional desde novembro/2025.

## Detalhamento por Beneficio

---

### Vale Gas SP (SP) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: sp-vale-gas
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 100 bimestral | Valor R$ 110 bimestral (3 parcelas/ano = R$ 330/ano) | Incorreto | Corrigido para R$ 110 |
| Renda familiar ate R$ 3.200 | Renda per capita ate R$ 178 (~R$ 712 para familia de 4) | Incorreto | Corrigido |
| Sem restricao Bolsa Familia | NAO pode receber Bolsa Familia | Incorreto | Adicionada regra recebeBolsaFamilia = false |
| sourceUrl generico bolsadopovo | URL especifica existe | Simplificado | Corrigido para URL da SDS |

**Fontes**:
- https://www.desenvolvimentosocial.sp.gov.br/acoes-de-protecao-social/vale-gas/
- https://fdr.com.br/2023/09/12/bolsa-do-povo-atualiza-o-valor-do-vale-gas-para-os-moradores-de-sao-paulo/

---

### Vale Gas Social Ceara (CE) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: ce-vale-gas
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 50-100/mes | 3 recargas gratuitas de botijao por ano (~R$ 28/mes) | Incorreto | Corrigido |
| Renda familiar ate R$ 872 | Renda per capita ate R$ 273 (~R$ 1.092 para familia de 4) | Incorreto | Corrigido |
| Exige Bolsa Familia (correto) | Sim, beneficiario do Bolsa Familia com cadastro ativo | Conforme | Mantido |
| Entrega via Cagece | Tiquete trocado em distribuidora credenciada | Incorreto | Corrigido |
| sourceUrl generico ceara.gov.br | URL especifica da SPS existe | Simplificado | Corrigido para SPS |

**Fontes**:
- https://www.sps.ce.gov.br/institucional/secretarias-executivas/protecao-social/protecao-social-basica/vale-gas-social-destaques/
- https://www.ceara.gov.br/2026/02/06/governo-do-ceara-inicia-distribuicao-do-vale-gas-social-na-proxima-segunda-feira/

---

### Vale Gas Capixaba (ES) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: es-vale-gas-capixaba
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Renda familiar ate R$ 872 | Renda per capita ate R$ 218 (conforme, mesmo valor) | Conforme | Mantido |
| Sem exigencia Bolsa Familia | OBRIGATORIO receber Bolsa Familia | Incorreto | Adicionada regra |
| Sem exigencia crianca | OBRIGATORIO ter crianca menor de 6 anos | Incorreto | Adicionada regra temCrianca0a6 |
| "Automatico para Bolsa Capixaba" | Selecao pela Setades via CadUnico | Incorreto | Corrigido |
| Nao pode receber Auxilio Gas federal | Regra existente mas nao modelavel no schema | Simplificado | Nota na descricao |
| sourceUrl generico setades.es.gov.br | URL especifica existe | Simplificado | Corrigido |

**Fontes**:
- https://setades.es.gov.br/vale-gas-capixaba
- https://prodest.es.gov.br/Noticia/prodest-viabiliza-sistema-de-concessao-do-vale-gas-capixaba

---

### Vale Gas Maranhao (MA) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: ma-vale-gas
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 50-100/mes | 3 recargas de botijao por ano (~R$ 25/mes) | Incorreto | Corrigido |
| Renda familiar ate R$ 872 | Renda per capita = R$ 0,00 (extrema vulnerabilidade) | Incorreto | Corrigido para 0 |
| Pagamento em dinheiro | Vale trocado na distribuidora credenciada | Incorreto | Corrigido |
| CRAS como local | Distribuicao via SEDES nos municipios | Simplificado | Corrigido |
| sourceUrl generico ma.gov.br | URL da SEDES existe | Simplificado | Corrigido |

**Fontes**:
- https://sedes.ma.gov.br/servicos/solicitar-vale-gas
- https://sedes.ma.gov.br/noticias/vale-gas-nova-etapa-inicia-nesta-quinta-feira-7

---

### Vale Gas Para (PA) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: pa-vale-gas
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| R$ 100 bimestral (mensal R$ 50) | R$ 100 em 2 parcelas (programa pontual, nao recorrente) | Incorreto | Corrigido tipo para one_time |
| Renda familiar ate R$ 872 | Renda per capita = R$ 0,00 (extrema pobreza) | Incorreto | Corrigido |
| Sem exigencia Bolsa Familia | OBRIGATORIO receber Bolsa Familia | Incorreto | Adicionada regra |
| Pagamento via cartao | Credito via Banpara | Simplificado | Corrigido |

**Fontes**:
- https://www.agenciapara.com.br/noticia/40016/vale-gas-comeca-nova-rodada-de-pagamentos-nesta-segunda-feira-12
- https://agenciapara.com.br/noticia/35321/estado-vai-pagar-terceira-parcela-do-vale-gas-a-partir-de-14-de-marco

---

### Vale Gas Tocantins (TO) -- PROGRAMA ESTADUAL CONFIRMADO
**ID**: to-vale-gas-tocantins
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| R$ 100 bimestral (mensal R$ 50-60) | 3 recargas de botijao (programa pontual) | Incorreto | Corrigido tipo para one_time |
| Renda familiar ate R$ 872 | Renda per capita ate R$ 178 (~R$ 712 para familia de 4) | Incorreto | Corrigido |
| Sem restricao Bolsa Familia | NAO pode receber Bolsa Familia | Incorreto | Adicionada regra |
| CRAS como local | Site valegas.to.gov.br + CRAS | Simplificado | Corrigido |
| sourceUrl generico to.gov.br | URL especifica existe | Simplificado | Corrigido |

**Fontes**:
- https://valegas.to.gov.br/
- https://www.to.gov.br/setas/vale-gas/1k2aa6l8re0h
- https://www.to.gov.br/secom/noticias/governo-do-tocantins-comeca-a-execucao-do-programa-estadual-vale-gas-que-vai-fornecer-recarga-de-botijao-de-gas-para-familias-de-52-municipios/6te1w774vxg3

---

### Vale Gas Acre (AC) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: ac-vale-gas-acre
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; refere-se ao Gas do Povo (federal) | Simplificado | Atualizado descricao e sourceUrl |
| Valor R$ 100 bimestral | Botijao ~R$ 122 (maior do pais), 4-6 recargas/ano | Incorreto | Corrigido |
| Renda ate R$ 872 | Renda per capita ate meio SM (~R$ 759) | Incorreto | Corrigido para R$ 3.036 |

**Fontes**:
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx
- https://diariodoacre.com.br/gas-do-povo-novo-vale-gas-2025-muda-forma-de-pagamento-e-define-precos-por-estado/

---

### Vale Gas Amazonas (AM) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: am-vale-gas-amazonas
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; 546 mil familias via Gas do Povo | Simplificado | Atualizado descricao e sourceUrl |
| Valor generico | 4-6 recargas/ano no Gas do Povo | Incorreto | Corrigido |

**Fontes**:
- https://amazonasatual.com.br/gas-do-povo-inclui-546-350-familias-no-amazonas-conheca-o-programa/

---

### Vale Gas Amapa (AP) -- PROGRAMA ESTADUAL PEQUENO
**ID**: ap-vale-gas-amapa
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Existe "Vale Gas Social" estadual pequeno (5.483 familias em 2025) | Simplificado | Atualizado descricao |
| Valor generico | Recargas de botijao via emenda parlamentar + Tesouro Estadual | Simplificado | Mantido |
| Poucos detalhes disponiveis | Programa com informacao limitada | Simplificado | Nota adicionada |

**Fontes**:
- https://agenciaamapa.com.br/noticia/33562/balanco-2025-governo-do-amapa-avanca-no-desenvolvimento-economico-do-estado

---

### Vale Gas Goias (GO) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: go-vale-gas
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; Goiania recebe Gas do Povo | Simplificado | Atualizado descricao e sourceUrl |
| Valor R$ 100-120 bimestral | Botijao ~R$ 98 em GO, 4-6/ano | Incorreto | Corrigido |

**Fontes**:
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx

---

### Vale Gas MS (MS) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: ms-vale-gas
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; Gas do Povo (federal) com botijao a R$ 99 | Simplificado | Atualizado descricao e sourceUrl |
| Valor R$ 100 bimestral | 4-6 recargas/ano | Incorreto | Corrigido |

**Fontes**:
- https://www.campograndenews.com.br/economia/gas-do-povo-vai-pagar-r-98-as-revendedoras-de-mato-grosso-do-sul

---

### Vale Gas MT (MT) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: mt-vale-gas
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; MT tem o botijao mais caro do pais (R$ 125) | Simplificado | Atualizado descricao e sourceUrl |
| Valor R$ 100 bimestral | Botijao R$ 125, 4-6 recargas/ano | Incorreto | Corrigido |

**Fontes**:
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx

---

### Vale Gas Social PR (PR) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: pr-vale-gas-social
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; Gas do Povo federal (botijao ~R$ 96) | Simplificado | Atualizado descricao e sourceUrl |
| Ha projeto municipal em Curitiba | Projeto de lei municipal, nao estadual | Simplificado | Nao aplicavel |

**Fontes**:
- https://www.curitiba.pr.leg.br/informacao/noticias/projeto-de-lei-cria-vale-gas-para-familias-de-baixa-renda-em-curitiba

---

### Vale Gas Rondonia (RO) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: ro-vale-gas-rondonia
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; somente Gas do Povo federal | Simplificado | Atualizado descricao e sourceUrl |

**Fontes**:
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx

---

### Vale Gas Roraima (RR) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: rr-vale-gas-roraima
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; 67 mil familias via Gas do Povo (botijao ~R$ 113) | Simplificado | Atualizado descricao e sourceUrl |

**Fontes**:
- https://www.folhabv.com.br/cotidiano/programa-federal-garantira-gas-de-cozinha-para-familias-em-situacao-de-vulnerabilidade

---

### Vale Gas SC (SC) -- PROGRAMA FEDERAL (Gas do Povo)
**ID**: sc-vale-gas-sc
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Nao ha programa estadual; somente Gas do Povo federal | Simplificado | Atualizado descricao e sourceUrl |

**Fontes**:
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx

---

## Correcoes Aplicadas

### Programas Estaduais Confirmados (6 estados)

| ID | Campo | Antes | Depois | Fonte |
|----|-------|-------|--------|-------|
| sp-vale-gas | estimatedValue.min/max | 50/50 | 55/55 | SDS SP |
| sp-vale-gas | estimatedValue.description | R$ 100 a cada 2 meses | R$ 110 a cada 2 meses (3 parcelas/ano) | SDS SP |
| sp-vale-gas | rendaFamiliarMensal.value | 3200 | 712 | SDS SP (per capita R$ 178) |
| sp-vale-gas | Adicionada regra | - | recebeBolsaFamilia = false | SDS SP |
| sp-vale-gas | sourceUrl | bolsadopovo.sp.gov.br | desenvolvimentosocial.sp.gov.br | SDS SP |
| ce-vale-gas | estimatedValue | R$ 50-100/mes | R$ 30-35/mes (3 recargas/ano) | SPS CE |
| ce-vale-gas | rendaFamiliarMensal.value | 872 | 1092 | SPS CE (per capita R$ 273) |
| ce-vale-gas | sourceUrl | ceara.gov.br | sps.ce.gov.br | SPS CE |
| es-vale-gas-capixaba | Adicionada regra | - | recebeBolsaFamilia = true | Setades ES |
| es-vale-gas-capixaba | Adicionada regra | - | temCrianca0a6 = true | Setades ES |
| es-vale-gas-capixaba | sourceUrl | setades.es.gov.br/ | setades.es.gov.br/vale-gas-capixaba | Setades ES |
| ma-vale-gas | estimatedValue | R$ 50-100/mes | R$ 25-30/mes (3 recargas/ano) | SEDES MA |
| ma-vale-gas | rendaFamiliarMensal.value | 872 | 0 | SEDES MA (renda R$ 0) |
| ma-vale-gas | sourceUrl | ma.gov.br | sedes.ma.gov.br/servicos/solicitar-vale-gas | SEDES MA |
| pa-vale-gas | estimatedValue.type | monthly | one_time | SEASTER PA |
| pa-vale-gas | rendaFamiliarMensal.value | 872 | 0 | SEASTER PA (renda R$ 0) |
| pa-vale-gas | Adicionada regra | - | recebeBolsaFamilia = true | SEASTER PA |
| to-vale-gas-tocantins | estimatedValue.type | monthly | one_time | SETAS TO |
| to-vale-gas-tocantins | rendaFamiliarMensal.value | 872 | 712 | SETAS TO (per capita R$ 178) |
| to-vale-gas-tocantins | Adicionada regra | - | recebeBolsaFamilia = false | SETAS TO |
| to-vale-gas-tocantins | sourceUrl | to.gov.br | valegas.to.gov.br | SETAS TO |

### Programas Federais Reclassificados (10 estados)

| ID | Campo | Antes | Depois | Fonte |
|----|-------|-------|--------|-------|
| ac-vale-gas-acre | shortDescription | Programa estadual | Gas do Povo federal (R$ 122 no AC) | Caixa |
| ac-vale-gas-acre | sourceUrl | ac.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| ac-vale-gas-acre | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| am-vale-gas-amazonas | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| am-vale-gas-amazonas | sourceUrl | seas.am.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| am-vale-gas-amazonas | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| am-vale-gas-amazonas | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| go-vale-gas | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| go-vale-gas | sourceUrl | goias.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| go-vale-gas | rendaFamiliarMensal.value | 4000 | 3036 | Gas do Povo (1/2 SM) |
| go-vale-gas | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| ms-vale-gas | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| ms-vale-gas | sourceUrl | ms.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| ms-vale-gas | rendaFamiliarMensal.value | 3200 | 3036 | Gas do Povo (1/2 SM) |
| ms-vale-gas | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| mt-vale-gas | shortDescription | Programa estadual | Gas do Povo federal (R$ 125) | Caixa |
| mt-vale-gas | sourceUrl | mt.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| mt-vale-gas | rendaFamiliarMensal.value | 3200 | 3036 | Gas do Povo (1/2 SM) |
| mt-vale-gas | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| pr-vale-gas-social | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| pr-vale-gas-social | sourceUrl | desenvolvimentosocial.pr.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| pr-vale-gas-social | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| pr-vale-gas-social | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| ro-vale-gas-rondonia | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| ro-vale-gas-rondonia | sourceUrl | rondonia.ro.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| ro-vale-gas-rondonia | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| ro-vale-gas-rondonia | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| rr-vale-gas-roraima | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| rr-vale-gas-roraima | sourceUrl | roraima.rr.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| rr-vale-gas-roraima | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| rr-vale-gas-roraima | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |
| sc-vale-gas-sc | shortDescription | Programa estadual | Gas do Povo federal | Caixa |
| sc-vale-gas-sc | sourceUrl | sds.sc.gov.br | caixa.gov.br/gas-do-povo | Caixa |
| sc-vale-gas-sc | rendaFamiliarMensal.value | 872 | 3036 | Gas do Povo (1/2 SM) |
| sc-vale-gas-sc | whereToApply + howToApply | CRAS generico | Revenda credenciada Gas do Povo | Caixa |

## Analise Critica

### Problema Sistemico Identificado

O principal problema encontrado nesta auditoria e a **criacao de programas estaduais de vale gas ficticios**. De 16 beneficios listados como "estaduais", apenas 6 possuem programa estadual confirmado com fontes oficiais. Os demais 10 sao referenciamentos ao programa federal Gas do Povo (antigo Auxilio Gas) que foram erroneamente apresentados como programas estaduais proprios.

### Recomendacoes

1. **Reclassificar os 10 beneficios federais**: Considerar mover para o catalogo federal ou manter como "acesso ao programa federal no estado" com esclarecimento claro
2. **Revisar criterios de elegibilidade**: Os 6 programas estaduais tinham criterios de renda incorretos (generico R$ 872 vs criterios especificos de cada programa)
3. **Verificar periodicidade**: Varios programas nao sao "mensais" -- sao 3 recargas por ano (CE, MA, TO) ou pagamentos pontuais (PA)
4. **Atualizar vinculo com Bolsa Familia**: Informacao critica omitida -- CE, ES e PA exigem Bolsa Familia; SP e TO exigem NAO receber Bolsa Familia

### Sobre o Gas do Povo (Federal)

O programa federal Gas do Povo foi lancado em set/2025 e substituiu o Auxilio Gas. Principais caracteristicas:
- Botijao gratis (nao dinheiro) em revendas credenciadas
- Renda per capita ate meio salario minimo (R$ 759)
- 4-6 recargas/ano conforme tamanho da familia
- Meta: 15,5 milhoes de familias ate mar/2026
- Precos variam por estado: R$ 89,67 (mais barato) a R$ 122,12 (AC, mais caro)

## Fontes Consultadas

- https://www.desenvolvimentosocial.sp.gov.br/acoes-de-protecao-social/vale-gas/
- https://www.sps.ce.gov.br/institucional/secretarias-executivas/protecao-social/protecao-social-basica/vale-gas-social-destaques/
- https://setades.es.gov.br/vale-gas-capixaba
- https://sedes.ma.gov.br/servicos/solicitar-vale-gas
- https://www.agenciapara.com.br/noticia/40016/vale-gas-comeca-nova-rodada-de-pagamentos-nesta-segunda-feira-12
- https://valegas.to.gov.br/
- https://www.to.gov.br/setas/vale-gas/1k2aa6l8re0h
- https://www.caixa.gov.br/programas-sociais/programa-gas-do-povo/Paginas/default.aspx
- https://agenciagov.ebc.com.br/noticias/202509/gas-do-povo-entenda-como-funciona-programa-que-amplia-acesso-ao-gas-de-cozinha
- https://www.ceara.gov.br/2026/02/06/governo-do-ceara-inicia-distribuicao-do-vale-gas-social-na-proxima-segunda-feira/
- https://amazonasatual.com.br/gas-do-povo-inclui-546-350-familias-no-amazonas-conheca-o-programa/
- https://www.folhabv.com.br/cotidiano/programa-federal-garantira-gas-de-cozinha-para-familias-em-situacao-de-vulnerabilidade
- https://www.campograndenews.com.br/economia/gas-do-povo-vai-pagar-r-98-as-revendedoras-de-mato-grosso-do-sul
- https://diariodoacre.com.br/gas-do-povo-novo-vale-gas-2025-muda-forma-de-pagamento-e-define-precos-por-estado/
- https://agenciaamapa.com.br/noticia/33562/balanco-2025-governo-do-amapa-avanca-no-desenvolvimento-economico-do-estado

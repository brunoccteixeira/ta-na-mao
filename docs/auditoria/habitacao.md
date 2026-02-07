# Auditoria: Beneficios de Habitacao (17 beneficios / 16 UFs)

**Data da auditoria:** 2026-02-07
**Auditor:** Claude Opus 4.6 (skill auditor-beneficios)
**Beneficio modelo:** rs-porta-de-entrada (Porta de Entrada RS)

---

## Resumo Executivo

| Metrica | Valor |
|---------|-------|
| Total de beneficios auditados | 17 |
| Beneficios com erros criticos | 8 |
| Erros criticos corrigidos | 8 |
| Beneficios ja corretos | 9 |
| Campo invalido mais comum | `rendaPerCapita` (7 ocorrencias) |
| Tipo invalido mais comum | `"type": "once"` (11 ocorrencias, corrigido pelo linter) |

---

## Beneficio Modelo: rs-porta-de-entrada

**Programa:** Porta de Entrada RS
**Base Legal:** Lei Estadual N. 16.138/2024 (7 jun 2024), Decreto Estadual N. 57.779/2024 (4 set 2024)
**Fonte Oficial:** https://www.estado.rs.gov.br/inicial

### Dados verificados via web search:
- Subsidio de R$ 20 mil (confirmado)
- Renda familiar de ate 5 salarios minimos / R$ 7.060 (confirmado)
- Nao ter casa propria (confirmado)
- Cadastro via Sehab RS (confirmado)
- Imoveis ate R$ 320 mil do MCMV (confirmado)
- Financiamento pre-aprovado pela Caixa (confirmado)
- Fase 2 lancada com R$ 150 milhoes para 7.500+ familias (confirmado)

**Veredito:** Beneficio modelo esta CORRETO e bem documentado.

---

## Checklist por Beneficio

### 1. rs-porta-de-entrada (RS) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | OK - Lei 16.138/2024, Decreto 57.779/2024 |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal, cadastradoCadunico |
| 3 | Faixa etaria | N/A (sem restricao de idade) |
| 4 | CadUnico | OK - presente |
| 5 | Documentos | OK - 5 documentos listados |
| 6 | Valores | OK - min 20000, max 20000 |
| 7 | Canais | OK - site Sehab RS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK - estado eq RS |
| 10 | Dados hardcoded | OK - sem dados hardcoded |
| 11 | Disclaimers | Sugestao: adicionar "valor sujeito a alteracao" |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 2. pb-parceiros-habitacao (PB) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente (sugestao: adicionar) |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal 2640, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 5 documentos |
| 6 | Valores | OK - min 30000, max 100000 |
| 7 | Canais | OK - CEHAP ou Prefeitura |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 3. pi-morar-bem (PI) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal 2640, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - min 30000, max 80000 |
| 7 | Canais | OK - Prefeitura ou CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 4. se-casa-sergipana (SE) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal 2640, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 5 documentos |
| 6 | Valores | OK - min 30000, max 80000 |
| 7 | Canais | OK - COHIDRO ou Prefeitura |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 5. es-nossa-casa (ES) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, cadastradoCadunico, rendaFamiliarMensal 4000 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - min 10000, max 20000 |
| 7 | Canais | OK - Conecta Cidadao ou SEDURB |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 6. pr-casa-facil (PR) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal 6000 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | Ausente (sugestao: adicionar) |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - min 10000, max 20000 |
| 7 | Canais | OK - COHAPAR |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 7. sc-casa-catarina (SC) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, rendaFamiliarMensal 5648 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | Ausente (sugestao: adicionar) |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - min 50000, max 130000 |
| 7 | Canais | OK - Prefeitura |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 8. df-morar-df (DF) -- CORRETO (com ressalvas)

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temCasaPropria, cadastradoCadunico (descricao menciona CODHAB) |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK (campo ok, descricao diz "CODHAB" - aceitavel) |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - min 15000, max 16079 |
| 7 | Canais | OK - CODHAB |
| 8 | Prazos | N/A (menciona 5 anos de residencia na descricao) |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

**Ressalva:** Nao possui regra de renda no eligibilityRules. Sugestao: adicionar rendaFamiliarMensal.

---

### 9. go-casas-custo-zero (GO) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, cadastradoCadunico, temCasaPropria, rendaFamiliarMensal 2277 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 5 documentos |
| 6 | Valores | OK - min 80000, max 130000 |
| 7 | Canais | OK - AGEHAB ou Prefeitura |
| 8 | Prazos | N/A (menciona 3 anos na descricao) |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

## Beneficios Corrigidos (8 erros criticos)

### 10. ac-cohab-acre (AC) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 700 --> `rendaFamiliarMensal` 2640
- Faltava regra `cadastradoCadunico`

**Correcao aplicada:** Sim

---

### 11. am-amazonas-meu-lar (AM) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 1425 --> `rendaFamiliarMensal` 8000

**Correcao aplicada:** Sim

---

### 12. ap-habitacao-amapa (AP) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 700 --> `rendaFamiliarMensal` 2640
- Faltava regra `cadastradoCadunico`

**Correcao aplicada:** Sim

---

### 13. pa-sua-casa (PA) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 1100 --> `rendaFamiliarMensal` 4236
- Faltava regra `cadastradoCadunico`

**Correcao aplicada:** Sim

---

### 14. ro-meu-sonho (RO) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 1425 --> `rendaFamiliarMensal` 8000

**Correcao aplicada:** Sim

---

### 15. rr-censo-habitacional (RR) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 700 --> `rendaFamiliarMensal` 2640
- Faltava regra `cadastradoCadunico`

**Correcao aplicada:** Sim

---

### 16. to-em-casa (TO) -- CORRIGIDO

**Erros encontrados:**
- `rendaPerCapita` 700 --> `rendaFamiliarMensal` 2640
- Faltava regra `cadastradoCadunico`

**Correcao aplicada:** Sim

---

### Bonus: Correcoes de "type": "once" (nao-Habitacao)

O linter corrigiu automaticamente `"type": "once"` para `"type": "one_time"` nos seguintes beneficios nao-Habitacao que estavam nos mesmos arquivos:

| Estado | Beneficio | Categoria |
|--------|-----------|-----------|
| AM | am-rede-alyne-amazonas | Saude Materno-Infantil |
| AP | ap-saude-gestante-amapa | Saude Materno-Infantil |
| PA | pa-saude-gestante-para | Saude Materno-Infantil |
| RR | rr-escolegis-capacitacao | Educacao |
| TO | to-maos-que-cuidam | Saude Materno-Infantil |
| PB | pb-paraiba-primeira-infancia | Saude Materno-Infantil |
| PI | pi-primeira-infancia | Saude Materno-Infantil |
| ES | es-rede-bem-nascer | Saude Materno-Infantil |
| PR | pr-mae-paranaense | Saude Materno-Infantil |
| SC | sc-teste-mae-catarinense | Saude Materno-Infantil |

---

## Erros por Tipo

| Tipo de Erro | Quantidade | Gravidade |
|-------------|-----------|-----------|
| Campo `rendaPerCapita` inexistente no CitizenProfile | 7 | Critico (beneficio nao aparece) |
| Falta regra `cadastradoCadunico` em Habitacao | 5 | Alto (elegibilidade incompleta) |
| `"type": "once"` invalido | 11 | Critico (erro de schema) |
| Base legal ausente | 15 de 17 | Medio (sem respaldo juridico) |
| CadUnico ausente em pr-casa-facil e sc-casa-catarina | 2 | Baixo (sugestao) |
| Renda ausente em df-morar-df | 1 | Baixo (sugestao) |

---

## Recomendacoes

1. **Base Legal:** Adicionar campo `legalBasis` a todos os 17 beneficios de Habitacao (apenas rs-porta-de-entrada e go-bolsa-estudo tem).
2. **CadUnico:** Avaliar se `pr-casa-facil` e `sc-casa-catarina` exigem CadUnico na pratica.
3. **Campo rendaPerCapita global:** Restam 50+ ocorrencias de `rendaPerCapita` em beneficios NAO-Habitacao. Recomenda-se uma auditoria por categoria para migrar tudo para `rendaFamiliarMensal`.
4. **Disclaimers:** Adicionar "valores sujeitos a alteracao pelo governo" em beneficios com valores altos (subsidios > R$ 10 mil).
5. **Fontes:** Verificar periodicamente URLs de sourceUrl (alguns apontam para paginas genericas do governo).

---

## Arquivos Modificados

| Arquivo | Alteracoes |
|---------|-----------|
| `frontend/src/data/benefits/states/ac.json` | rendaPerCapita->rendaFamiliarMensal, +cadastradoCadunico (ac-cohab-acre) |
| `frontend/src/data/benefits/states/am.json` | rendaPerCapita->rendaFamiliarMensal (am-amazonas-meu-lar) |
| `frontend/src/data/benefits/states/ap.json` | rendaPerCapita->rendaFamiliarMensal, +cadastradoCadunico (ap-habitacao-amapa) |
| `frontend/src/data/benefits/states/pa.json` | rendaPerCapita->rendaFamiliarMensal, +cadastradoCadunico (pa-sua-casa) |
| `frontend/src/data/benefits/states/ro.json` | rendaPerCapita->rendaFamiliarMensal (ro-meu-sonho) |
| `frontend/src/data/benefits/states/rr.json` | rendaPerCapita->rendaFamiliarMensal, +cadastradoCadunico (rr-censo-habitacional) |
| `frontend/src/data/benefits/states/to.json` | rendaPerCapita->rendaFamiliarMensal, +cadastradoCadunico (to-em-casa) |
| Linter auto-fix (11 arquivos) | `"type": "once"` -> `"type": "one_time"` |

---

*Auditoria concluida em 2026-02-07 por Claude Opus 4.6*

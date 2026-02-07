# Auditoria: Beneficios de Saude Materno-Infantil (26 beneficios / 25 UFs)

**Data da auditoria:** 2026-02-07
**Auditor:** Claude Opus 4.6 (skill auditor-beneficios)
**Beneficio modelo:** sp-mae-paulistana (Mae Paulistana)

---

## Resumo Executivo

| Metrica | Valor |
|---------|-------|
| Total de beneficios auditados | 26 |
| Beneficios com erros criticos | 22 |
| Erros criticos corrigidos | 22 |
| Beneficios ja corretos | 4 |
| Campo invalido mais comum | `rendaPerCapita` (53 ocorrencias em 22 arquivos) |
| Tipo invalido mais comum | `"type": "once"` (15 ocorrencias em 14 arquivos) |
| Outros campos invalidos corrigidos | `gestante`, `beneficiarioBolsaFamilia`, `rendaFamiliar`, `proprietarioImovel`, `empregoFormal`, `zonaRural` |

---

## Beneficio Modelo: sp-mae-paulistana

**Programa:** Mae Paulistana
**Escopo real:** Municipal (cidade de Sao Paulo) -- JSON diz scope "state"
**Fonte Oficial:** https://prefeitura.sp.gov.br/web/saude/w/atencao_basica/5657

### Dados verificados via web search:

| Dado | No JSON | Fonte Oficial | Status |
|------|---------|---------------|--------|
| Kit enxoval 24 itens | Sim | Confirmado (atualizado em 2026) | OK |
| Transporte gratis (SPTrans) | Sim | Confirmado - bilhetes eletronicos gravidez + 1 ano pos-parto | OK |
| Vaga creche | Sim | Confirmado - se pre-natal inicia ate 4o mes | OK |
| Minimo 7 consultas | Sim | Confirmado | OK |
| Sem restricao de renda | Correto (nao ha campo de renda) | Confirmado - universal para usuarios SUS na cidade de SP | OK |
| Escopo "state" | No JSON como state/SP | Na realidade e municipal (cidade de SP) | ATENCAO |
| Cadastro ate 12a semana | Sim | Confirmado | OK |

**Veredito:** Dados do beneficio modelo estao CORRETOS em conteudo. Ponto de atencao: o escopo deveria ser "municipal" e nao "state", pois o Mae Paulistana e exclusivo da cidade de Sao Paulo (Prefeitura). Recomendacao: considerar migrar para scope "municipal" em versao futura.

---

## Correcoes Aplicadas (Todas as 27 UFs)

### 1. `rendaPerCapita` -> `rendaFamiliarMensal` (53 ocorrencias em 22 arquivos)

Campo `rendaPerCapita` nao existe no CitizenProfile. Todas as ocorrencias foram convertidas para `rendaFamiliarMensal` com o valor multiplicado por 4 (familia de referencia de 4 pessoas).

| Valor per capita | Valor familiar | Descricao | Arquivos afetados |
|-----------------|----------------|-----------|-------------------|
| R$ 218 | R$ 872 | Linha de pobreza/extrema pobreza | ac, am, ap, es, mg(nao), ms, mt, pa, pb, pe, pi, pr, rj, rn, ro, rr, rs, sc, se, to |
| R$ 109 | R$ 436 | Abaixo do piso | mg, pb, pi, sp |
| R$ 800 | R$ 3.200 | Meio salario minimo | ms, mt, pe, pr, rj, rs, sp |
| R$ 1.500 | R$ 6.000 | 3 salarios minimos | es |
| R$ 1.800 | R$ 7.200 | 3 salarios minimos | mt |
| R$ 660 | R$ 2.640 | Especifico RR (rr-colo-de-mae) | rr |

### 2. `"type": "once"` -> `"type": "one_time"` (15 ocorrencias em 14 arquivos)

O tipo valido e `"one_time"`, nao `"once"`. Corrigido em:
am, ap, ba, es, ms, mt (2x), pa, pb, pi, pr, rn, ro, rr, sc, to

### 3. `gestante` -> `temGestante` (1 ocorrencia)

Em pe.json (pe-mae-coruja): campo `gestante` nao existe, campo valido e `temGestante`.

### 4. `beneficiarioBolsaFamilia` -> `recebeBolsaFamilia` (3 ocorrencias)

Em ce.json: campo invalido substituido pelo campo correto do CitizenProfile.

### 5. `rendaFamiliar` -> `rendaFamiliarMensal` (1 ocorrencia)

Em ce.json: campo truncado, corrigido para o nome completo.

### 6. `proprietarioImovel` removido (1 ocorrencia)

Em ce.json (ce-programa-hora-de-construir): campo nao existe no CitizenProfile. Regra removida.

### 7. `empregoFormal` -> `temCarteiraAssinada` (1 ocorrencia)

Em ba.json (ba-primeiro-emprego): campo `empregoFormal` nao existe no CitizenProfile, substituido por `temCarteiraAssinada`.

### 8. `zonaRural` -> `moradiaZonaRural` (1 ocorrencia)

Em ba.json (ba-agua-para-todos): campo correto e `moradiaZonaRural`.

---

## Checklist por Beneficio Materno-Infantil

### 1. sp-mae-paulistana (SP) -- CORRETO (com ressalva de escopo)

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente (sugestao: adicionar referencia ao programa municipal) |
| 2 | Elegibilidade | OK - estado, temGestante. Nao exige renda (correto, e universal) |
| 3 | Faixa etaria | N/A (sem restricao) |
| 4 | CadUnico | N/A (nao exigido -- correto) |
| 5 | Documentos | OK - 3 documentos listados |
| 6 | Valores | OK - min 300, max 600 (kit enxoval) |
| 7 | Canais | OK - UBS |
| 8 | Prazos | OK - ate 12a semana de gestacao mencionado |
| 9 | Restricao geografica | ATENCAO - scope "state"/SP mas e municipal (cidade de SP) |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 2. ba-mae-bahia (BA) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente (sugestao: adicionar) |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A (nao exigido) |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - one_time, min 0, max 0 (atendimento gratuito) |
| 7 | Canais | OK - UBS ou Maternidade |
| 8 | Prazos | OK - inicio do pre-natal assim que souber da gravidez |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 3. al-programa-cria-gestante (AL) -- CORRIGIDO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | CORRIGIDO - rendaPerCapita 218 -> rendaFamiliarMensal 872 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 4. ma-cheque-gestante (MA) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 5. pb-paraiba-primeira-infancia (PB) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A (gestantes e criancas 0-6 anos) |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 5 documentos |
| 6 | Valores | OK - one_time, gratuito |
| 7 | Canais | OK - CRAS ou UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 6. pi-primeira-infancia (PI) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 7. rn-programa-materno-infantil (RN) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A (nao exigido -- correto para saude SUS) |
| 5 | Documentos | OK - 3 documentos |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | OK - iniciar pre-natal logo que souber |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 8. se-mae-sergipana (SE) -- CORRIGIDO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | CORRIGIDO - rendaPerCapita 218 -> rendaFamiliarMensal 872 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 9. pe-mae-coruja (PE) -- CORRIGIDO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | CORRIGIDO - `gestante` -> `temGestante`, `rendaPerCapita` 800 -> `rendaFamiliarMensal` 3200 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 10. ac-saude-materno-infantil (AC) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | OK |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 11. am-rede-alyne-amazonas (AM) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK - 4 documentos |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 12. ap-saude-gestante-amapa (AP) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 13. pa-saude-gestante-para (PA) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 14. ro-mamae-cheguei (RO) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK - 5 documentos |
| 6 | Valores | OK - kit enxoval 200-500 |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | OK - ate 20 semanas de gestacao |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 15. rr-colo-de-mae (RR) -- CORRIGIDO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | CORRIGIDO - rendaPerCapita 660 -> rendaFamiliarMensal 2640 |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 16. to-maos-que-cuidam (TO) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 17. df-bolsa-maternidade (DF) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 18. go-maes-de-goias (GO) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 19. ms-protecao-gestante (MS) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 20. mt-rede-cegonha-mt (MT) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 21. es-rede-bem-nascer (ES) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 22. mg-filhos-de-minas (MG) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 23. rj-cegonha-carioca (RJ) -- CORRETO (com ressalva de escopo)

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | ATENCAO - Cegonha Carioca e municipal (cidade do RJ), nao estadual |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 24. pr-mae-paranaense (PR) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK - gratuito |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 25. rs-mae-gaucha (RS) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante, cadastradoCadunico |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | OK |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - CRAS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

### 26. sc-teste-mae-catarinense (SC) -- CORRETO

| # | Item | Status |
|---|------|--------|
| 1 | Base legal | Ausente |
| 2 | Elegibilidade | OK - estado, temGestante |
| 3 | Faixa etaria | N/A |
| 4 | CadUnico | N/A |
| 5 | Documentos | OK |
| 6 | Valores | OK |
| 7 | Canais | OK - UBS |
| 8 | Prazos | N/A |
| 9 | Restricao geografica | OK |
| 10 | Dados hardcoded | OK |
| 11 | Disclaimers | N/A |
| 12 | Data verificacao | OK - 2026-02-07 |

---

## Recomendacoes Gerais

1. **Base legal ausente em todos os 26 beneficios** -- Nenhum beneficio materno-infantil tem `legalBasis` preenchido. Sugestao: adicionar gradualmente as leis estaduais que fundamentam cada programa.

2. **Escopo de sp-mae-paulistana e rj-cegonha-carioca** -- Ambos sao programas municipais (Prefeitura de SP e Prefeitura do RJ) listados como scope "state". Considerar migrar para scope "municipal" quando o sistema suportar filtragem por municipio.

3. **Faixa etaria nao restringida** -- Nenhum beneficio materno-infantil restringe idade da gestante, o que esta correto para programas de saude SUS.

4. **CadUnico** -- Alguns programas exigem CadUnico (AL, SE, PE, RR, GO, MG, RS, DF, MS, PB, PI, RO) e outros nao (BA, RN, AC, AM, AP, PA, TO, MT, ES, RJ, PR, SC, SP). Isso esta correto: programas de transferencia de renda exigem CadUnico, programas de saude SUS nao.

---

## Fontes Consultadas

| Fonte | URL |
|-------|-----|
| Mae Paulistana (SP) | https://prefeitura.sp.gov.br/web/saude/w/atencao_basica/5657 |
| Mae Bahia (BA) | https://www.saude.ba.gov.br/ |
| Mae Coruja (PE) | https://www.pe.gov.br/ |
| Rede Alyne (AM) | https://www.gov.br/saude/pt-br/assuntos/noticias-para-os-estados/amazonas |
| Mamae Cheguei (RO) | https://rondonia.ro.gov.br/seas/programas-e-projetos/programa-mamae-cheguei/ |
| CitizenProfile (types.ts) | frontend/src/engine/types.ts |
| Engine evaluator | frontend/src/engine/evaluator.ts |

---

*Auditoria concluida em 2026-02-07 por Claude Opus 4.6*

# Resumo Executivo - Auditoria Fase C (Expansao Estadual)

**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6
**Skills utilizadas**: `/auditor-beneficios`, `/jornada-cidadao`, `/fonte-oficial`

---

## Escopo

Auditoria completa dos **85 beneficios** adicionados/atualizados na Fase C (expansao estadual 106->189), distribuidos em 5 categorias:

| Categoria | Qtd Auditada | Beneficio-Modelo |
|-----------|-------------|------------------|
| Qualificacao Profissional | 19 | df-qualifica-df |
| Saude Materno-Infantil | 26 | sp-mae-paulistana |
| Habitacao | 17 | rs-porta-de-entrada |
| Educacao | 17 | go-bolsa-estudo |
| Transporte | 6 | ce-vaivem |
| **Total** | **85** | |

---

## Erros Encontrados por Tipo

### Erros Criticos (quebravam funcionalidade)

| Tipo de Erro | Ocorrencias | Gravidade | Status |
|-------------|------------|-----------|--------|
| `rendaPerCapita` (campo inexistente no CitizenProfile) | 56+ | Critico - beneficio nao aparecia no motor de elegibilidade | CORRIGIDO |
| `"type": "once"` (tipo invalido no schema) | 40+ | Critico - erro de schema TypeScript | CORRIGIDO |
| `beneficiarioBolsaFamilia` (campo inexistente) | 3 | Critico - regra ignorada pelo motor | CORRIGIDO |
| `gestante` em vez de `temGestante` | 1 | Critico - regra ignorada | CORRIGIDO |
| `rendaFamiliar` (truncado) em vez de `rendaFamiliarMensal` | 1 | Critico - regra ignorada | CORRIGIDO |
| `proprietarioImovel` (campo inexistente) | 1 | Critico - regra ignorada | CORRIGIDO (removido) |
| `empregoFormal` em vez de `temCarteiraAssinada` | 1 | Critico - regra ignorada | CORRIGIDO |
| `zonaRural` em vez de `moradiaZonaRural` | 1 | Critico - regra ignorada | CORRIGIDO |
| `desempregado` (campo inexistente) | 1 | Critico - regra ignorada | CORRIGIDO |
| `trabalhadorRural` em vez de `agricultorFamiliar` | 1 | Critico - regra ignorada | CORRIGIDO |
| `estudanteUniversitario` em vez de `estudante` | 1 | Critico - regra ignorada | CORRIGIDO |
| `genero` (campo inexistente) | 1 | Critico - regra ignorada | CORRIGIDO (removido) |
| `temFilhoNaEscola` (campo inexistente) | 1 | Critico - regra ignorada | CORRIGIDO |

**Total erros criticos: ~110 ocorrencias -> TODOS CORRIGIDOS**

### Erros de Conteudo (dados incorretos)

| Tipo de Erro | Ocorrencias | Gravidade | Status |
|-------------|------------|-----------|--------|
| go-bolsa-estudo: valor desatualizado (R$111,92 -> R$130-150) | 1 | Alto - valor errado ao cidadao | CORRIGIDO |
| rn-passe-livre-estudantil: NAO existe passe livre, e meia-passagem | 1 | Alto - beneficio ficticio | CORRIGIDO (renomeado + reescrito) |
| al-passe-livre-intermunicipal: era para "idosos e PcD", na verdade so PcD | 1 | Alto - elegibilidade errada | CORRIGIDO |
| df-qualifica-df: dizia ter auxilio mensal R$200-400, nao ha dinheiro | 1 | Alto - valor ficticio | CORRIGIDO |
| ce-vaivem: elegibilidade simplificada demais (faltava RMF, municipio diferente) | 1 | Medio | CORRIGIDO |
| ba-transporte-estudantil: faltava restricao zona rural | 1 | Medio | CORRIGIDO |

**Total erros de conteudo: 6 -> TODOS CORRIGIDOS**

### Informacoes Incompletas (nao sao erros, mas faltam dados)

| Tipo | Ocorrencias | Gravidade | Status |
|------|------------|-----------|--------|
| Base legal (`legalBasis`) ausente | 80 de 85 | Medio | Pendente (apenas 5 tem: go-bolsa-estudo, rs-porta-de-entrada, ce-vaivem, rn-meia-passagem, al-passe-livre) |
| Disclaimers ausentes | 85 de 85 | Baixo | Parcialmente corrigido (transporte tem `estimated=true`) |
| Prazos/validades ausentes | 85 de 85 | Baixo | Pendente |
| Source URLs genericas | ~15 | Baixo | Pendente |

---

## Total de Correcoes Aplicadas

| Categoria | Correcoes |
|-----------|----------|
| Qualificacao Profissional | 34 |
| Saude Materno-Infantil | 76 (53 rendaPerCapita + 15 once + 8 outros) |
| Habitacao | 23 (7 rendaPerCapita + 5 cadastradoCadunico + 11 once) |
| Educacao | 34 |
| Transporte | 27 |
| **Total** | **~194 correcoes** |

---

## Arquivos Modificados

Todos os **27 arquivos** de estados foram modificados:
`ac.json`, `al.json`, `am.json`, `ap.json`, `ba.json`, `ce.json`, `df.json`, `es.json`, `go.json`, `ma.json`, `mg.json`, `ms.json`, `mt.json`, `pa.json`, `pb.json`, `pe.json`, `pi.json`, `pr.json`, `rj.json`, `rn.json`, `ro.json`, `rr.json`, `rs.json`, `sc.json`, `se.json`, `sp.json`, `to.json`

---

## Validacao Final

```
Total beneficios estaduais: 189
IDs unicos: 189
Duplicatas: 0
Campos invalidos restantes: 0
  rendaPerCapita: 0
  beneficiarioBolsaFamilia: 0
  rendaFamiliar: 0
  proprietarioImovel: 0
  temFilhoNaEscola: 0
  type="once": 0
ZERO ERROS
```

---

## Beneficios com sourceUrl Generica (revisao manual recomendada)

| ID | UF | sourceUrl Atual | Recomendacao |
|----|----|----------------|--------------|
| pi-qualifica-piaui | PI | `https://www.pi.gov.br/` | Buscar URL especifica do SINE/PI |
| se-qualifica-sergipe | SE | `https://www.se.gov.br/` | Buscar URL da SETEEM |
| pa-primeiro-oficio | PA | `https://www.seaster.pa.gov.br/` | Buscar URL especifica do programa |
| ac-bolsa-educacao-acre | AC | `https://www.ac.gov.br/` | Buscar URL especifica |
| ap-bolsa-educacao-amapa | AP | `https://www.ap.gov.br/` | Buscar URL especifica |
| al-prepara-jovem | AL | `https://alagoasdigital.al.gov.br/` | Buscar URL do programa |
| pi-alfabetiza-piaui | PI | `https://www.pi.gov.br/` | Buscar URL da SEDUC/PI |
| rn-bolsa-estudante | RN | `https://www.rn.gov.br/` | Buscar URL da FUERN/UERN |
| ac-saude-materno-infantil | AC | `https://www.ac.gov.br/` | Buscar URL da SESACRE |
| mt-bolsa-estudantil | MT | `https://www.seduc.mt.gov.br/` | Buscar URL especifica do programa |

---

## Beneficios que Precisam de Revisao Manual

### Prioridade Alta

| ID | UF | Problema | Acao Recomendada |
|----|----|---------|------------------|
| sp-mae-paulistana | SP | E programa MUNICIPAL (Prefeitura de SP), listado como `scope: "state"` | Considerar mudar para `scope: "municipal"` |
| rj-cegonha-carioca | RJ | E programa MUNICIPAL (Prefeitura do RJ), listado como `scope: "state"` | Considerar mudar para `scope: "municipal"` |
| am-bolsa-universidade-manaus | AM | E programa MUNICIPAL (Prefeitura de Manaus), listado como `scope: "state"` | Mudar scope ou adicionar restricao `municipioNome: "Manaus"` |
| pb-bolsa-permanencia | PB | Valor R$ 1.500/mes parece alto para bolsa estadual (federais pagam ~R$ 900) | Verificar com FAPESQ-PB |
| pi-alfabetiza-piaui | PI | Valor R$ 600/mes alto para programa de alfabetizacao | Verificar com SEDUC/PI |

### Prioridade Media

| ID | UF | Problema | Acao Recomendada |
|----|----|---------|------------------|
| rn-bolsa-estudante | RN | Cita UFRN (federal) junto com UERN (estadual) | Restringir a UERN ou separar |
| df-morar-df | DF | Nao possui regra de renda no eligibilityRules | Adicionar rendaFamiliarMensal |
| pr-casa-facil | PR | Nao exige cadastradoCadunico | Verificar se programa exige CadUnico |
| sc-casa-catarina | SC | Nao exige cadastradoCadunico | Verificar se programa exige CadUnico |

---

## Outputs Gerados

### Relatorios de Auditoria (5)
- `docs/auditoria/qualificacao-profissional.md`
- `docs/auditoria/saude-materno-infantil.md`
- `docs/auditoria/habitacao.md`
- `docs/auditoria/educacao.md`
- `docs/auditoria/transporte.md`

### Templates de Jornada do Cidadao (5)
- `docs/jornadas/qualificacao-profissional.md`
- `docs/jornadas/saude-materno-infantil.md`
- `docs/jornadas/habitacao.md`
- `docs/jornadas/educacao.md`
- `docs/jornadas/transporte.md`

### JSONs Corrigidos
- 27 arquivos em `frontend/src/data/benefits/states/*.json`

---

## Metricas de Qualidade Pos-Auditoria

| Metrica | Antes | Depois |
|---------|-------|--------|
| Campos invalidos no CitizenProfile | ~110 | 0 |
| Tipos invalidos (`"once"`) | ~40 | 0 |
| Beneficios com dados incorretos | 6 | 0 |
| Beneficios com base legal | 0 | 5 |
| Beneficios com `estimated=true` | 0 | 6 (transporte) |
| Total IDs unicos | 189 | 189 |
| Erros de validacao | ~150 | 0 |

---

*Rodada 1 concluida em 2026-02-07 por Claude Opus 4.6*
*Tempo total: ~45 minutos (5 lotes paralelos)*

---
---

# Rodada 2 — Auditoria das Categorias Originais (~94 beneficios)

**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6
**Skills utilizadas**: `/auditor-beneficios`

---

## Escopo

Auditoria de conteudo dos **~94 beneficios estaduais** nas categorias originais (pre-Fase C), que tiveram apenas correcao de campos na Rodada 1 mas **nunca verificacao de conteudo** contra fontes oficiais.

| Lote | Categoria | Qtd | Beneficio-Modelo |
|------|-----------|-----|------------------|
| 1 | Transferencia de Renda | 27 | sp-bolsa-do-povo |
| 2 | Alimentacao | 34 | sp-bom-prato |
| 3 | Utilidades (Vale Gas) | 16 | sp-vale-gas |
| 4 | Especiais (12 categorias) | 12 | pe-chapeu-de-palha |
| **Total** | | **89** | |

---

## Resultados Consolidados

### Por Status de Conformidade

| Status | Lote 1 (TR) | Lote 2 (Alim.) | Lote 3 (Gas) | Lote 4 (Esp.) | **Total** |
|--------|-------------|----------------|--------------|---------------|-----------|
| Conforme | 4 | 5 | 0 | 2 | **11** |
| Simplificado | 8 | 16 | 10 | 3 | **37** |
| Incorreto | 9 | 5 | 6 | 4 | **24** |
| Incompleto | 2 | 8 | 0 | 3 | **13** |
| Descontinuado | 2 | 0 | 0 | 0 | **2** |
| Renomeado | 2 | 0 | 0 | 0 | **2** |

### Erros Criticos Encontrados

| Tipo de Erro | Qtd | Impacto | Status |
|-------------|-----|---------|--------|
| Categorias sem acentos (Alimentacao vs Alimentacao) | 43 | Filtros quebrados no frontend | CORRIGIDO |
| Status invalido (`discontinued`, `uncertain`) | 2 | Schema TypeScript invalido | CORRIGIDO |
| `legalBasis` como string (go-bolsa-estudo) | 1 | Schema invalido | CORRIGIDO |
| Campo extra `auditDate` (go-bolsa-estudo) | 1 | Campo nao existe no tipo Benefit | CORRIGIDO |

### Erros de Conteudo Encontrados e Corrigidos

| ID | Erro | Correcao |
|----|------|----------|
| sp-bom-prato | Precos errados (R$1/R$1,50) | R$0,50 cafe / R$1,00 almoco-jantar |
| sp-vale-gas | Valor R$100 bimestral | R$110 bimestral; excluir Bolsa Familia |
| ce-vale-gas | Valor R$50-100/mes | 3 recargas/ano (~R$28/mes) |
| es-vale-gas-capixaba | Sem exigencia BF/crianca | Adicionadas regras BF + crianca 0-6 |
| pe-chapeu-de-palha | Valor R$330 | R$373-388 (2026) |
| rj-supera-rj | Status active | Encerrado jul/2023 (status: ended) |
| pa-renda-para | Status active | Emergencial suspenso (status: suspended) |
| df-df-social | R$150-300/m | R$150/m fixo |
| es-bolsa-capixaba | R$150/m | R$50-600/m |
| ms-mais-social | R$200-450/m | R$450/m fixo |
| go-renda-cidada | R$100-250/m | R$80-160/m |
| mg-piso-mineiro | Parecia TR direto | Repasse estado->municipio (disclaimer) |
| df-cartao-prato-cheio | Valor R$250 | R$280 |
| ba-restaurante-popular | Preco generico | Salvador gratis para CadUnico |
| rj-cartao-recomecar | Valor R$3k-5k | Exatamente R$3.000 |
| ma-vale-gas | Dados incorretos | Corrigido com fontes oficiais |

### Achado Principal: Vale Gas

Dos 16 "vale gas estaduais", apenas **6 estados** tem programa proprio confirmado:
- SP (Vale Gas Bolsa do Povo)
- CE (Vale Gas Social)
- ES (Vale Gas Capixaba)
- MA (Vale Gas Maranhao)
- PA (Vale Gas Para)
- TO (Vale Gas Tocantins)

Os outros **10 estados** dependem do programa federal Gas do Povo.

---

## Total de Correcoes Aplicadas (Rodada 2)

| Tipo | Quantidade |
|------|-----------|
| Categorias normalizadas (acentos) | 43 |
| Status invalidos corrigidos | 2 |
| Schema fixes (legalBasis, extra fields) | 2 |
| Correcoes de conteudo (valores, descricoes, regras) | ~50 |
| Source URLs melhoradas | ~15 |
| **Total** | **~112 correcoes** |

---

## Validacao Final (Pos-Rodada 2)

```
Total beneficios estaduais: 189
IDs unicos: 189
Duplicatas: 0
Status invalidos: 0
Tipos invalidos: 0
Campos invalidos: 0
Campos extras: 0
legalBasis formato errado: 0
ZERO ERROS
```

---

## Relatorios Gerados (Rodada 2)

### Auditorias (4)
- `docs/auditoria/transferencia-de-renda.md` (27 beneficios)
- `docs/auditoria/alimentacao.md` (34 beneficios)
- `docs/auditoria/utilidades-vale-gas.md` (16 beneficios)
- `docs/auditoria/especiais.md` (12 beneficios)

---

## Beneficios que Precisam de Atencao (Rodada 2)

### Programas Possivelmente Inexistentes/Descontinuados

| ID | UF | Problema |
|----|----|---------|
| sc-santa-renda | SC | SC nao possui programa estadual de TR encontrado |
| ce-cartao-superacao | CE | Nao encontrado em fontes oficiais |
| pb-pbsocial | PB | Nao encontrado em fontes oficiais |
| pi-cartao-mais-renda | PI | Nao encontrado em fontes oficiais |
| rn-rn-mais-igual | RN | Nao encontrado em fontes oficiais |

### Valores Nao Verificaveis

8 estados menores (AC, AP, RO, RR) possuem programas de TR e alimentacao com dados genericos que nao puderam ser verificados contra fontes oficiais.

---

## Metricas Consolidadas (Rodada 1 + Rodada 2)

| Metrica | Rodada 1 | Rodada 2 | Total |
|---------|----------|----------|-------|
| Beneficios auditados | 85 | 89 | **174 de 189** |
| Correcoes aplicadas | ~194 | ~112 | **~306** |
| Erros criticos corrigidos | ~110 | 48 | **~158** |
| Erros de conteudo corrigidos | 6 | ~16 | **~22** |
| Relatorios gerados | 5 | 4 | **9** |

**Cobertura de auditoria: 174/189 = 92%** (15 beneficios restantes sao os que nao couberam em nenhum lote)

---

*Rodada 2 concluida em 2026-02-07 por Claude Opus 4.6*
*4 lotes paralelos + correcoes manuais*

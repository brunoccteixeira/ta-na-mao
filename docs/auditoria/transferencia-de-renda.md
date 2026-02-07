# Auditoria: Transferencia de Renda (27 beneficios estaduais)
**Data**: 2026-02-07

## Resumo
- Total auditados: 27
- Conforme: 4 (am-auxilio-estadual-permanente, rs-devolve-icms, se-cartao-mais-inclusao, mt-ser-familia)
- Simplificado: 8 (ac, ap, pb, pi, rn, ro, rr, to - programas nao verificaveis com fontes oficiais)
- Incorreto: 9 (es-bolsa-capixaba, df-df-social, ms-mais-social, go-renda-cidada, mg-piso-mineiro, sp-renda-cidada, al-cartao-cria, pr-familia-paranaense, ce-cartao-superacao)
- Descontinuado: 2 (rj-supera-rj, pa-renda-para)
- Renomeado: 2 (rs-mais-igual -> rs-familia-gaucha, ma-mais-social -> ma-maranhao-livre-da-fome)
- Incompleto: 2 (sp-bolsa-do-povo, sc-santa-renda)
- Correcoes aplicadas: 10 arquivos JSON modificados

## Beneficio-modelo: Bolsa do Povo SP (sp-bolsa-do-povo)

### Fonte oficial
- Pagina oficial: https://www.bolsadopovo.sp.gov.br/
- Base legal: Lei Estadual 17.372/2021
- Programa guarda-chuva com varias acoes (Acao Jovem, Merenda em Casa, Frente de Trabalho, etc.)

### O que diziamos vs O que a fonte diz

| Item | JSON | Fonte oficial | Status |
|------|------|---------------|--------|
| Valor mensal | R$ 100-540 | Varia de R$ 100 a R$ 2.490 conforme a acao | SIMPLIFICADO |
| Renda limite | R$ 3.200 (R$ 800 per capita) | Varia por acao; muitas usam per capita R$ 218 | SIMPLIFICADO |
| CadUnico | Obrigatorio | Obrigatorio para todas as acoes | OK |
| Canal | Site + CRAS | Site bolsadopovo.sp.gov.br + CRAS | OK |
| Documentos | CPF, NIS, comp. residencia | Varia por acao | SIMPLIFICADO |

### Checklist 12 itens
1. **Base legal**: Lei 17.372/2021 -- NAO DOCUMENTADA no JSON
2. **Elegibilidade**: Generica demais (programa guarda-chuva) -- SIMPLIFICADO
3. **Faixa etaria**: Nao especificada (varia por acao) -- SIMPLIFICADO
4. **CadUnico**: Corretamente exigido -- OK
5. **Documentos**: Genericos -- SIMPLIFICADO
6. **Valores**: R$ 100-540 subestima acoes de ate R$ 2.490 -- SIMPLIFICADO
7. **Canais**: Site + CRAS corretos -- OK
8. **Prazos**: Nao informados -- INCOMPLETO
9. **Geo**: SP -- OK
10. **Hardcoded**: Valores dentro da faixa mais comum -- OK
11. **Disclaimers**: Ausente -- INCOMPLETO
12. **Data**: 2026-02-04 -- OK

---

## Tabela de conformidade

| ID | UF | Nome | Valor JSON | Valor Real | Status | Corrigido? |
|----|-----|------|-----------|------------|--------|------------|
| sp-bolsa-do-povo | SP | Bolsa do Povo | R$100-540/m | R$100-2490/m | SIMPLIFICADO | Nao |
| sp-renda-cidada | SP | Renda Cidada | R$80-115/m | R$80/m fixo | SIMPLIFICADO | Nao |
| am-auxilio-estadual-permanente | AM | Auxilio Estadual | R$150/m | R$150/m | CONFORME | -- |
| rs-devolve-icms | RS | Devolve ICMS | R$30-33/m | R$100/trimestre | CONFORME | -- |
| mt-ser-familia | MT | Ser Familia | R$150-300/m | R$150-300/m | CONFORME | -- |
| se-cartao-mais-inclusao | SE | CMais Inclusao | R$100-300/m | Confirmado ativo | CONFORME | Sim (fonte/desc) |
| df-df-social | DF | DF Social | R$150-300/m | R$150/m fixo | INCORRETO | Sim |
| es-bolsa-capixaba | ES | Bolsa Capixaba | R$150/m | R$50-600/m | INCORRETO | Sim |
| ms-mais-social | MS | Mais Social | R$200-450/m | R$450/m fixo | INCORRETO | Sim |
| go-renda-cidada | GO | Renda Cidada | R$100-250/m | R$80-160/m | INCORRETO | Sim |
| mg-piso-mineiro | MG | Piso Mineiro | R$65-130/m | R$0 (repasse mun.) | INCORRETO | Sim |
| al-cartao-cria | AL | Cartao CRIA | R$100-300/m | R$150/m fixo | INCORRETO | Nao* |
| pr-familia-paranaense | PR | Fam. Paranaense | R$100-300/m | Complementa a R$95 pc | INCORRETO | Nao* |
| ce-cartao-superacao | CE | Cartao Superacao | R$100-300/m | NAO ENCONTRADO | INCORRETO | Nao* |
| rj-supera-rj | RJ | Supera RJ | R$200-500/m | ENCERRADO jul/2023 | DESCONTINUADO | Sim |
| pa-renda-para | PA | Renda Para | R$100-200/m | Emergencial (encerrado?) | DESCONTINUADO | Sim |
| rs-mais-igual | RS | RS Mais Igual | R$50-150/m | NAO EXISTE | RENOMEADO | Sim (-> Familia Gaucha) |
| ma-mais-social | MA | Mais Social | R$100-350/m | R$200+50/crianca | RENOMEADO | Sim (-> MA Livre da Fome) |
| ac-auxilio-renda-acre | AC | Auxilio Renda Acre | R$100-150/m | Nao verificavel | SIMPLIFICADO | Nao |
| ap-auxilio-social-amapa | AP | Auxilio Social AP | R$100-150/m | Nao verificavel | SIMPLIFICADO | Nao |
| pb-pbsocial | PB | PB Social | R$100-300/m | Nao encontrado | SIMPLIFICADO | Nao |
| pi-cartao-mais-renda | PI | Cartao Mais Renda | R$100-300/m | Nao encontrado | SIMPLIFICADO | Nao |
| rn-rn-mais-igual | RN | RN Mais Igual | R$100-300/m | Nao encontrado | SIMPLIFICADO | Nao |
| ro-auxilio-renda-rondonia | RO | Aux. Renda RO | R$100-150/m | Programa Vencer R$200/m | SIMPLIFICADO | Nao |
| rr-auxilio-social-roraima | RR | Aux. Social RR | R$100-150/m | Nao verificavel | SIMPLIFICADO | Nao |
| sc-santa-renda | SC | Santa Renda | R$100-200/m | Nao encontrado (SC nao tem TR estadual) | INCOMPLETO | Nao |
| to-auxilio-social-tocantins | TO | Aux. Social TO | R$100-150/m | Nao verificavel | SIMPLIFICADO | Nao |

*Nao corrigidos nesta rodada para manter escopo; flagged para proxima auditoria.

**Legenda**: CONFORME = dados corretos, SIMPLIFICADO = dados estimados/genericos, INCORRETO = dados errados corrigidos ou flagged, DESCONTINUADO = programa encerrado, RENOMEADO = nome errado corrigido, INCOMPLETO = falta informacao critica

---

## Detalhes das correcoes aplicadas

### 1. es-bolsa-capixaba (Espirito Santo) -- INCORRETO -> CORRIGIDO
**Arquivo**: `frontend/src/data/benefits/states/es.json`
**Erros encontrados**:
- Valor era R$150 fixo; real e R$50 a R$600 (media R$164)
- Renda per capita era R$218; real e R$155
- Faltava regra: NAO pode receber Bolsa Familia
- Source URL generica

**Correcoes**:
- estimatedValue: min 150->50, max 150->600
- rendaFamiliarMensal: 872->620 (R$155 per capita x 4)
- Adicionada regra recebeBolsaFamilia eq false
- sourceUrl atualizada para pagina especifica da SETADES
- Fonte: https://setades.es.gov.br/Acessar-o-beneficio-do-Bolsa-Capixaba

### 2. rj-supera-rj (Rio de Janeiro) -- DESCONTINUADO
**Arquivo**: `frontend/src/data/benefits/states/rj.json`
**Erros encontrados**:
- Programa ENCERRADO em julho de 2023 pelo Gov. Claudio Castro
- Beneficiarios migrados para Bolsa Familia
- Estava marcado como "active"

**Correcoes**:
- status: "active" -> "discontinued"
- shortDescription: atualizada informando encerramento
- howToApply: redirecionando para Bolsa Familia
- max value: 500->380 (valor real era R$200+R$80+R$50x2)
- rendaFamiliarMensal: 872->840 (per capita R$210)
- sourceUrl: atualizada para noticia da Agencia Brasil sobre encerramento
- Fonte: https://agenciabrasil.ebc.com.br/geral/noticia/2023-07/governo-estadual-encerra-programa-supera-rj

### 3. rs-mais-igual -> rs-familia-gaucha (Rio Grande do Sul)
**Arquivo**: `frontend/src/data/benefits/states/rs.json`
**Erros encontrados**:
- Programa "RS Mais Igual" NAO EXISTE
- Programa real e "Familia Gaucha", lancado em 2025

**Correcoes**:
- id: "rs-mais-igual" -> "rs-familia-gaucha"
- name: "RS Mais Igual" -> "Familia Gaucha"
- Valores: R$200 base + R$50 por crianca 0-6 (max R$250)
- Temporario: 22 meses de duracao
- 92 municipios participantes
- Selecao por IVF/RS (Indice de Vulnerabilidade Familiar)
- sourceUrl: https://social.rs.gov.br/familia-gaucha
- Fonte: https://estado.rs.gov.br/transferencia-de-renda-do-programa-familia-gaucha-e-aprovada-pela-assembleia-e-se-tornara-lei-estadual

### 4. df-df-social (Distrito Federal) -- INCORRETO -> CORRIGIDO
**Arquivo**: `frontend/src/data/benefits/states/df.json`
**Erros encontrados**:
- Valor era R$150-300 (variavel); real e R$150 fixo
- Renda per capita era R$218; real e R$606

**Correcoes**:
- estimatedValue: max 300->150, description fixa
- rendaFamiliarMensal: 872->2424 (R$606 per capita x 4)
- Fonte: pesquisa web confirmou R$150/mes fixo, 70k familias

### 5. ms-mais-social (Mato Grosso do Sul) -- INCORRETO -> CORRIGIDO
**Arquivo**: `frontend/src/data/benefits/states/ms.json`
**Erros encontrados**:
- Valor era R$200-450; real e R$450 fixo (desde jan/2024)
- Renda era per capita R$218; real e meio salario minimo (~R$759)
- Uso exclusivo para alimentos, gas e produtos de limpeza/higiene
- Residencia minima de 2 anos em MS
- Source URL generica

**Correcoes**:
- estimatedValue: min 200->450, max 450->450
- rendaFamiliarMensal: 872->3036 (meio SM per capita x 4)
- shortDescription: atualizada com valor e numero de beneficiarios
- sourceUrl: https://www.sead.ms.gov.br/programas-e-projetos/mais-social/
- Fonte: https://www.sead.ms.gov.br/perguntas-e-respostas-sobre-o-programa-mais-social/

### 6. go-renda-cidada (Goias) -- INCORRETO -> CORRIGIDO
**Arquivo**: `frontend/src/data/benefits/states/go.json`
**Erros encontrados**:
- Valor era R$100-250; real e R$80-160
- Renda era R$1.090; real e per capita R$150 = R$600 para familia de 4
- Duracao: 24 meses renovaveis
- Operado pela Caixa

**Correcoes**:
- estimatedValue: min 100->80, max 250->160
- rendaFamiliarMensal: 1090->600 (R$150 per capita x 4)
- sourceUrl: atualizada para pagina oficial do programa
- Fonte: https://goias.gov.br/controladoria/programa-renda-cidada-torna-se-mais-eficaz-e-transparente/

### 7. mg-piso-mineiro (Minas Gerais) -- INCORRETO -> CORRIGIDO
**Arquivo**: `frontend/src/data/benefits/states/mg.json`
**Erros encontrados**:
- CRITICO: O "Piso Mineiro" NAO e um beneficio direto ao cidadao
- E um mecanismo de co-financiamento estadual para municipios (R$5/familia repassado as prefeituras)
- Estava representado como transferencia direta de R$65-130/mes ao cidadao

**Correcoes**:
- estimatedValue: min/max -> 0 (nao ha pagamento direto)
- shortDescription: corrigida para informar que e repasse ao municipio
- howToApply: redirecionando cidadao ao CRAS para acoes municipais
- Adicionado campo estimated e estimatedRationale explicando a natureza do repasse
- Fonte: pesquisa web confirmou que e co-financiamento, nao transferencia direta

### 8. ma-mais-social -> ma-maranhao-livre-da-fome (Maranhao)
**Arquivo**: `frontend/src/data/benefits/states/ma.json`
**Erros encontrados**:
- Programa "Mais Social" com este formato NAO EXISTE no MA
- Programa real e "Maranhao Livre da Fome" (lancado mai/2025)
- Valor R$200/mes + R$50 por crianca 0-6 (nao R$100-350)
- Exige Bolsa Familia como pre-requisito

**Correcoes**:
- id: "ma-mais-social" -> "ma-maranhao-livre-da-fome"
- name: "Mais Social" -> "Maranhao Livre da Fome"
- Valores: R$200 base + R$50/crianca 0-6 (max R$350)
- Adicionada regra recebeBolsaFamilia eq true
- 95 mil familias atendidas
- sourceUrl: https://maranhaolivredafome.ma.gov.br/
- Fonte: https://www.correiobraziliense.com.br/opiniao/2025/05/7147834-maranhao-livre-da-fome-um-marco-no-desenvolvimento-social-e-economico.html

### 9. se-cartao-mais-inclusao (Sergipe) -- CONFORME (melhorado)
**Arquivo**: `frontend/src/data/benefits/states/se.json`
**Melhorias**:
- Confirmado programa ativo e permanente (Lei 9.238/2023)
- Modalidades: CMais Cidadania, CMais Sergipe Acolhe, CMais Ser Crianca
- Inscricoes abertas pelo site cmaisinscricoes.assistenciasocial.se.gov.br
- Cartoes entregues nas agencias do Banese
- sourceUrl atualizada com pagina oficial da SEASIC

### 10. pa-renda-para (Para) -- DESCONTINUADO/INCERTO
**Arquivo**: `frontend/src/data/benefits/states/pa.json`
**Erros encontrados**:
- Programa era emergencial (COVID-19), criado em 2020
- Teve fases: Renda Para 100 (R$100), 400 (R$400), 500 (R$500)
- Operado pelo Banpara
- Ultimos pagamentos registrados em 2021-2022
- Status "active" era incorreto

**Correcoes**:
- status: "active" -> "uncertain"
- estimatedValue type: "monthly" -> "one_time"
- shortDescription: atualizada informando natureza emergencial
- sourceUrl: atualizada para pagina especifica do Renda Para na SEASTER
- Adicionados campos estimated e estimatedRationale

---

## Programas nao verificaveis (SIMPLIFICADOS)

Os 8 programas abaixo usam nomes genericos, sourceUrls genericas (portal do estado) e nao foram encontrados em buscas web. Provavelmente sao estimativas baseadas em programas federais/tipicos, nao programas estaduais reais com legislacao propria:

| ID | UF | Problema | Recomendacao |
|----|-----|----------|--------------|
| ac-auxilio-renda-acre | AC | Nenhum resultado web | Pesquisar "Acoprotege" ou programa real do AC |
| ap-auxilio-social-amapa | AP | Nenhum resultado web | Verificar no site da SEAD-AP |
| pb-pbsocial | PB | Nome nao encontrado. PB tem "Paraiba que Acolhe" (orfaos COVID) | Substituir por programa real |
| pi-cartao-mais-renda | PI | Nome nao encontrado. PI tem "Luz do Povo" e "Gas do Povo" | Substituir por programa real |
| rn-rn-mais-igual | RN | Nome nao encontrado | Pesquisar programa real do RN |
| ro-auxilio-renda-rondonia | RO | RO tem "Programa Vencer" (R$200/mes, 1 ano) | Substituir por Vencer |
| rr-auxilio-social-roraima | RR | Nenhum resultado web | Verificar no site do gov RR |
| to-auxilio-social-tocantins | TO | Nenhum resultado web | Verificar na SETAS-TO |

### Nota sobre Santa Catarina (sc-santa-renda)
Santa Catarina NAO possui programa estadual de transferencia de renda. Uma proposta (PL 0092.0/2021) para criar "Programa de Renda Basica" ainda tramita. O "Santa Renda" no JSON provavelmente e ficticio. SC tem outros beneficios (Gestacao Multipla R$592/crianca, Bolsa Estudantil R$50-568) mas nenhum de transferencia de renda pura.

---

## Programas flagged para proxima auditoria

### al-cartao-cria (Alagoas)
- Valor no JSON: R$100-300/mes
- Pesquisa indica R$150/mes fixo
- Precisa corrigir para min/max 150

### pr-familia-paranaense (Parana)
- Valor no JSON: R$100-300/mes
- Pesquisa indica "Renda Familia Paranaense" que complementa renda ate R$95 per capita
- Nome e valores precisam correcao

### ce-cartao-superacao (Ceara)
- Programa nao encontrado em buscas web
- CE tem "Cartao Mais Infancia" (R$100/mes, 0-6 anos) e "Ceara Sem Fome" (R$300/mes)
- Possivelmente confundido com outro programa
- Precisa verificacao com a SPS-CE

### sp-renda-cidada (Sao Paulo)
- Valor no JSON: R$80-115/mes
- Pesquisa indica R$80/mes fixo (nao faixa)
- Correcao menor, baixa prioridade

### sp-bolsa-do-povo (Sao Paulo)
- Programa guarda-chuva com muitas acoes
- Valor maximo pode chegar a R$2.490 (Frente de Trabalho)
- JSON usa R$540 como maximo, que cobre apenas acoes menores

---

## Checklist por beneficio

| ID | BaseLeg | Elegib | Idade | CadUn | Docs | Valores | Canais | Prazos | Geo | Hardcode | Discl | Data | Class. |
|----|---------|--------|-------|-------|------|---------|--------|--------|-----|----------|-------|------|--------|
| sp-bolsa-do-povo | N/A | SIMP | N/A | OK | SIMP | SIMP | OK | N/A | OK | OK | N/A | OK | INCOMPLETO |
| sp-renda-cidada | N/A | OK | N/A | OK | OK | SIMP | OK | N/A | OK | OK | N/A | OK | SIMPLIFICADO |
| am-auxilio-estadual | N/A | OK | N/A | OK | OK | OK | OK | N/A | OK | OK | N/A | OK | CONFORME |
| rs-devolve-icms | N/A | OK | N/A | OK | OK | OK | OK | N/A | OK | OK | N/A | OK | CONFORME |
| rs-familia-gaucha | N/A | OK | N/A | OK | OK | CORR | OK | CORR | OK | CORR | N/A | CORR | CORRIGIDO |
| mt-ser-familia | N/A | OK | N/A | OK | OK | OK | OK | N/A | OK | OK | N/A | OK | CONFORME |
| se-cartao-mais-inclusao | N/A | OK | N/A | OK | OK | OK | CORR | N/A | OK | OK | N/A | CORR | CONFORME |
| df-df-social | N/A | CORR | N/A | OK | OK | CORR | OK | N/A | OK | CORR | N/A | CORR | CORRIGIDO |
| es-bolsa-capixaba | N/A | CORR | N/A | OK | OK | CORR | OK | N/A | OK | CORR | N/A | CORR | CORRIGIDO |
| ms-mais-social | N/A | CORR | N/A | OK | OK | CORR | OK | N/A | OK | CORR | N/A | CORR | CORRIGIDO |
| go-renda-cidada | N/A | CORR | N/A | OK | OK | CORR | OK | CORR | OK | CORR | N/A | CORR | CORRIGIDO |
| mg-piso-mineiro | N/A | CORR | N/A | OK | OK | CORR | CORR | N/A | OK | CORR | CORR | CORR | CORRIGIDO |
| al-cartao-cria | N/A | OK | N/A | OK | OK | INC | OK | N/A | OK | INC | N/A | OK | INCORRETO* |
| pr-familia-paranaense | N/A | OK | N/A | OK | OK | INC | OK | N/A | OK | INC | N/A | OK | INCORRETO* |
| ce-cartao-superacao | N/A | INC | N/A | N/A | OK | INC | OK | N/A | OK | INC | N/A | OK | INCORRETO* |
| rj-supera-rj | N/A | CORR | N/A | OK | OK | CORR | CORR | CORR | OK | CORR | CORR | CORR | DESCONTINUADO |
| pa-renda-para | N/A | OK | N/A | OK | OK | CORR | OK | CORR | OK | CORR | CORR | CORR | DESCONTINUADO |
| ma-maranhao-livre-fome | N/A | CORR | N/A | CORR | CORR | CORR | CORR | CORR | OK | CORR | N/A | CORR | CORRIGIDO |
| ac-auxilio-renda-acre | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| ap-auxilio-social-amapa | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| pb-pbsocial | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| pi-cartao-mais-renda | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| rn-rn-mais-igual | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| ro-auxilio-renda-rondonia | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| rr-auxilio-social-roraima | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |
| sc-santa-renda | N/A | INC | N/A | OK | OK | INC | OK | N/A | OK | INC | N/A | OK | INCOMPLETO |
| to-auxilio-social-tocantins | N/A | SIMP | N/A | OK | OK | SIMP | OK | N/A | OK | SIMP | N/A | OK | SIMPLIFICADO |

**Legenda**: OK = conforme, SIMP = simplificado, CORR = corrigido nesta auditoria, INC = incompleto/incorreto nao corrigido, N/A = nao aplicavel
*Flagged para proxima auditoria

---

## Fontes consultadas

### Programas confirmados
- [Bolsa Capixaba - SETADES](https://setades.es.gov.br/Acessar-o-beneficio-do-Bolsa-Capixaba)
- [Mais Social MS - SEAD](https://www.sead.ms.gov.br/programas-e-projetos/mais-social/)
- [Renda Cidada GO - Controladoria](https://goias.gov.br/controladoria/programa-renda-cidada-torna-se-mais-eficaz-e-transparente/)
- [Familia Gaucha RS - SEDES](https://social.rs.gov.br/familia-gaucha)
- [Familia Gaucha aprovada na Assembleia RS](https://estado.rs.gov.br/transferencia-de-renda-do-programa-familia-gaucha-e-aprovada-pela-assembleia-e-se-tornara-lei-estadual)
- [Maranhao Livre da Fome](https://maranhaolivredafome.ma.gov.br/)
- [Cartao Mais Inclusao SE - SEASIC](https://assistenciasocial.se.gov.br/seasic-divulga-lista-dos-contemplados-com-o-cartao-cmais/)
- [CMais Inclusao - inscricoes](https://a8se.com/noticias/sergipe/programa-cmais-inclusao-esta-com-inscricoes-abertas-em-sergipe/)
- [Renda Para - SEASTER](https://www.seaster.pa.gov.br/rendapara.html)
- [Renda Para - Lei 9318/2021](https://www.legisweb.com.br/legislacao/?id=420622)

### Programas descontinuados
- [Supera RJ encerrado - Agencia Brasil](https://agenciabrasil.ebc.com.br/geral/noticia/2023-07/governo-estadual-encerra-programa-supera-rj)
- [Supera RJ - site oficial (FAQ)](https://www.superarj.rj.gov.br/faq)

### Programas nao encontrados
- ac-auxilio-renda-acre: nenhum resultado web
- ap-auxilio-social-amapa: nenhum resultado web
- pb-pbsocial: PB tem "Paraiba que Acolhe" (orfaos COVID, R$559/mes)
- pi-cartao-mais-renda: PI tem "Luz do Povo" e "Gas do Povo"
- rn-rn-mais-igual: nenhum resultado web
- ro-auxilio-renda-rondonia: RO tem "Programa Vencer" (R$200/mes)
- rr-auxilio-social-roraima: nenhum resultado web
- sc-santa-renda: SC nao tem TR estadual (PL em tramitacao)
- to-auxilio-social-tocantins: nenhum resultado web
- ce-cartao-superacao: nao encontrado (CE tem Cartao Mais Infancia e Ceara Sem Fome)

---

## Proximos passos
1. **Prioridade alta**: Corrigir al-cartao-cria (R$150 fixo), pr-familia-paranaense (complementa a R$95 pc), ce-cartao-superacao (verificar com SPS-CE)
2. **Prioridade media**: Substituir 8 programas genericos (AC, AP, PB, PI, RN, RO, RR, TO) por programas reais verificados
3. **Prioridade media**: Decidir se sc-santa-renda deve ser removido (SC nao tem TR estadual)
4. **Prioridade baixa**: Adicionar base legal (legalBasis) em todos os programas confirmados
5. **Prioridade baixa**: Adicionar disclaimers em valores estimados

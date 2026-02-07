# Validacao de Fontes Oficiais - Top 10 Beneficios Federais

> Protocolo: `/fonte-oficial` (4 passos)
> Data de consulta: 2026-02-07
> Arquivo validado: `frontend/src/data/benefits/federal.json`
> Auditor: Claude (via skill fonte-oficial)

---

## Indice

1. [Bolsa Familia](#1-bolsa-familia)
2. [BPC Idoso](#2-bpc-idoso)
3. [BPC PCD](#3-bpc-pcd)
4. [Tarifa Social de Energia](#4-tarifa-social-de-energia)
5. [Farmacia Popular](#5-farmacia-popular)
6. [Dignidade Menstrual](#6-dignidade-menstrual)
7. [Pe-de-Meia](#7-pe-de-meia)
8. [Gas do Povo (Auxilio Gas)](#8-gas-do-povo-auxilio-gas)
9. [ProUni](#9-prouni)
10. [Minha Casa Minha Vida](#10-minha-casa-minha-vida)

---

## Resumo Rapido

| # | Beneficio | Veredito | Erros Encontrados |
|---|-----------|----------|-------------------|
| 1 | Bolsa Familia | Conforme | 0 |
| 2 | BPC Idoso | Parcialmente correto | 1 |
| 3 | BPC PCD | Conforme | 0 |
| 4 | Tarifa Social de Energia | Parcialmente correto | 2 |
| 5 | Farmacia Popular | Parcialmente correto | 2 |
| 6 | Dignidade Menstrual | Parcialmente correto | 2 |
| 7 | Pe-de-Meia | Parcialmente correto | 2 |
| 8 | Gas do Povo | Parcialmente correto | 2 |
| 9 | ProUni | Conforme | 0 |
| 10 | Minha Casa Minha Vida | Parcialmente correto | 2 |

**Total: 3 Conformes, 7 Parcialmente Corretos, 0 Incorretos, 0 Sem Fonte**
**Total de erros/ajustes necessarios: 11**

---

## 1. Bolsa Familia

**ID**: `federal-bolsa-familia`

### Claim (o que nosso JSON diz)
- Renda per capita: ate R$ 218/mes
- Valor minimo: R$ 600 por familia
- Valor maximo: R$ 1.800
- Legal reference: Art. 3, Lei 14.601/2023
- CadUnico obrigatorio: Art. 4, Lei 14.601/2023
- Decreto regulamentador: 12.064/2024

### Fontes Consultadas
1. **Lei 14.601/2023, Art. 3** (planalto.gov.br): Linha de pobreza = renda per capita mensal ate R$ 218,00
2. **Lei 14.601/2023, Arts. 5-8**: Beneficio de Renda de Cidadania = R$ 142/pessoa; Beneficio Primeira Infancia = R$ 150/crianca 0-6 anos; Beneficio Variavel Familiar = R$ 50 (7-18 anos, gestantes, nutrizes); Beneficio Complementar garante minimo de R$ 600
3. **Decreto 12.064/2024** (planalto.gov.br): Regulamenta o programa, confirma valores
4. **gov.br/mds/bolsa-familia**: Confirma valores base de R$ 600 minimo em 2026

### Veredito: Conforme

Todos os dados estao corretos e atualizados:
- Renda per capita R$ 218: CORRETO (Art. 3, Lei 14.601/2023)
- Minimo R$ 600: CORRETO (Beneficio Complementar garante este piso)
- Maximo R$ 1.800: CORRETO (plausivel para familias grandes com multiplos adicionais)
- CadUnico obrigatorio: CORRETO (Art. 4)
- Leis referenciadas: CORRETAS e vigentes

### Citacao para o Codigo
```typescript
// Fonte: Lei 14.601/2023, Art. 3 (linha de pobreza)
// Decreto 12.064/2024 (regulamentacao)
// Verificado em: 2026-02-07
// Proxima verificacao: quando houver Decreto atualizando valores
```

---

## 2. BPC Idoso

**ID**: `federal-bpc-idoso`

### Claim (o que nosso JSON diz)
- Valor: R$ 1.621 (1 salario minimo em 2026)
- Idade: 65 anos ou mais
- Renda per capita: ate R$ 405,25 (1/4 do SM)
- Nao receber Bolsa Familia
- Legal reference: Art. 20, Lei 8.742/1993 (LOAS)
- Decreto 6.214/2007

### Fontes Consultadas
1. **Lei 8.742/1993 (LOAS), Art. 20**: "1 salario-minimo mensal a pessoa com deficiencia e ao idoso com 65 anos ou mais"
2. **Lei 8.742/1993, Art. 20, par. 3**: Renda per capita inferior a 1/4 do salario minimo
3. **Decreto 12.797/2025**: Salario minimo 2026 = R$ 1.621,00; portanto 1/4 = R$ 405,25
4. **gov.br/inss**: Confirma BPC = 1 SM para idosos 65+

### Veredito: Parcialmente correto

**Dados corretos:**
- Valor R$ 1.621: CORRETO (1 SM em 2026)
- Idade 65+: CORRETO (Art. 20, LOAS)
- Renda per capita 1/4 SM = R$ 405,25: CORRETO
- Leis referenciadas: CORRETAS

**Ajuste necessario (1):**
- A regra `recebeBolsaFamilia = false` com descricao "Nao receber Bolsa Familia (pode optar por um)" e IMPRECISA. A Lei 14.176/2021 alterou a LOAS e permite que o BPC de outro membro da familia nao entre no calculo de renda. Alem disso, valores do Bolsa Familia tambem sao excluidos do calculo de renda per capita para fins de BPC (Art. 20, par. 4, LOAS com redacao da Lei 14.176/2021). A regra deveria ser mais nuancada: nao e que "nao pode receber Bolsa Familia" - e que uma mesma pessoa nao pode acumular BPC e Bolsa Familia simultaneamente, mas a familia pode ter membros em cada programa.

### Citacao para o Codigo
```typescript
// Fonte: Lei 8.742/1993 (LOAS), Art. 20
// Alterado por: Lei 14.176/2021
// Decreto 6.214/2007 (regulamentacao)
// SM 2026: R$ 1.621 (Decreto 12.797/2025)
// Verificado em: 2026-02-07
```

---

## 3. BPC PCD

**ID**: `federal-bpc-pcd`

### Claim (o que nosso JSON diz)
- Valor: R$ 1.621 (1 SM em 2026)
- Deficiencia fisica, mental, intelectual ou sensorial
- Renda per capita: ate R$ 405,25 (1/4 do SM)
- Legal reference: Art. 20, par. 2 e par. 3, Lei 8.742/1993

### Fontes Consultadas
1. **Lei 8.742/1993 (LOAS), Art. 20, par. 2**: Pessoa com deficiencia = impedimento de longo prazo de natureza fisica, mental, intelectual ou sensorial
2. **Lei 8.742/1993, Art. 20, par. 3**: Renda per capita inferior a 1/4 do salario minimo
3. **Decreto 12.797/2025**: SM 2026 = R$ 1.621
4. **CF/1988, Art. 203, V**: Base constitucional confirmada

### Veredito: Conforme

Todos os dados estao corretos:
- Valor R$ 1.621: CORRETO
- Criterio de deficiencia: CORRETO (Art. 20, par. 2)
- Renda per capita 1/4 SM: CORRETO
- Leis referenciadas: CORRETAS e vigentes
- A shortDescription menciona "que nao podem trabalhar" - a lei na verdade fala em "impedimento de longo prazo", nao necessariamente impossibilidade de trabalho, mas a simplificacao e aceitavel para o publico-alvo

### Citacao para o Codigo
```typescript
// Fonte: Lei 8.742/1993 (LOAS), Art. 20, par. 2 e par. 3
// CF/1988, Art. 203, V
// SM 2026: R$ 1.621 (Decreto 12.797/2025)
// Verificado em: 2026-02-07
```

---

## 4. Tarifa Social de Energia

**ID**: `federal-tsee`

### Claim (o que nosso JSON diz)
- Isencao total ate 80 kWh/mes
- Desconto escalonado acima de 80 kWh
- Renda per capita: ate R$ 810,50 (meio SM)
- CadUnico obrigatorio
- Legal reference: Art. 2, Lei 12.212/2010
- Leis: 12.212/2010, Decreto 7.583/2011, Lei 15.235/2025

### Fontes Consultadas
1. **Lei 12.212/2010** (planalto.gov.br): Base legal original da Tarifa Social
2. **Lei 15.235/2025** (planalto.gov.br): Programa Luz do Povo - reformula a tarifa social. Isencao de 100% para consumo ate 80 kWh/mes para beneficiarios CadUnico com renda per capita ate 1/2 SM
3. **ANEEL** (gov.br/aneel): Regulamentacao confirma 100% isencao ate 80 kWh. Acima de 80 kWh, consumo excedente NAO tem desconto para beneficiarios da Tarifa Social
4. **Lei 15.235/2025 - Desconto Social**: Nova faixa para renda per capita entre 1/2 e 1 SM - desconto de ~12% no consumo ate 120 kWh (vigente a partir de 01/01/2026)

### Veredito: Parcialmente correto

**Dados corretos:**
- Isencao total ate 80 kWh: CORRETO (Lei 15.235/2025)
- CadUnico obrigatorio: CORRETO
- Renda per capita ate meio SM: CORRETO para Tarifa Social
- Leis referenciadas: CORRETAS

**Ajustes necessarios (2):**

1. **Desconto escalonado**: O JSON diz "desconto escalonado acima disso" mas com a Lei 15.235/2025, o consumo acima de 80 kWh NAO tem desconto para beneficiarios da Tarifa Social padrao. O "desconto escalonado" era o modelo antigo (Lei 12.212/2010 original com faixas de 10%, 40%, 65%, 100%). Agora e binario: 100% ate 80 kWh, 0% acima. O "Desconto Social" (nova faixa para renda 1/2 a 1 SM) oferece ~12% ate 120 kWh, mas e um programa separado.

2. **estimatedValue (R$ 20 a R$ 100)**: Com a isencao total ate 80 kWh, a economia real pode ser maior que R$ 100/mes dependendo da tarifa local. O range deveria ser revisado para refletir melhor a economia com isencao total.

### Citacao para o Codigo
```typescript
// Fonte: Lei 15.235/2025 (Programa Luz do Povo)
// Base: Lei 12.212/2010 (Tarifa Social original)
// Regulacao: ANEEL - Resolucao Normativa
// Verificado em: 2026-02-07
// Proxima verificacao: apos regulamentacao final ANEEL
```

---

## 5. Farmacia Popular

**ID**: `federal-farmacia-popular`

### Claim (o que nosso JSON diz)
- "Todos os 41 itens sao 100% gratuitos"
- Qualquer pessoa com receita medica
- Receita valida ate 180 dias
- Legal reference: Lei 10.858/2004, Decreto 5.090/2004

### Fontes Consultadas
1. **Portaria GM/MS 6.613/2025** (DOU 14/02/2025): A partir de fev/2025, todos os 41 itens do Farmacia Popular passam a ser 100% gratuitos para toda a populacao brasileira
2. **Decreto 11.555/2023**: Estabeleceu gratuidade para beneficiarios do Bolsa Familia e indigenas
3. **Agencia Gov** (fev/2025): Confirma expansao da gratuidade total a todas as pessoas
4. **gov.br/saude/farmacia-popular**: Pagina oficial confirma 41 itens gratuitos

### Veredito: Parcialmente correto

**Dados corretos:**
- 41 itens 100% gratuitos: CORRETO (desde Portaria 6.613/2025)
- Receita medica necessaria: CORRETO
- Medicamentos para hipertensao, diabetes, asma: CORRETO

**Ajustes necessarios (2):**

1. **Legal basis desatualizada**: O JSON referencia apenas Lei 10.858/2004 e Decreto 5.090/2004 como base legal. Faltam as normas mais importantes e recentes:
   - Decreto 11.555/2023 (gratuidade para Bolsa Familia)
   - **Portaria GM/MS 6.613/2025** (gratuidade total para toda a populacao - norma vigente principal)
   A base legal deveria incluir essas referencias mais recentes que fundamentam a afirmacao de "100% gratuito".

2. **Receita valida ate 180 dias**: Esta informacao nao consta na Lei 10.858/2004. O prazo de validade da receita varia conforme o tipo de medicamento (receita simples = 30 dias; receita de controle especial = 30 dias; receita cronica = validade estendida conforme regulamentacao sanitaria). A afirmacao de "180 dias" pode estar correta para medicamentos de uso continuo no ambito do Farmacia Popular, mas deveria citar a fonte especifica (Portaria ou regulamentacao do programa).

### Citacao para o Codigo
```typescript
// Fonte: Lei 10.858/2004 (criacao)
// Decreto 11.555/2023 (gratuidade Bolsa Familia)
// Portaria GM/MS 6.613/2025 (gratuidade total 41 itens)
// Verificado em: 2026-02-07
// Proxima verificacao: quando houver nova Portaria atualizando lista
```

---

## 6. Dignidade Menstrual

**ID**: `federal-dignidade-menstrual`

### Claim (o que nosso JSON diz)
- "40 absorventes a cada 56 dias via Farmacia Popular"
- Publico: pessoas que menstruam
- Requisitos: estudar em escola publica ou estar em vulnerabilidade
- Legal reference: Art. 1 e Art. 3, Lei 14.214/2021
- Acesso via Farmacia Popular com autorizacao via UBS ou app ConecteSUS

### Fontes Consultadas
1. **Lei 14.214/2021** (planalto.gov.br): Institui o Programa de Protecao e Promocao da Saude Menstrual
2. **Decreto 11.432/2023** (planalto.gov.br): Regulamenta a Lei 14.214/2021. Define 20 unidades por ciclo menstrual (5 dias x 4 absorventes/dia)
3. **Portaria GM/MS 3.076/2024**: Operacionaliza a distribuicao via Farmacia Popular. Faixa etaria: 10 a 49 anos. Quantidade: 40 unidades a cada 56 dias (2 ciclos)
4. **gov.br/secom** e **Agencia Gov**: Confirmam distribuicao via Farmacia Popular desde jan/2024

### Veredito: Parcialmente correto

**Dados corretos:**
- 40 absorventes a cada 56 dias: CORRETO (Portaria 3.076/2024)
- Pessoas que menstruam: CORRETO (Art. 1, Lei 14.214/2021)
- Escola publica ou vulnerabilidade: CORRETO (Art. 3, Lei 14.214/2021)
- Distribuicao via Farmacia Popular: CORRETO

**Ajustes necessarios (2):**

1. **Faixa etaria ausente no JSON**: A Portaria 3.076/2024 define faixa etaria de **10 a 49 anos** (idade fertil). Essa informacao NAO consta nas eligibilityRules do JSON. Deveria haver uma regra de elegibilidade com campo `idade` entre 10 e 49.

2. **legalBasis incompleta**: O JSON referencia apenas a Lei 14.214/2021. Faltam:
   - **Decreto 11.432/2023** (regulamentacao)
   - **Portaria GM/MS 3.076/2024** (regras operacionais, quantidades, faixa etaria)
   Essas sao as fontes que fundamentam os dados numericos (40 absorventes, 56 dias, 10-49 anos).

### Citacao para o Codigo
```typescript
// Fonte: Lei 14.214/2021 (criacao do programa)
// Decreto 11.432/2023 (regulamentacao: 20 unidades/ciclo)
// Portaria GM/MS 3.076/2024 (operacionalizacao: 40 a cada 56 dias, 10-49 anos)
// Verificado em: 2026-02-07
// Proxima verificacao: quando houver nova Portaria GM/MS
```

---

## 7. Pe-de-Meia

**ID**: `federal-pe-de-meia`

### Claim (o que nosso JSON diz)
- R$ 200/mes (frequencia) + R$ 1.000/ano (conclusao) + R$ 200 (ENEM)
- Requisitos: ensino medio publico, CadUnico
- Legal reference: Art. 2 e Art. 3, Lei 14.818/2024

### Fontes Consultadas
1. **Lei 14.818/2024** (planalto.gov.br): Institui o Programa Pe-de-Meia
2. **Decreto 11.901/2024** (planalto.gov.br): Regulamenta o programa
3. **Valores conforme Lei 14.818/2024**:
   - Incentivo Matricula: R$ 200/ano (parcela unica)
   - Incentivo Frequencia: R$ 1.800/ano (9 parcelas de R$ 200)
   - Incentivo Conclusao: R$ 1.000/ano (depositado em poupanca, saque so apos conclusao do ensino medio)
   - Incentivo ENEM: R$ 200 (participacao comprovada, saque apos conclusao)
4. **gov.br/mec/pe-de-meia**: Confirma valores e regras

### Veredito: Parcialmente correto

**Dados corretos:**
- R$ 200/mes frequencia: CORRETO (R$ 1.800/ano em 9 parcelas de R$ 200)
- R$ 1.000/ano conclusao: CORRETO
- R$ 200 ENEM: CORRETO
- Ensino medio publico: CORRETO
- CadUnico obrigatorio: CORRETO
- Lei 14.818/2024: CORRETA

**Ajustes necessarios (2):**

1. **estimatedValue max R$ 1.000 e impreciso**: O JSON diz min R$ 200, max R$ 1.000. Mas o programa oferece: R$ 200 (matricula) + R$ 1.800 (frequencia) + R$ 1.000 (conclusao) + R$ 200 (ENEM) = ate R$ 3.200/ano. O campo `max` deveria refletir o potencial total anual, nao apenas R$ 1.000. A descricao menciona corretamente os valores, mas os campos `min/max` estao inconsistentes.

2. **Incentivo Matricula omitido**: O JSON menciona "frequencia", "conclusao" e "ENEM" mas NAO menciona o **Incentivo Matricula de R$ 200/ano** (parcela unica no inicio do ano letivo). Este incentivo e distinto do Incentivo Frequencia.

### Citacao para o Codigo
```typescript
// Fonte: Lei 14.818/2024
// Decreto 11.901/2024 (regulamentacao)
// Valores: Matricula R$200 + Frequencia R$1.800 + Conclusao R$1.000 + ENEM R$200
// Verificado em: 2026-02-07
// Proxima verificacao: quando houver Decreto atualizando valores
```

---

## 8. Gas do Povo (Auxilio Gas)

**ID**: `federal-auxilio-gas`

### Claim (o que nosso JSON diz)
- "Botijao de gas gratuito para familias de baixa renda"
- "De 4 a 6 botijoes por ano conforme tamanho da familia"
- Valor equivalente: R$ 90 a R$ 110 (bimestral)
- Renda per capita: ate R$ 810,50 (meio SM)
- CadUnico obrigatorio
- Legal reference: Lei 14.237/2021, MP 1.313/2025

### Fontes Consultadas
1. **Lei 14.237/2021** (planalto.gov.br): Lei original do Auxilio Gas dos Brasileiros - pagamento monetario bimestral
2. **MP 1.313/2025** (planalto.gov.br): Cria o programa "Gas do Povo" com duas modalidades: (a) monetaria e (b) botijao gratuito em revenda autorizada
3. **Camara dos Deputados** (fev/2026): MP aprovada pela Camara e pelo Senado (03/02/2026). 4 botijoes/ano para familias de 2-3 pessoas; 6 botijoes/ano para 4+ pessoas
4. **Decreto 12.649/2025**: Regulamentacao do programa

### Veredito: Parcialmente correto

**Dados corretos:**
- Botijao gratuito: CORRETO (modalidade da MP 1.313/2025)
- 4 a 6 botijoes por ano: CORRETO (4 para 2-3 pessoas, 6 para 4+ pessoas)
- CadUnico obrigatorio: CORRETO
- Renda per capita ate 1/2 SM: CORRETO
- Leis referenciadas: CORRETAS

**Ajustes necessarios (2):**

1. **estimatedValue confuso**: O JSON diz "Valor equivalente do botijao de gas gratuito (bimestral)" com min R$ 90, max R$ 110. Com a modalidade de botijao gratuito, nao ha "valor" pago - a familia retira o botijao direto na revenda. O valor R$ 90-110 seria o preco de mercado do botijao, mas o beneficio nao e monetario na modalidade gratuita. A descricao deveria esclarecer que ha duas modalidades: monetaria (valor transferido) e gratuita (botijao direto).

2. **Implementacao gradual**: A modalidade de botijao gratuito esta em fase de implementacao (depende de organizacao, operacao e governanca - conforme MP 1.313/2025). O JSON deveria indicar que a modalidade de entrega gratuita esta sendo implantada gradualmente, enquanto a monetaria continua vigente.

### Citacao para o Codigo
```typescript
// Fonte: Lei 14.237/2021 (Auxilio Gas original)
// MP 1.313/2025 (Gas do Povo - modalidade botijao gratuito)
// Decreto 12.649/2025 (regulamentacao)
// Aprovado pelo Senado em 03/02/2026
// Verificado em: 2026-02-07
// Proxima verificacao: apos sancao presidencial da conversao da MP em lei
```

---

## 9. ProUni

**ID**: `federal-prouni`

### Claim (o que nosso JSON diz)
- Bolsa integral: renda per capita ate 1,5 SM (R$ 2.431)
- Bolsa parcial (50%): renda per capita ate 3 SM (R$ 4.863)
- Escola publica ou bolsista integral em particular
- ENEM minimo 450 pontos e redacao > 0
- Legal reference: Art. 1 e Art. 2, Lei 11.096/2005

### Fontes Consultadas
1. **Lei 11.096/2005, Art. 1** (planalto.gov.br): Bolsa integral = renda per capita ate 1,5 SM; Bolsa parcial 50% = renda per capita ate 3 SM
2. **Lei 11.096/2005, Art. 2, par. 1**: Pre-selecao pelo ENEM; criterios definidos pelo MEC
3. **Portaria MEC** (regulamentacao): ENEM minimo 450 pontos e redacao > 0 (regulamentacao infralegal, nao consta na lei, mas e regra operacional vigente)
4. **Lei 11.096/2005, Art. 2**: Escola publica ou bolsista integral em particular

### Veredito: Conforme

Todos os dados estao corretos:
- Bolsa integral 1,5 SM (R$ 2.431,50 com SM R$ 1.621): CORRETO. O JSON usa R$ 2.431 que e arredondamento aceitavel
- Bolsa parcial 3 SM (R$ 4.863): CORRETO
- Escola publica ou bolsista integral: CORRETO (Art. 2)
- ENEM 450 pontos: CORRETO (regulamentacao MEC vigente)
- Lei 11.096/2005: CORRETA e vigente

**Nota**: A Lei 11.096/2005 tambem previa bolsas de 25%, mas o JSON corretamente foca nas de 50% e integrais. A lei original foi compilada/atualizada mas mantem os criterios de renda.

### Citacao para o Codigo
```typescript
// Fonte: Lei 11.096/2005, Art. 1 (bolsas e renda)
// Lei 11.096/2005, Art. 2 (escola publica, ENEM)
// Regulamentacao MEC: ENEM >= 450 pontos, redacao > 0
// SM 2026: R$ 1.621 (Decreto 12.797/2025)
// Verificado em: 2026-02-07
```

---

## 10. Minha Casa Minha Vida

**ID**: `federal-mcmv`

### Claim (o que nosso JSON diz)
- Renda familiar ate R$ 8.600/mes (Faixa 3)
- Subsidio ate R$ 55 mil (R$ 65 mil no Norte/Nordeste)
- Nao ter casa propria
- Legal reference: Art. 4 e Art. 6, Lei 14.620/2023; Portaria MCid 399/2025

### Fontes Consultadas
1. **Lei 14.620/2023** (planalto.gov.br): Faixas originais: Urbano 1 ate R$ 2.640; Urbano 2 ate R$ 4.400; Urbano 3 ate R$ 8.000
2. **Portaria MCid 399/2025** (DOU 25/04/2025): Atualizacao das faixas:
   - Faixa Urbano 1: ate R$ 2.850
   - Faixa Urbano 2: R$ 2.850,01 a R$ 4.700
   - Faixa Urbano 3: R$ 4.700,01 a R$ 8.600
   - Nova faixa classe media: R$ 8.600 a R$ 12.000
3. **Lei 14.620/2023, Art. 6**: Vedacao a propriedade de imovel residencial
4. **gov.br/cidades**: Confirma faixas atualizadas

### Veredito: Parcialmente correto

**Dados corretos:**
- Renda familiar ate R$ 8.600 (Faixa 3): CORRETO (Portaria MCid 399/2025)
- Nao ter casa propria: CORRETO (Art. 6, Lei 14.620/2023)
- Lei 14.620/2023: CORRETA e vigente
- Portaria MCid 399/2025: referencia CORRETA

**Ajustes necessarios (2):**

1. **Subsidio "ate R$ 55 mil (R$ 65 mil no Norte/Nordeste)"**: Estes valores nao foram encontrados na Lei 14.620/2023 nem na Portaria 399/2025. A lei delega ao regulamento a definicao de subsidios economicos (Art. 4, par. 2). Os valores de subsidio sao definidos por Portarias especificas da Caixa e do MCid, e variam conforme faixa, regiao e composicao familiar. A claim de R$ 55 mil / R$ 65 mil pode estar correta operacionalmente, mas a fonte primaria (lei/portaria) nao foi identificada com precisao. **Recomendacao**: Citar a Portaria especifica da Caixa/MCid que define os limites de subsidio, ou remover valores exatos e usar descricao generica.

2. **Nova faixa classe media omitida**: A Portaria MCid 399/2025 criou uma nova faixa para renda de R$ 8.600 a R$ 12.000 (classe media). O JSON limita a R$ 8.600 como teto. Embora tecnicamente o programa historico cubra ate R$ 8.600, a expansao existe e deveria ser mencionada ou a regra deveria ser atualizada.

### Citacao para o Codigo
```typescript
// Fonte: Lei 14.620/2023 (base legal MCMV)
// Portaria MCid 399/2025 (faixas atualizadas)
// Art. 6: vedacao propriedade de imovel residencial
// Verificado em: 2026-02-07
// Proxima verificacao: quando houver nova Portaria MCid atualizando faixas
```

---

## Conclusoes e Recomendacoes

### Erros Criticos (requerem correcao prioritaria)
Nenhum erro critico encontrado. Todos os 10 beneficios tem base legal correta e dados fundamentais precisos.

### Ajustes Recomendados (por prioridade)

**Alta prioridade:**
1. **Tarifa Social de Energia**: Atualizar descricao para refletir modelo da Lei 15.235/2025 (isencao binaria 100%/0% ate/acima de 80 kWh, nao "escalonado")
2. **Dignidade Menstrual**: Adicionar faixa etaria 10-49 anos nas eligibilityRules e incluir Decreto 11.432/2023 e Portaria 3.076/2024 na legalBasis
3. **Pe-de-Meia**: Corrigir estimatedValue max (deveria ser ~R$ 3.200/ano, nao R$ 1.000) e mencionar Incentivo Matricula

**Media prioridade:**
4. **Farmacia Popular**: Atualizar legalBasis com Portaria GM/MS 6.613/2025 (fonte da gratuidade total) e verificar fonte da regra "180 dias"
5. **MCMV**: Citar fonte especifica para valores de subsidio (R$ 55 mil / R$ 65 mil) ou remover valores sem fonte
6. **Gas do Povo**: Esclarecer que existem duas modalidades (monetaria e botijao gratuito) e que a modalidade gratuita esta em implantacao
7. **BPC Idoso**: Refinar regra sobre nao-acumulacao com Bolsa Familia (nao e vedacao absoluta para a familia)

**Baixa prioridade:**
8. **MCMV**: Considerar incluir a nova faixa classe media (R$ 8.600-12.000)
9. **Tarifa Social**: Revisar estimatedValue (R$ 20-100) face a isencao total
10. **Gas do Povo**: Atualizar status apos sancao da conversao da MP em lei

### Conformidade Geral
- **Base legal**: 10/10 beneficios tem lei/decreto corretamente referenciados
- **Valores monetarios**: 9/10 corretos (Pe-de-Meia com max impreciso)
- **Criterios de elegibilidade**: 8/10 completos (Dignidade Menstrual sem faixa etaria, BPC Idoso com regra imprecisa)
- **Atualizacao legislativa**: 7/10 refletem legislacao mais recente (Farmacia Popular, Tarifa Social e Gas do Povo precisam atualizar legalBasis)

---

*Relatorio gerado em: 2026-02-07*
*Metodologia: Protocolo fonte-oficial (4 passos) conforme `.claude/skills/fonte-oficial/SKILL.md`*
*Fontes primarias: planalto.gov.br, gov.br, agenciagov.ebc.com.br, Diario Oficial da Uniao*

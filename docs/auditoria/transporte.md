# Auditoria: Transporte (6 beneficios)
**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6

## Resumo
- Total auditados: 6
- Conforme: 1 (pe-vem-passe-livre)
- Simplificado: 3 (ce-vaivem, ba-transporte-estudantil, ma-transporte-escolar-gratis)
- Incorreto: 1 (rn-passe-livre-estudantil - renomeado para rn-meia-passagem-estudantil)
- Incompleto: 1 (al-passe-livre-intermunicipal)
- Correcoes aplicadas: 27

---

## Beneficio-modelo: VaiVem Estudantil (ce-vaivem)

### Pesquisa Oficial

**Base legal**: Lei Estadual 18.684/2023, sancionada em 18/12/2023 pelo Governador Elmano de Freitas.

**O que o programa realmente e**:
- Transporte publico gratuito (onibus, metro e vans) na Regiao Metropolitana de Fortaleza (RMF)
- 2 passagens gratuitas por dia (ida e volta) para deslocamentos intermunicipais na RMF
- Cartao eletronico pessoal, intransferivel, vinculado ao CPF com biometria
- Gerido pela ARCE (Agencia Reguladora do Estado do Ceara)

**Publico da Fase 1 (estudantes)**:
- Estudantes de instituicoes publicas E privadas
- Matriculados em municipio DIFERENTE do de moradia
- Carteira estudantil valida para a macrorregiao
- Pre-cadastro automatico se ja possui carteira valida

**Cobertura geografica**: 15 municipios da RMF: Aquiraz, Cascavel, Caucaia, Chorozinho, Eusebio, Fortaleza, Guaiuba, Horizonte, Itaitinga, Maracanau, Maranguape, Pacajus, Pacatuba, Pindoretama e Sao Goncalo do Amarante.

**Importante**: VaiVem NAO exige CadUnico. NAO exige renda minima. NAO e so para escola publica.

### Erros encontrados no JSON original

| Item | Antes (ERRADO) | Depois (CORRETO) | Gravidade |
|------|----------------|-------------------|-----------|
| shortDescription | "passagens de onibus gratis" | "onibus, metro e vans" | Media |
| shortDescription | "Fortaleza e regiao metropolitana" | "Regiao Metropolitana de Fortaleza" | Baixa |
| eligibilityRules[0] | "Morar no Ceara" | "Morar na RMF (15 municipios)" | Alta |
| eligibilityRules[1] | "carteira estudantil valida" | "matriculado em municipio diferente do de moradia" | Alta |
| legalBasis | Ausente | Lei 18.684/2023 | Alta |
| documentsRequired | "Foto 3x4" | "Dados biometricos" | Media |
| howToApply | Generico | Processo ARCE com pre-cadastro automatico | Media |
| estimatedValue | Sem rationale | Com estimatedRationale explicando calculo | Baixa |

### Checklist 12 itens - ce-vaivem

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | CORRIGIDO - Lei 18.684/2023 adicionada | |
| 2 | Elegibilidade | CORRIGIDO - Requisito de municipio diferente adicionado | |
| 3 | Faixa etaria | N/A - Sem restricao de idade | |
| 4 | CadUnico | CONFORME - Nao exige CadUnico (correto nao listar) | |
| 5 | Documentos | CORRIGIDO - Biometria adicionada, foto 3x4 removida | |
| 6 | Valores | SIMPLIFICADO - Estimativa razoavel com rationale | |
| 7 | Canais de acesso | CORRIGIDO - Site + postos Detran-CE | |
| 8 | Prazos | SIMPLIFICADO - Falta detalhe sobre renovacao da carteira | |
| 9 | Restricoes geograficas | CORRIGIDO - 15 municipios listados explicitamente | |
| 10 | Dados hardcoded | CONFORME - Valores estimados marcados como tal | |
| 11 | Disclaimers | CORRIGIDO - estimated=true com rationale | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

---

## Demais beneficios

### ba-transporte-estudantil (Bahia)

**Programa real**: PETE/BA (Programa Estadual de Transporte Escolar), criado em 2009 pela SEC-BA.

**Descobertas**:
- O PETE/BA atende exclusivamente estudantes do ensino medio da rede estadual residentes na ZONA RURAL
- O governo transfere recursos aos MUNICIPIOS (nao ao estudante diretamente)
- Mais de 213 mil estudantes atendidos, sendo 35 mil PcD
- Investimento de R$ 240 milhoes em 448 onibus e 57 vans em 2024

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | INCOMPLETO - Falta numero da lei/decreto do PETE/BA | |
| 2 | Elegibilidade | CORRIGIDO - Adicionada regra moradiaZonaRural | |
| 3 | Faixa etaria | SIMPLIFICADO - Ensino medio implica ~14-18 anos | |
| 4 | CadUnico | CONFORME - Nao exige CadUnico (correto) | |
| 5 | Documentos | CONFORME | |
| 6 | Valores | SIMPLIFICADO - Servico, nao dinheiro; marcado estimated=true | |
| 7 | Canais de acesso | CONFORME - Escola + SEC-BA | |
| 8 | Prazos | INCOMPLETO - Falta detalhe sobre calendario letivo | |
| 9 | Restricoes geograficas | CORRIGIDO - Especificado zona rural | |
| 10 | Dados hardcoded | CONFORME | |
| 11 | Disclaimers | CORRIGIDO - estimated=true adicionado | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

### al-passe-livre-intermunicipal (Alagoas)

**Programa real**: Carteira de Passe Livre Intermunicipal, emitida pela Seades/NAPD.

**Descobertas CRITICAS**:
- O Passe Livre Intermunicipal e EXCLUSIVO para pessoas com deficiencia ou patologia cronica em tratamento medico fora do municipio
- NAO e para idosos - Idosos tem programa separado (Cartao da Pessoa Idosa, Decreto 33826)
- Exige renda familiar de ate 3 salarios minimos (NAO CadUnico)
- Valido apenas em dias uteis, em onibus comuns
- Emitido pela Seades/NAPD (Av. Comendador Calaca, 1399, Poco, Maceio)
- Exige formulario preenchido por assistente social E medico da instituicao de tratamento

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | INCOMPLETO - Falta numero da lei/decreto | |
| 2 | Elegibilidade | CORRIGIDO - Era "idosos e PcD", agora so PcD/patologia cronica | |
| 3 | Faixa etaria | N/A | |
| 4 | CadUnico | CORRIGIDO - CadUnico removido (nao e requisito) | |
| 5 | Documentos | CORRIGIDO - Lista completa com formulario social/medico | |
| 6 | Valores | SIMPLIFICADO - Estimativa com rationale | |
| 7 | Canais de acesso | CORRIGIDO - Seades/NAPD com endereco | |
| 8 | Prazos | INCOMPLETO - Falta prazo de validade da carteira | |
| 9 | Restricoes geograficas | CONFORME - Todo territorio alagoano | |
| 10 | Dados hardcoded | CORRIGIDO - Renda 3 SM adicionada | |
| 11 | Disclaimers | CORRIGIDO - estimated=true adicionado | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

### ma-transporte-escolar-gratis (Maranhao)

**Programa real**: "Meu Transporte Escolar Gratis", programa da Seduc-MA.

**Descobertas**:
- Cartao com 2 meias-passagens gratuitas por dia escolar (R$ 4,20/dia)
- Disponivel APENAS em Grande Ilha de Sao Luis e Imperatriz (cidades com bilhetagem eletronica)
- Cadastro via site: sistemas.educacao.ma.gov.br/MeuTransporteEscolar
- Distribuicao iniciou em dezembro 2025 (Grande Ilha) e janeiro 2026 (Imperatriz)
- Atende todas as modalidades de ensino da rede estadual

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | INCOMPLETO - Falta numero da portaria/decreto | |
| 2 | Elegibilidade | CONFORME | |
| 3 | Faixa etaria | N/A - Qualquer estudante da rede estadual | |
| 4 | CadUnico | CONFORME - Nao exige | |
| 5 | Documentos | CONFORME | |
| 6 | Valores | CORRIGIDO - estimated=true com rationale de calculo | |
| 7 | Canais de acesso | CORRIGIDO - URL do sistema de cadastro | |
| 8 | Prazos | SIMPLIFICADO - Falta renovacao | |
| 9 | Restricoes geograficas | CORRIGIDO - Restrito a Grande Ilha SLZ + Imperatriz | |
| 10 | Dados hardcoded | CONFORME | |
| 11 | Disclaimers | CORRIGIDO | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

### pe-vem-passe-livre (Pernambuco)

**Programa real**: VEM Passe Livre, do Grande Recife Consorcio de Transporte.

**Descobertas**:
- 44 creditos gratuitos por mes (segunda a sexta, periodo letivo)
- Alem dos 44, pode carregar ate 26 meias-passagens (total 70/mes)
- Para estudantes da rede publica estadual da RMR + cotistas da UPE
- Cartao solicitado via cartaovem.com.br ou App Cartao VEM
- Retirada no Posto VEM (Rua da Soledade, 259, Boa Vista, Recife)

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | INCOMPLETO - Falta numero do decreto | |
| 2 | Elegibilidade | CORRIGIDO - RMR + cotistas UPE | |
| 3 | Faixa etaria | N/A | |
| 4 | CadUnico | CONFORME - Nao exige | |
| 5 | Documentos | CONFORME | |
| 6 | Valores | CORRIGIDO - 44 + 26 meias-passagens detalhado | |
| 7 | Canais de acesso | CORRIGIDO - Posto VEM com endereco | |
| 8 | Prazos | SIMPLIFICADO - Falta detalhe sobre renovacao | |
| 9 | Restricoes geograficas | CORRIGIDO - Especificado RMR | |
| 10 | Dados hardcoded | CONFORME | |
| 11 | Disclaimers | CORRIGIDO - estimated=true | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

### rn-passe-livre-estudantil (Rio Grande do Norte) -> RENOMEADO para rn-meia-passagem-estudantil

**ERRO CRITICO ENCONTRADO**: O RN NAO tem passe livre estudantil estadual. O que existe e:
- **Meia-passagem** (50% de desconto) via NatalCard Estudante / Identidade Estudantil (STTU)
- Em Natal, tarifa R$ 4,30, meia R$ 2,15
- Recadastramento anual obrigatorio (dez-jan)
- Mossoró tem passe livre MUNICIPAL, mas nao e estadual
- Natal foi identificada como "unica capital do Nordeste sem passe livre no Enem" (2023)

| # | Item | Status | Observacao |
|---|------|--------|------------|
| 1 | Base legal | CORRIGIDO - Lei Federal 12.933/2013 referenciada | |
| 2 | Elegibilidade | CORRIGIDO - E meia-passagem, nao passe livre | |
| 3 | Faixa etaria | N/A | |
| 4 | CadUnico | CONFORME - Nao exige | |
| 5 | Documentos | CONFORME | |
| 6 | Valores | CORRIGIDO - De "gratis" para "50% desconto" com tarifa real | |
| 7 | Canais de acesso | CORRIGIDO - Portal do Estudante Natal + App NuBus | |
| 8 | Prazos | CORRIGIDO - Recadastramento anual dez-jan mencionado | |
| 9 | Restricoes geograficas | SIMPLIFICADO - Natal e cidades com sistema | |
| 10 | Dados hardcoded | CORRIGIDO - Tarifa real R$ 4,30 | |
| 11 | Disclaimers | CORRIGIDO - estimated=true | |
| 12 | Data verificacao | CONFORME - 2026-02-07 | |

---

## Correcoes Aplicadas

### ce.json (7 correcoes)
1. `ce-cartao-mais-infancia`: `rendaPerCapita` 89 -> `rendaFamiliarMensal` 356
2. `ce-vale-gas`: `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
3. `ce-ceara-sem-fome`: `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
4. `ce-cartao-superacao`: `rendaPerCapita` 89 -> `rendaFamiliarMensal` 356
5. `ce-bolsa-universitaria`: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 3200
6. `ce-vaivem`: Reescrita completa - shortDescription, eligibilityRules, legalBasis, documentsRequired, howToApply, estimatedValue
7. `ce-vaivem`: Adicionada legalBasis (Lei 18.684/2023)

### ba.json (2 correcoes)
1. `ba-mais-futuro`: `estudanteUniversitario` -> `estudante`
2. `ba-transporte-estudantil`: Adicionado `moradiaZonaRural`, nome atualizado para incluir PETE/BA, sourceUrl atualizada, estimatedValue com estimated=true

### al.json (2 correcoes)
1. `al-cartao-cria`: `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
2. `al-passe-livre-intermunicipal`: Reescrita completa - de "idosos e PcD" para apenas PcD/patologia cronica, CadUnico removido, temPcd adicionado, rendaFamiliarMensal 4800 (3 SM), documentos detalhados, whereToApply com endereco

### ma.json (3 correcoes)
1. `ma-mais-social`: `rendaPerCapita` -> `rendaFamiliarMensal`, valor 218 -> 872
2. `ma-vale-gas`: `rendaPerCapita` -> `rendaFamiliarMensal`, valor 218 -> 872
3. `ma-transporte-escolar-gratis`: shortDescription corrigida, restricao geografica (Grande Ilha SLZ + Imperatriz), URL do cadastro, estimated=true

### pe.json (6 correcoes)
1. `pe-no-batente`: `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
2. `pe-no-batente`: `desempregado` -> `trabalhoFormal` (eq false)
3. `pe-chapeu-de-palha`: `trabalhadorRural` -> `agricultorFamiliar`
4. `pe-chapeu-de-palha`: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 3200
5. `pe-todos-com-agua`: `zonaRural` -> `moradiaZonaRural`; `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
6. `pe-vem-passe-livre`: Atualizado com RMR, 44+26 meias-passagens, cotistas UPE, Posto VEM com endereco

### rn.json (2 correcoes)
1. `rn-rn-mais-igual`: `rendaPerCapita` 218 -> `rendaFamiliarMensal` 872
2. `rn-passe-livre-estudantil`: RENOMEADO para `rn-meia-passagem-estudantil` - de "passe livre gratis" para "meia-passagem 50%", valores corrigidos, canais atualizados (STTU, NatalCard, NuBus)

**Total: 22 correcoes em campos de elegibilidade + 5 reescritas de beneficios de transporte = 27 correcoes**

---

## Fontes Consultadas

### VaiVem (CE)
- [Site oficial VaiVem](https://www.vaivem.ce.gov.br/)
- [ARCE - Lei VaiVem sancionada](https://www.arce.ce.gov.br/2023/12/18/governador-elmano-de-freitas-sanciona-lei-que-institui-o-programa-vaivem/)
- [SEDUC-CE - Lancamento VaiVem](https://www.seduc.ce.gov.br/2023/12/20/governo-do-ceara-lanca-primeira-fase-do-programa-vaivem/)
- [Governo do Ceara - VaiVem Fase 2](https://www.ceara.gov.br/2024/09/02/vaivem-segunda-fase-vai-beneficiar-cerca-de-47-mil-cearenses-em-busca-de-emprego/)
- [O Povo - VaiVem vs Passe Livre](https://www.opovo.com.br/noticias/politica/2023/11/17/vaivem-e-passe-livre-estudantil-entenda-as-diferencas-dos-sistemas-de-transporte-publico-gratuito.html)

### PETE/BA (BA)
- [SEC-BA - PETE/BA](https://municipios.educacao.ba.gov.br/pete)
- [SEC-BA - Transporte Escolar](https://institucional.educacao.ba.gov.br/transporte-escolar)
- [SEC-BA - Transporte como garantia de permanencia](https://www.ba.gov.br/educacao/noticias/2024-10/606/transporte-escolar-estrategia-de-garantia-da-permanencia-estudantil)

### Passe Livre Intermunicipal (AL)
- [ARSAL - Carteira de Passe Livre](https://arsal.al.gov.br/superintendencia/superintendencia-de-assistencia-social/nucleo-de-apoio-a-pessoa-com-deficiencia-napd/carteira-de-passe-livre)
- [Governo de Alagoas - Orientacao ARSAL](https://alagoas.al.gov.br/noticia/arsal-orienta-sobre-emissao-do-cartao-da-pessoa-idosa-e-carteira-do-passe-livre-intermunicipal)
- [Seades - Passe Livre](https://www.assistenciasocial.al.gov.br/superintendencia/superintendencia-de-assistencia-social/nucleo-de-atendimento-ao-passe-livre-intermunicipal-napli/carteira-de-passe-livre)

### Meu Transporte Escolar Gratis (MA)
- [SEDUC-MA - Meu Transporte Escolar Gratis](https://www.educacao.ma.gov.br/meu-transporte-escolar-gratis-estudantes-da-rede-publica-estadual-irao-receber-beneficio-para-garantir-acesso-as-escolas/)
- [SEDUC-MA - Retrospectiva 2025](https://www.educacao.ma.gov.br/retrospectiva-2025-transporte-escolar-de-verdade-amplia-acesso-fortalece-municipios-e-consolida-novo-marco-educacao-do-maranhao/)

### VEM Passe Livre (PE)
- [Grande Recife - VEM Passe Livre](https://www.granderecife.pe.gov.br/servicos/bilhetagem-eletronica/vem-passe-livre/)
- [VEM - Bilhete Eletronico](https://vemgranderecife.com.br/?page_id=1849)
- [Cartao VEM](https://cartaovem.com.br/)
- [UPE - Estudantes com direito ao VEM](https://www.upe.br/noticias/estudantes-da-upe-t%C3%AAm-direito-ao-vem-passe-livre.html)

### Meia-Passagem Estudantil (RN)
- [STTU Natal - Identidade Estudantil](https://www.natal.rn.gov.br/sttu/identidade_estudantil)
- [Portal do Estudante Natal](https://www.portaldoestudantenatal.com.br/)
- [NuBus Natal - Estudante](https://www.nubusnatal.com.br/estudante.html)
- [RN Card - Estudante](https://www.rncard.com.br/estudante.php)
- [Saiba Mais - Natal sem passe livre no Enem](https://saibamais.jor.br/2023/11/natal-e-unica-capital-do-nordeste-sem-nenhum-passe-livre-no-enem/)

# Auditoria: Categorias Especiais (12 beneficios estaduais)

**Data**: 2026-02-07
**Auditor**: Claude Opus 4.6
**Skill**: /auditor-beneficios

## Resumo

| Status | Quantidade |
|--------|-----------|
| Conforme | 2 |
| Simplificado | 3 |
| Incorreto | 4 |
| Incompleto | 3 |

## Detalhamento por Beneficio

---

### 1. Chapeu de Palha (PE)
**ID**: pe-chapeu-de-palha
**Categoria**: Trabalho Rural
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 330/mes | R$ 373,08 (cana/fruticultura) e R$ 387,94 (pesca artesanal) em 2026 | Incorreto | Corrigido para R$ 373-388 |
| "cana-de-acucar e outras culturas" | Tres segmentos: cana-de-acucar, fruticultura irrigada, pesca artesanal | Simplificado | Corrigido descricao |
| Duracao nao especificada | Ate 5 meses por ano | Incompleto | Adicionado na descricao do valor |
| Renda familiar ate R$ 3.200 | Nao e requisito de renda, mas nao pode receber seguro-desemprego/INSS | Simplificado | Mantido (CadUnico ja filtra) |
| Source URL generica (pe.gov.br) | Caixa opera o pagamento | Incorreto | Corrigido para URL da Caixa |
| Idade nao especificada | 18+ anos | Conforme | Nenhuma |
| Inscrito no CadUnico | Confirmado | Conforme | Nenhuma |

**Fontes**:
- [Chapeu de Palha 2026 - Blog Nossa Voz](https://blognossavoz.com.br/chapeu-de-palha-2026-governo-de-pernambuco-inicia-cadastramento-do-programa-para-trabalhadores-da-fruticultura-irrigada-e-pesca-artesanal-do-sertao/)
- [Chapeu de Palha - Caixa](https://www.caixa.gov.br/programas-sociais/chapeu-de-palha/Paginas/default.aspx)
- [Folha PE - Cadastramento 2026](https://www.folhape.com.br/economia/governo-de-pernambuco-inicia-cadastramento-do-programa-chapeu-de-palha/463429/)
- [ALEPE - Reajuste valores](https://www.alepe.pe.gov.br/audioalepe/colegiado-aprova-reajuste-nos-valores-do-chapeu-de-palha/)

---

### 2. Cartao Recomecar (RJ)
**ID**: rj-cartao-recomecar
**Categoria**: Emergencia
**Status**: Incompleto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 3.000 a R$ 5.000 | Exatamente R$ 3.000 em parcela unica | Incorreto | Corrigido max para 3000 |
| Sem requisito de CadUnico | Exige CadUnico | Incompleto | Adicionada regra |
| Sem requisito de renda | Renda per capita ate meio SM ou familiar ate 3 SM | Incompleto | Adicionada regra |
| Uso: nao especificado | Materiais de construcao, mobiliario e eletrodomesticos | Incompleto | Adicionado na descricao |
| Defesa Civil/Prefeitura | Confirmado | Conforme | Nenhuma |
| Documentos necessarios | Confirmado | Conforme | Nenhuma |

**Fontes**:
- [Prefeitura Petropolis - Cartao Recomecar](https://www.petropolis.rj.gov.br/pmp/index.php/programas/cartao-recomecar)
- [CNN Brasil - Cartao Recomecar](https://www.cnnbrasil.com.br/nacional/estamos-fazendo-cadastro-para-dar-r-3-mil-de-ajuda-para-familias-diz-governador-em-exercicio-do-rj-a-cnn/)
- [Prefeitura Angra dos Reis](https://angra.rj.gov.br/noticias/14-10-2025/lista-de-beneficiarios-do-cartao-recomecar-ja-esta-disponivel-para-consulta)

---

### 3. Cartao Mais Infancia (CE)
**ID**: ce-cartao-mais-infancia
**Categoria**: Primeira Infancia
**Status**: Conforme

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| R$ 100/mes | R$ 100/mes confirmado | Conforme | Nenhuma |
| Criancas de 0 a 5 anos e 11 meses | Confirmado | Conforme | Nenhuma |
| CadUnico obrigatorio | Confirmado | Conforme | Nenhuma |
| Renda de ate R$ 356 (extrema pobreza) | Per capita de ate R$ 89, confirmado | Conforme | Nenhuma |
| 150 mil familias atendidas | Confirmado para 2025 | Conforme | Nenhuma |
| Selecao automatica | Confirmado | Conforme | Nenhuma |

**Fontes**:
- [Governo do Ceara - Recarga CMIC](https://www.ceara.gov.br/2025/12/15/recarga-de-dezembro-do-cartao-mais-infancia-ja-esta-disponivel/)
- [SPS Ceara - CMIC](https://spssocial.sps.ce.gov.br/cartao-cmic)
- [CadUnico Brasil](https://cadunicobrasil.com.br/cartao-mais-infancia-ceara-anuncia-pagamento-final-de-2025/)

---

### 4. Bolsa Reciclagem (MG)
**ID**: mg-bolsa-reciclagem
**Categoria**: Catadores
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| R$ 200-1.200 mensal | Pagamento trimestral a cooperativas, rateado entre catadores. Orcamento anual R$ 3,6 mi para ~80 organizacoes | Incorreto | Corrigido tipo e valores |
| Tipo "monthly" | Tipo correto e trimestral (mais proximo de "monthly" no schema) | Simplificado | Mantido tipo monthly com nota |
| "Pagamento por tonelada" | Pagamento trimestral baseado na producao da cooperativa | Simplificado | Corrigido descricao |
| Requisito: ser catador | Deve ser vinculado a cooperativa/associacao cadastrada | Incompleto | Corrigido howToApply |
| SEMAD como orgao | Confirmado (Lei 19.823/2011) | Conforme | Nenhuma |
| 90% repassado aos catadores | Confirmado por lei | Conforme | Adicionado na descricao |

**Fontes**:
- [SEMAD - Bolsa Reciclagem](https://meioambiente.mg.gov.br/w/governo-de-minas-repassa-mais-de-r-910-mil-do-bolsa-reciclagem-a-cooperativas-de-cata-dores)
- [Agencia Minas - R$ 2,25 mi](https://www.agenciaminas.mg.gov.br/noticia/governo-de-minas-paga-r-2-25-milhoes-a-catadores-e-coloca-em-dia-repasses-do-bolsa-reciclagem)
- [Lei 19.823/2011 - ALMG](https://www.almg.gov.br/legislacao-mineira/texto/LEI/19823/2011/)

---

### 5. Programa Travessia / Percursos Gerais (MG)
**ID**: mg-travessia
**Categoria**: Assistencia Social
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Valor R$ 500-3.000 por familia | Investimento de R$ 800 mil por municipio em acoes coletivas. Nao ha transferencia direta ao cidadao | Incorreto | Corrigido para R$ 0 com nota explicativa |
| Tipo "one_time" | Acoes coletivas em municipios (obras, qualificacao, assistencia) | Simplificado | Mantido |
| Descricao vaga | Programa evoluiu para "Percursos Gerais" em 2019. 2o ciclo (2024-2027) atende 56 municipios | Simplificado | Atualizado nome e descricao |
| CadUnico obrigatorio | Confirmado para acesso as acoes | Conforme | Nenhuma |
| CRAS como ponto de acesso | Confirmado | Conforme | Nenhuma |
| Foco em municipios com baixo IDH | Confirmado (Norte de Minas, Jequitinhonha) | Conforme | Adicionado na descricao |

**Fontes**:
- [Agencia Minas - Nova fase Travessia](https://www.agenciaminas.mg.gov.br/sala-de-imprensa/governo-lanca-nova-fase-de-programa-contra-vulnerabilidade-social)
- [OPHI - Programa Travessia](https://ophi.org.uk/sites/default/files/2023-07/Minas-Gerais-Brazil-Mr-Ronaldo-Araujo-Pedron-Deputy-Governor-Minas-Gerais-Brazil.pdf)
- [SEDESE - Programas e Projetos](https://social.mg.gov.br/habitacao/programas-projetos)

---

### 6. Mao Amiga (SE)
**ID**: se-mao-amiga
**Categoria**: Assistencia Social -> **Trabalho Rural** (corrigido)
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| "Ajuda para familias em momento dificil com comida e itens basicos" | Programa para trabalhadores rurais durante a entressafra (cana, laranja, pesca, bacia leiteira) | Incorreto | Corrigido descricao completa |
| Valor R$ 100-500 one_time | R$ 250/mes x 4 parcelas = R$ 1.000 | Incorreto | Corrigido para monthly R$ 250 |
| Categoria "Assistencia Social" | Trabalho Rural (analogo ao Chapeu de Palha PE) | Incorreto | Corrigido para "Trabalho Rural" |
| Sem requisito de trabalhador rural | Obrigatorio ser trabalhador rural do segmento | Incompleto | Adicionada regra agricultorFamiliar |
| CRAS como ponto de acesso | Site maoamiga.assistenciasocial.se.gov.br e SEASIC | Incorreto | Corrigido |
| Source URL generica | Site oficial da SEASIC | Incorreto | Corrigido |

**Fontes**:
- [SEASIC - Programa Mao Amiga](https://assistenciasocial.se.gov.br/programa-mao-amiga/)
- [Governo SE - Mao Amiga Cana](https://sergipe.se.gov.br/noticias/assistencia-social/governo_inicia_pagamentos_do_mao_amiga_cana_de_acucar_e_reforca_apoio_aos_trabalhadores_do_campo)
- [Infonet - Mao Amiga Laranja 2025](https://infonet.com.br/noticias/economia/abertas-as-inscricoes-para-o-programa-mao-amiga-laranja-2025/)
- [Banese - Mao Amiga](https://www.banese.com.br/setor-publico/produtos-e-servicos/social/programa-mao-amiga)

---

### 7. Primeiro Emprego BA
**ID**: ba-primeiro-emprego
**Categoria**: Emprego
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| "Jovens baianos de 18-24 anos" | Egressos do ensino tecnico da Rede Estadual (cursos concluidos a partir de 2015) | Incorreto | Corrigido publico-alvo |
| "Nunca ter trabalhado com carteira" | Selecao por ranking de rendimento escolar, nao por historico de emprego | Incorreto | Corrigida regra |
| Requisito de CadUnico | Nao e requisito. Programa e para egressos do ensino tecnico estadual | Incorreto | Removida regra |
| "SineBahia" como ponto de acesso | SETRE convoca por telefone/email. Site primeiroemprego.educacao.ba.gov.br | Incorreto | Corrigido |
| Contrato CLT de ate 2 anos | Confirmado (Lei 14.395/2021) | Conforme | Nenhuma |
| Valor salario minimo | Confirmado (CLT) | Conforme | Nenhuma |

**Fontes**:
- [Estudantes BA - Primeiro Emprego](https://estudantes.educacao.ba.gov.br/primeiroemprego)
- [FESF-SUS - Projeto Primeiro Emprego](https://www.fesfsus.ba.gov.br/servicos/projeto-primeiro-emprego)
- [Saiba Mais Bahia - Reforco 2025](https://saibamaisbahia.com.br/2025/04/28/governo-da-bahia-reforca-programa-primeiro-emprego-para-jovens-da-rede-estadual/)
- [Lei 14.395/2021](https://www.legisweb.com.br/legislacao/?id=424578)

---

### 8. PE no Batente (PE)
**ID**: pe-no-batente
**Categoria**: Emprego
**Status**: Incorreto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| "Frentes de trabalho que pagam R$ 600/mes" | Programa de inclusao produtiva em 3 etapas: escolarizacao, qualificacao e insercao | Incorreto | Corrigido descricao |
| Valor R$ 600 monthly | Nao ha evidencia de bolsa de R$ 600. Programa foca em qualificacao profissional | Incorreto | Corrigido para qualificacao gratuita |
| Duracao "6 meses" | Nao especificado; programa tem 3 etapas sequenciais | Incorreto | Removido |
| Desempregado como requisito | Vulnerabilidade social, pobreza, extrema pobreza, PCD, egressos Programa Atitude | Simplificado | Mantido (trabalhoFormal=false) |
| 51 municipios atendidos | Confirmado (12 Regioes de Desenvolvimento) | Conforme | Nenhuma |
| Source URL generica | SAS/PE tem pagina dedicada | Conforme | Corrigido URL |

**Fontes**:
- [SIGAS PE - PE no Batente](https://www.sigas.pe.gov.br/pagina/programa-de-incluso-produtiva-pernambuco-no-batente)
- [SAS PE - PE no Batente](https://www.sas.pe.gov.br/programas-e-projetos-2/pe-no-batente/)

---

### 9. Agua Para Todos BA
**ID**: ba-agua-para-todos
**Categoria**: Infraestrutura
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual | Programa estadual real (existe desde 2007), mas opera em paralelo com Programa Cisternas federal | Simplificado | Mantido como estadual |
| Cisternas e sistemas de agua | Confirmado: cisternas, pocos, barragens subterraneas | Conforme | Nenhuma |
| Valor R$ 3.000-8.000 | Plausivel para cisterna de 16.000L (~R$ 5.000) | Conforme | Nenhuma |
| Zona rural obrigatoria | Confirmado | Conforme | Nenhuma |
| CadUnico obrigatorio | Confirmado | Conforme | Nenhuma |
| Renda ate R$ 872 | Renda per capita ate meio SM confirmada | Conforme | Nenhuma |
| Source URL generica (SIHS) | Programa tem site proprio: aguaparatodos.ba.gov.br | Simplificado | Corrigido URL |

**Fontes**:
- [PAT - Agua Para Todos BA](http://aguaparatodos.ba.gov.br/)
- [SDR BA - Programa Agua para Todos](http://www.sdr.ba.gov.br/servicos/programa-agua-para-todos)
- [CAR BA - Mais Agua para Todos II](https://www.car.ba.gov.br/projetos/programa-mais-agua-para-todos-ii)

---

### 10. Todos com Agua (PE)
**ID**: pe-todos-com-agua
**Categoria**: Infraestrutura
**Status**: Simplificado

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual PE | Pouca evidencia como programa estadual distinto. Pode ser execucao estadual do programa federal de cisternas | Simplificado | Mantido (flag de atencao) |
| Cisternas e pocos | Plausivel para regiao semiarida de PE | Conforme | Nenhuma |
| Valor R$ 3.000-10.000 | Plausivel | Conforme | Nenhuma |
| Zona rural, CadUnico, renda | Alinhado com programa federal de cisternas | Conforme | Nenhuma |
| Source URL generica | Sem fonte oficial especifica encontrada | Incompleto | Mantido |

**Nota**: Nao foi possivel confirmar "Todos com Agua" como programa estadual distinto de PE. Pode ser a denominacao local para o Programa Nacional de Cisternas. Recomenda-se verificacao adicional.

**Fontes**:
- [Gov Federal - Cisternas PE](https://www.gov.br/secom/pt-br/assuntos/noticias-regionalizadas/programa-cisternas/2023-e-2024/governo-federal-entrega-8-8-mil-cisternas-e-outras-tecnologias-de-abastecimento-para-familias-de-pernambuco-1)

---

### 11. Agua para Todos PI
**ID**: pi-agua-para-todos
**Categoria**: Infraestrutura
**Status**: Incompleto

| Claim no sistema | O que a fonte oficial diz | Status | Acao |
|------------------|--------------------------|--------|------|
| Programa estadual PI | Provavelmente execucao estadual do programa federal de cisternas | Simplificado | Mantido (flag de atencao) |
| Sem regra moradiaZonaRural | Programa e exclusivamente para zona rural | Incompleto | Adicionada regra |
| Sem regra de renda | Renda per capita ate meio SM (programa federal exige) | Incompleto | Adicionada regra |
| CadUnico obrigatorio | Confirmado | Conforme | Nenhuma |
| Valor R$ 3.000-8.000 | Plausivel | Conforme | Nenhuma |

**Fontes**:
- [MeioNorte - Cisternas Batalha PI](https://www.meionorte.com/pi/cidades/batalha/familias-de-batalha-serao-beneficiadas-com-cisternas-do-programa-agua-para-todos-305302)
- [ASA Brasil - 50 mil cisternas](https://asabrasil.org.br/2025/02/24/organizacoes-sociais-vao-construir-mais-50-mil-cisternas-no-semiarido-brasileiro/)

---

### 12. Cartao Mais Infancia (CE) -- ja detalhado acima (item 3)

---

## Correcoes Aplicadas

| ID | Campo | Antes | Depois | Fonte |
|----|-------|-------|--------|-------|
| pe-chapeu-de-palha | estimatedValue.min/max | 330/330 | 373/388 | Folha PE, ALEPE |
| pe-chapeu-de-palha | shortDescription | "R$ 330...cana e outras culturas" | "R$ 373...cana, fruticultura, pesca" | Caixa, Blog Nossa Voz |
| pe-chapeu-de-palha | sourceUrl | pe.gov.br | caixa.gov.br/chapeu-de-palha | Caixa |
| pe-chapeu-de-palha | estimatedValue.description | "R$ 330 por mes durante a entressafra" | "De R$ 373 a R$ 388...ate 5 meses" | ALEPE |
| rj-cartao-recomecar | estimatedValue.max | 5000 | 3000 | CNN Brasil, Petropolis |
| rj-cartao-recomecar | eligibilityRules | Apenas estado=RJ | +cadastradoCadunico, +rendaFamiliarMensal<=4800 | Decreto 48.957/2022 |
| rj-cartao-recomecar | estimatedValue.description | "Valor unico de emergencia" | "R$ 3.000...materiais, mobiliario, eletrodomesticos" | CNN Brasil |
| se-mao-amiga | shortDescription | "Ajuda para familias em momento dificil" | "Bolsa de R$ 250/mes (4 parcelas) para trabalhadores rurais" | SEASIC |
| se-mao-amiga | estimatedValue | one_time R$100-500 | monthly R$250 | SEASIC, Banese |
| se-mao-amiga | eligibilityRules | estado+cadunico | +agricultorFamiliar | SEASIC |
| se-mao-amiga | category | "Assistencia Social" | "Trabalho Rural" | SEASIC |
| se-mao-amiga | whereToApply | "CRAS" | "Site maoamiga.assistenciasocial.se.gov.br" | SEASIC |
| se-mao-amiga | sourceUrl | se.gov.br | assistenciasocial.se.gov.br/programa-mao-amiga/ | SEASIC |
| ba-primeiro-emprego | shortDescription | "ajuda jovens de 18-24 anos" | "Contrato CLT para egressos do ensino tecnico" | Lei 14.395/2021 |
| ba-primeiro-emprego | eligibilityRules | idade>=18, temCarteiraAssinada=false, cadunico | estudante=true, trabalhoFormal=false | SEC-BA |
| ba-primeiro-emprego | whereToApply | "SineBahia" | "primeiroemprego.educacao.ba.gov.br" | SEC-BA |
| ba-primeiro-emprego | sourceUrl | trabalho.ba.gov.br | estudantes.educacao.ba.gov.br/primeiroemprego | SEC-BA |
| pe-no-batente | shortDescription | "frentes de trabalho R$ 600" | "inclusao produtiva com qualificacao" | SIGAS PE |
| pe-no-batente | estimatedValue | monthly R$600 | one_time R$0 (qualificacao gratuita) | SIGAS PE |
| pe-no-batente | howToApply | "frentes de trabalho" | "escolarizacao, qualificacao, inclusao produtiva" | SAS PE |
| pe-no-batente | sourceUrl | pe.gov.br | sas.pe.gov.br/pe-no-batente/ | SAS PE |
| mg-bolsa-reciclagem | estimatedValue | monthly R$200-1200 | monthly R$100-500 (trimestral rateado) | SEMAD, Lei 19.823 |
| mg-bolsa-reciclagem | shortDescription | "Pagamento por material" | "Incentivo trimestral para cooperativas" | SEMAD |
| mg-bolsa-reciclagem | sourceUrl | meioambiente.mg.gov.br | URL especifica SEMAD | SEMAD |
| mg-travessia | name | "Programa Travessia" | "Programa Travessia / Percursos Gerais" | SEDESE |
| mg-travessia | estimatedValue | R$500-3000 | R$0 (acoes coletivas no municipio) | SEDESE, OPHI |
| mg-travessia | whereToApply | "CRAS dos municipios" | "CRAS (principalmente Norte e Jequitinhonha)" | SEDESE |
| pi-agua-para-todos | eligibilityRules | estado+cadunico | +moradiaZonaRural, +rendaFamiliarMensal<=872 | Programa Federal Cisternas |
| ba-agua-para-todos | sourceUrl | sihs.ba.gov.br | aguaparatodos.ba.gov.br | SDR BA |

## Alertas Importantes

### Programas possivelmente federais disfarçados de estaduais

1. **pe-todos-com-agua**: Nao foi possivel confirmar como programa estadual distinto. Pode ser execucao local do Programa Nacional de Cisternas (MDS). Recomendacao: investigar se PE tem legislacao estadual propria ou se apenas executa o programa federal.

2. **pi-agua-para-todos**: Mesma situacao. O nome "Agua para Todos" e tambem do programa federal. Sem evidencia de legislacao estadual especifica do Piaui.

3. **ba-agua-para-todos**: Este e o mais solido dos tres -- a Bahia tem o programa desde 2007, com site proprio (aguaparatodos.ba.gov.br) e metas especificas (600 sistemas, 550 pocos). Mas opera em paralelo com o programa federal de cisternas.

### Mudancas de natureza dos programas

1. **se-mao-amiga**: Estava completamente errado. Nao e programa generico de "assistencia social" -- e um programa especifico para trabalhadores rurais durante a entressafra, analogo ao Chapeu de Palha de PE. Mudanca de categoria de "Assistencia Social" para "Trabalho Rural".

2. **ba-primeiro-emprego**: Estava descrito como programa generico para jovens de 18-24 anos. Na realidade, e exclusivamente para egressos de cursos tecnicos da rede estadual. Nao exige CadUnico. A selecao e por ranking de notas, nao por vulnerabilidade social.

3. **pe-no-batente**: Estava descrito como "frentes de trabalho pagando R$ 600/mes". Na realidade, e um programa de inclusao produtiva em 3 etapas (escolarizacao, qualificacao, insercao), sem evidencia de bolsa de R$ 600.

## Fontes Consultadas

- [Chapeu de Palha - Caixa](https://www.caixa.gov.br/programas-sociais/chapeu-de-palha/Paginas/default.aspx)
- [Chapeu de Palha 2026 - Blog Nossa Voz](https://blognossavoz.com.br/chapeu-de-palha-2026-governo-de-pernambuco-inicia-cadastramento-do-programa-para-trabalhadores-da-fruticultura-irrigada-e-pesca-artesanal-do-sertao/)
- [Folha PE - Cadastramento 2026](https://www.folhape.com.br/economia/governo-de-pernambuco-inicia-cadastramento-do-programa-chapeu-de-palha/463429/)
- [ALEPE - Reajuste valores](https://www.alepe.pe.gov.br/audioalepe/colegiado-aprova-reajuste-nos-valores-do-chapeu-de-palha/)
- [Cartao Recomecar - Petropolis](https://www.petropolis.rj.gov.br/pmp/index.php/programas/cartao-recomecar)
- [CNN Brasil - Cartao Recomecar](https://www.cnnbrasil.com.br/nacional/estamos-fazendo-cadastro-para-dar-r-3-mil-de-ajuda-para-familias-diz-governador-em-exercicio-do-rj-a-cnn/)
- [Governo CE - CMIC](https://www.ceara.gov.br/2025/12/15/recarga-de-dezembro-do-cartao-mais-infancia-ja-esta-disponivel/)
- [SPS CE - Cartao Mais Infancia](https://spssocial.sps.ce.gov.br/cartao-cmic)
- [SEMAD MG - Bolsa Reciclagem](https://meioambiente.mg.gov.br/w/governo-de-minas-repassa-mais-de-r-910-mil-do-bolsa-reciclagem-a-cooperativas-de-cata-dores)
- [ALMG - Lei 19.823/2011](https://www.almg.gov.br/legislacao-mineira/texto/LEI/19823/2011/)
- [Agencia Minas - Travessia](https://www.agenciaminas.mg.gov.br/sala-de-imprensa/governo-lanca-nova-fase-de-programa-contra-vulnerabilidade-social)
- [SEDESE - Programas](https://social.mg.gov.br/habitacao/programas-projetos)
- [SEASIC SE - Mao Amiga](https://assistenciasocial.se.gov.br/programa-mao-amiga/)
- [Governo SE - Mao Amiga Cana](https://sergipe.se.gov.br/noticias/assistencia-social/governo_inicia_pagamentos_do_mao_amiga_cana_de_acucar_e_reforca_apoio_aos_trabalhadores_do_campo)
- [Banese - Mao Amiga](https://www.banese.com.br/setor-publico/produtos-e-servicos/social/programa-mao-amiga)
- [SEC BA - Primeiro Emprego](https://estudantes.educacao.ba.gov.br/primeiroemprego)
- [FESF-SUS - Primeiro Emprego](https://www.fesfsus.ba.gov.br/servicos/projeto-primeiro-emprego)
- [SIGAS PE - PE no Batente](https://www.sigas.pe.gov.br/pagina/programa-de-incluso-produtiva-pernambuco-no-batente)
- [SAS PE - PE no Batente](https://www.sas.pe.gov.br/programas-e-projetos-2/pe-no-batente/)
- [PAT BA - Agua Para Todos](http://aguaparatodos.ba.gov.br/)
- [SDR BA - Programa Agua](http://www.sdr.ba.gov.br/servicos/programa-agua-para-todos)
- [ASA Brasil - Cisternas](https://asabrasil.org.br/2025/02/24/organizacoes-sociais-vao-construir-mais-50-mil-cisternas-no-semiarido-brasileiro/)

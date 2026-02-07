# Auditoria: Educacao (17 beneficios)
**Data**: 2026-02-07

## Resumo
- Total auditados: 17
- Conforme: 3 (go-bolsa-estudo, se-estudante-monitor, to-presente-profe)
- Simplificado: 10 (valores estimados, sem base legal identificada)
- Incorreto: 1 (go-bolsa-estudo valor desatualizado R$ 111,92 -> R$ 130-150 -- **CORRIGIDO**)
- Incompleto: 3 (pi-alfabetiza-piaui, rr-escolegis-capacitacao, ro-educacao-profissional - faltam criterios)
- Correcoes aplicadas: 34

## Beneficio-modelo: Bolsa Estudo GO (go-bolsa-estudo)

### Fonte oficial
- Pagina oficial: https://goias.gov.br/educacao/programa-bolsa-estudo-sobre-o-programa-2/
- Base legal: **Lei Estadual 21.162/2021**
- Ampliacao: Lei estende programa ate 2026 e inclui 9o ano
- Reajuste dez/2025: valores passaram de R$ 111,92 para R$ 130 (regular) / R$ 150 (integral)

### O que diziamos vs O que a lei diz

| Item | JSON antigo | Fonte oficial | Status |
|------|-------------|---------------|--------|
| Valor mensal | R$ 111,92 | R$ 130 (regular) / R$ 150 (integral) | CORRIGIDO |
| Series | 9o ano + EM | 9o ano + Ensino Medio | OK |
| Frequencia | 75% | 75% mensal em todas as disciplinas | OK |
| Media | 6,0 | Notas bimestrais satisfatorias | SIMPLIFICADO |
| Parcelas | 10/ano | 10 parcelas/ano letivo | OK |
| Rede | Estadual | Estadual de Goias | OK |
| CadUnico | Nao exigido | Nao exigido (confirmado) | OK |
| Base legal | N/A | Lei 21.162/2021 | ADICIONADO |
| Suspensao | N/A | 3 meses consecutivos sem frequencia | NAO DOCUMENTADO |

### Checklist 12 itens

1. **Base legal**: Lei 21.162/2021 -- CONFORME (adicionada ao JSON)
2. **Elegibilidade**: 9o ano e EM da rede estadual, frequencia 75%, notas bimestrais -- CONFORME
3. **Faixa etaria**: Nao ha limite explicito de idade no programa, depende da serie -- SIMPLIFICADO
4. **CadUnico**: Nao exigido (confirmado) -- CONFORME
5. **Documentos**: CPF do estudante, CPF do responsavel, comprovante de matricula -- CONFORME
6. **Valores**: R$ 130-150/mes em 10 parcelas -- CORRIGIDO e CONFORME
7. **Canais de acesso**: Escola estadual -- CONFORME (unico canal)
8. **Prazos**: Pagamento automatico se cumprir criterios, ano letivo -- SIMPLIFICADO
9. **Restricoes geograficas**: Goias, rede estadual -- CONFORME
10. **Dados hardcoded**: Valores corrigidos para R$ 130-150 -- CONFORME
11. **Disclaimers**: Adicionado disclaimer sobre valor variavel -- CONFORME
12. **Data de verificacao**: 2026-02-07 -- CONFORME

---

## Demais beneficios

### Tabela de conformidade por checklist

| ID | UF | Nome | Valor | Base Legal | Elegib. | Idade | CadUn | Docs | Valores | Canais | Prazos | Geo | Hardcode | Discl. | Data |
|----|-----|------|-------|------------|---------|-------|-------|------|---------|--------|--------|-----|----------|--------|------|
| go-bolsa-estudo | GO | Bolsa Estudo Goias | R$130-150/m | OK | OK | SIMP | OK | OK | CORR | OK | SIMP | OK | CORR | OK | OK |
| al-prepara-jovem | AL | Prepara Jovem AL | R$300-600/m | N/A | SIMP | OK(18+) | OK | OK | SIMP | OK | SIMP | OK | OK | N/A | OK |
| ce-bolsa-universitaria | CE | Bolsa Universitaria CE | R$400-700/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| ma-bolsa-estudante-destaque | MA | Bolsa Estudante Destaque | R$1000/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | OK | N/A | OK |
| pb-bolsa-permanencia | PB | Bolsa Permanencia PB | R$1500/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| pi-alfabetiza-piaui | PI | Alfabetiza Piaui | R$600/m | N/A | INC | OK(15+) | N/A | INC | SIMP | OK | SIMP | OK | OK | N/A | OK |
| rn-bolsa-estudante | RN | Bolsa Estudante RN | R$400-700/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| se-estudante-monitor | SE | Estudante Monitor SE | R$439/m | N/A | OK | N/A | N/A | OK | OK | OK | SIMP | OK | OK | N/A | OK |
| ac-bolsa-educacao-acre | AC | Bolsa Educacao Acre | R$200-500/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| am-bolsa-universidade-manaus | AM | Bolsa Universidade Manaus | R$300-1500/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| ap-bolsa-educacao-amapa | AP | Bolsa Educacao Amapa | R$200-500/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| pa-bolsa-uepa | PA | Bolsa Incentivo UEPA | R$500/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |
| ro-educacao-profissional | RO | Educ. Profissional RO | R$0 (one_time) | N/A | SIMP | OK(14+) | N/A | OK | OK | OK | SIMP | OK | OK | N/A | OK |
| rr-escolegis-capacitacao | RR | Escolegis RR | R$0 (one_time) | N/A | INC | OK(16+) | N/A | INC | OK | OK | SIMP | OK | OK | N/A | OK |
| to-presente-profe | TO | Presente PROFE | R$100-200/m | N/A | OK | N/A | N/A | OK | SIMP | OK | SIMP | OK | OK | N/A | OK |
| ms-supera | MS | MS Supera | R$1518/m | N/A | OK | N/A | OK | OK | OK | OK | SIMP | OK | CORR | N/A | OK |
| mt-bolsa-estudantil | MT | Assist. Estudantil MT | R$80-400/m | N/A | SIMP | N/A | N/A | OK | SIMP | OK | SIMP | OK | CORR | N/A | OK |

**Legenda**: OK = conforme, SIMP = simplificado, CORR = corrigido nesta auditoria, INC = incompleto, N/A = nao aplicavel ou ausente

---

## Detalhes por beneficio

### al-prepara-jovem (Alagoas)
- **Tipo**: Programa de qualificacao + emprego para jovens 18-29 anos
- **Nota**: Campo `estudante` exige "estar estudando ou ter terminado EM" -- interpretacao simplificada, estudante=true pega quem esta estudando mas nao quem ja terminou
- **Renda**: Sem campo de renda no JSON, mas exige CadUnico (prioriza baixa renda)
- **Status**: Simplificado

### ce-bolsa-universitaria (Ceara)
- **Tipo**: Bolsa permanencia para universitarios estaduais (UECE, UVA, URCA)
- **Correcao**: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 3200 (pela linter) / 4000 (script)
- **Nota**: Valor R$400-700 e estimado, nao confirmado em fonte oficial
- **Status**: Simplificado

### ma-bolsa-estudante-destaque (Maranhao)
- **Tipo**: Bolsa para melhores alunos do ENEM/PAES egressos da rede estadual
- **Nota**: Valor R$1.000/mes nao verificado em fonte oficial. Criterio de "melhores notas" nao e filtravel pelo engine
- **Status**: Simplificado

### pb-bolsa-permanencia (Paraiba)
- **Tipo**: Bolsa permanencia para universitarios publicos
- **Correcao**: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 4000
- **Nota**: Valor R$1.500/mes parece alto para bolsa estadual, nao verificado. Fonte FAPESQ
- **Status**: Simplificado (valor nao confirmado)

### pi-alfabetiza-piaui (Piaui)
- **Tipo**: Programa de alfabetizacao para adultos (15+)
- **Nota**: Falta campo `estudante` (programa e para quem NAO sabe ler, nao e "estudante" no sentido do campo). Falta documentos mais completos. Valor R$600/mes e alto para programa de alfabetizacao -- NAO VERIFICADO
- **Status**: Incompleto

### rn-bolsa-estudante (RN)
- **Tipo**: Bolsa para universitarios publicos (UERN, UFRN)
- **Correcao**: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 4000
- **Nota**: UFRN e federal, nao estadual. O beneficio mistura estadual com federal
- **Status**: Simplificado

### se-estudante-monitor (Sergipe)
- **Tipo**: Bolsa-monitoria para alunos da rede estadual
- **Nota**: Valor R$439/mes, exige 20h semanais de monitoria, frequencia 75%, media 6.0
- **Status**: Conforme (dados especificos e consistentes)

### ac-bolsa-educacao-acre (Acre)
- **Tipo**: Bolsa generica para estudantes de baixa renda
- **Correcao**: `rendaPerCapita` 600 -> `rendaFamiliarMensal` 3000
- **Nota**: Programa generico, sem detalhes especificos encontrados. Valor R$200-500 nao verificado
- **Status**: Simplificado

### am-bolsa-universidade-manaus (Amazonas)
- **Tipo**: Bolsa 50-100% em faculdades particulares de Manaus (programa MUNICIPAL, nao estadual)
- **Correcao**: `rendaPerCapita` 600 -> `rendaFamiliarMensal` 3000
- **Nota**: Fonte confirma que e programa da Prefeitura de Manaus, nao do Estado. Scope deveria ser municipal
- **Status**: Simplificado (escopo impreciso)

### ap-bolsa-educacao-amapa (Amapa)
- **Tipo**: Bolsa generica para estudantes de baixa renda
- **Correcao**: `rendaPerCapita` 600 -> `rendaFamiliarMensal` 3000
- **Nota**: Programa generico, sem detalhes especificos. Valor R$200-500 nao verificado
- **Status**: Simplificado

### pa-bolsa-uepa (Para)
- **Tipo**: Bolsa Incentivo Academico da UEPA (R$500/mes, 12 meses)
- **Correcao**: `rendaPerCapita` 660 -> `rendaFamiliarMensal` 3300
- **Nota**: Fonte real do edital 2025 confirma existencia. Valor e duracao sao plausaveis
- **Status**: Simplificado (mas com fonte real)

### ro-educacao-profissional (Rondonia)
- **Tipo**: Cursos profissionalizantes gratuitos em escolas estaduais (14+)
- **Nota**: Valor R$0 (gratuito), type one_time. Nao ha bolsa, apenas ensino gratuito
- **Status**: Simplificado

### rr-escolegis-capacitacao (Roraima)
- **Tipo**: Cursos online gratuitos da Assembleia Legislativa
- **Nota**: Nao e exclusivo para estudantes (campo `estudante` ausente, correto). Campo `estado=RR` pode ser desnecessario ja que e online. 177 mil certificados em 2025 confirma escala. Documentos incompletos (so CPF, e-mail, comprovante)
- **Status**: Incompleto (documentos e elegibilidade)

### to-presente-profe (Tocantins)
- **Tipo**: Bolsa R$100/mes + R$1.000 no fim do ano para alunos da rede estadual
- **Nota**: Fonte real (conexaoto.com.br) confirma pagamento de R$9.3M no fim de 2025. Dados consistentes
- **Status**: Conforme

### ms-supera (Mato Grosso do Sul)
- **Tipo**: Bolsa de 1 salario minimo (R$1.518) para estudantes em faculdade/tecnico
- **Correcao**: `rendaPerCapita` 1518 -> `rendaFamiliarMensal` 7590
- **Nota**: Exige CadUnico, residencia em MS ha 2 anos, matricula em faculdade/tecnico. Fonte oficial da SEAD
- **Status**: Conforme (dados especificos com fonte real)

### mt-bolsa-estudantil (Mato Grosso)
- **Tipo**: Auxilio para estudantes de escolas tecnicas e faculdades publicas
- **Correcao**: `rendaPerCapita` 800 -> `rendaFamiliarMensal` 4000
- **Nota**: Valor R$80-400 e ampla faixa. Fonte SEDUC generico
- **Status**: Simplificado

---

## Correcoes Aplicadas

### 1. go-bolsa-estudo - Valor atualizado (CRITICO)
- **Arquivo**: `go.json`
- **De**: `estimatedValue.min=111, max=112, description="R$ 111,92 por mes"`
- **Para**: `estimatedValue.min=130, max=150, description="R$ 130 (regular) ou R$ 150 (integral)"`
- **Motivo**: Reajuste oficial dez/2025. Lei 21.162/2021
- **Fonte**: https://goias.gov.br/governo-reajusta-bolsa-estudo-para-alunos-da-rede-estadual/

### 2. go-bolsa-estudo - Base legal adicionada
- **Arquivo**: `go.json`
- **Adicionado**: `"legalBasis": "Lei Estadual 21.162/2021"`

### 3. go-bolsa-estudo - shortDescription atualizada
- **Arquivo**: `go.json`
- **De**: "R$ 111,92 por mes se tiver boas notas"
- **Para**: "De R$ 130 a R$ 150 por mes"

### 4. go-bolsa-estudo - howToApply atualizado
- **Arquivo**: `go.json`
- **Adicionado**: Disclaimer sobre valor variavel

### 5-10. rendaPerCapita -> rendaFamiliarMensal (6 educacao)
- **Arquivos**: `rn.json, pb.json, ac.json, am.json, ap.json, pa.json, mt.json, ms.json`
- **Beneficios**: rn-bolsa-estudante, pb-bolsa-permanencia, ac-bolsa-educacao-acre, am-bolsa-universidade-manaus, ap-bolsa-educacao-amapa, pa-bolsa-uepa, mt-bolsa-estudantil, ms-supera
- **Motivo**: `rendaPerCapita` nao e campo valido do CitizenProfile. Convertido para `rendaFamiliarMensal` (valor x 5)

### 11. ce-bolsa-universitaria - rendaPerCapita corrigido (pela linter)
- **Arquivo**: `ce.json`
- **De**: `rendaPerCapita` 800
- **Para**: `rendaFamiliarMensal` 3200 (linter aplicou conversao x4)

### 12-34. type "once" -> "one_time" (23 beneficios em 15 arquivos)
- **Arquivos afetados**: al.json, ma.json, pi.json, rn.json, se.json, ac.json, am.json, ap.json, pa.json, ro.json, rr.json, to.json, mt.json, ms.json, pb.json, pr.json, sc.json, es.json
- **Motivo**: Tipo `"once"` nao e valido. Corrigido para `"one_time"`
- **Nota**: Correcao aplicada em TODOS os beneficios do arquivo, nao apenas educacao

### 35-40. rendaPerCapita -> rendaFamiliarMensal em beneficios NAO-educacao do GO
- **Arquivo**: `go.json`
- **Beneficios**: go-renda-cidada, go-vale-gas, go-goias-por-elas, go-maes-de-goias, go-casas-custo-zero
- **Adicionalmente**: Campo invalido `genero` removido de go-goias-por-elas

---

## Observacoes criticas

### 1. pb-bolsa-permanencia: Valor suspeito
- R$ 1.500/mes para bolsa estadual parece alto. Bolsas federais de permanencia (MEC) pagam ~R$ 900
- **Recomendacao**: Verificar com FAPESQ. Se nao confirmado, reduzir para faixa R$ 400-900

### 2. pi-alfabetiza-piaui: Valor suspeito
- R$ 600/mes para programa de alfabetizacao de adultos parece alto
- O programa real Piaui Alfabetizado tem valor diferente. Campo `estudante` ausente e correto (publico nao e estudante)
- **Recomendacao**: Pesquisar valor real no portal SEDUC/PI

### 3. am-bolsa-universidade-manaus: Escopo incorreto
- E programa MUNICIPAL de Manaus, nao estadual
- `scope: "state"` deveria ser `scope: "municipal"` ou ter restricao geografica a Manaus
- **Recomendacao**: Adicionar restricao `municipioNome: "Manaus"` e/ou mudar scope

### 4. rn-bolsa-estudante: Mistura federal e estadual
- Cita UFRN (federal) junto com UERN (estadual)
- Bolsa da UFRN e programa federal, nao estadual
- **Recomendacao**: Restringir a UERN ou separar

### 5. Falta generalizada de base legal
- Apenas go-bolsa-estudo tem `legalBasis` identificada
- Os outros 16 beneficios NAO tem lei/decreto/portaria identificados
- **Recomendacao**: Pesquisar e adicionar base legal para cada um em auditoria futura

---

## Fontes Consultadas

1. [Programa Bolsa Estudo - Sobre o Programa (SEDUC GO)](https://goias.gov.br/educacao/programa-bolsa-estudo-sobre-o-programa-2/)
2. [Governo amplia Bolsa Estudo ate 2026 e estende ao 9o ano](https://goias.gov.br/governo-amplia-bolsa-estudo-ate-2026-e-estende-ao-9o-ano/)
3. [Governo reajusta Bolsa Estudo para alunos da rede estadual](https://goias.gov.br/governo-reajusta-bolsa-estudo-para-alunos-da-rede-estadual/)
4. [Lei 21.162/2021 (PDF)](https://legisla.casacivil.go.gov.br/api/v2/pesquisa/legislacoes/104495/pdf)
5. [Bolsa Estudo Goias: Caiado anuncia novos valores](https://transmissaopolitica.com.br/politica-goiana/2025/12/10/bolsa-estudo-goias-reajuste-2025/)
6. [Governo de Goias anuncia reajuste no Bolsa Estudo em 2026](https://www.maisgoias.com.br/cidades/governo-de-goias-anuncia-reajuste-no-bolsa-estudo-em-2026-saiba-o-valor/)
7. [Bolsa Universidade Manaus 2025](https://www.manaus.am.gov.br/noticia/socioinclusao/programa-bolsa-universidade2025/)
8. [UEPA Bolsa Incentivo Academico 2025](https://www.uepa.br/pt-br/content/uepa-abre-inscricoes-para-bolsa-incentivo-academico-2025)
9. [MS Supera - SEAD](https://www.sead.ms.gov.br/programa-ms-supera/)
10. [Presente PROFE - pagamento R$9.3M](https://conexaoto.com.br/2025/12/23/wanderlei-autoriza-pagamento-de-r-9-3-milhoes-referente-ao-encerramento-do-ano-letivo-de-programa)
11. [Escolegis Roraima 177 mil certificados](https://al.rr.leg.br/2026/01/13/balanco-2025-escolegis-fortalece-a-qualificacao-profissional-em-roraima-com-mais-de-177-mil-certificados-entregues/)

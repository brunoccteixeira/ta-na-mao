# Benchmarking: Plataformas de Acesso a Benefícios Sociais

> **Tá na Mão vs. Mercado Global**
> Última atualização: 2026-02-04

---

## 1. Tabela Comparativa Principal

| Dimensão | **Tá na Mão** (BR) | **Propel** (EUA) | **Wizbii** (FR) | **Turn2us** (UK) | **Haqdarshak** (IN) | **Single Stop** (EUA) |
|---|---|---|---|---|---|---|
| **País** | Brasil | EUA | França (→ IT, ES) | Reino Unido | Índia (30+ estados) | EUA (50 estados) |
| **Fundação** | 2024 | 2016 | 2010 (pivot 2020) | 2012 | 2016 | 2007 |
| **O que faz** | Plataforma multi-canal de acesso a benefícios federais, estaduais, municipais e setoriais | App de gestão de EBT/SNAP + savings + emprego | Simulador de 500+ ajudas financeiras + advisory humano | Calculadora de benefícios + busca de grants + advocacy | Acesso a 5.000+ esquemas gov via agentes de campo + app | Screening de 20+ benefícios em universidades e comunidades |
| **Benefícios cobertos** | 229 (federal + 27 UFs + 40 municípios + setorial) | SNAP, WIC, Summer EBT | 500+ ajudas (moradia, bolsas, emprego, saúde) | Universal Credit, PIP, ESA, Housing, Pension, grants | 5.000+ esquemas em 14+ idiomas | Medicaid, SNAP, tax credits, utilities, 20+ programas |
| **Público-alvo** | 60M classes C/DE, 14M idosos digitais | 21.6M households EBT | Jovens 18-30 (estudantes, empregados) | Qualquer pessoa em dificuldade financeira UK | Famílias rurais e semi-urbanas Índia | Estudantes universitários e comunidades de baixa renda |
| **Modelo de negócio** | B2C + B2G (dashboards municipais) | B2C (interchange + ads) | B2B2C (empresas subsidiam) | Caridade (doações + subsidiárias) | B2C (agentes de campo) + B2G + B2B (CSR) | Nonprofit (filantropia + gov grants) |
| **Canais** | Android + PWA + WhatsApp + Voice (roadmap) | iOS + Android + Web | Web + App | Web + widgets embeddáveis + chatbot | App móvel + 52K agentes de campo | Web + presencial em universidades |
| **IA/Tech** | Gemini 2.0 Flash + 40+ tools + MCP | AI safety net tools + fraud detection | Algoritmo de matching + advisory humano | Calculadora + chatbot + API embeddável | Rules engine + app multilíngue | Screening engine + resource map |
| **Funding** | Pre-seed / bootstrapped | $68.2M (a16z, Kleiner Perkins) | ~$30.4M | GBP 7.7M/ano (charity) | $3.29M (Acumen) | Nonprofit (Robin Hood Foundation) |
| **Escala** | MVP (229 benefícios, 40 municípios) | 5M+ households, 52 estados | 11M+ usuários, 1M/ano no simulador | 4.8M users, 2.4M cálculos/ano | 7.6M famílias, 52K agentes | 116.7K indivíduos/ano |
| **Valor desbloqueado** | R$ 800-1.200/família/ano (target) | — | — | GBP 5.396/usuário/ano (GBP 12.9B total) | INR 18.800 crore ($2.2B total) | $698M/ano (FY24) |

---

## 2. Análise por Dimensão Estratégica

### 2.1 Modelos de Negócio

| Modelo | Quem usa | Prós | Contras | Aplicável ao Tá na Mão? |
|---|---|---|---|---|
| **B2C Ads/Interchange** | Propel | Escala massiva, gratuito pro usuário | Depende de volume, pode conflitar com missão social | Parcialmente — marketplace de serviços (bancos, microcrédito) |
| **B2B2C (corporates subsidiam)** | Wizbii | Sustentável, alinha interesses | Requer sales B2B forte | Sim — empresas como Caixa, Itaú, operadoras podem subsidiar |
| **B2G (governo paga)** | Nava, Beam UK, Single Stop | Contratos grandes, estável | Ciclo de vendas longo, dependência política | Sim — dashboards para prefeituras, CRAS digital |
| **Charity/Nonprofit** | Turn2us, BDT | Missão clara, grants disponíveis | Dependente de doações, difícil escalar | Parcialmente — como complemento, não core |
| **Hybrid Field Agent + Tech** | Haqdarshak | Alcança offline, cria empregos locais | Complexo de operar, unit economics difícil | Interessante — agentes comunitários do CRAS como "haqdarshaks" |
| **Success Fee** | Amar Assist (BR) | Alinha incentivo, zero risco pro usuário | Difícil com benefícios gratuitos | Limitado — funciona melhor para INSS/trabalhista |

### 2.2 Forças Únicas do Tá na Mão (já existentes)

| Força | Descrição | Concorrência |
|---|---|---|
| **Cobertura 3 níveis** | Federal + Estadual + Municipal + Setorial num só lugar | Nenhum concorrente tem |
| **40+ tools de agente AI** | Mais completo que qualquer concorrente em termos de ferramentas AI | Nenhum concorrente tem |
| **Carta de encaminhamento com QR** | Gera documento para validação no CRAS — ponte digital-presencial | Nenhum concorrente tem |
| **Score de vulnerabilidade preditivo** | 0-100 com recomendações proativas | Nenhum concorrente tem |
| **Detector de golpes** | Alerta PIX falso, pirâmides, empréstimos predatórios | Nenhum concorrente tem |
| **Multi-canal real** | Android + PWA + WhatsApp | Nenhum concorrente BR tem isso |
| **Dinheiro esquecido** | PIS/PASEP, FGTS, Valores a Receber integrados | Nenhum concorrente tem |
| **LGPD-first** | Consentimento granular, portabilidade, exclusão | Nenhum concorrente tem |

### 2.3 Gaps e Oportunidades de Melhoria

| Gap | Quem faz bem | O que o Tá na Mão pode aprender |
|---|---|---|
| **Advisory humano** | Wizbii (advisors dedicados), Haqdarshak (agentes de campo) | Integrar agentes comunitários de saúde / assistentes sociais como "multiplicadores" na plataforma |
| **Fraud protection do usuário** | Propel (card lock, transaction blocking) | Expandir alerta de golpes para monitoramento ativo de transações suspeitas |
| **Embeddable tools / API** | Turn2us (widgets para parceiros), Entitledto | Oferecer API/widgets para ONGs, CRAS, igrejas, associações embutirem o verificador de elegibilidade |
| **Grants/doações privadas** | Turn2us (1.700+ organizações), Single Stop | Mapear fundos filantrópicos brasileiros (Instituto Unibanco, Itaú Social, BNDES Fundo Social) como fonte complementar |
| **Expense optimization** | Wizbii (energia, telecom, streaming), Propel (grocery savings) | Agregar comparador de tarifas sociais (energia TSEE, telefone, internet subsidiada) |
| **Proactive outreach via dados** | Benefits Data Trust (identifica elegíveis proativamente) | Usar dados de CadÚnico/IBGE para push notifications proativas: "Você pode ter direito a X" |
| **Advocacy e policy** | Turn2us (advocacy sistêmica), Beam UK | Publicar relatórios de impacto (ESG) e advocacy por simplificação de benefícios |
| **Escala de funding** | Propel ($68M), Wizbii ($30M) | Considerar pitch para a16z Fintech, Omidyar Network, Luminate, Google.org Impact Challenge |

---

## 3. Concorrentes Diretos no Brasil

| Player | Tipo | Ameaça | Diferencial do Tá na Mão |
|---|---|---|---|
| **Caixa Tem / Benefícios Sociais** | Gov (Caixa) | Alta — é o app oficial | Tá na Mão agrega TODOS os benefícios (não só Caixa), mais user-friendly, AI |
| **Meu INSS** | Gov (Dataprev) | Média — só INSS | Tá na Mão cobre INSS + assistência + setorial |
| **CadÚnico App** | Gov | Média — só consulta | Tá na Mão verifica elegibilidade e gera carta de encaminhamento |
| **Amar Assist** | Privado (success fee) | Baixa — foco em INSS | Tá na Mão é gratuito e cobre mais programas |
| **Nenhum privado equivalente** | — | — | **Tá na Mão ocupa um espaço vazio no Brasil** |

---

## 4. Perfil Detalhado dos Concorrentes Globais

### 4.1 Propel (EUA)

**Fundação**: 2016
**Funding**: $68.2M (a16z, Kleiner Perkins, Nyca Partners)
**Escala**: 5M+ households/mês, 52 estados

**Produtos**:
- **Providers App**: Gestão de EBT/SNAP balance, transaction history
- **Fresh EBT**: Localizador de lojas com desconto
- **Jobs**: Vagas de emprego para beneficiários
- **Savings**: Cashback e ofertas exclusivas

**Modelo de negócio**:
- Interchange fees (quando usuários gastam via parcerias)
- Publicidade segmentada
- Parcerias com retailers

**O que aprender**:
- Transformou gestão de benefícios em fintech
- Monetização sem cobrar do usuário vulnerável
- AI para fraud detection e safety net

### 4.2 Wizbii (França)

**Fundação**: 2010 (pivot para benefícios em 2020)
**Funding**: ~$30.4M
**Escala**: 11M+ usuários, 1M simulações/ano

**Produtos**:
- **Simulador de ajudas**: 500+ benefícios em 5 minutos
- **Wizbii Money**: Advisory humano gratuito
- **Wizbii Drive**: Financiamento de carta de motorista
- **Wizbii Jobs**: Emprego para jovens

**Modelo de negócio**:
- B2B2C: Empresas (bancos, seguradoras, telcos) pagam para oferecer o serviço aos funcionários/clientes
- White-label para corporates

**O que aprender**:
- Advisory humano como diferencial
- Expansão internacional (França → Itália, Espanha)
- B2B2C viabiliza sustentabilidade

### 4.3 Turn2us (UK)

**Fundação**: 2012 (charity)
**Revenue**: GBP 7.7M/ano
**Escala**: 4.8M usuários, 2.4M cálculos/ano, GBP 12.9B valor desbloqueado

**Produtos**:
- **Benefits Calculator**: Verificador de elegibilidade
- **Grants Search**: 1.700+ fundos de caridade
- **Turn2us Helpline**: Suporte telefônico
- **Policy & Advocacy**: Lobby por simplificação

**Modelo de negócio**:
- Caridade (doações individuais e corporativas)
- Subsidiárias comerciais (software, consultoria)
- Government grants

**O que aprender**:
- Métricas de impacto (GBP 5.396/usuário)
- Embeddable widgets para parceiros
- Advocacy sistêmica por reforma de benefícios

### 4.4 Haqdarshak (Índia)

**Fundação**: 2016
**Funding**: $3.29M (Acumen, Omidyar)
**Escala**: 7.6M famílias, 52K agentes de campo, INR 18.800 crore ($2.2B) desbloqueados

**Produtos**:
- **App de cidadão**: 5.000+ esquemas em 14 idiomas
- **Rede de agentes**: 52K "haqdarshaks" em comunidades rurais
- **B2G dashboards**: Analytics para governos estaduais
- **B2B CSR**: Empresas financiam acesso para comunidades

**Modelo de negócio**:
- B2C: Pequena taxa por serviço de aplicação
- B2G: Contratos com governos estaduais
- B2B: Corporates pagam via CSR

**O que aprender**:
- Hybrid digital + human (agentes de campo)
- Escala em regiões de baixa conectividade
- Multilíngue desde o início

### 4.5 Single Stop (EUA)

**Fundação**: 2007
**Escala**: 116.7K indivíduos/ano, $698M valor desbloqueado/ano

**Produtos**:
- **Benefits Screener**: 20+ programas federais/estaduais
- **Tax Prep**: Preparação de impostos gratuita (EITC)
- **Financial Coaching**: Aconselhamento financeiro
- **Campus Integration**: Embedded em 100+ universidades

**Modelo de negócio**:
- Nonprofit
- Filantropia (Robin Hood Foundation)
- Government grants
- University partnerships

**O que aprender**:
- Foco em estudantes universitários (first-gen, low-income)
- Integração com instituições existentes
- Métricas de impacto rigorosas

---

## 5. Referências e Fontes

| Empresa | Fonte |
|---|---|
| Propel | [joinpropel.com](https://joinpropel.com), Crunchbase, TechCrunch |
| Wizbii | [wizbii.com](https://wizbii.com), PitchBook, Les Echos |
| Turn2us | [turn2us.org.uk](https://turn2us.org.uk), Charity Commission UK |
| Haqdarshak | [haqdarshak.com](https://haqdarshak.com), Acumen Portfolio |
| Single Stop | [singlestop.org](https://singlestop.org), Annual Reports |
| Benefits Data Trust | [bdtrust.org](https://bdtrust.org) |
| Entitledto | [entitledto.co.uk](https://entitledto.co.uk) |
| Nava PBC | [navapbc.com](https://navapbc.com) |
| Beam UK | [beam.org](https://beam.org) |

---

*Documento preparado para planejamento estratégico do Tá na Mão.*

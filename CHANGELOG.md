# Changelog - Tá na Mão

## [Unreleased]

### Added

#### Fase C — Expansão Estadual do Catálogo (106→189 benefícios)
- **83 novos benefícios estaduais** distribuídos nos 27 estados (de 3-6 para 7 cada)
- **Catálogo total: 257 benefícios** (43 federal + 25 setorial + 189 estadual)
- Categorias preenchidas por estado: Qualificação Profissional, Habitação, Saúde Materno-Infantil, Educação, Transporte
- Todos os benefícios baseados em programas reais pesquisados em fontes oficiais estaduais
- **Lote Nordeste (9 UFs)**: AL, BA, CE, MA, PB, PE, PI, RN, SE — programas como CRIA-AL, Mãe Bahia, VaiVem-CE, Qualifica PE
- **Lote Norte (7 UFs)**: AC, AM, AP, PA, RO, RR, TO — programas como CETAM-AM, Mamãe Cheguei-RO, Profissão Estudante-TO
- **Lote Centro-Oeste (4 UFs)**: DF, GO, MS, MT — programas como QualificaDF, Mães de Goiás, MS Supera, PEQ-MT
- **Lote Sul+Sudeste (7 UFs)**: ES, MG, RJ, SP, PR, RS, SC — programas como Mãe Paulistana, Porta de Entrada-RS, Casa Catarina
- Zero mudanças em TypeScript ou Python — apenas edição de 27 arquivos JSON

#### Fase B — Expansão Setorial do Catálogo (10→25 benefícios)
- **15 novos benefícios setoriais** em `sectoral.json`, com pesquisa oficial (Gov.br, Planalto, ANTT, Receita Federal)
- **Setor Doméstica (NEW — 3):** FGTS Doméstica (LC 150/2015), Seguro-Desemprego Doméstica, Vale-Transporte Doméstica
- **Setor CLT (NEW — 2):** FGTS – Saque e Direitos (Lei 8.036/1990), 13º Salário e Férias +1/3
- **Setor PCD (1→4):** Passe Livre Interestadual (Lei 8.899/1994), Isenção IPI Carro (Lei 8.989/1995), Cota de Emprego (Lei 8.213/1991)
- **Setor Catadores (1→3):** CATAFORTE, Pró-Catador (Decreto 11.414/2023)
- **Setor Entregadores/Motoristas (1→3):** MEI para Entregadores, Regulamentação de Apps (PLP 12/2024)
- **Setor Agricultores (4→5):** PNAE – Alimentação Escolar (Lei 15.226/2025)
- **Setor Pescadores (2→3):** Registro Geral da Pesca (RGP)
- **Setor MEI/Autônomos (1→2):** PRONAMPE – Crédito do Empreendedor
- **Novo campo `trabalhadoraDomestica`** em CitizenProfile (frontend + backend)
- **Novos setores `clt` e `pcd`** na constante SECTORS
- **Mappings `domestica`/`clt`** no evaluator sectorMap
- **Wizard StepTrabalho** — CLT agora mostra opções setoriais; mapping doméstica adicionado

#### CRAS Finder - Encontrar CRAS próximos
- **Endpoint `GET /api/v1/nearby/cras`** — Busca por GPS (lat/lng) ou CEP, raio configurável, fallback para JSON local
- **`CrasFinder` view** (`src/views/CrasFinder.tsx`) — Busca dual (GPS + CEP), toggle mapa/lista, cards com ligar/traçar rota
- **`CrasMap` component** (`src/components/Map/CrasMap.tsx`) — Mapa Leaflet interativo com markers, popups, raio de busca
- **`useNearbyCras` hook** (`src/hooks/useNearbyCras.ts`) — Integração com API, cálculo de distância Haversine
- **Rota `/cras`** via Next.js App Router em `app/(public)/cras/page.tsx`
- **Fallback database** — 86 CRAS de exemplo cobrindo todos os 27 estados
- **Testes de ingestão** — Suite completa para pipeline SAGI API com ~40 test cases
- **Tipo `CrasCardData`** em `chatClient.ts` para integração com agente

#### Home Redesign (Wizbii-style)
- **Hero com foto** — Imagem Gemini (mãe brasileira + bebê) em grid 50/50, blend suave à esquerda
- **Destaques fluorescentes** — Marca-texto verde (`linear-gradient`) em "seus direitos!", "benefícios sociais", etc.
- **Layout espaçado** — Tipografia maior (3.5rem), padding generoso, bullet points estilo Wizbii (→)
- **CTA pill-shaped** — Botão rounded-full com hover scale

#### Tema Claro para Páginas Públicas
- **Sistema de CSS custom properties** — `.theme-light` e `.theme-dark` wrappers via `index.css`
- **`PublicLayout`** em `App.tsx` — Todas as 6 rotas públicas envolvidas em `.theme-light` via layout route
- **Migração de 14 arquivos** de classes hardcoded dark (bg-slate-*, text-white, border-slate-*) para `var()` references
  - Páginas: Home, Catalog, BenefitDetail, About, Eligibility
  - Wizard: EligibilityWizard, BasicInfoStep, FamilyStep, IncomeStep, WorkStep, SpecialStep, RightsWallet
- **Admin permanece dark** — `WizardPage` usa `.theme-dark` wrapper
- Cores de acento (emerald, status colors) inalteradas — funcionam em ambos os temas

#### Transparência Jurídica (Base Legal)
- **Novos tipos** em `engine/types.ts`: `LegalBasisType`, `LegalReference`
  - `legalReference?: string` em `EligibilityRule`
  - `legalBasis?: { laws: LegalReference[] }` em `Benefit`
- **Base legal de 10 benefícios federais** em `federal.json`:
  - Bolsa Família (Lei 14.601/2023), BPC (Lei 8.742/1993 LOAS, CF/1988 Art. 203),
    TSEE (Lei 12.212/2010), Farmácia Popular (Lei 10.858/2004), Auxílio Gás (Lei 14.237/2021),
    MCMV (Lei 14.620/2023), Seguro-Desemprego (Lei 7.998/1990),
    Dignidade Menstrual (Lei 14.214/2021), Passe Livre (Lei 8.899/1994)
  - URLs do planalto.gov.br para cada lei/decreto
- **Seção "Base legal"** em `BenefitDetail.tsx` — Cards com badge de tipo, número, descrição e link externo
- **Referência legal expansível** em `CriterionCard.tsx` — Elemento `<details>` com ícone de balança quando `rule.legalReference` existe

## [1.6.0] - 2026-02-03 - Implementação Backend P2 + P3 (15 skills)

### Added

#### P2 — Prioridade Média (6 skills implementadas)

- **educacao-financeira** (`alerta_golpes.py`) — 3 tools, 19 testes
  - `verificar_golpe()` — Detecta 5 tipos de golpes comuns (PIX falso, empréstimo consignado, cadastro falso, pirâmide, falso benefício)
  - `simular_orcamento()` — Simulador de orçamento familiar com alertas e orientações
  - `consultar_educacao_financeira()` — Micro-lições financeiras e opções de microcrédito (CrediAmigo, Agroamigo, PRONAF)

- **mei-simplificado** (`simulador_mei.py`) — 2 tools, 19 testes
  - `simular_impacto_mei()` — Simula impacto de formalização MEI em cada benefício (BF, BPC, TSEE, Farmácia Popular)
  - `guia_formalizacao_mei()` — Guia em 5 passos para se tornar MEI

- **vulnerabilidade-preditiva** (`score_vulnerabilidade.py`) — 1 tool, 16 testes
  - `analisar_vulnerabilidade()` — Score 0-100 em 6 dimensões (renda 30%, composição 20%, moradia 15%, trabalho 15%, proteção 10%, território 10%)
  - Faixas: BAIXO (0-25), MODERADO (26-50), ALTO (51-75), CRITICO (76-100)
  - Recomendações proativas de benefícios baseadas no perfil

- **rede-suas** (`rede_suas.py`) — 2 tools, 23 testes
  - `classificar_necessidade_suas()` — Roteamento por keywords para CRAS, CREAS, Centro POP, CAPS, Conselho Tutelar
  - `listar_equipamentos_suas()` — Informações dos equipamentos SUAS com serviços oferecidos

- **a11y-auditor** (`legibilidade.py`) — 1 tool, 19 testes
  - `auditar_texto()` — Índice Flesch adaptado para português (meta ≥60), detecção de 22 jargões governamentais com substituições em linguagem simples

- **dados-abertos** (`jobs/dados_abertos/`) — 1 tool, 22 testes
  - Pipeline ETL: Extrator → Transformador → Carregador → Orquestrador
  - `consultar_dados_abertos()` — Dados públicos de 6 programas (BF, BPC, TSEE, Farmácia Popular, Auxílio Gás, Seguro Defeso)
  - Agenda de atualização e alertas de qualidade de dados

#### P3 — Prioridade Futura (9 skills implementadas)

- **voz-acessivel** (`comandos_voz.py`) — 3 tools, 16 testes
  - `mapear_comando_voz()` — Mapeamento de 7 comandos de voz (regex) para intenções do sistema
  - `listar_comandos_voz()` — Lista comandos disponíveis
  - `configurar_voz()` — Configurações Web Speech API (pt-BR, rate=0.85)

- **orcamento-participativo** (`orcamento_participativo.py`) — 2 tools, 13 testes
  - `buscar_consultas_abertas()` — Consultas participativas federais, estaduais e municipais
  - `explicar_proposta()` — Explicação de propostas em linguagem simples
  - Guia de votação por canal (web, presencial, WhatsApp)

- **economia-solidaria** (`economia_solidaria.py`) — 3 tools, 18 testes
  - `buscar_cooperativas()` — Catálogo de cooperativas com moedas sociais (Palmas, Mumbuca, Sampa, Capivari)
  - `buscar_feiras()` — Feiras solidárias e da agricultura familiar
  - `guia_criar_cooperativa()` — 6 passos + programas de fomento (PAA, PNAE, PRONAF)

- **impacto-esg** (`relatorio_impacto.py`) — 2 tools, 16 testes
  - `gerar_relatorio_impacto()` — Relatório anonimizado (LGPD Art. 12) com 4 categorias de métricas
  - `consultar_impacto_social()` — Métricas por tipo (acesso, financeiro, inclusão, eficiência)
  - 5 ODS impactados (1, 2, 10, 11, 16)

- **indicadores-sociais** (`indicadores_sociais.py`) — 2 tools, 19 testes
  - `consultar_indicadores()` — Painel completo: população, renda, IDH, Gini, pobreza, saneamento
  - `comparar_municipios()` — Comparativo entre 2-5 municípios vs. média nacional
  - Interpretações em linguagem simples (IDH, Gini, pobreza)
  - Dados mock para 5 municípios (SP, RJ, Salvador, Brasília, Manaus)

- **painel-gestor** (`dashboard_gestor.py`) — 1 tool, 14 testes
  - `consultar_dashboard_gestor()` — 3 módulos: visão geral, lacunas de cobertura, benchmark
  - KPIs: população, famílias CadÚnico, cobertura BF, IDH, taxa de pobreza
  - Alertas automáticos (cobertura baixa, pobreza alta, saneamento crítico)
  - Estimativa de equipamentos SUAS necessários

- **mapa-social** (`mapa_social.py`) — 3 tools, 17 testes
  - `listar_camadas()` — 14 camadas em 3 categorias (indicadores, equipamentos, análise)
  - `consultar_mapa_social()` — Dados choropleth, pontos de equipamentos, heatmaps
  - `identificar_desertos()` — Desertos de assistência social por ratio famílias/CRAS
  - Classificação: ADEQUADO, INSUFICIENTE, CRÍTICO, SEM_COBERTURA

- **pesquisa-campo** (`pesquisa_campo.py`) — 3 tools, 18 testes
  - `listar_questionarios()` — 3 templates (satisfação, necessidades, atendimento CRAS)
  - `registrar_resposta()` — Registro 100% anônimo (sem CPF, nome ou telefone)
  - `gerar_relatorio_pesquisa()` — Relatório agregado (mínimo 10 respostas) + NPS
  - Coleta multi-canal (app, web, WhatsApp, presencial)

- **seguranca-cidada** (`seguranca_cidada.py`) — 5 tools, 38 testes
  - `registrar_consentimento()` — Consentimento granular por finalidade (LGPD Art. 7)
  - `revogar_consentimento()` — Revogação individual ou total
  - `exportar_dados()` — Portabilidade de dados (LGPD Art. 18, V)
  - `excluir_dados()` — Direito ao esquecimento (LGPD Art. 18, VI) com confirmação
  - `consultar_politica_privacidade()` — Política em linguagem simples
  - Classificação de dados em 4 categorias (pessoais, sensíveis, menores, financeiros)
  - Plano de resposta a incidentes em 5 etapas
  - Hash SHA-256 para CPF e IP (nunca armazenados em texto)

### Changed
- **agent.py** — 24 novas FunctionDeclarations + TOOL_FUNCTIONS registradas (total: ~70 tools)
- **prompts.py** — Documentação de P2 + P3 adicionada ao SYSTEM_PROMPT

### Stats
- **36 arquivos** alterados/criados
- **8.262 linhas** adicionadas
- **731 testes** passando (0 falhas)
- **15 novas skills** com **~340 novos testes**

---

## [1.5.0] - 2026-02-03 - Skills de Conhecimento Estratégico

### Added
- **23 novas skills** cobrindo gestão pública, assistência social, economia e tecnologia
  - **P0 — Crítico:** `cadunico-api` (API CadÚnico via Conecta Gov.br), `whatsapp-flows` (fluxos conversacionais WhatsApp), `rede-protecao` (rede de proteção social + detecção de urgência)
  - **P1 — Alto:** `govbr-integrator` (Login Único + APIs Conecta), `pwa-offline` (Service Workers, IndexedDB, Background Sync), `monitor-legislacao` (scraping DOU + análise com IA), `direitos-trabalhistas` (calculadoras de rescisão e seguro-desemprego), `acompanhante-digital` (modo acompanhante para agentes comunitários)
  - **P2 — Médio:** `educacao-financeira` (micro-lições + detector de golpes), `mei-simplificado` (simulador "perco o Bolsa Família se virar MEI?"), `vulnerabilidade-preditiva` (score de risco social), `rede-suas` (navegação CRAS/CREAS/CAPS/Centro POP), `a11y-auditor` (auditoria WCAG 2.1 AA), `dados-abertos` (pipeline ETL de dados governamentais)
  - **P3 — Futuro:** `voz-acessivel` (speech-to-text/text-to-speech pt-BR), `orcamento-participativo` (votação participativa), `economia-solidaria` (diretório de cooperativas), `impacto-esg` (relatórios ODS), `indicadores-sociais` (APIs IBGE/IPEA/MDS), `painel-gestor` (dashboard B2G), `mapa-social` (choropleth de vulnerabilidade), `pesquisa-campo` (questionários + análise com IA), `seguranca-cidada` (LGPD com consentimento granular)
- Skill `changelog` para manter documentação padronizada de mudanças
- 25 skills pré-existentes versionadas no git (antes ficavam apenas locais)
- README.md das skills reorganizado em 8 categorias com 49 skills no total

### Changed
- `.gitignore` atualizado: `.claude/` agora é versionada (apenas `settings.local.json` ignorado)

---

## [2026-01-29] - Sprint 12: Benefícios Municipais

### 🎯 Foco: Catálogo Municipal de Benefícios

Implementação da Fase 2 do MVP Website - adição de benefícios municipais ao catálogo, cobrindo os 40 maiores municípios brasileiros.

### ✅ Frontend

#### Nova Estrutura de Dados Municipais
- **`frontend/src/data/benefits/municipalities/`** - Pasta com 40 arquivos JSON
- Cada arquivo nomeado pelo código IBGE do município (ex: `3550308.json` para São Paulo)
- Estrutura padronizada com metadados, regras de elegibilidade e documentos

#### Municípios Cobertos (40)
**Top 10:**
- São Paulo, Rio de Janeiro, Brasília, Salvador, Fortaleza
- Belo Horizonte, Manaus, Curitiba, Recife, Porto Alegre

**Capitais Regionais (11-20):**
- Goiânia, Belém, Guarulhos, Campinas, São Luís
- São Gonçalo, Maceió, Duque de Caxias, Campo Grande, Natal

**Demais Capitais e Grandes Cidades (21-40):**
- Teresina, São Bernardo, João Pessoa, Osasco, Santo André
- Ribeirão Preto, Uberlândia, Contagem, Sorocaba, Aracaju
- Cuiabá, Feira de Santana, Joinville, Aparecida de Goiânia
- Londrina, Juiz de Fora, Ananindeua, Porto Velho, Niterói, Macapá

#### Atualizações no Engine
- **`catalog.ts`** - Carregamento dinâmico de benefícios municipais via código IBGE
  - Nova função `getBenefitsForMunicipality()`
  - Nova função `getMunicipalitiesWithBenefits()`
  - Atualizado `getAllBenefits()` para incluir municipais
  - Atualizado `getBenefitById()` para buscar em municipais
  - Atualizado `getBenefitsByScope()` com scope 'municipal'
  - Atualizado `getCatalogStats()` com contadores municipais

#### Atualizações no RightsWallet
- **Nova categoria "Benefícios Municipais"** com ícone 🏘️ e cor ciano
- Detecção automática de benefícios municipais pelo padrão de ID
- Agrupamento de resultados: Federal → Estadual → Municipal → Setorial
- Dica atualizada para mencionar benefícios estaduais E municipais

#### Atualizações no Catalog
- **Novo filtro "Municipal"** nos botões de scope
- Mapeamento de 40 códigos IBGE para nomes de municípios
- Badge ciano para benefícios municipais
- Busca por nome de município

### 📊 Estatísticas do Catálogo

| Tipo | Quantidade |
|------|------------|
| Federais | 16 |
| Estaduais | 106 |
| Municipais | 97 |
| Setoriais | 10 |
| **Total** | **229 benefícios** |

### 📝 Categorias de Benefícios Municipais

| Categoria | Exemplos |
|-----------|----------|
| Transferência de Renda | Auxílio BH (R$ 600), Mais Social (R$ 450), Bora Belém |
| Moradia | Bolsa Moradia BH (R$ 800), Aluguel Social, Locação Social |
| Alimentação | Restaurantes Populares, Cestas Básicas, Bom Prato |
| Transporte | Passe Livre Idoso, Passe Livre Estudantil, Tarifa Social |
| Educação | Bolsa Universidade, Bolsa Nota Dez, Todo Jovem na Escola |
| Utilidades | Tarifa Social Água, Vale Gás, Conta em Dia |
| Primeira Infância | Primeiro Passo, Bolsa Creche |
| Qualificação | CNH Social, Primeira Chance, Nosso Futuro |

### 🧪 Verificação

- Build passou sem erros
- 40 arquivos JSON municipais criados
- 97 benefícios municipais no catálogo
- Filtro por município funcionando
- RightsWallet exibe categoria municipal

---

## [2026-01-28] - Sprint 11: Crédito Imobiliário (MCMV)

### 🎯 Foco: Plataforma de Orientação Habitacional

Transformar módulo MCMV de simples verificação de renda para plataforma completa de orientação habitacional.

### ✅ Backend

#### Módulo MCMV Reescrito
- **`mcmv.py`** - 7 critérios de elegibilidade completos
  - Faixas atualizadas 2026 (R$ 2.850 a R$ 12.000)
  - Nova Faixa 4 para classe média (até R$ 500 mil)
  - Grupos prioritários (situação de rua, violência, BPC/BF)
  - Benefício 100% gratuito para BPC/Bolsa Família Faixa 1

#### Novas Tools
- **`simulador_mcmv.py`** - Simulador de financiamento
  - `simular_financiamento_mcmv()` - Cálculo completo com SAC/Price
  - `simular_reforma()` - Programa Reforma Casa Brasil
  - `comparar_modalidades()` - Comparação aquisição vs reforma vs locação
- **`carta_habitacao.py`** - Carta específica para habitação
  - Simulação de financiamento incluída
  - Checklist de documentos por faixa
  - Lógica de encaminhamento (CRAS → Prefeitura → CAIXA)
  - QR Code para validação

#### Atualizações
- **`regras_elegibilidade/__init__.py`** - CitizenProfile com 12 novos campos
- **`triagem_universal.py`** - Campo `habitacao` enriquecido com faixa, subsídio e alternativas
- **`documentos_por_beneficio.json`** - MCMV e MCMV_REFORMAS adicionados

### 📊 Impacto

| Antes | Depois |
|-------|--------|
| 1 critério (renda) | 7 critérios completos |
| Sem simulação | Simulador com Price/SAC |
| Sem alternativas | Compra vs reforma vs locação |
| Encaminhamento genérico | Lógica CRAS/Prefeitura/CAIXA |
| 27 tools | 29 tools (+2) |

### 🧪 Testes
- **42 testes unitários** para módulo MCMV (`tests/test_mcmv.py`)
- Cobertura de todas as faixas de renda
- Testes de grupos prioritários
- Testes de simulação de financiamento

### 📝 Documentação
- `backend/docs/AGENT.md` - Tools simulador_mcmv e carta_habitacao documentadas
- Faixas MCMV 2026 documentadas

---

## [2025-01-28] - Sprint 10: Carteira de Direitos

### 🎯 Foco: Triagem de Elegibilidade + Carta de Encaminhamento

Implementação do formulário inteligente de triagem e carta de encaminhamento para CRAS.

### ✅ Backend

#### Módulo regras_elegibilidade/ (8 verificadores)
- `bolsa_familia.py` - Regras Bolsa Família
- `bpc.py` - Regras BPC/LOAS (idoso + PCD)
- `farmacia_popular.py` - Regras Farmácia Popular
- `tsee.py` - Regras Tarifa Social de Energia
- `auxilio_gas.py` - Regras Auxílio Gás
- `garantia_safra.py` - Regras Garantia-Safra
- `seguro_defeso.py` - Regras Seguro Defeso
- `mcmv.py` - Regras Minha Casa Minha Vida

#### Novas Tools
- **`triagem_universal.py`** - Triagem multi-benefício consolidada
  - Avalia todos os 8 benefícios de uma vez
  - Retorna elegibilidade, motivo e próximos passos
  - Gera "Carteira de Direitos" visual
- **`gerar_carta_encaminhamento.py`** - PDF + QR Code para CRAS
  - Dados do cidadão pré-preenchidos
  - Composição familiar
  - Checklist de documentos
  - QR Code para validação online

#### Novos Endpoints
- **`routers/carta.py`** - Endpoints de geração e validação
  - `POST /api/v1/carta/gerar` - Gera carta com PDF
  - `GET /api/v1/carta/{codigo}` - Consulta carta
  - `GET /api/v1/carta/{codigo}/pdf` - Download PDF
  - `POST /api/v1/carta/{codigo}/validar` - Valida QR Code

#### Novo Model
- **`models/carta_encaminhamento.py`** - Persistência de cartas
  - Código único de validação
  - Dados do cidadão (hash CPF)
  - Benefícios solicitados
  - CRAS de destino
  - Validade (30 dias)

### ✅ Frontend

#### EligibilityWizard/ (8 componentes)
- `EligibilityWizard.tsx` - Wizard principal de 4 etapas
- `BasicInfoStep.tsx` - Coleta CPF e cidade
- `FamilyStep.tsx` - Composição familiar
- `IncomeStep.tsx` - Renda familiar (slider)
- `SpecialStep.tsx` - Condições especiais (idoso, PCD, gestante)
- `RightsWallet.tsx` - Carteira de Direitos visual
- `EncaminhamentoCard.tsx` - Card com PDF + QR Code
- `types.ts` - Tipos TypeScript

#### Integração no App.tsx
- Botão FAB 🎯 "Descobrir Direitos" no canto inferior
- Abre wizard em modal/drawer
- Resultado integrado ao chat

### 📊 Impacto

| Antes | Depois |
|-------|--------|
| Triagem conversacional (10+ perguntas) | Wizard visual (4 etapas) |
| Resultado por benefício | Carteira de Direitos consolidada |
| Cidadão vai ao CRAS sem preparação | Carta de encaminhamento pré-preenchida |
| Atendimento CRAS 2h | Atendimento estimado 30min |

### 📝 Documentação
- `backend/docs/API.md` - Endpoints /carta
- `backend/docs/AGENT.md` - Tools triagem_universal e gerar_carta_encaminhamento

---

## [2025-01-05] - Melhorias de Código e Testes

### ✅ Adicionado

#### Testes Unitários Completos
- **ProfileViewModelTest** - 7 casos de teste cobrindo todas as funcionalidades
- **HistoryViewModelTest** - 6 casos de teste para histórico de consultas
- **BenefitDetailViewModelTest** - 5 casos de teste para detalhes de benefícios
- **100% de cobertura de ViewModels** - Todos os 12 ViewModels principais têm testes

#### Documentação
- **SETUP_JAVA.md** - Guia completo de instalação do Java 17
- **TESTING_GUIDE.md** - Guia completo de testes e build do app
- **IMPROVEMENTS_SUMMARY.md** - Resumo detalhado de todas as melhorias

### 🔧 Melhorado

#### AgentResponseParser
- Removida função duplicada `parseBrazilianCurrency`
- Código mais limpo e reutilizável
- Parsing centralizado e consistente

#### ProfileViewModel
- Cache strategy documentada
- Parsing centralizado usando AgentResponseParser
- Código mais limpo e manutenível

#### FirebaseMessagingService
- TODO convertido em documentação clara
- Estrutura preparada para implementação futura

### 📊 Métricas
- **ViewModels**: 12
- **Testes Unitários**: 12 (100% de ViewModels)
- **TODOs Resolvidos**: 2/2
- **Refatorações**: 1 (código duplicado removido)
- **Documentação Criada**: 3 arquivos

## [2025-01-05] - Sprint 10: Android Play Store Ready

### 🎯 Foco: Preparação para Publicação na Play Store

App Android pronto para publicação com features completas e APK assinado.

### ✅ Adicionado

#### WalletRepository (Carteira de Benefícios)
- **`WalletRepositoryImpl.kt`** - Implementação real do repositório
  - Chamada à API `/api/v1/programs/beneficiario/{cpf}`
  - Injeção com Hilt no WalletViewModel
  - Substituição de dados mock por dados reais da API

#### BenefitDetailScreen (Detalhe do Benefício)
- **`BenefitDetailScreen.kt`** - Nova tela de detalhes
  - Nome e descrição do benefício
  - Valor mensal/anual formatado
  - Datas de pagamento (último e próximo)
  - Status visual (ativo, pendente, elegível)
  - Requisitos e documentos necessários
  - Botões de ação contextuais
- **`BenefitDetailViewModel.kt`** - ViewModel com estados
- **Rota no NavHost** - `benefit/{benefitId}` registrada
- **Screen.kt** - BenefitDetail adicionado às rotas

#### Configuração de Signing para Release
- **Keystore de produção** criado (`tanamao-release.keystore`)
- **Signing config** em `build.gradle.kts`
  - Suporte a keystore via `local.properties`
  - Variáveis: KEYSTORE_PATH, KEYSTORE_PASSWORD, KEY_ALIAS, KEY_PASSWORD
- **APK v2 signed** verificado com apksigner

### 🔧 Corrigido

#### Erros de Compilação (10+ fixes)
- `icon` → `leadingIcon`/`trailingIcon` em PropelButton
- `textoImprimivel` → `printableText` no domain model
- Import faltando: `formatNumber` em MoneyScreen
- Conflito de enum: `BenefitStatus` qualificado
- PropelCard colors param → Material Card
- `TaNaMaoTextStyles` → `MaterialTheme.typography`
- MessageType: adicionado `MONEY_RESULT`, `MEDICINE_RESULT`
- DocumentList type mismatch → wrapper `MessageMetadata.DocumentList`
- CircleShape import faltando
- ExperimentalFoundationApi OptIn
- Gson Hilt provider adicionado
- backup_rules.xml: removido domain `cache` inválido

### 📦 Build Release

| Item | Status |
|------|--------|
| Kotlin compilation | ✅ |
| Hilt DI compilation | ✅ |
| Lint vital checks | ✅ |
| R8 minification | ✅ |
| Resource shrinking | ✅ |
| APK signed (v2 scheme) | ✅ |

**Output:** `TaNaMao-release-v1.0.0.apk` (3.6 MB)

### 📊 Checklist Play Store

| Item | Status |
|------|--------|
| Ícone do app | ✅ |
| Splash screen | ✅ |
| ProGuard/R8 | ✅ |
| Minificação | ✅ |
| Shrink resources | ✅ |
| Signing key | ✅ |
| versionCode | 1 |
| versionName | 1.0.0 |

---

## [2025-01-03] - Melhorias no Perfil e Parsing

### 🎯 Foco: Perfil do Usuário e Exportação LGPD

Melhorias significativas no perfil do usuário, exportação de dados para conformidade LGPD e parsing robusto de respostas do agente.

### ✅ Adicionado

#### Perfil do Usuário
- **Seção "Dinheiro Esquecido"** no ProfileScreen
  - Verificação automática de PIS/PASEP, SVR e FGTS ao abrir o perfil
  - Visualização de valores disponíveis por tipo de dinheiro esquecido
  - Card destacado quando há dinheiro disponível
  - Breakdown detalhado (PIS/PASEP, Valores a Receber, FGTS)
  - Navegação para tela Money para ver detalhes e resgatar
  - Estados visuais: loading, dinheiro encontrado, nenhum dinheiro, estado inicial

#### Exportação de Dados (LGPD)
- **Função `exportUserData()`** no ProfileViewModel
  - Gera relatório completo formatado com todos os dados do usuário
  - Inclui: informações pessoais, estatísticas, benefícios, histórico de consultas
  - Formato texto legível para exportação/compartilhamento
- **Função `shareUserData()`** para compartilhamento
  - Compartilhamento via Intent do Android
  - Integração no PrivacySettingsScreen
  - Usuário pode escolher salvar em arquivo, enviar por email, WhatsApp, etc.

#### Parsing de Respostas do Agente
- **Melhorias no `AgentResponseParser`**:
  - `parseUserBenefits()` melhorado com extração de status e datas de pagamento
  - Funções auxiliares adicionadas:
    - `extractUserName()` - Extração robusta de nome do usuário
    - `extractTotalReceived()` - Extração de total recebido com múltiplos padrões
    - `extractPaymentDates()` - Extração de datas de pagamento (último e próximo)
  - `parseMoneyCheckResult()` mais robusto:
    - Detecção melhorada de valores
    - Extração de prazos/deadlines quando mencionados
    - Extração de links/URLs quando disponíveis
  - Funções faltantes implementadas:
    - `parseMoneyResult()` - Wrapper para MoneyResult
    - `parseMedicineResult()` - Extração de medicamentos elegíveis
    - `parseEligibilityResult()` - Extração de elegibilidade com score e critérios
    - `parseDocumentList()` - Extração de lista de documentos
    - `parseLocationCard()` - Extração de informações de localização (CRAS/farmácias)

### 🔄 Melhorado

#### ProfileViewModel
- **Cache melhorado** com campos `totalReceived` e `totalReceivedThisYear`
- **Parsing centralizado** usando `AgentResponseParser` em vez de regex manual
- **Código mais limpo** e manutenível
- **Data class `ForgottenMoneyInfo`** para informações de dinheiro esquecido

#### AgentResponseParser
- **`parseUserBenefits()`** agora extrai:
  - Status do benefício (ACTIVE, PENDING, ELIGIBLE, BLOCKED, NOT_ELIGIBLE)
  - Datas de pagamento (último e próximo)
  - Suporte a mais programas (Auxílio Brasil, Dignidade Menstrual)
- **`parseMoneyCheckResult()`** mais robusto:
  - Suporta mais formatos de resposta
  - Extração de prazos quando mencionados
  - Melhor detecção de valores em diferentes formatos

### 📊 Impacto

| Antes | Depois |
|-------|--------|
| Parsing manual com regex em ViewModels | Parsing centralizado e robusto |
| Sem exportação de dados LGPD | Exportação completa e funcional |
| Sem visualização de dinheiro esquecido no perfil | Seção dedicada com verificação automática |
| Parsing limitado de benefícios | Extração completa (status, datas, valores) |

### 📝 Notas Técnicas

- **ProfileViewModel**: Agora usa `AgentResponseParser` para todas as extrações, eliminando código duplicado
- **PrivacySettingsScreen**: Integrado com ProfileViewModel para exportação de dados
- **AgentResponseParser**: Parser centralizado para todas as respostas do agente, facilitando manutenção

---

## [2025-01-28] - Sprint 9: Entregador de Direitos

### 🎯 Foco: De "Tutorial de Cadastro" para "Entregador de Direitos"

Implementação da visão estratégica consolidada após pesquisa de mercado.

**Descoberta-chave**: 80% dos brasileiros já têm Gov.br. O problema não é cadastro, é a ÚLTIMA MILHA.

**Oportunidade identificada**: R$ 42 bilhões em dinheiro esquecido (PIS/PASEP + SVR + FGTS).

### ✅ Adicionado

#### Pilar 1: Dinheiro Esquecido (5 novas tools)
- `consultar_dinheiro_esquecido` - Mostra R$ 42 bi disponíveis
- `guia_pis_pasep` - Passo-a-passo para PIS/PASEP (R$ 26 bi, 10,5M pessoas)
- `guia_svr` - Passo-a-passo para Valores a Receber BC (R$ 8-10 bi)
- `guia_fgts` - Passo-a-passo para FGTS (R$ 7,8 bi) - **PRAZO: 30/12/2025**
- `verificar_dinheiro_por_perfil` - Triagem baseada no perfil

#### Pilar 2: Copiloto de Navegação (2 novas tools)
- `meus_dados` - Visão consolidada: benefícios + valores + alertas
- `gerar_alertas_beneficios` - Alertas proativos (CadÚnico >2 anos, pagamento atrasado)

#### Pilar 3: Ponte CRAS-Digital (2 novas tools)
- `preparar_pre_atendimento_cras` - Checklist personalizada de documentos
- `gerar_formulario_pre_cras` - Formulário pré-preenchido para levar ao CRAS

#### Melhorias no Chat
- Botão "Dinheiro esquecido" como opção primária na tela inicial
- Botões contextuais para PIS/PASEP, SVR, FGTS quando relevante
- Botão "Dinheiro esquecido" nas opções de programas

### 📊 Impacto

| Antes | Depois |
|-------|--------|
| 16 tools | 25 tools (+9) |
| Foco em cadastro | Foco em entrega de valor |
| Usuário vai ao CRAS sem preparação | Usuário chega com documentos e formulário prontos |
| Não mencionava dinheiro esquecido | Destaque para R$ 42 bi disponíveis |

### 📝 Documentação
- `docs/VISAO_ESTRATEGICA.md` - Documento consolidado com pesquisa + visão
- `backend/docs/AGENT.md` - Atualizado com Sprint 9

---

## [2025-01] - Acessibilidade e Linguagem Simples

### 🎯 Foco: Cidadão de Baixa Renda e Baixa Escolaridade

O app é para cidadãos vulneráveis. Toda interface usa linguagem simples, sem siglas ou termos técnicos.

### ✅ Adicionado

#### Backend
- **Endpoints Nearby** (`/api/v1/nearby/`)
  - `GET /nearby/farmacias` - Farmácias próximas por GPS ou CEP
  - `GET /nearby/cras` - CRAS próximos por GPS ou CEP
  - Retorna links prontos: Google Maps, Waze, WhatsApp
  - Veja `backend/docs/API.md` seção "Serviços Próximos"

- **Botões Contextuais no Chat**
  - Após "Tenho direito?", mostra opções específicas de programas
  - Botões: Bolsa Família, Remédio de graça, BPC, Desconto na luz
  - Corrigido: CRAS não aparece mais em fluxo de Farmácia Popular

#### Android
- **Tela de Mapa Redesenhada**
  - Antes: Grid de cobertura por estado (dados para gestores)
  - Agora: "Serviços perto de você" com Farmácias e CRAS
  - Botões de ação: Abrir no Maps, Ligar, WhatsApp
  - Usa GPS do dispositivo para localização

### 🔄 Alterado

#### Glossário de Linguagem Simples

| Antes (Técnico) | Depois (Simples) |
|-----------------|------------------|
| Verificar elegibilidade | Tenho direito? |
| CRAS | Posto de assistência social |
| BPC/LOAS | Ajuda para idosos e pessoas com deficiência |
| CadÚnico | Cadastro do governo para receber ajudas |
| TSEE | Desconto na conta de luz |
| Renda per capita | Dinheiro que cada pessoa da casa ganha |
| PCD | Pessoa com deficiência |
| Laudo médico | Papel do médico |
| Comprovante de residência | Conta de luz ou água com seu endereço |
| Farmácia credenciada | Farmácia que dá remédio de graça |

### 📝 Notas

- **IMPORTANTE**: Farmácia Popular = vai direto na farmácia (não precisa ir ao CRAS)
- Mapa agora é útil para o cidadão, não para gestores
- Chat adapta botões baseado no contexto da conversa

---

## [2024] - Melhorias de Infraestrutura e Qualidade

### ✅ Adicionado

#### Backend
- **Migração completa para SQLAlchemy Async**
  - Todos os routers convertidos para async (100%)
  - Melhor performance e concorrência (2-3x mais requisições simultâneas)
  - Veja `backend/docs/ASYNC_MIGRATION.md` para detalhes técnicos

- **Testes Automatizados**
  - Suíte completa de testes com pytest
  - Testes assíncronos com `httpx.AsyncClient`
  - Fixtures para DB e cliente HTTP
  - Testes para endpoints: programs, aggregations, agent

- **Observabilidade**
  - Logging estruturado com `structlog` (logs JSON)
  - Métricas Prometheus (`/metrics` endpoint)
  - Health checks detalhados (`/health` endpoint)
  - Exception handlers centralizados

- **Performance**
  - Cache Redis implementado
  - Índices de banco de dados otimizados
  - Multi-stage Docker builds

- **Segurança**
  - Credenciais removidas de código
  - Arquivo `.env.example` para todas as variáveis
  - Validação de configuração

#### Frontend
- **Testes**
  - Vitest configurado
  - React Testing Library para componentes
  - Error Boundaries para tratamento de erros

- **Developer Experience**
  - Error handling centralizado
  - Melhor estrutura de testes

#### Android
- **Testes Unitários**
  - Testes para ViewModels principais (Home, Chat, Search, Wallet, Municipality, Settings, Map)
  - MockK para mocks
  - Turbine para testes de Flow
  - Testes instrumentados (estrutura criada)

#### CI/CD
- **GitHub Actions**
  - Workflows para backend (lint, type-check, test)
  - Workflows para frontend (lint, test, build)
  - Workflows para Android (build, test)

- **Pre-commit Hooks**
  - black (Python)
  - ruff (Python)
  - mypy (Python)
  - eslint (TypeScript/JavaScript)
  - ktlint (Kotlin)

#### Documentação
- `docs/ARCHITECTURE.md` - Arquitetura do sistema
- `docs/DEPLOYMENT.md` - Guia de deployment
- `docs/TROUBLESHOOTING.md` - Troubleshooting comum
- `backend/docs/ASYNC_MIGRATION.md` - Documentação da migração async
- `STATUS_FINAL.md` - Status das melhorias implementadas

#### Developer Experience
- Makefiles para comandos comuns (backend, frontend)
- Docker Compose de produção
- Dockerfiles otimizados (multi-stage)
- `.dockerignore` para builds mais rápidos

### 🔧 Melhorado

- **API Documentation**: Exemplos e descrições melhoradas
- **Error Handling**: Tratamento centralizado de exceções
- **Code Quality**: Linting e formatação automatizada
- **Build Performance**: Docker builds otimizados

### 📝 Notas

- Backend agora é 100% assíncrono - melhor aproveitamento de recursos
- Todos os testes passando - qualidade garantida
- CI/CD configurado - integração contínua ativa
- Documentação completa e atualizada






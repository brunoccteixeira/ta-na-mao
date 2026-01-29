# Funcionalidades - App Android Tá na Mão

Este documento descreve as funcionalidades do app Android Tá na Mão, organizadas por fases de desenvolvimento.

## Visão Geral

O Tá na Mão Android é um app que permite aos cidadãos brasileiros:
- Visualizar dados de programas sociais em todo o Brasil
- Descobrir benefícios disponíveis em seu município
- Verificar elegibilidade para programas sociais
- Receber orientações personalizadas via assistente de IA

---

## Status de Implementação

| Feature | Status | Notas |
|---------|--------|-------|
| Tela Home | ✅ Implementado | KPIs, seletor de programas, quick actions |
| Tela de Busca | ✅ Implementado | Autocomplete funcional |
| Detalhes Município | ✅ Implementado | Cards de programas |
| Tela de Mapa | 🚧 Placeholder | Estrutura criada, visualização pendente |
| Assistente IA (Chat) | 🚧 Placeholder | Estrutura criada, integração LLM pendente |
| Ranking | 📋 Planejado | Não iniciado |
| Gráficos | 📋 Planejado | Vico adicionado, não integrado |
| Notificações Push | 📋 Planejado | Não iniciado |
| Modo Offline | 📋 Planejado | Room configurado, cache não implementado |
| Widget | 📋 Planejado | Não iniciado |
| Toggle de Tema | ✅ Implementado | Claro/Escuro/Sistema com persistência |
| Tela de Configurações | ✅ Implementado | Acesso via Perfil → Aparência |

**Legenda**: ✅ Implementado | 🚧 Em Desenvolvimento | 📋 Planejado

---

## Fase 1: MVP (Minimum Viable Product)

### 1.1 Tela Home

**Objetivo**: Apresentar visão geral dos programas sociais no Brasil.

**Status**: ✅ **IMPLEMENTADO**

**Funcionalidades**:
- [x] KPIs nacionais (cards com métricas principais)
  - População total
  - Famílias no CadÚnico
  - Total de beneficiários
  - Taxa de cobertura média
  - Gap de atendimento
- [ ] Seletor de programas (chips ou toggle buttons)
  - Bolsa Família / CadÚnico
  - BPC/LOAS
  - Farmácia Popular
  - TSEE
  - Dignidade Menstrual
- [ ] Quick actions (botões de acesso rápido)
  - Ver mapa
  - Buscar município
  - Falar com assistente

**Endpoint**: `GET /aggregations/national`

**Mockup**:
```
┌─────────────────────────────────────┐
│        TÁ NA MÃO                    │
├─────────────────────────────────────┤
│  [BF] [BPC] [Farm] [TSEE] [Dig]     │
├─────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐            │
│  │População│ │CadÚnico │            │
│  │  215M   │ │ 20.6M   │            │
│  └─────────┘ └─────────┘            │
│  ┌─────────┐ ┌─────────┐            │
│  │Benefic. │ │Cobertura│            │
│  │ 12.4M   │ │  42%    │            │
│  └─────────┘ └─────────┘            │
├─────────────────────────────────────┤
│  [🗺️ Mapa] [🔍 Buscar] [💬 Chat]   │
└─────────────────────────────────────┘
```

---

### 1.2 Tela de Mapa

**Objetivo**: Visualização geográfica da cobertura de programas sociais.

**Status**: 🚧 **PLACEHOLDER** - Estrutura criada, visualização do mapa pendente.

**Funcionalidades**:
- [ ] Mapa do Brasil com estados coloridos (choropleth)
- [ ] Seleção de métrica para coloração
  - Cobertura (%)
  - Beneficiários (número absoluto)
  - Gap (famílias não atendidas)
  - Valor (R$)
- [ ] Interação com estados
  - Tap: navega para municípios do estado
  - Long press: mostra tooltip com dados
- [ ] Zoom para nível municipal
  - Ao selecionar estado, carrega municípios
- [ ] Legenda dinâmica com escala de cores
- [ ] Botão de voltar (navegação hierárquica)

**Endpoints**:
- `GET /geo/states` - GeoJSON dos estados
- `GET /geo/municipalities?state_code=XX` - GeoJSON dos municípios

**Escala de Cores (Cobertura)**:
| Faixa | Cor | Significado |
|-------|-----|-------------|
| 80%+ | Verde escuro | Excelente |
| 60-79% | Verde claro | Bom |
| 40-59% | Amarelo | Regular |
| 20-39% | Laranja | Baixo |
| <20% | Vermelho | Crítico |

**Mockup**:
```
┌─────────────────────────────────────┐
│ ← Mapa       [Cobertura ▼]          │
├─────────────────────────────────────┤
│                                     │
│         ┌─────────────┐             │
│        /    Norte     \             │
│       /                \            │
│      │   ┌─────┐       │            │
│      │  / NE  /        │            │
│       \/     /──────────│           │
│        \    │  Sudeste │            │
│         \   │          │            │
│          \  └──┬───────┘            │
│           \    │ Sul               │
│            \───┘                    │
│                                     │
├─────────────────────────────────────┤
│ █ 80%+ █ 60% █ 40% █ 20% █ <20%    │
└─────────────────────────────────────┘
```

---

### 1.3 Tela de Busca

**Objetivo**: Permitir busca rápida de municípios.

**Status**: ✅ **IMPLEMENTADO**

**Funcionalidades**:
- [x] Campo de busca com autocomplete
  - Mínimo 2 caracteres
  - Debounce de 300ms
- [ ] Lista de resultados
  - Nome do município
  - Estado (sigla)
  - Código IBGE
  - População
- [ ] Tap no resultado navega para detalhes
- [ ] Histórico de buscas recentes (local)

**Endpoint**: `GET /municipalities/search?q=XXX`

**Mockup**:
```
┌─────────────────────────────────────┐
│ ← Buscar Município                  │
├─────────────────────────────────────┤
│  🔍 [Campinas                    ]  │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ Campinas - SP                   ││
│  │ IBGE: 3509502 | Pop: 1.2M       ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ Campina Grande - PB             ││
│  │ IBGE: 2504009 | Pop: 411k       ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ Campina Grande do Sul - PR      ││
│  │ IBGE: 4104204 | Pop: 45k        ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

### 1.4 Tela de Detalhes do Município

**Objetivo**: Mostrar dados detalhados de programas em um município.

**Status**: ✅ **IMPLEMENTADO**

**Funcionalidades**:
- [x] Header com informações básicas
  - Nome, estado, região
  - População
  - Código IBGE
- [ ] Lista de programas disponíveis
  - Card por programa com:
    - Nome do programa
    - Beneficiários
    - Famílias
    - Valor total (R$)
    - Taxa de cobertura (barra de progresso)
- [ ] Comparação com média estadual/nacional
- [ ] Data da última atualização

**Endpoint**: `GET /municipalities/{ibge_code}/programs`

**Mockup**:
```
┌─────────────────────────────────────┐
│ ← Campinas - SP                     │
│   Sudeste | Pop: 1.223.237          │
│   IBGE: 3509502                     │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ Farmácia Popular                ││
│  │ 45.678 beneficiários            ││
│  │ R$ 1.370.340,00                 ││
│  │ Cobertura: ████████░░ 51%       ││
│  │ Atualizado: Out/2025            ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ BPC/LOAS                        ││
│  │ 12.345 beneficiários            ││
│  │ R$ 16.049.700,00                ││
│  │ Cobertura: █████░░░░░ 14%       ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ TSEE                            ││
│  │ 89.456 beneficiários            ││
│  │ Cobertura: ██████████ 62%       ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

### 1.5 Ranking de Municípios

**Objetivo**: Mostrar os municípios com melhor/pior desempenho.

**Status**: 📋 **PLANEJADO** - Não iniciado. API backend disponível.

**Funcionalidades**:
- [ ] Toggle entre critérios de ordenação
  - Por cobertura (%)
  - Por número de beneficiários
- [ ] Filtro por estado (opcional)
- [ ] Lista com top 10/20 municípios
  - Posição (medalha para top 3)
  - Nome e estado
  - Métrica principal
- [ ] Tap para ver detalhes do município

**Endpoint**: `GET /programs/{code}/ranking`

**Mockup**:
```
┌─────────────────────────────────────┐
│ ← Ranking | Farmácia Popular        │
│   [Cobertura] [Beneficiários]       │
│   Estado: [Todos ▼]                 │
├─────────────────────────────────────┤
│  🥇 São Domingos do Cariri - PB     │
│     Cobertura: 89%                  │
│  ─────────────────────────────────  │
│  🥈 Cacimba de Dentro - PB          │
│     Cobertura: 87%                  │
│  ─────────────────────────────────  │
│  🥉 Juru - PB                       │
│     Cobertura: 85%                  │
│  ─────────────────────────────────  │
│  4. Várzea - PB                     │
│     Cobertura: 84%                  │
│  ─────────────────────────────────  │
│  5. Zabelê - PB                     │
│     Cobertura: 83%                  │
└─────────────────────────────────────┘
```

---

### 1.6 Configurações de Tema

**Objetivo**: Permitir ao usuário escolher o tema visual do app.

**Status**: ✅ **IMPLEMENTADO**

**Funcionalidades**:
- [x] Toggle entre 3 modos de tema:
  - Sistema (segue configuração do dispositivo)
  - Claro (sempre light mode)
  - Escuro (sempre dark mode)
- [x] Persistência com DataStore
- [x] Aplicação imediata sem reiniciar o app
- [x] Navegação: Perfil → Aparência → Tema do aplicativo

**Arquivos**:
- `data/preferences/ThemePreferences.kt` - Armazenamento com DataStore
- `presentation/ui/settings/SettingsViewModel.kt` - Gerenciamento de estado
- `presentation/ui/settings/SettingsScreen.kt` - Interface do usuário

**Mockup**:
```
┌─────────────────────────────────────┐
│ ← Configurações                     │
├─────────────────────────────────────┤
│                                     │
│  Aparência                          │
│  ┌─────────────────────────────────┐│
│  │         Tema                    ││
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ││
│  │  │Sistema│ │ Claro │ │Escuro │ ││
│  │  │  📱   │ │  ☀️   │ │  🌙   │ ││
│  │  └───────┘ └───────┘ └───────┘ ││
│  └─────────────────────────────────┘│
│                                     │
│  Sobre                              │
│  ┌─────────────────────────────────┐│
│  │ Versão: 1.0.0                   ││
│  │ Desenvolvido por: Tá na Mão     ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## Fase 2: Recursos Avançados

### 2.1 Assistente IA (Chatbot)

**Objetivo**: Ajudar cidadãos a descobrir benefícios elegíveis.

**Status**: 🚧 **PLACEHOLDER** - Tela criada, integração com LLM pendente. Veja [AGENTS.md](./AGENTS.md) para especificação técnica.

**Funcionalidades**:
- [ ] Interface de chat conversacional
- [ ] Fluxos de triagem:
  - Identificação de perfil (idade, renda, composição familiar)
  - Verificação de elegibilidade por programa
  - Orientação sobre documentos necessários
  - Localização de pontos de atendimento
- [ ] Respostas contextualizadas por município
- [ ] Histórico de conversas

**Integração**: OpenAI GPT-4 ou Anthropic Claude

**Fluxo de Triagem**:
```
1. "Olá! Sou o assistente Tá na Mão."
2. "Qual sua cidade?" → [Busca município]
3. "Qual sua faixa de renda familiar?"
   - Até R$ 218/pessoa
   - Entre R$ 218 e R$ 660/pessoa
   - Acima de R$ 660/pessoa
4. "Quantas pessoas moram na sua casa?"
5. "Há idosos (65+) ou pessoas com deficiência?"
6. → Apresenta programas elegíveis
7. → Orienta sobre documentos e onde solicitar
```

---

### 2.2 Gráficos de Tendência

**Objetivo**: Mostrar evolução histórica dos programas.

**Funcionalidades**:
- [ ] Gráfico de linha com série temporal
  - Beneficiários por mês
  - 12-120 meses de histórico
- [ ] Filtro por programa e estado
- [ ] Zoom e pan no gráfico
- [ ] Tooltip com valores exatos

**Endpoint**: `GET /aggregations/time-series`

---

### 2.3 Notificações Push

**Objetivo**: Manter usuários informados sobre atualizações.

**Funcionalidades**:
- [ ] Notificação de novos dados disponíveis
- [ ] Alertas de programas com inscrições abertas
- [ ] Lembretes de documentação
- [ ] Configurações de preferências

**Integração**: Firebase Cloud Messaging (FCM)

---

### 2.4 Comparativo Demográfico

**Objetivo**: Visualizar perfil das famílias cadastradas.

**Funcionalidades**:
- [ ] Gráfico de barras - Faixas de renda
  - Extrema pobreza
  - Pobreza
  - Baixa renda
- [ ] Gráfico de barras - Faixas etárias
  - 0-5 anos
  - 6-14 anos
  - 15-17 anos
  - 18-64 anos
  - 65+ anos
- [ ] Toggle entre visualizações

**Endpoint**: `GET /aggregations/demographics`

---

## Fase 3: Funcionalidades Premium

### 3.1 Modo Offline

**Objetivo**: Permitir uso sem conexão à internet.

**Funcionalidades**:
- [ ] Download de dados por estado
- [ ] Cache de GeoJSON simplificado
- [ ] Sincronização automática quando online
- [ ] Indicador de última atualização

**Implementação**:
- Room Database para cache local
- WorkManager para sync em background
- 50MB de armazenamento estimado por estado

---

### 3.2 Widget de Homescreen

**Objetivo**: Acesso rápido às informações do município.

**Funcionalidades**:
- [ ] Widget pequeno (2x2)
  - Município favorito
  - Taxa de cobertura
  - Número de beneficiários
- [ ] Widget grande (4x2)
  - Todos os programas
  - Mini gráfico de tendência
- [ ] Tap abre o app

**Implementação**: Glance (Jetpack Compose para Widgets)

---

### 3.3 Compartilhamento de Dados

**Objetivo**: Permitir exportar e compartilhar informações.

**Funcionalidades**:
- [ ] Exportar dados do município (JSON/CSV)
- [ ] Compartilhar card visual (imagem)
- [ ] Deep links para municípios específicos
- [ ] Integração com apps de mensagem

---

### 3.4 Localização Automática

**Objetivo**: Detectar município do usuário automaticamente.

**Funcionalidades**:
- [ ] Permissão de localização (opcional)
- [ ] Geocodificação reversa
- [ ] Sugestão de município mais próximo
- [ ] Definir município favorito

**Permissões**: `ACCESS_COARSE_LOCATION`

---

## Métricas de Sucesso

### KPIs do App

| Métrica | Meta | Medição |
|---------|------|---------|
| Downloads | 100k em 6 meses | Play Console |
| DAU | 10k | Analytics |
| Sessão média | 3 min | Analytics |
| Taxa de retenção D7 | 40% | Analytics |
| Crash-free rate | 99.5% | Crashlytics |
| ANR rate | <0.1% | Play Console |

### Métricas de Impacto

| Métrica | Descrição |
|---------|-----------|
| Consultas de elegibilidade | Usuários que completaram triagem |
| Municípios acessados | Diversidade geográfica |
| Programas visualizados | Engajamento por programa |
| Compartilhamentos | Viralidade |

---

## Roadmap de Desenvolvimento

```
Fase 1 (MVP) - 8 semanas
├── Semana 1-2: Setup projeto + Arquitetura
├── Semana 3-4: Tela Home + API Integration
├── Semana 5-6: Mapa + GeoJSON
├── Semana 7: Busca + Detalhes
└── Semana 8: Testes + Polish

Fase 2 - 6 semanas
├── Semana 9-10: Assistente IA
├── Semana 11-12: Gráficos + Time Series
├── Semana 13: Notificações Push
└── Semana 14: Demographics + Testes

Fase 3 - 4 semanas
├── Semana 15-16: Modo Offline
├── Semana 17: Widget + Compartilhamento
└── Semana 18: Localização + Polish Final
```

---

## Acessibilidade

O app deve seguir as diretrizes de acessibilidade Android:

- [ ] Content descriptions para elementos visuais
- [ ] Contraste mínimo de 4.5:1 para texto
- [ ] Tamanho de touch target mínimo de 48dp
- [ ] Suporte a TalkBack
- [ ] Suporte a fontes grandes do sistema
- [ ] Navegação por teclado/D-pad

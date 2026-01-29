# Arquitetura Modular - Tá na Mão

## Visão Geral da Plataforma

O Tá na Mão é organizado em módulos funcionais que cobrem diferentes aspectos dos direitos sociais do cidadão brasileiro.

```
┌─────────────────────────────────────────────────────────────┐
│                    TÁ NA MÃO - PLATAFORMA                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ MÓDULO 0    │  │ MÓDULO 1    │  │ MÓDULO 2            │  │
│  │ Documentação│  │ Dinheiro    │  │ Saúde               │  │
│  │ Zero        │  │ Esquecido   │  │                     │  │
│  │             │  │             │  │ • Farmácia Popular  │  │
│  │ • Certidão  │  │ • PIS/PASEP │  │ • Dignidade Menstr. │  │
│  │ • CPF       │  │ • SVR       │  │ • Vacinas           │  │
│  │ • RG        │  │ • FGTS      │  │ • Consultas         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ MÓDULO 3    │  │ MÓDULO 4    │  │ MÓDULO 5            │  │
│  │ Energia     │  │ Assistência │  │ Carteira            │  │
│  │             │  │ Social      │  │ de Direitos         │  │
│  │ • TSEE      │  │             │  │                     │  │
│  │ • Luz do    │  │ • CadÚnico  │  │ • Federal           │  │
│  │   Povo      │  │ • CRAS prep │  │ • Estadual          │  │
│  │             │  │ • BPC/LOAS  │  │ • Municipal         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MÓDULO 6: ÚLTIMA MILHA (Parceiros)                   │   │
│  │                                                      │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐     │   │
│  │  │ iFood  │ │ Rappi  │ │ RD     │ │ Lotéricas  │     │   │
│  │  │ Entrega│ │ Entrega│ │ Saúde  │ │ Saque      │     │   │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘     │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐     │   │
│  │  │ Pix    │ │ Caixa  │ │ CRAS   │ │ ONGs       │     │   │
│  │  │ Auto   │ │ Tem    │ │ Local  │ │ Voluntários│     │   │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  CANAIS: WhatsApp │ SMS │ 0800 │ Lotérica │ CRAS │ Web     │
└─────────────────────────────────────────────────────────────┘
```

## Módulos Detalhados

### Módulo 0: Documentação Zero (Pré-Jornada)

**Problema**: Aproximadamente 3 milhões de brasileiros não possuem documentação alguma.

**Objetivo**: Criar um fluxo para pessoas sem CPF, guiando-as até a obtenção de documentos básicos.

```
┌─────────────────────────────────────────────────────────────┐
│  JORNADA DOCUMENTAÇÃO ZERO                                  │
├─────────────────────────────────────────────────────────────┤
│  1. Identificação por nome + data nascimento + mãe         │
│  2. Busca de certidão de nascimento (cartórios)            │
│  3. Orientação para emissão de CPF                         │
│  4. Agendamento em mutirões de documentação                │
│  5. Acompanhamento até obtenção do CPF                     │
│  6. → Inicia jornada normal de benefícios                  │
└─────────────────────────────────────────────────────────────┘
```

**Tools disponíveis**:
- `identificar_cidadao` - Identificação por dados pessoais
- `buscar_mutirao` - Localiza mutirões de documentação
- `verificar_elegibilidade_sem_docs` - Verifica elegibilidade prévia
- `gerar_carta_encaminhamento` - Gera documento para CRAS

**Status**: ✅ Implementado (backend/app/agent/tools/)

---

### Módulo 1: Dinheiro Esquecido

**Objetivo**: Identificar e orientar sobre valores esquecidos que o cidadão pode resgatar.

**Programas cobertos**:

| Programa | Descrição | Valores Estimados |
|----------|-----------|-------------------|
| **PIS/PASEP** | Cotas do fundo para trabalhadores | R$ 23,4 bi disponíveis |
| **SVR** | Sistema de Valores a Receber (Banco Central) | R$ 8,6 bi |
| **FGTS** | Contas inativas/saque-aniversário | Variável |
| **Restituição IR** | Imposto de renda a restituir | Variável |

**Tools disponíveis**:
- `consultar_dinheiro_esquecido` - Consulta consolidada
- `verificar_pis_pasep` - Específico PIS/PASEP
- `verificar_svr` - Valores a Receber BCB
- `verificar_fgts` - Consulta FGTS

**Status**: ✅ Implementado

---

### Módulo 2: Saúde

**Objetivo**: Facilitar acesso a medicamentos gratuitos e programas de saúde.

**Subprogramas**:

#### 2.1 Farmácia Popular
- Medicamentos 100% gratuitos para hipertensão, diabetes, asma
- Desconto de até 90% em outros medicamentos

**Fluxo implementado**:
```
Receita → OCR → Identificar medicamentos → Buscar farmácia → Pedido/Orientação
```

#### 2.2 Dignidade Menstrual
- Absorventes gratuitos para pessoas cadastradas no CadÚnico
- Distribuição via UBS e escolas

#### 2.3 Vacinas e Consultas
- Orientação sobre campanhas de vacinação
- Agendamento de consultas no SUS

**Tools disponíveis**:
- `processar_receita` - OCR de receitas médicas
- `buscar_farmacia` - Farmácias próximas
- `buscar_medicamento` - Verifica disponibilidade
- `preparar_pedido` - Monta pedido para farmácia

**Status**: ✅ Implementado (fluxo completo Farmácia Popular)

---

### Módulo 3: Energia

**Objetivo**: Facilitar acesso a tarifas reduzidas de energia elétrica.

**Programas**:

| Programa | Benefício | Elegibilidade |
|----------|-----------|---------------|
| **TSEE** | Desconto de 10-65% na conta de luz | CadÚnico com renda até 1/2 SM |
| **Luz do Povo** | Isenção total para baixo consumo | Consumo < 30 kWh/mês |

**Fluxo**:
```
Verificar CadÚnico → Elegibilidade → Orientar cadastro na distribuidora
```

**Status**: 🔄 Parcialmente implementado (consulta TSEE)

---

### Módulo 4: Assistência Social

**Objetivo**: Centralizar acesso aos principais programas de transferência de renda e assistência.

**Programas**:

| Programa | Descrição | Valor |
|----------|-----------|-------|
| **Bolsa Família** | Transferência de renda | R$ 600 base + variáveis |
| **BPC/LOAS** | Idosos e PCDs sem renda | R$ 1.412 (salário mínimo) |
| **Auxílio-Gás** | Ajuda para gás de cozinha | R$ 102 a cada 2 meses |
| **CadÚnico** | Cadastro para todos os programas | Porta de entrada |

**Tools disponíveis**:
- `consultar_beneficio` - Consulta situação de benefícios
- `gerar_checklist` - Lista documentos necessários
- `buscar_cras` - CRAS mais próximo
- `pre_atendimento_cras` - Formulário pré-preenchido

**Status**: ✅ Implementado

---

### Módulo 5: Carteira de Direitos

**Objetivo**: Consolidar todos os direitos do cidadão em uma visualização única.

**Estrutura da Carteira**:

```
┌──────────────────────────────────────────────────────────────┐
│                    CARTEIRA DE DIREITOS                      │
├──────────────────────────────────────────────────────────────┤
│ CPF: ***.***.***-12          Nome: Maria Silva               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ DIREITOS FEDERAIS                                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ✅ Bolsa Família ............ R$ 600/mês               │ │
│  │ ✅ Farmácia Popular ......... Acesso garantido         │ │
│  │ ⚡ TSEE ..................... Não ativado (elegível)   │ │
│  │ 💰 PIS/PASEP ................ R$ 1.200 disponível      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ DIREITOS ESTADUAIS (SP)                                 │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ✅ Passe Livre .............. Ativo                    │ │
│  │ ⚡ Bom Prato ................ Elegível                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ DIREITOS MUNICIPAIS (São Paulo)                         │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ ✅ Bilhete Único ............ Ativo                    │ │
│  │ ⚡ Renda Cidadã ............. Verificar                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Níveis**:
- **Federal**: Programas do Governo Federal
- **Estadual**: Programas específicos de cada estado
- **Municipal**: Programas de cada município

**Status**: 🔄 Em desenvolvimento (interface Android disponível)

---

### Módulo 6: Última Milha (Parceiros)

**Problema**: Ativação de benefício ≠ Recebimento efetivo

**Objetivo**: Garantir que o cidadão receba fisicamente o que tem direito.

#### 6.1 Entrega de Medicamentos

| Parceiro | Cobertura | Tipo de Integração |
|----------|-----------|-------------------|
| **iFood** | 1.500 cidades | API (parceria 2025) |
| **Rappi** | 300 cidades | API existente |
| **RD Saúde** | Nacional (3.453 lojas) | API/WhatsApp |
| **Farmácias locais** | Capilaridade | WhatsApp Business |

**Fluxo**:
```
1. Ativar Farmácia Popular via Tá na Mão
2. Identificar farmácia credenciada mais próxima
3. Opções:
   a) Retirar na farmácia (mapa + direções)
   b) Delivery via iFood/Rappi
   c) Entrega solidária (voluntários/CRAS)
4. Tracking em tempo real
5. Confirmação de recebimento
```

#### 6.2 Saque de Dinheiro

| Canal | Pontos | Integração |
|-------|--------|------------|
| **Lotéricas** | 13.000 | Caixa Econômica |
| **Correspondentes** | 50.000+ | Múltiplos bancos |
| **Pix** | Universal | Instantâneo |
| **Caixa Tem** | ATMs | App + Código |

**Fluxo**:
```
1. Direito identificado (ex: PIS R$ 1.200)
2. Pergunta: "Como quer receber?"
   a) Pix para conta (CPF)
   b) Caixa Tem (código de saque)
   c) Lotérica (mapa + instruções)
3. Execução assistida
4. Confirmação
```

#### 6.3 Entrega de Absorventes

| Canal | Público | Método |
|-------|---------|--------|
| **UBS/Postos** | Geral | Retirada com CNS |
| **Escolas** | Estudantes | Distribuição direta |
| **CRAS** | CadÚnico | Agendamento |
| **Domiciliar** | Mobilidade reduzida | ONGs parceiras |

**Status**: 📋 Planejado (conceitual)

---

## Integrações Externas

### APIs Governamentais

| API | Uso | Status |
|-----|-----|--------|
| **Conecta GOV.BR** | CadÚnico, CPF, situação cadastral | Conceitual |
| **Banco Central** | SVR (Valores a Receber) | Conceitual |
| **INSS** | BPC, aposentadorias | Conceitual |
| **Caixa** | FGTS, PIS | Conceitual |

### MCP Servers Implementados

| MCP Server | Uso no Ta na Mao | Status | Wrapper |
|------------|------------------|--------|---------|
| **Brasil API MCP** | CEP, CNPJ, DDD, bancos, feriados | Implementado | `brasil_api.py` |
| **Google Maps MCP** | Geocoding, busca de locais, rotas | Implementado | `google_maps.py` |
| **PDF/OCR MCP** | OCR de receitas medicas | Implementado | `pdf_ocr.py` |
| **Twilio MCP** | SMS, WhatsApp, Voice | Configurado | - |
| **Redis MCP** | Cache e sessoes | Configurado | - |
| **ChromaDB MCP** | RAG de beneficios | Configurado | - |
| **Playwright MCP** | Automacao de portais Gov.br | Configurado | - |

### Configuracao MCP

Arquivo `.mcp.json` na raiz do projeto:

```json
{
  "mcpServers": {
    "brasil-api": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@mauricio-cantu/brasil-api-mcp"]
    },
    "google-maps": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-google-maps"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "${GOOGLE_MAPS_API_KEY}"
      }
    },
    "pdf-ocr": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-pdf"]
    }
  }
}
```

Para documentacao completa, ver `docs/MCP_SETUP.md`.

---

## Estrutura de Codigo

```
backend/app/
├── agent/
│   ├── mcp/               # Wrappers MCP (Model Context Protocol)
│   │   ├── __init__.py    # Exports e manager
│   │   ├── base.py        # Cliente MCP base
│   │   ├── brasil_api.py  # Wrapper Brasil API
│   │   ├── google_maps.py # Wrapper Google Maps
│   │   └── pdf_ocr.py     # Wrapper PDF/OCR
│   ├── channels/          # Handlers multicanal
│   │   ├── base.py        # Interface base
│   │   ├── sms_handler.py # Handler SMS
│   │   └── voice_handler.py # Handler Voz
│   ├── subagents/         # Sub-agentes especializados
│   │   ├── farmacia_agent.py
│   │   ├── beneficio_agent.py
│   │   └── documentacao_agent.py
│   ├── tools/             # Ferramentas disponiveis
│   │   ├── consultar_beneficio.py
│   │   ├── dinheiro_esquecido.py
│   │   ├── buscar_farmacia.py
│   │   └── ...
│   ├── orchestrator.py    # Orquestrador principal
│   └── context.py         # Contexto da conversa
├── routers/
│   ├── agent.py           # Endpoints WhatsApp/Web
│   ├── sms.py             # Endpoints SMS
│   ├── voice.py           # Endpoints Voz
│   └── webhook.py         # Webhooks gerais
└── models/
    └── ...
```

---

## Roadmap de Implementação

### Fase 1: Fundação Multicanal
- [x] WhatsApp via Twilio
- [x] Documentação Zero (tools)
- [ ] SMS básico
- [ ] 0800 com URA

### Fase 2: Expansão de Módulos
- [ ] Carteira de Direitos estadual
- [ ] Integração com APIs Gov.br
- [ ] Última Milha (parceiro piloto)

### Fase 3: Escala Nacional
- [ ] Terminais em lotéricas
- [ ] Tablets em CRAS
- [ ] API aberta para estados/municípios
- [ ] Múltiplos parceiros de entrega

---

## Métricas de Sucesso

| Métrica | Meta | Atual |
|---------|------|-------|
| Benefícios ativados | 100k/mês | N/A |
| Dinheiro resgatado | R$ 10M/mês | N/A |
| Medicamentos entregues | 50k/mês | N/A |
| NPS geral | > 70 | N/A |
| Tempo médio de resolução | < 5 min | N/A |

---

## Referencias

### Programas Sociais
- [Portal da Transparencia](https://portaldatransparencia.gov.br/)
- [Conecta GOV.BR](https://www.gov.br/conecta/)
- [Valores a Receber - BCB](https://valoresareceber.bcb.gov.br/)
- [Farmacia Popular](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/f/farmacia-popular)
- [CadUnico](https://www.gov.br/cidadania/pt-br/acoes-e-programas/cadastro-unico)

### MCP (Model Context Protocol)
- [MCP Setup Guide](./MCP_SETUP.md)
- [Twilio MCP](https://www.twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server)
- [Google Maps MCP](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- [Brasil API MCP](https://github.com/mauricio-cantu/brasil-api-mcp)
- [mcp-pdf](https://github.com/rsp2k/mcp-pdf)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

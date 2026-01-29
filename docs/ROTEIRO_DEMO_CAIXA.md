# Roteiro de Demonstracao - Ta na Mao
## Apresentacao para Equipe de TI da CAIXA

**Duracao:** 30-45 minutos
**Formato:** Demo ao vivo + discussao tecnica
**Publico:** Equipe de TI da CAIXA Economica Federal

---

## Agenda

| Tempo | Topico |
|-------|--------|
| 5 min | Contexto e problema |
| 20 min | Demo ao vivo (4 cenarios) |
| 10 min | Arquitetura tecnica |
| 10 min | Discussao e proximos passos |

---

## 1. Abertura (5 minutos)

### Slide 1: O Problema

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    2,7 MILHOES DE BRASILEIROS                                  │
│    nao tem NENHUM documento                                    │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │  Sem RG → Sem CPF → Sem CadUnico → Sem Bolsa Familia   │ │
│    │                                                         │ │
│    │  O CICLO DA EXCLUSAO                                    │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    Quem sao?                                                   │
│    • Pessoas em situacao de rua                                │
│    • Indigenas em areas remotas                                │
│    • Quilombolas                                               │
│    • Populacao rural isolada                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Fala:

> "A CAIXA esta em 100% dos municipios brasileiros e ja tem a biometria de 90% dos beneficiarios do Bolsa Familia. Mas existe uma ponta que ainda nao conseguimos alcancar: os que nao tem nem o primeiro documento. O Ta na Mao quer ajudar a CAIXA a chegar nessa populacao."

### Slide 2: O que o Ta na Mao faz

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    TA NA MAO: Facilitando o acesso a direitos sociais          │
│                                                                 │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│    │ CONSULTA │───▶│ ORIENTA  │───▶│ENCAMINHA │               │
│    │beneficios│    │documentos│    │ ao CRAS  │               │
│    └──────────┘    └──────────┘    └──────────┘               │
│                                                                 │
│    HOJE: Funciona com CPF                                      │
│    NOVO: Funciona MESMO SEM DOCUMENTOS                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Demo ao Vivo (20 minutos)

### Preparacao

**Antes da demo:**
- Backend rodando localmente ou em staging
- Frontend aberto no navegador
- Terminal pronto para mostrar logs (opcional)
- Dados de teste preparados

**Dica:** Ter um "plano B" com screenshots caso algo falhe.

---

### CENARIO 1: Cidadao COM CPF (Baseline)
**Tempo: 3 minutos**

> "Primeiro, vou mostrar como funciona hoje para quem TEM documentos."

**Acao no app:**
```
Usuario: "Quero saber se tenho direito ao Bolsa Familia"
Agente: "Claro! Me passa seu CPF que eu consulto pra voce."
Usuario: "123.456.789-00"
Agente: [Consulta base de beneficiarios]
        "Encontrei! Voce ja recebe Bolsa Familia, valor de R$ 600,00.
         Parcela de janeiro ja foi depositada."
```

**Ponto a destacar:**
> "Isso funciona porque temos os dados do Portal da Transparencia indexados por CPF. Mas e quem nao tem CPF?"

---

### CENARIO 2: Cidadao SEM CPF - Identificacao por NIS
**Tempo: 4 minutos**

> "Agora, uma pessoa que nao lembra o CPF mas tem o cartao do Bolsa Familia com o NIS."

**Acao no app:**
```
Usuario: "Quero ver meus beneficios mas nao sei meu CPF"
Agente: "Sem problema! Voce tem o cartao do Bolsa Familia ai?
         No cartao tem um numero chamado NIS, com 11 digitos."
Usuario: "Tenho sim, o numero e 12345678901"
Agente: [Consulta por NIS - NOVA FUNCIONALIDADE]
        "Encontrei pelo NIS! Maria da Silva, voce recebe:
         - Bolsa Familia: R$ 600,00
         - Auxilio Gas: R$ 104,00
         Quer que eu mostre os proximos passos?"
```

**Mostrar no codigo:**
```python
# backend/app/agent/tools/identificar_cidadao.py
def identificar_por_nis(nis: str) -> IdentificacaoResult:
    """Busca por NIS - alternativa ao CPF"""
    beneficiario = Beneficiario.buscar_por_nis(db, nis)
    # ...
```

**Ponto a destacar:**
> "O NIS ja existe nos dados que a CAIXA tem. Habilitamos como metodo alternativo de identificacao."

---

### CENARIO 3: Cidadao SEM NENHUM DOCUMENTO
**Tempo: 8 minutos** (cenario principal)

> "Agora o cenario mais importante: uma pessoa em situacao de rua, sem nenhum documento."

**Acao no app:**
```
Usuario: "Oi, eu quero saber se tenho direito a algum beneficio"
Agente: "Ola! Vou te ajudar. Voce tem CPF ou cartao do Bolsa Familia?"
Usuario: "Nao tenho nada, perdi tudo"
Agente: "Sem problema! Mesmo sem documentos eu posso te ajudar.
         Vou fazer algumas perguntas pra verificar se voce
         pode ter direito a beneficios. Pode ser?"
Usuario: "Pode sim"
```

**ETAPA 1: Questionario de Elegibilidade**
```
Agente: "Quantas pessoas moram com voce?"
Usuario: "So eu"

Agente: "Voce tem alguma renda por mes? Pode ser bico, esmola..."
Usuario: "Uns 200 reais de bico"

Agente: "Voce tem onde dormir fixo ou esta na rua?"
Usuario: "To na rua faz 3 meses"

Agente: "Voce tem algum documento? Certidao de nascimento,
         carteira de trabalho, titulo de eleitor..."
Usuario: "Acho que tenho certidao la na minha cidade natal"
```

**ETAPA 2: Resultado da Elegibilidade**
```
Agente: "Deixa eu te contar o que descobri:

         VOCE PODE TER DIREITO A:
         ✓ Bolsa Familia (estimado R$ 600/mes)
         ✓ Tarifa Social de Energia
         ✓ Farmacia Popular (medicamentos gratis)

         ATENCAO - VOCE ESTA EM SITUACAO DE RUA:
         O CRAS tem atendimento especial pra voce!
         Nao precisa de comprovante de endereco.

         SOBRE DOCUMENTOS:
         Voce disse que tem Certidao de Nascimento.
         Sabia que o CadUnico ACEITA certidao? Nao precisa de RG!

         Quer que eu gere uma carta pra voce levar ao CRAS?"
Usuario: "Quero sim!"
```

**Mostrar no codigo:**
```python
# backend/app/agent/tools/verificar_elegibilidade_sem_docs.py
def verificar_elegibilidade_sem_docs(
    qtd_pessoas_familia: int = 1,
    renda_total_familiar: float = 0,
    situacao_moradia: str = "rua",
    tem_certidao_nascimento: bool = True,
    # ...
) -> ElegibilidadeResult:
    """Verifica elegibilidade SEM exigir CPF"""

    faixa = calcular_faixa_renda(renda, pessoas)
    # R$ 200 / 1 pessoa = R$ 200 per capita
    # Isso e EXTREMA POBREZA (< R$ 105) ou POBREZA (< R$ 218)

    if faixa in [EXTREMA_POBREZA, POBREZA]:
        programas.append("BOLSA_FAMILIA")
    # ...
```

**ETAPA 3: Geracao da Carta de Encaminhamento**
```
Agente: "Pronto! Gerei sua Carta de Encaminhamento.

         [EXIBE CARTA COM:]
         - Seus dados (nome que voce informou)
         - Programas que pode ter direito
         - QR Code de validacao
         - Orientacoes para o CRAS

         Codigo de validacao: A1B2C3D4

         Voce pode:
         1. Mostrar essa tela no CRAS
         2. Tirar print e levar
         3. Pedir pra alguem imprimir

         Quer que eu encontre o CRAS mais perto de voce?"
```

**Mostrar a carta gerada (HTML):**

```
┌─────────────────────────────────────────────────────────────────┐
│           CARTA DE ENCAMINHAMENTO                               │
│           Sistema Ta na Mao                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CODIGO: A1B2C3D4                        [QR CODE]             │
│                                                                 │
│  ⚠️ PESSOA EM SITUACAO DE RUA - Atendimento prioritario        │
│                                                                 │
│  DADOS DO CIDADAO                                              │
│  Nome: Joao (informado pelo proprio)                           │
│  Situacao: Rua ha 3 meses                                      │
│  Renda: R$ 200,00                                              │
│                                                                 │
│  PROGRAMAS PARA VERIFICAR                                      │
│  ✓ Bolsa Familia (estimado R$ 600)                             │
│  ✓ Tarifa Social de Energia                                    │
│  ✓ Farmacia Popular                                            │
│                                                                 │
│  DOCUMENTOS QUE POSSUI                                         │
│  • Certidao de Nascimento (na cidade natal)                    │
│                                                                 │
│  ORIENTACOES                                                   │
│  1. CRAS pode aceitar Certidao como documento                  │
│  2. Nao precisa de comprovante de endereco                     │
│  3. Pergunte sobre mutiroes de documentacao                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Gerado em: 15/01/2025 | Valido por 30 dias                    │
└─────────────────────────────────────────────────────────────────┘
```

**Ponto a destacar:**
> "Essa carta nao da o beneficio - quem decide e o CRAS. Mas ela agiliza o atendimento porque os dados ja estao pre-preenchidos. E o mais importante: a pessoa SAI DAQUI SABENDO QUE PODE TER DIREITO e COM UM CAMINHO CLARO."

---

### CENARIO 4: Busca de Mutiroes de Documentacao
**Tempo: 3 minutos**

> "Alem de encaminhar ao CRAS, tambem conectamos aos mutiroes Registre-se! do CNJ."

**Acao no app:**
```
Usuario: "Como faco pra tirar meus documentos?"
Agente: "Boa pergunta! Existem mutiroes gratuitos de documentacao.
         Deixa eu ver o que tem perto de voce...

         Qual seu estado?"
Usuario: "Sao Paulo"
Agente: "Encontrei! Proximos mutiroes em SP:

         📅 MUTIRAO DE DOCUMENTACAO - SAO PAULO
         Data: 10 a 14 de fevereiro de 2025
         Locais:
         • Poupatempo Se (Praca da Se) - 7h as 19h
         • CRAS Republica (Rua do Arouche, 24) - 8h as 17h
         • Centro POP Luz - 8h as 17h

         Documentos emitidos:
         ✓ Certidao de Nascimento (1a e 2a via)
         ✓ RG / CIN
         ✓ CPF
         ✓ Cadastro no CadUnico

         NAO PRECISA DE NENHUM DOCUMENTO pra ir!
         A equipe ajuda a localizar seus registros.

         Quer que eu te lembre quando chegar perto da data?"
```

**Mostrar no codigo:**
```python
# backend/app/agent/tools/buscar_mutirao.py
def buscar_mutirao(uf: str = "SP") -> MutiraoResult:
    """Busca mutiroes de documentacao"""
    mutiroes = carregar_mutiroes()
    # Filtra por UF e data futura
    # ...
```

**Mostrar dados:**
```json
// backend/data/mutiroes_registrese.json
{
  "nome": "Mutirao de Documentacao - Sao Paulo Capital",
  "data_inicio": "2025-02-10",
  "locais": [
    {"nome": "Poupatempo Se", "endereco": "Praca da Se..."}
  ],
  "servicos": ["Certidao de Nascimento", "RG", "CPF", "CadUnico"]
}
```

**Ponto a destacar:**
> "Esses dados hoje sao manuais, mas podemos automatizar com scraping do site do CNJ. O importante e que conectamos a pessoa ao servico certo."

---

## 3. Arquitetura Tecnica (10 minutos)

### Slide: Visao Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA TA NA MAO                        │
└─────────────────────────────────────────────────────────────────┘

     CIDADAO
        │
        ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   FRONTEND    │     │   ANDROID     │     │   WHATSAPP    │
│  React + TS   │     │    Kotlin     │     │    Twilio     │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └──────────┬──────────┴──────────┬──────────┘
                   │                     │
                   ▼                     ▼
        ┌─────────────────────────────────────────┐
        │              BACKEND (FastAPI)          │
        │                                         │
        │  ┌─────────────────────────────────┐   │
        │  │     AGENTE IA (Gemini 2.0)      │   │
        │  │                                  │   │
        │  │  ┌───────────┐ ┌────────────┐   │   │
        │  │  │Orquestrador│ │Sub-agentes │   │   │
        │  │  └───────────┘ └────────────┘   │   │
        │  │                                  │   │
        │  │  TOOLS:                          │   │
        │  │  • identificar_cidadao          │   │ ◀── NOVO
        │  │  • verificar_elegibilidade      │   │ ◀── NOVO
        │  │  • gerar_carta_encaminhamento   │   │ ◀── NOVO
        │  │  • buscar_mutirao               │   │ ◀── NOVO
        │  │  • consultar_beneficio          │   │
        │  │  • buscar_cras                  │   │
        │  │  • buscar_farmacia              │   │
        │  └─────────────────────────────────┘   │
        │                                         │
        └─────────────────┬───────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ PostgreSQL│  │   Redis   │  │  APIs     │
    │ + PostGIS │  │  (Cache)  │  │ Externas  │
    └───────────┘  └───────────┘  └───────────┘
           │
           │ Dados indexados:
           │ • Portal Transparencia (BF, BPC)
           │ • CadUnico (via MiSocial)
           │ • Farmacias credenciadas
           │ • CRAS por municipio
           │ • Mutiroes Registre-se!
```

### Slide: Fluxo de Identificacao Multimodal

```
┌─────────────────────────────────────────────────────────────────┐
│              PIRAMIDE DE IDENTIFICACAO                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │    CPF      │ Confianca: ALTA
                    │  (11 dig)   │ Busca por hash SHA256
                    └──────┬──────┘
                           │ nao encontrou?
                           ▼
                    ┌─────────────┐
                    │    NIS      │ Confianca: ALTA
                    │  (11 dig)   │ Busca direta no banco
                    └──────┬──────┘
                           │ nao encontrou?
                           ▼
                    ┌─────────────┐
                    │   NOME +    │ Confianca: MEDIA
                    │  MUNICIPIO  │ Busca fuzzy + confirmacao
                    └──────┬──────┘
                           │ nao encontrou?
                           ▼
                    ┌─────────────┐
                    │QUESTIONARIO │ Confianca: BAIXA
                    │ELEGIBILIDADE│ Coleta dados, gera carta
                    └─────────────┘

    EM TODOS OS CASOS: O cidadao SAI com uma orientacao!
```

### Slide: Stack Tecnica

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| **Frontend Web** | React + TypeScript | Moderno, tipado, componentes reutilizaveis |
| **App Android** | Kotlin + Compose | Nativo, performatico, Material 3 |
| **Backend** | FastAPI (Python) | Async, rapido, OpenAPI nativo |
| **Agente IA** | Google Gemini 2.0 | Multimodal, function calling, portugues |
| **Banco** | PostgreSQL + PostGIS | Robusto, queries geograficas |
| **Cache** | Redis | Sessoes, rate limiting |
| **Infra** | Docker + AWS | Escalavel, seguro |

### Slide: Integracao com CAIXA (Proposta)

```
┌─────────────────────────────────────────────────────────────────┐
│                 INTEGRACAO PROPOSTA COM CAIXA                   │
└─────────────────────────────────────────────────────────────────┘

    TA NA MAO                              CAIXA
    ─────────                              ─────

┌───────────────┐                    ┌───────────────┐
│ Identificacao │───── VALIDAR ─────▶│   Base de     │
│  por NIS      │◀──── CPF+NIS ──────│  Biometria    │
└───────────────┘                    └───────────────┘
                                            │
┌───────────────┐                           │
│    Carta de   │                           │
│ Encaminhamento│                           ▼
└───────┬───────┘                    ┌───────────────┐
        │                            │   Sistema     │
        │                            │   IPD/IC      │
        │                            │    (MGI)      │
        ▼                            └───────────────┘
┌───────────────┐                           │
│     CRAS      │◀─── DADOS PRE-CADASTRO ───┘
│  Atendimento  │
└───────────────┘

BENEFICIOS DA INTEGRACAO:
• Validacao biometrica para evitar fraudes
• Dados pre-preenchidos no CadUnico
• Rastreabilidade fim-a-fim
• Busca ativa de vulneraveis
```

---

## 4. Discussao e Proximos Passos (10 minutos)

### Perguntas para a Equipe de TI

1. **Integracao de dados:**
   - Qual o melhor caminho para validar NIS em tempo real?
   - Podemos usar a base de biometria para verificacao?

2. **Seguranca:**
   - Quais requisitos de seguranca para integracao?
   - Como fazer autenticacao entre sistemas?

3. **Infraestrutura:**
   - Podemos hospedar na infra da CAIXA ou parceria AWS?
   - Qual o SLA esperado para integracao?

### Proposta de Piloto

| Item | Proposta |
|------|----------|
| **Local** | 3 CRAS em SP (Centro, Zona Sul, Zona Leste) |
| **Duracao** | 3 meses |
| **Meta** | 500 cidadaos sem documentos atendidos |
| **Equipe** | 2 devs Ta na Mao + apoio TI CAIXA |
| **Custo** | R$ 300.000 |

### Call to Action

> "O que precisamos da CAIXA para comecar:
> 1. **Acesso a sandbox** para testar integracao com dados de NIS
> 2. **Ponto focal tecnico** para alinhar APIs
> 3. **Validacao do piloto** em 3 CRAS
>
> Com isso, em 3 meses conseguimos mostrar resultados concretos
> de inclusao de pessoas que hoje estao invisiveis ao sistema."

---

## Anexo: Checklist Pre-Demo

### Ambiente
- [ ] Backend rodando (local ou staging)
- [ ] Frontend funcionando
- [ ] Dados de teste carregados
- [ ] Conexao de internet estavel

### Dados de Teste
- [ ] CPF valido com beneficios: `123.456.789-00`
- [ ] NIS valido: `12345678901`
- [ ] Cenario de pessoa sem docs preparado

### Backup
- [ ] Screenshots de cada tela
- [ ] Video gravado do fluxo completo
- [ ] Slides em PDF (caso projetor falhe)

### Materiais
- [ ] Documento da proposta de Introdutores (impresso)
- [ ] Cartoes de visita
- [ ] QR Code para o app (se tiver versao publica)

---

## Anexo: Respostas para Perguntas Frequentes

**P: "Isso nao vai gerar fraude?"**
> R: O sistema nao concede beneficios - apenas orienta e encaminha. Quem decide e o CRAS, com atendimento presencial. Alem disso, temos controles: codigo de validacao, rastreabilidade, limite de consultas.

**P: "Qual a diferenca pro app da CAIXA?"**
> R: O app da CAIXA e excelente pra quem JA TEM cadastro. O Ta na Mao foca em quem AINDA NAO CONSEGUE acessar - e o "pre-atendimento" que conecta ao sistema formal.

**P: "Voces guardam dados sensiveis?"**
> R: CPF e armazenado como hash SHA256 (nao reversivel). Dados de questionario sao temporarios e criptografados. Seguimos LGPD.

**P: "E se a pessoa mentir no questionario?"**
> R: A elegibilidade final e verificada pelo CRAS presencialmente. O questionario e apenas uma triagem inicial para orientacao.

**P: "Como escala isso?"**
> R: A arquitetura e serverless-ready. O agente IA (Gemini) escala automaticamente. O gargalo e humano (atendimento no CRAS), nao tecnologico.

---

## Contato

**Equipe Ta na Mao**
- Email: [seu email]
- WhatsApp: [seu numero]
- GitHub: [link do repo]

*"Facilitando o acesso a direitos sociais para todos os brasileiros"*

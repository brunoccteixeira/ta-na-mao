# Proposta: Sistema de Introdutores para Inclusao de Cidadaos Sem Documentacao

**Documento para discussao com MDS e CAIXA Economica Federal**

**Versao:** 1.0
**Data:** Janeiro 2025
**Autor:** Equipe Ta na Mao

---

## Sumario Executivo

Esta proposta apresenta um **Sistema de Introdutores** para o Ta na Mao, inspirado no modelo bem-sucedido do Aadhaar (India) e nas recomendacoes do Banco Mundial (ID4D). O objetivo e criar um mecanismo seguro para identificar e incluir cidadaos brasileiros em extrema vulnerabilidade que nao possuem documentacao basica.

### O Problema

- **2,7 milhoes de brasileiros** nao possuem nenhum documento de identificacao (Censo 2022)
- Maioria sao pessoas em situacao de rua, indigenas, quilombolas, populacao rural remota
- Sem documentos → sem CadUnico → sem acesso a Bolsa Familia, BPC, Farmacia Popular
- O ciclo de exclusao se perpetua: sem documento, nao acessa beneficio; sem beneficio, nao consegue se estabilizar para tirar documento

### A Solucao Proposta

Um sistema onde **agentes de confianca** (introdutores) podem atestar a identidade de cidadaos sem documentos, permitindo:
1. Consulta de elegibilidade a beneficios
2. Pre-cadastro para encaminhamento ao CRAS
3. Priorizacao em mutiroes de documentacao
4. Acesso a servicos basicos enquanto regulariza situacao

---

## 1. Contexto e Fundamentacao

### 1.1 Case Internacional: Aadhaar (India)

O sistema Aadhaar da India enfrentou desafio similar: como cadastrar 1,3 bilhao de pessoas, muitas sem qualquer documento previo?

**Solucao adotada:** Sistema de Introdutores

> "Recognizing the difficulty that many already-marginalized individuals face when asked to provide Proof of Identity (POI) and Proof of Address (POA), the Unique Identification Authority of India has developed the Introducer system."
> — Reach Alliance, 2023

**Como funciona no Aadhaar:**
- Introdutores sao pessoas autorizadas (funcionarios publicos, lideres comunitarios, diretores de escola, representantes de ONGs)
- O introdutor atesta ("vouches for") a identidade de quem nao tem documentos
- A pessoa e cadastrada com base na biometria + atestado do introdutor
- Sistema ja cadastrou mais de 1,3 bilhao de pessoas

**Resultados:**
- 99,9% da populacao adulta da India tem Aadhaar
- Reducao de 47% em fraudes em programas sociais
- Economia de US$ 33 bilhoes em vazamentos

### 1.2 Recomendacoes do Banco Mundial (ID4D)

O programa ID4D (Identification for Development) do Banco Mundial recomenda:

1. **Desacoplar identidade de nacionalidade**: A identificacao deve ser universal, independente de status migratório ou documental
2. **Identificacao progressiva**: Comecar com o que a pessoa tem, ir construindo o perfil
3. **Multiplos pontos de entrada**: Nao depender de um unico documento
4. **Vouching/Atestado**: Permitir que terceiros de confianca atestem identidade

> "Legal and digital IDs are key to inclusion—unlocking access to healthcare, education, finance, and social protection."
> — World Bank ID4D, 2024

### 1.3 Contexto Brasileiro

**Iniciativas existentes:**
- **Decreto de Biometria (jul/2025)**: CAIXA ja tem biometria de 90% dos beneficiarios do Bolsa Familia
- **IPD/IC**: Infraestrutura Publica Digital de Identificacao Civil do MGI
- **CIN**: Carteira de Identidade Nacional unificada
- **Mutiroes Registre-se!**: CNJ emitiu 60 mil certidoes em 2024

**Gap identificado:**
- Nenhuma dessas iniciativas resolve o problema de quem **nao tem nenhum documento** para comecar
- O sistema de introducao preencheria esse gap

---

## 2. Proposta Detalhada

### 2.1 Definicao de Introdutor

**Introdutor** e uma pessoa fisica ou juridica, previamente cadastrada e autorizada, que pode atestar a identidade de um cidadao sem documentacao.

### 2.2 Quem Pode Ser Introdutor

| Categoria | Exemplos | Justificativa |
|-----------|----------|---------------|
| **Agentes Publicos** | Assistentes sociais do CRAS, agentes de saude da familia, educadores sociais | Ja tem relacao de confianca com populacao vulneravel |
| **Lideres Comunitarios** | Presidentes de associacoes de moradores, lideres de comunidades tradicionais | Conhecem pessoalmente os moradores |
| **Representantes de ONGs** | Coordenadores de abrigos, organizacoes de apoio a populacao de rua | Trabalham diretamente com os mais vulneraveis |
| **Servidores de Instituicoes** | Diretores de escolas, responsaveis por abrigos publicos | Tem registros institucionais das pessoas |
| **Agentes Religiosos** | Padres, pastores, lideres religiosos cadastrados | Historico de atuacao social, conhecem a comunidade |

### 2.3 Requisitos para Ser Introdutor

1. **Pessoa Fisica:**
   - CPF valido
   - Sem pendencias criminais graves
   - Vinculo comprovado com instituicao (publica, ONG, religiosa)
   - Capacitacao basica (online, 2 horas)

2. **Pessoa Juridica (Instituicao):**
   - CNPJ ativo
   - Atuacao comprovada em assistencia social
   - Termo de responsabilidade assinado
   - Representante legal identificado

### 2.4 Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUXO DO SISTEMA DE INTRODUTORES                  │
└─────────────────────────────────────────────────────────────────────┘

1. CADASTRO DO INTRODUTOR
   ┌─────────────────┐
   │  Instituicao    │──▶ Solicita cadastro como introdutor
   │  ou Agente      │    (formulario online + documentos)
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Validacao      │──▶ MDS/CAIXA valida instituicao
   │  (MDS/CAIXA)    │    e representante legal
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Capacitacao    │──▶ Curso online obrigatorio (2h)
   │  Online         │    sobre responsabilidades e uso
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Credencial     │──▶ Recebe acesso ao sistema
   │  Digital        │    com limite de introducoes/mes
   └─────────────────┘


2. INTRODUCAO DE CIDADAO
   ┌─────────────────┐
   │  Cidadao sem    │──▶ Procura introdutor (CRAS, ONG, etc)
   │  Documentos     │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Introdutor     │──▶ Coleta dados basicos:
   │  Coleta Dados   │    - Nome completo
   │                 │    - Data nascimento (aprox)
   │                 │    - Local nascimento
   │                 │    - Foto
   │                 │    - Biometria (se disponivel)
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Introdutor     │──▶ "Atesto que conheco esta pessoa
   │  Atesta         │    e que as informacoes sao verdadeiras"
   │                 │    + Assinatura digital
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  Sistema Gera   │──▶ ID Temporario (valido 90 dias)
   │  ID Temporario  │    Vinculado ao introdutor
   └─────────────────┘


3. USO DO ID TEMPORARIO
   ┌─────────────────┐
   │  Cidadao usa    │──▶ Pode:
   │  ID Temporario  │    - Consultar elegibilidade
   │                 │    - Gerar carta encaminhamento
   │                 │    - Prioridade em mutiroes
   │                 │    - Pre-cadastro no CadUnico
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  CRAS Valida    │──▶ Atendimento presencial
   │  e Regulariza   │    Emissao de documentos
   │                 │    Cadastro definitivo
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │  ID Temporario  │──▶ Vinculado ao CPF definitivo
   │  Convertido     │    Historico preservado
   └─────────────────┘
```

### 2.5 Controles e Seguranca

**Prevencao de Fraudes:**

| Controle | Descricao |
|----------|-----------|
| **Limite de Introducoes** | Cada introdutor pode fazer ate X introducoes/mes |
| **Auditoria Cruzada** | Sistema detecta mesma pessoa introduzida por diferentes introdutores |
| **Verificacao Biometrica** | Se disponivel, compara com bases existentes (TSE, CAIXA) |
| **Rastreabilidade** | Toda introducao fica vinculada ao introdutor (responsabilidade) |
| **Validade Limitada** | ID temporario expira em 90 dias se nao regularizado |
| **Score do Introdutor** | Introducoes que viram cadastros validos aumentam score; fraudes reduzem |

**Responsabilidades do Introdutor:**

- Responde civil e criminalmente por atestados falsos
- Pode ter credencial suspensa ou revogada
- Deve manter registros de quem introduziu

### 2.6 Integracao com Sistemas Existentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA DE INTEGRACAO                     │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   TA NA MAO     │
                    │   (Frontend)    │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                      API INTRODUTORES                               │
│  - Cadastro de introdutores                                        │
│  - Registro de introducoes                                         │
│  - Geracao de ID temporario                                        │
│  - Consulta de status                                              │
└────────────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   CADUNICO  │    │    CAIXA    │    │     TSE     │
   │   (MDS)     │    │  Biometria  │    │  Biometria  │
   └─────────────┘    └─────────────┘    └─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   IPD/IC (MGI)  │
                    │   Base Unificada│
                    └─────────────────┘
```

---

## 3. Aspectos Legais

### 3.1 Fundamentacao Juridica

**Constituicao Federal:**
- Art. 1o, III: Dignidade da pessoa humana
- Art. 3o, III: Erradicar a pobreza e reduzir desigualdades
- Art. 6o: Direito a assistencia aos desamparados

**Legislacao Infraconstitucional:**
- Lei 8.742/1993 (LOAS): Assistencia social como direito
- Decreto 6.135/2007 (CadUnico): Cadastro para programas sociais
- Lei 13.709/2018 (LGPD): Tratamento de dados pessoais

### 3.2 Adequacao a LGPD

| Principio LGPD | Aplicacao no Sistema |
|----------------|---------------------|
| **Finalidade** | Dados usados exclusivamente para inclusao em programas sociais |
| **Necessidade** | Coleta minima: nome, nascimento, foto, local |
| **Transparencia** | Cidadao informado sobre uso dos dados |
| **Seguranca** | Dados criptografados, acesso controlado |
| **Nao Discriminacao** | Sistema projetado para incluir, nao excluir |

### 3.3 Instrumento Juridico Necessario

Sugerimos a criacao de:

1. **Portaria Conjunta MDS/MGI/CAIXA** regulamentando:
   - Requisitos para introdutores
   - Validade do ID temporario
   - Responsabilidades e penalidades
   - Integracao com CadUnico

2. **Termo de Adesao** para introdutores com:
   - Responsabilidades civis e criminais
   - Autorizacao de auditoria
   - Compromisso de capacitacao

---

## 4. Implementacao

### 4.1 Fases

| Fase | Descricao | Prazo | Responsavel |
|------|-----------|-------|-------------|
| **1. Piloto** | Teste em 3 CRAS de SP/RJ com 50 introdutores | 3 meses | Ta na Mao + CRAS |
| **2. Validacao** | Avaliacao de resultados, ajustes | 1 mes | MDS/CAIXA |
| **3. Expansao** | Ampliacao para capitais | 6 meses | MDS |
| **4. Escala** | Disponibilizacao nacional | 12 meses | MDS/CAIXA/MGI |

### 4.2 Metricas de Sucesso

| Metrica | Meta Piloto | Meta Escala |
|---------|-------------|-------------|
| Cidadaos introduzidos | 500 | 50.000/ano |
| Taxa de conversao (ID temp → CPF) | 70% | 80% |
| Tempo medio de regularizacao | 30 dias | 15 dias |
| Fraudes detectadas | <1% | <0,5% |
| Satisfacao dos introdutores | >80% | >90% |

### 4.3 Orcamento Estimado (Piloto)

| Item | Custo |
|------|-------|
| Desenvolvimento de software | R$ 150.000 |
| Capacitacao de introdutores (50) | R$ 25.000 |
| Equipamentos (tablets para CRAS) | R$ 50.000 |
| Operacao (3 meses) | R$ 75.000 |
| **Total Piloto** | **R$ 300.000** |

---

## 5. Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Fraude por introdutores | Media | Alto | Limites, auditoria, score, responsabilizacao |
| Baixa adesao de CRAS | Media | Medio | Capacitacao, incentivos, suporte tecnico |
| Resistencia legal | Baixa | Alto | Parecer juridico previo, portaria conjunta |
| Problemas de integracao | Media | Medio | APIs padronizadas, testes extensivos |
| Uso indevido de dados | Baixa | Alto | Criptografia, auditoria, LGPD compliance |

---

## 6. Proximos Passos

1. **Imediato:** Apresentar proposta ao MDS e CAIXA
2. **30 dias:** Obter parecer juridico sobre viabilidade
3. **60 dias:** Definir CRAS para piloto
4. **90 dias:** Iniciar desenvolvimento e capacitacao
5. **120 dias:** Lancar piloto

---

## 7. Conclusao

O Sistema de Introdutores representa uma oportunidade unica de:

- **Incluir 2,7 milhoes de brasileiros** hoje invisiveis ao Estado
- **Aplicar modelo comprovado** internacionalmente (Aadhaar)
- **Complementar iniciativas existentes** (IPD/IC, CIN, Registre-se!)
- **Posicionar o Brasil** como referencia em inclusao digital

A proposta esta alinhada com:
- Agenda 2030 da ONU (ODS 16.9: Identidade legal para todos)
- Recomendacoes do Banco Mundial (ID4D)
- Compromissos do governo brasileiro com erradicacao da pobreza

**Solicitamos reuniao para apresentacao detalhada e discussao dos proximos passos.**

---

## Referencias

1. World Bank. "ID4D - Identification for Development". https://id4d.worldbank.org/
2. Reach Alliance. "Aadhaar: Providing Proof of Identity to a Billion". 2023.
3. UIDAI. "Aadhaar Enrolment Guide". https://uidai.gov.in/
4. CNJ. "Programa Registre-se!". https://www.cnj.jus.br/programas-e-acoes/registre-se/
5. IBGE. Censo 2022 - Pessoas sem documentacao.
6. Agencia Brasil. "Biometria passa a ser obrigatoria para beneficios sociais". Jul/2025.

---

## Anexos

### Anexo A: Modelo de Termo de Adesao do Introdutor

```
TERMO DE ADESAO AO SISTEMA DE INTRODUTORES
Programa Ta na Mao

Eu, [NOME COMPLETO], CPF [XXX.XXX.XXX-XX], representante da
instituicao [NOME DA INSTITUICAO], CNPJ [XX.XXX.XXX/XXXX-XX],
declaro que:

1. Li e compreendi as responsabilidades do introdutor
2. Comprometo-me a atestar apenas pessoas que conheco pessoalmente
3. Estou ciente da responsabilidade civil e criminal por atestados falsos
4. Autorizo auditoria dos registros de introducao
5. Concluirei a capacitacao obrigatoria em 30 dias

Data: ___/___/______
Assinatura: _______________________
```

### Anexo B: Fluxo de Telas do Sistema (Wireframes)

[Wireframes a serem desenvolvidos apos aprovacao da proposta]

### Anexo C: Perguntas Frequentes

**P: O ID temporario da direito a beneficios?**
R: Nao diretamente. Ele permite consultar elegibilidade e agiliza o cadastro no CadUnico, mas o beneficio so e concedido apos regularizacao documental.

**P: E se o introdutor mentir?**
R: O introdutor responde civil e criminalmente. Alem disso, o sistema rastreia todas as introducoes e aplica auditoria cruzada. Introducoes fraudulentas resultam em revogacao da credencial e possivel processo.

**P: Como garantir que a pessoa nao esta sendo cadastrada duas vezes?**
R: O sistema usa verificacao biometrica (quando disponivel) e cruzamento de dados (nome + data nascimento + local). Casos suspeitos sao sinalizados para verificacao manual.

**P: O sistema substitui o CadUnico?**
R: Nao. E um "pre-CadUnico" que facilita a inclusao de quem hoje nao consegue nem chegar ao CRAS. O objetivo final e sempre o cadastro oficial.

# Fontes de Dados Oficiais

Este documento descreve as fontes de dados utilizadas pelo sistema Tá na Mão.

## Resumo

| Programa | Fonte | URL | Formato | Atualização |
|----------|-------|-----|---------|-------------|
| **CadÚnico** | API MiSocial (MDS) | aplicacoes.mds.gov.br/sagi/servicos/misocial | JSON/SOLR | Mensal |
| Bolsa Família | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| BPC/LOAS | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| Farmácia Popular | OpenDataSUS | opendatasus.saude.gov.br | CSV/ZIP | Mensal |
| TSEE | ANEEL | dadosabertos.aneel.gov.br | CSV | Mensal |
| Dignidade Menstrual | OpenDataSUS | opendatasus.saude.gov.br | CSV/ZIP | Mensal |
| **Auxílio Gás** | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Bimestral |
| **Seguro Defeso** | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| **Auxílio Inclusão** | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| **Garantia-Safra** | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Anual (safra) |

---

## 1. Bolsa Família (Novo Bolsa Família)

### Descrição
Principal programa de transferência de renda do Brasil, atendendo famílias em situação de pobreza e extrema pobreza.

**Nota**: O Bolsa Família agora é tratado como programa social separado. Os dados do CadÚnico são obtidos diretamente via API MiSocial (ver seção 6).

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2023 até atual

### Estrutura do CSV
```
MÊS REFERÊNCIA, MÊS COMPETÊNCIA, UF, CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO, CPF FAVORECIDO, NIS FAVORECIDO, NOME FAVORECIDO, VALOR PARCELA
```

### Mapeamento SIAFI → IBGE
O Portal usa códigos SIAFI (4 dígitos) que são convertidos para IBGE (7 dígitos) usando o arquivo `data/siafi_ibge_mapping.csv`.

### Verificação de Consistência
- **Dados oficiais (MDS)**: ~21 milhões de famílias beneficiárias
- **Nossa ingestão**: 20.658.029 famílias (Out/2024)
- **Cobertura média**: 47,73% das famílias do CadÚnico
- **Status**: ✅ Consistente

### Relação com CadÚnico
O Bolsa Família é um programa social que atende famílias cadastradas no CadÚnico:
- 100% dos beneficiários estão no CadÚnico
- Cobertura = famílias BF / famílias CadÚnico
- Os dados do CadÚnico são obtidos separadamente via API MiSocial

---

## 2. BPC/LOAS - Benefício de Prestação Continuada

### Descrição
Benefício assistencial de um salário mínimo mensal para idosos (65+) e pessoas com deficiência de baixa renda.

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/bpc

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2019 até atual

### Estrutura do CSV
```
CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO, UF, VALOR PARCELA, ...
```

### Mapeamento SIAFI → IBGE
O Portal usa códigos SIAFI (4 dígitos) que são convertidos para IBGE (7 dígitos) usando o arquivo `data/siafi_ibge_mapping.csv`.

### Verificação de Consistência
- **Dados oficiais**: ~6 milhões de beneficiários
- **Nossa ingestão**: 6.231.589 beneficiários (Out/2024)
- **Status**: ✅ Consistente

---

## 3. Farmácia Popular do Brasil

### Descrição
Programa que oferece medicamentos gratuitos ou com desconto através de farmácias credenciadas.

### Fonte
- **OpenDataSUS** - Ministério da Saúde
- URL: https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil

### Dados Disponíveis
- `pfpbben.csv.zip` - Total de pessoas atendidas
- `pfpbdm.csv.zip` - Absorventes (Dignidade Menstrual)
- `sntpbh.csv.zip` - Medicamentos para hipertensão
- `sntpbd.csv.zip` - Medicamentos para diabetes
- Períodos: **2016-2025 (10 anos de histórico)**

### Estrutura do CSV
```csv
co_anomes,co_ibge,vl_indicador_calculado_mun,no_municipio,sg_uf,...
202510,120030,1268.0,"Cruzeiro Do Sul","AC",...
```

### URLs Diretas
```
https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbben.csv.zip
https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbdm.csv.zip
```

### Verificação de Consistência
- **Dados oficiais**: 24,7 milhões/ano (~12M/mês)
- **Nossa ingestão**: 12.430.549 beneficiários (Out/2025)
- **Status**: ✅ Consistente

### Série Histórica Disponível
```
2016: 10.023.278 beneficiários
2017:  9.806.655 (-2.2%)
2018:  9.242.546 (-5.8%)
2019:  9.646.071 (+4.4%)
2020:  8.000.619 (-17.1%)  ← Pandemia
2021:  8.416.862 (+5.2%)
2022:  8.413.782 (-0.0%)
2023:  9.308.163 (+10.6%)
2024: 10.359.016 (+11.3%)
2025: 12.430.549 (+20.0%)  ← Recorde
```

---

## 4. TSEE - Tarifa Social de Energia Elétrica

### Descrição
Desconto na conta de energia elétrica para famílias de baixa renda.

### Fonte
- **ANEEL** - Agência Nacional de Energia Elétrica
- URL: https://dadosabertos.aneel.gov.br/

### Dados Disponíveis
- Beneficiários por distribuidora/estado
- Consumo (MWh)
- Valor do subsídio
- Categorias: baixa renda, indígena, quilombola, BPC

### URL Direta
```
https://dadosabertos.aneel.gov.br/dataset/942de3e1-0b52-4e41-a6c1-eff9f3b7c7d6/resource/87764789-84c3-4592-a845-cb2b317f6142/download/sistema-controle-subvencoes-programas-sociais.csv
```

### Verificação de Consistência
- **Dados oficiais**: ~14 milhões de beneficiários
- **Nossa ingestão**: 14.328.607 beneficiários
- **Status**: ✅ Consistente

---

## 5. Dignidade Menstrual

### Descrição
Distribuição gratuita de absorventes higiênicos através do Farmácia Popular.

### Fonte
- **OpenDataSUS** - Ministério da Saúde
- Mesma fonte do Farmácia Popular

### Dados Disponíveis
- Pessoas atendidas por município
- Períodos: 2024-2025

### URL Direta
```
https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbdm.csv.zip
```

### Verificação de Consistência
- **Dados oficiais**: 2,5 milhões acumulado (357k/mês)
- **Nossa ingestão**: 357.730 beneficiários (Out/2025)
- **Status**: ✅ Consistente

### Nota
Os dados mensais (~358k) são menores que o acumulado oficial (2,5M) porque representam atendimentos únicos naquele mês, não o total histórico.

---

## Auxílio Gás dos Brasileiros ⭐ NOVO

### Descrição
Auxílio financeiro para compra de botijão de gás de cozinha (GLP) para famílias de baixa renda inscritas no CadÚnico. Pago bimestralmente.

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/auxilio-gas

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2022 até atual

### Estrutura do CSV
```
MÊS REFERÊNCIA, UF, CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO, NIS FAVORECIDO, NOME FAVORECIDO, VALOR PARCELA
```

### Mapeamento SIAFI → IBGE
O Portal usa códigos SIAFI que são convertidos para IBGE usando o arquivo `data/siafi_ibge_mapping.csv`.

### Verificação de Consistência
- **Dados oficiais (MDS)**: ~5,8 milhões de famílias beneficiárias
- **Frequência**: Pagamento BIMESTRAL
- **Script**: `ingest_auxilio_gas.py`
- **Status**: ✅ Implementado

### Elegibilidade
- Famílias inscritas no CadÚnico com renda per capita até R$ 218
- Beneficiários do Bolsa Família
- Beneficiários do BPC

---

## Seguro Defeso ⭐ NOVO

### Descrição
Benefício de um salário mínimo mensal para pescadores artesanais durante o período de defeso (reprodução das espécies aquáticas). O período varia conforme a espécie e região.

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/seguro-defeso

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2019 até atual

### Estrutura do CSV
```
MÊS REFERÊNCIA, UF, CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO, NIS FAVORECIDO, NOME FAVORECIDO, VALOR PARCELA
```

### Mapeamento SIAFI → IBGE
O Portal usa códigos SIAFI que são convertidos para IBGE usando o arquivo `data/siafi_ibge_mapping.csv`.

### Verificação de Consistência
- **Dados oficiais**: ~400-600 mil pescadores beneficiários/mês
- **Frequência**: Mensal (durante período de defeso)
- **Script**: `ingest_seguro_defeso.py`
- **Status**: ✅ Implementado

### Nota
Os dados variam significativamente por mês e região, pois dependem do calendário de defeso de cada espécie aquática. Municípios costeiros e ribeirinhos têm maior concentração de beneficiários.

---

## Auxílio Inclusão ⭐ NOVO

### Descrição
Benefício para pessoas com deficiência beneficiárias do BPC que ingressam no mercado de trabalho formal. Substitui o BPC, permitindo que a pessoa trabalhe sem perder totalmente o benefício. Valor: meio salário mínimo.

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/auxilio-inclusao

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2022 até atual

### Estrutura do CSV
```
MÊS REFERÊNCIA, UF, CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO, NIS FAVORECIDO, NOME FAVORECIDO, VALOR PARCELA
```

### Mapeamento SIAFI → IBGE
O Portal usa códigos SIAFI que são convertidos para IBGE usando o arquivo `data/siafi_ibge_mapping.csv`.

### Verificação de Consistência
- **Dados oficiais**: ~45 mil beneficiários
- **Frequência**: Mensal
- **Script**: `ingest_auxilio_inclusao.py`
- **Status**: ✅ Implementado

### Elegibilidade
- Beneficiário do BPC (pessoa com deficiência)
- Que aceite emprego formal (CLT)
- Benefício é de meio salário mínimo (complementar ao salário)
- Se perder o emprego, pode retornar ao BPC integral

### Nota
O Auxílio Inclusão é um programa ainda pequeno, mas importante para incentivar a inclusão de pessoas com deficiência no mercado de trabalho formal.

---

## Garantia-Safra ⭐ NOVO

### Descrição
Benefício de R$ 1.200 para agricultores familiares do semiárido que perdem safra por seca ou excesso de chuvas.

### Fonte
- **Portal da Transparência** - Controladoria-Geral da União (CGU)
- URL: https://portaldatransparencia.gov.br/download-de-dados/garantia-safra

### Dados Disponíveis
- Beneficiários por município (código SIAFI)
- Valor das parcelas
- Períodos: 2019 até atual

### Verificação de Consistência
- **Dados oficiais (MDA)**: ~560 mil agricultores em 744 municípios
- **Frequência**: Pagamentos de janeiro a junho
- **Script**: `ingest_garantia_safra.py`
- **Status**: ✅ Implementado

### Elegibilidade
- Agricultor familiar no semiárido (área da SUDENE)
- Área cultivada de 0,6 a 5 hectares
- Cultivo de feijão, milho, arroz, algodão ou mandioca
- Renda familiar mensal de até 1,5 salário mínimo
- Município aderiu ao programa

### Nota
O Garantia-Safra é pago quando há perda de pelo menos 50% da safra por seca ou excesso hídrico. Os dados variam conforme condições climáticas de cada ano.

---

## Dados Geográficos

### IBGE - Estados e Municípios

- **API Localidades**: https://servicodados.ibge.gov.br/api/v1/localidades
- **API Malhas**: https://servicodados.ibge.gov.br/api/v3/malhas

### Dados Disponíveis
- 27 estados
- 5.570 municípios
- Geometrias (MultiPolygon)
- População estimada

---

---

## 6. CadÚnico - Dados Reais

### Descrição

O CadÚnico (Cadastro Único para Programas Sociais) é a base de dados que identifica famílias de baixa renda.

### Método Recomendado: API MiSocial ⭐

- **Fonte**: SAGI/MDS - API MiSocial
- **URL**: https://aplicacoes.mds.gov.br/sagi/servicos/misocial/
- **Vantagem**: Dados oficiais completos, API pública, sem autenticação
- **Dados**: Famílias, pessoas, faixas de pobreza, distribuição etária
- **Período**: Janeiro/2019 até o mês atual
- **Script**: `ingest_misocial_cadunico.py`

**Verificação de Consistência**:
- **Dados oficiais (MDS)**: ~41 milhões de famílias cadastradas
- **Nossa ingestão**: 41.539.082 famílias (Dez/2024)
- **Status**: ✅ Consistente

### Método Alternativo: Base dos Dados (BigQuery)

- **Fonte**: basedosdados.org
- **URL**: https://basedosdados.org/dataset/br-mds-cadu
- **Vantagem**: Dados granulares, consultas SQL
- **Limitação**: Requer conta Google Cloud
- **Script**: `ingest_basedosdados_cadunico.py`

### Método 3: SAGI RI (API)

- **Fonte**: Relatórios de Informações do MDS
- **URL**: https://aplicacoes.cidadania.gov.br/ri/
- **Vantagem**: Dados demográficos detalhados
- **Limitação**: API não documentada, pode ser instável
- **Script**: `ingest_sagi_cadunico.py`

### Método 4: Observatório MDS (RIv3)

- **Fonte**: Painel do Observatório de Políticas
- **URL**: https://paineis.mds.gov.br/
- **Vantagem**: Dados visuais convertidos
- **Limitação**: Experimental
- **Script**: `ingest_cadunico_real.py`

### Relação Bolsa Família ↔ CadÚnico

```
┌─────────────────────────────────────────────────┐
│              CADASTRO ÚNICO (CadÚnico)          │
│         ~85 milhões de pessoas cadastradas      │
│                                                 │
│   ┌─────────────────────────────────────────┐   │
│   │         BOLSA FAMÍLIA                   │   │
│   │      ~21 milhões de famílias            │   │
│   │   (100% cadastradas no CadÚnico)        │   │
│   └─────────────────────────────────────────┘   │
│                                                 │
│   + BPC/LOAS (6M)                               │
│   + TSEE (14M)                                  │
│   + Farmácia Popular (12M)                      │
│   + Auxílio Gás (5.8M)                          │
│   + Seguro Defeso (400-600k)                    │
│   + Auxílio Inclusão (45k)                      │
│   + Garantia-Safra (560k)                       │
│   + Outros programas...                         │
└─────────────────────────────────────────────────┘
```

O Bolsa Família é usado como proxy porque:
1. Representa as famílias mais vulneráveis
2. 100% estão no CadÚnico
3. Dados abertos e confiáveis

---

## 7. PIS/PASEP - Cotas Esquecidas

### Descrição

Trabalhadores que contribuíram para PIS/PASEP entre 1971-1988 podem ter cotas disponíveis para saque. Estimativa: **R$ 26,3 bilhões** não resgatados.

### Fonte

- **Caixa Econômica Federal** (PIS)
- **Banco do Brasil** (PASEP)
- URL: https://www.caixa.gov.br/beneficios-trabalhador/pis/Paginas/default.aspx

### Dados Disponíveis

- Consulta individual via CPF
- Não há dados abertos agregados por município
- Integração futura via API Caixa (vide roadmap)

### Público Elegível

- Trabalhadores cadastrados PIS/PASEP entre 1971-1988
- Herdeiros de trabalhadores falecidos
- Estimativa: ~10 milhões de cotistas

---

## 8. Integração Futura - Apps Caixa

### Visão

Além do app próprio Tá na Mão, a plataforma poderá operar via API integrada aos apps da Caixa Econômica Federal, ampliando o alcance.

### Canais de Integração Planejados

| Canal | Usuários | Integração |
|-------|----------|------------|
| **Caixa Tem** | 70M+ | API REST para consulta de benefícios |
| **App FGTS** | 60M+ | Webhook para notificações de direitos |
| **Internet Banking** | 40M+ | Widget de benefícios não resgatados |
| **Lotéricas** | 13k pontos | Consulta via terminal |

### Arquitetura de Integração

```
┌──────────────────────────────────────────────────────────┐
│                    TÁ NA MÃO API                         │
│                (Backend - FastAPI)                       │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
   │  App    │   │  Caixa   │   │   App   │   │ WhatsApp │
   │Tá na Mão│   │   Tem    │   │  FGTS   │   │   Bot    │
   │(Android)│   │  (API)   │   │  (API)  │   │  (API)   │
   └─────────┘   └──────────┘   └─────────┘   └──────────┘
```

### Endpoints para Integração (Fase Futura)

```http
# Consultar benefícios por CPF (requer autenticação)
GET /api/v2/citizen/{cpf}/benefits

# Verificar elegibilidade para programas
POST /api/v2/citizen/eligibility-check

# Iniciar jornada de ativação
POST /api/v2/citizen/activate-benefit
```

### Roadmap de Integração

| Fase | Período | Escopo |
|------|---------|--------|
| **Piloto** | 2025 | App próprio + WhatsApp |
| **Fase 2** | 2026 | Integração Caixa Tem (consulta) |
| **Fase 3** | 2026-27 | Integração FGTS + Poupança Social |
| **Nacional** | 2027+ | Todos os canais Caixa |

---

## Referências Oficiais

- [Portal da Transparência](https://portaldatransparencia.gov.br/)
- [OpenDataSUS](https://opendatasus.saude.gov.br/)
- [ANEEL Dados Abertos](https://dadosabertos.aneel.gov.br/)
- [IBGE APIs](https://servicodados.ibge.gov.br/)
- [Ministério da Saúde - Farmácia Popular](https://www.gov.br/saude/pt-br/composicao/sectics/farmacia-popular)
- [Ministério da Saúde - Dignidade Menstrual](https://www.gov.br/saude/pt-br/composicao/saps/dignidade-menstrual)
- [Base dos Dados - CadÚnico](https://basedosdados.org/dataset/br-mds-cadu)
- [SAGI - Relatórios de Informações](https://aplicacoes.cidadania.gov.br/ri/)
- [Caixa - PIS](https://www.caixa.gov.br/beneficios-trabalhador/pis/)

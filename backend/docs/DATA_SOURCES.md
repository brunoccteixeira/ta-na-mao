# Fontes de Dados Oficiais

Este documento descreve as fontes de dados utilizadas pelo sistema Tá na Mão.

## Resumo

| Programa | Fonte | URL | Formato | Atualização |
|----------|-------|-----|---------|-------------|
| Bolsa Família | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| BPC/LOAS | Portal da Transparência | portaldatransparencia.gov.br | CSV/ZIP | Mensal |
| Farmácia Popular | OpenDataSUS | opendatasus.saude.gov.br | CSV/ZIP | Mensal |
| TSEE | ANEEL | dadosabertos.aneel.gov.br | CSV | Mensal |
| Dignidade Menstrual | OpenDataSUS | opendatasus.saude.gov.br | CSV/ZIP | Mensal |

---

## 1. Bolsa Família (Novo Bolsa Família)

### Descrição
Principal programa de transferência de renda do Brasil, atendendo famílias em situação de pobreza e extrema pobreza. Usado como proxy para dados do CadÚnico.

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
- **Status**: ✅ Consistente

### Uso como Proxy CadÚnico
O Bolsa Família é usado como proxy para o CadÚnico porque:
- 100% dos beneficiários estão cadastrados no CadÚnico
- Representa as famílias mais vulneráveis
- Dados abertos e atualizados mensalmente

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

## Referências Oficiais

- [Portal da Transparência](https://portaldatransparencia.gov.br/)
- [OpenDataSUS](https://opendatasus.saude.gov.br/)
- [ANEEL Dados Abertos](https://dadosabertos.aneel.gov.br/)
- [IBGE APIs](https://servicodados.ibge.gov.br/)
- [Ministério da Saúde - Farmácia Popular](https://www.gov.br/saude/pt-br/composicao/sectics/farmacia-popular)
- [Ministério da Saúde - Dignidade Menstrual](https://www.gov.br/saude/pt-br/composicao/saps/dignidade-menstrual)

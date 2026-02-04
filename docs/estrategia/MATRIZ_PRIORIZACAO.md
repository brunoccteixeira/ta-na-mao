# Matriz de Priorização Estratégica — Tá na Mão

> Recomendações baseadas no benchmarking global
> Última atualização: 2026-02-04

---

## 1. Matriz de Priorização

| # | Iniciativa | Impacto | Esforço | Prioridade | Referência |
|---|---|---|---|---|---|
| 1 | Relatório de impacto quantificado | Alto (funding + advocacy) | Baixo | **P0** | Turn2us (£5.4K/user) |
| 2 | Push proativo de elegibilidade | Alto (engagement) | Médio | **P1** | Benefits Data Trust |
| 3 | API/Widget embeddável | Alto (distribuição) | Médio | **P1** | Turn2us, Entitledto |
| 4 | Marketplace de savings | Alto (revenue + valor) | Médio | **P1** | Propel, Wizbii |
| 5 | B2G dashboard para prefeituras | Alto (revenue) | Alto | **P2** | Haqdarshak |
| 6 | Rede de multiplicadores | Alto (alcance offline) | Alto | **P2** | Haqdarshak (52K agents) |
| 7 | Integração bancária B2B2C | Alto (distribuição) | Alto | **P2** | Wizbii |
| 8 | Grants privados | Médio (catálogo) | Médio | **P2** | Turn2us (1.700+ grants) |
| 9 | Open-source rules engine | Alto (posicionamento) | Alto | **P3** | Nava Strata, OpenSPP |
| 10 | Expansão LATAM | Alto (TAM) | Muito Alto | **P3** | — |

---

## 2. Detalhamento por Prioridade

### P0 — Executar Imediatamente

#### 1. Relatório de Impacto Quantificado

**O que é**: Documento público com métricas de valor desbloqueado por família/usuário.

**Por que P0**:
- Essencial para fundraising (investidores querem métricas de impacto)
- Diferencia de concorrentes gov (Caixa Tem não publica isso)
- Habilita advocacy e PR

**Benchmark**: Turn2us publica "£5.396/usuário" e "£12.9B total desbloqueado" — virou headline de mídia.

**Entregáveis**:
- [ ] Definir metodologia de cálculo (valor médio por benefício × taxa de conversão)
- [ ] Dashboard interno de tracking
- [ ] Report público trimestral
- [ ] Press release para mídia

**Métricas de sucesso**:
- Valor médio desbloqueado/família calculado (target: R$ 800-1.200/ano)
- 1 menção em mídia nacional em 90 dias

---

### P1 — Próximo Sprint (30-60 dias)

#### 2. Push Proativo de Elegibilidade

**O que é**: Notificações automáticas "Você pode ter direito a X" baseadas em perfil do usuário.

**Por que P1**:
- Aumenta engagement e retenção
- Reduz "benefício deixado na mesa"
- Diferencial vs. apps passivos (Caixa Tem)

**Benchmark**: Benefits Data Trust usa dados públicos para identificar elegíveis e fazer outreach proativo — 90% de taxa de resposta em populações-alvo.

**Entregáveis**:
- [ ] Motor de regras para matching perfil × benefício
- [ ] Sistema de push notifications (FCM + WhatsApp)
- [ ] Opt-in/opt-out LGPD
- [ ] A/B testing de mensagens

**Métricas de sucesso**:
- Taxa de abertura de push > 15%
- Taxa de conversão (push → verificação) > 5%

---

#### 3. API/Widget Embeddável

**O que é**: Permitir que ONGs, CRAS, igrejas, associações embutam o verificador de elegibilidade em seus sites.

**Por que P1**:
- Multiplica distribuição sem CAC
- Cria rede de parceiros
- Modelo validado (Turn2us tem 100+ parceiros usando widgets)

**Benchmark**: Entitledto oferece API e widgets white-label para housing associations, councils, charities.

**Entregáveis**:
- [ ] API REST pública documentada
- [ ] Widget JavaScript embedável
- [ ] Dashboard de parceiros
- [ ] Programa de onboarding de parceiros

**Métricas de sucesso**:
- 10 parceiros usando widget em 90 dias
- 1.000 verificações via parceiros/mês

---

#### 4. Marketplace de Savings

**O que é**: Ofertas exclusivas para beneficiários — descontos em farmácia, tarifa social de energia, internet subsidiada.

**Por que P1**:
- Gera valor adicional ao usuário
- Potencial de monetização (affiliate, interchange)
- Fideliza usuário no app

**Benchmark**: Propel oferece "Fresh EBT savings" com descontos em grocery; Wizbii agrega comparadores de tarifas.

**Entregáveis**:
- [ ] Catálogo de ofertas (energia TSEE, internet, farmácia)
- [ ] Parcerias com empresas (Drogasil, Claro, Enel)
- [ ] Seção "Economize" no app
- [ ] Tracking de valor economizado

**Métricas de sucesso**:
- 5 parcerias ativas em 90 dias
- R$ 50.000 economia total para usuários em 90 dias

---

### P2 — Roadmap Trimestral

#### 5. B2G Dashboard para Prefeituras

**O que é**: Painel analytics para secretarias municipais de assistência social — cobertura de benefícios, gaps, benchmarks.

**Por que P2**:
- Revenue stream B2G (CPSI Caixa até R$ 1.6M)
- Dados valiosos para políticas públicas
- Stickiness com governo

**Benchmark**: Haqdarshak vende dashboards para governos estaduais indianos; Single Stop fornece analytics para universidades.

**Entregáveis**:
- [ ] Dashboard de indicadores municipais
- [ ] Comparativo entre municípios
- [ ] Exportação de relatórios
- [ ] Pricing model (SaaS municipal)

**Métricas de sucesso**:
- 3 prefeituras piloto em 180 dias
- MRR de R$ 10.000 em 180 dias

---

#### 6. Rede de Multiplicadores

**O que é**: Treinar agentes comunitários de saúde (ACS) e assistentes sociais como "embaixadores" do Tá na Mão.

**Por que P2**:
- Alcança população offline
- Cria confiança (recomendação de pessoa conhecida)
- Modelo Haqdarshak validado (52K agentes)

**Benchmark**: Haqdarshak treina agentes locais que recebem pequena comissão por aplicação bem-sucedida.

**Entregáveis**:
- [ ] Programa de treinamento (vídeo + quiz)
- [ ] App simplificado para agentes
- [ ] Modelo de incentivo (gamificação ou micro-pagamento)
- [ ] Piloto em 1 município (parceria CRAS)

**Métricas de sucesso**:
- 50 multiplicadores treinados em 180 dias
- 500 famílias atendidas via multiplicadores em 180 dias

---

#### 7. Integração Bancária B2B2C

**O que é**: Parceria com fintechs (Nubank, PicPay, Caixa) para notificar clientes elegíveis dentro do app do banco.

**Por que P2**:
- Distribuição massiva (Nubank: 90M+ clientes)
- Modelo Wizbii validado
- Requer sales B2B sofisticado

**Benchmark**: Wizbii integra com bancos e seguradoras francesas — empresa subsidia acesso para funcionários/clientes.

**Entregáveis**:
- [ ] Proposta comercial B2B
- [ ] API de integração white-label
- [ ] Piloto com 1 fintech
- [ ] Case study de impacto

**Métricas de sucesso**:
- 1 parceria B2B assinada em 180 dias
- 10.000 verificações via parceiro em 180 dias

---

#### 8. Grants Privados

**O que é**: Mapear e integrar bolsas/auxílios de fundações e empresas brasileiras.

**Por que P2**:
- Expande catálogo além de benefícios governamentais
- Turn2us tem 1.700+ grants no catálogo
- Menor esforço que criar novos benefícios

**Benchmark**: Turn2us mapeia grants de caridades, empresas, fundações — usuário busca por categoria.

**Entregáveis**:
- [ ] Mapeamento de 50+ fundos brasileiros
- [ ] Integração no catálogo de benefícios
- [ ] Filtro "Privado/Fundação" no app
- [ ] Processo de atualização periódica

**Métricas de sucesso**:
- 50 grants privados catalogados em 180 dias
- 100 aplicações para grants via Tá na Mão em 180 dias

---

### P3 — Visão de Longo Prazo (6-12 meses)

#### 9. Open-Source Rules Engine

**O que é**: Disponibilizar o motor de elegibilidade como Digital Public Infrastructure (DPI) para outros países.

**Por que P3**:
- Posicionamento como líder regional
- Atrai contribuições da comunidade
- Modelo Nava Strata / OpenSPP

**Benchmark**: Nava criou "Strata" como plataforma open-source para benefícios; OpenSPP é framework FOSS para proteção social.

**Entregáveis**:
- [ ] Refatorar rules engine para ser agnóstico de país
- [ ] Documentação técnica completa
- [ ] Licença open-source (Apache 2.0 ou similar)
- [ ] Comunidade de contribuidores

**Métricas de sucesso**:
- Repo público com 100+ stars em 12 meses
- 1 implementação em outro país LATAM em 12 meses

---

#### 10. Expansão LATAM

**O que é**: Adaptar Tá na Mão para Colômbia (Sisbén), México (Bienestar), Argentina (ANSES).

**Por que P3**:
- TAM multiplica 5-10x
- Gap de mercado similar ao Brasil
- Requer funding significativo

**Países prioritários**:
1. **Colômbia**: Sisbén fragmentado, 50M população
2. **Argentina**: ANSES digital mas silos, 45M população
3. **México**: Bienestar centralizado, 130M população

**Entregáveis**:
- [ ] Estudo de mercado por país
- [ ] Adaptação legal (LGPD equivalente)
- [ ] Mapeamento de benefícios locais
- [ ] Piloto em 1 país

**Métricas de sucesso**:
- MVP em 1 país LATAM em 12 meses
- 10.000 usuários no novo país em 12 meses

---

## 3. Matriz Visual (Impacto × Esforço)

```
                            IMPACTO
                    Baixo           Alto
                ┌───────────────────────────┐
         Baixo  │                │ 1.Report │  ← QUICK WINS
                │                │   (P0)   │
    ESFORÇO     ├────────────────┼──────────┤
                │                │ 2.Push   │
                │                │ 3.Widget │  ← PRIORIZAR
         Médio  │ 8.Grants       │ 4.Saving │
                │   (P2)         │   (P1)   │
                ├────────────────┼──────────┤
                │                │ 5.B2G    │
                │                │ 6.Multip │  ← PLANEJAR
         Alto   │                │ 7.B2B2C  │
                │                │   (P2)   │
                ├────────────────┼──────────┤
                │                │ 9.Open   │
         Muito  │                │ 10.LATAM │  ← VISÃO
         Alto   │                │   (P3)   │
                └───────────────────────────┘
```

---

## 4. Cronograma Sugerido

```
2026-Q1 (Jan-Mar)
├── [P0] Relatório de impacto v1
├── [P1] Push proativo - MVP
└── [P1] API/Widget - Spec

2026-Q2 (Abr-Jun)
├── [P1] API/Widget - Launch
├── [P1] Marketplace savings - 5 parcerias
├── [P1] Push proativo - Rollout
└── [P2] B2G Dashboard - Piloto

2026-Q3 (Jul-Set)
├── [P2] Multiplicadores - Piloto 1 município
├── [P2] B2B2C - 1 parceria fintech
├── [P2] Grants privados - 50 catalogados
└── [P3] Open-source - Planning

2026-Q4 (Out-Dez)
├── [P2] B2G - 3 prefeituras
├── [P2] Multiplicadores - Escala
├── [P3] Open-source - MVP
└── [P3] LATAM - Estudo de mercado
```

---

## 5. Investimentos Estratégicos para Pitch

### 5.1 Investidores Target

| Investidor | Thesis | Ticket | Próximo passo |
|---|---|---|---|
| **a16z Fintech** | Fintech for underbanked | $10-50M | Intro via portfólio (Propel) |
| **Omidyar Network** | Digital public goods | $1-10M | Apply via website |
| **Google.org** | AI for social good | $1-5M | Impact Challenge |
| **Luminate** | Civic tech | $1-5M | RFP process |
| **Vox Capital** | Negócios de impacto BR | R$ 2-10M | Intro via ecossistema |
| **MOV Investimentos** | Impact investing BR | R$ 1-5M | Pitch direto |

### 5.2 Grants e Prêmios

| Oportunidade | Valor | Deadline |
|---|---|---|
| Google.org Impact Challenge | $2M | Anual (Mar-Abr) |
| BNDES Fundo Social | R$ 5M+ | Contínuo |
| Fundação Lemann | R$ 500K-2M | Anual |
| BID Lab | $150K-1M | Contínuo |
| Skoll Award | $1.5M | Anual (Jan) |

---

## 6. KPIs de Acompanhamento

| Métrica | Baseline | Target Q2 | Target Q4 |
|---|---|---|---|
| Usuários ativos/mês | MVP | 10.000 | 50.000 |
| Verificações de elegibilidade | — | 50.000 | 200.000 |
| Valor desbloqueado (R$) | — | R$ 5M | R$ 20M |
| Parceiros (widgets) | 0 | 10 | 30 |
| Prefeituras B2G | 0 | 3 | 10 |
| Multiplicadores treinados | 0 | 50 | 200 |
| NPS | — | 50+ | 60+ |

---

*Documento preparado para planejamento estratégico do Tá na Mão.*

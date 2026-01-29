# Tá na Mao - Guia de Demonstracao

## APK para Instalacao

```
/Users/brunoteixeira/Downloads/TaNaMao-debug.apk
```

**Tamanho:** 23MB
**Versao:** Sprint 6 (modo claro + Home redesenhada)

Para instalar: enviar para celular Android e abrir o arquivo.

---

## Novidades Sprint 6

### Modo Claro Automatico
- App segue tema do sistema (claro/escuro)
- Funciona em Android 8+
- Design Propel-inspired em ambos os modos

### Home Screen Redesenhada
- **Antes:** Indicadores Nacionais (foco governo)
- **Depois:** Conteudo para cidadao

**Proximos Pagamentos:**
```
Bolsa Familia R$600 em 5 dias
BPC R$1.412 em 12 dias
```

**Servicos Perto de Voce:**
- CRAS mais proximo
- Farmacias credenciadas

---

## Fluxos de Demonstração (Backend)

### Iniciar o Agente

```bash
cd backend
source venv/bin/activate
export GOOGLE_API_KEY="sua-chave-aqui"
python -m app.agent.agent
```

---

## Demo 1: Consulta de Benefícios por CPF

**Objetivo**: Mostrar que o cidadão pode consultar seus benefícios pelo CPF

```
Cidadão: Meu Bolsa Família tá vindo? CPF 529.982.247-25

Agente: Achei! Você está cadastrado:
        BOLSA FAMÍLIA: R$ 600,00
        Parcela: Janeiro/2025
        CADÚNICO: Ativo
```

**CPFs de Teste**:
| CPF | Nome | Benefício |
|-----|------|-----------|
| 529.982.247-25 | Maria Silva | Bolsa Família R$600 |
| 111.444.777-35 | João Pereira | BPC Idoso R$1.412 |
| 123.456.789-09 | José Ferreira | BPC PCD R$1.412 |

---

## Demo 2: Farmácia Popular (Fluxo Completo)

**Objetivo**: Mostrar pedido de medicamentos estilo iFood

```
Cidadão: Quero pegar remédio de graça

Agente: [Mostra checklist de documentos]
        Me fala seu CEP ou os remédios que precisa.

Cidadão: Losartana 50mg e Metformina 850mg

Agente: Entendi! Ambos são GRATUITOS no Farmácia Popular!
        Quer que eu envie o pedido pra farmácia preparar?

Cidadão: Sim, meu CEP é 04010-100

Agente: [Mostra farmácias próximas com links]
        - Google Maps
        - Waze
        - WhatsApp da farmácia
```

---

## Demo 3: Verificar Elegibilidade

**Objetivo**: Mostrar que o agente orienta sobre direitos

```
Cidadão: Tenho direito ao BPC? CPF 529.982.247-25

Agente: Você não recebe BPC atualmente.

        PRÓXIMOS PASSOS:
        1. Fazer inscrição no CadÚnico
        2. Agendar perícia no INSS (para PCD)
        3. Comprovar renda até 1/4 do salário mínimo

        Quer que eu prepare os documentos?
```

---

## Demo 4: Buscar CRAS (para benefícios sociais)

```
Cidadão: Quero me cadastrar no Bolsa Família

Agente: [Gera checklist de documentos]
        Me fala seu CEP que eu mostro o CRAS perto.

Cidadão: 04010-100

Agente: CRAS mais próximo:
        📍 CRAS Vila Mariana - 1,2km
        📞 (11) 3333-4444
        🕐 Seg-Sex 8h-17h
        [Ver no mapa]
```

---

## Estatisticas do Sistema

| Metrica | Valor |
|---------|-------|
| Programas rastreados | 7 |
| Municipios | 5.570 |
| Beneficiarios Bolsa Familia | ~21M |
| Beneficiarios BPC | ~6.2M |
| Tools do Agente | 13 |
| Sprints concluidos | 6 |

---

## Diferencial: Agente que FAZ

| Tradicional | Tá na Mão |
|-------------|-----------|
| "Vá ao CRAS" | Mostra CRAS + mapa + telefone |
| "Leve documentos" | Gera checklist personalizado |
| "Consulte seu benefício" | Mostra valor e data na hora |
| "Procure uma farmácia" | Envia pedido para farmácia preparar |

---

## Arquitetura

```
Cidadao -> App Android -> API FastAPI -> Agente Gemini -> Tools
                                              |
                                       [13 ferramentas]
```

### Lista Completa de Tools

| # | Tool | Descricao |
|---|------|-----------|
| 1 | `validar_cpf` | Valida CPF brasileiro |
| 2 | `buscar_cep` | Busca endereco pelo CEP (ViaCEP) |
| 3 | `consultar_api` | Consulta APIs gov.br |
| 4 | `gerar_checklist` | Lista de documentos por beneficio |
| 5 | `buscar_cras` | CRAS proximos com Maps/Waze/WhatsApp |
| 6 | `buscar_farmacia` | Farmacias credenciadas com links |
| 7 | `processar_receita` | Extrai medicamentos (Gemini Vision) |
| 8 | `enviar_whatsapp` | Envia mensagem via Twilio |
| 9 | `preparar_pedido` | Cria pedido estilo iFood |
| 10 | `consultar_pedido` | Status do pedido |
| 11 | `listar_pedidos_cidadao` | Historico de pedidos |
| 12 | `consultar_beneficio` | Consulta por CPF (Sprint 5) |
| 13 | `verificar_elegibilidade` | Verifica direito a beneficio |

---

## Demo 5: Home Screen (Sprint 6)

**Objetivo**: Mostrar interface focada no cidadao

```
1. Abrir o app
2. Na Home, mostrar:
   - "Proximos Pagamentos" com countdown
   - "Servicos Perto de Voce" (CRAS e Farmacias)
3. Mudar tema do celular (claro <-> escuro)
4. Ver app mudar automaticamente
```

**Pontos de destaque:**
- Design limpo, inspirado no Propel
- Nada de metricas governamentais
- Foco: "O que EU recebo?" e "Onde vou?"

---

## Roadmap com Caixa

| Fase | Integracao | Beneficio |
|------|------------|----------|
| 1 | API no Caixa Tem | 67M usuários ativos |
| 2 | API no app FGTS | Notificar direitos não sacados |
| 3 | WhatsApp Business | Atender via WhatsApp |

**Valor potencial**: R$ 42 bilhões em benefícios não sacados

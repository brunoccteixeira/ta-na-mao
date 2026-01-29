# Estratégia Multicanal - Tá na Mão

## Visão Geral

O Tá na Mão adota uma estratégia multicanal para maximizar o alcance e acessibilidade do serviço. Com aproximadamente 40-50% de penetração de smartphones em famílias de extrema pobreza, é fundamental oferecer múltiplos canais de acesso.

```
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE CANAIS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ WhatsApp │  │   SMS    │  │  Voice   │  │   Web    │    │
│  │ Handler  │  │ Handler  │  │ Handler  │  │ Handler  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │          │
│       └─────────────┴──────┬──────┴─────────────┘          │
│                            │                               │
│                    ┌───────▼───────┐                       │
│                    │ Channel       │                       │
│                    │ Normalizer    │                       │
│                    │ (Mensagem     │                       │
│                    │  Unificada)   │                       │
│                    └───────┬───────┘                       │
│                            │                               │
└────────────────────────────┼───────────────────────────────┘
                             │
                     ┌───────▼───────┐
                     │    Agent      │
                     │ Orchestrator  │
                     │  (Existente)  │
                     └───────────────┘
```

## Canais Suportados

| Canal | Público Alvo | Cobertura Estimada | Status |
|-------|--------------|-------------------|--------|
| **WhatsApp** | Smartphones com internet | 60-70% | ✅ Implementado |
| **SMS/USSD** | Feature phones e básicos | +20% | 🔄 Em desenvolvimento |
| **0800 (Voz)** | Telefone fixo/qualquer celular | +10% | 🔄 Em desenvolvimento |
| **Web** | Acesso via navegador | Complementar | ✅ Implementado |
| **Lotéricas** | Presencial (terminais) | Futuro | 📋 Planejado |
| **CRAS** | Presencial (tablets) | Futuro | 📋 Planejado |

## Canal SMS/USSD

### Arquitetura

O canal SMS funciona como um menu USSD-like, onde o usuário navega por opções numéricas.

```
Usuário envia SMS para número curto (ex: 28282)
                │
                ▼
┌─────────────────────────────────┐
│ "1" = Consultar benefícios      │
│ "2" = Dinheiro esquecido        │
│ "3" = Farmácia Popular          │
│ "4" = CRAS mais próximo         │
│ "5" = Falar com atendente       │
└─────────────────────────────────┘
                │
    Usuário responde "1"
                │
                ▼
┌─────────────────────────────────┐
│ "Digite seu CPF (só números):"  │
└─────────────────────────────────┘
                │
    Usuário: "12345678901"
                │
                ▼
┌─────────────────────────────────┐
│ Você tem 2 benefícios ativos:   │
│ - Bolsa Família: R$ 600/mês     │
│ - TSEE: Economia R$ 45/mês      │
│                                 │
│ Responda "M" para mais opções   │
└─────────────────────────────────┘
```

### Estados de Navegação SMS

```python
class SMSState(str, Enum):
    """Estados do fluxo SMS."""

    MENU_PRINCIPAL = "menu_principal"
    AGUARDANDO_CPF = "aguardando_cpf"
    AGUARDANDO_CEP = "aguardando_cep"
    RESULTADO = "resultado"
    MENU_SECUNDARIO = "menu_secundario"
```

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/sms/webhook` | Recebe SMS do provedor |
| POST | `/api/v1/sms/status` | Status de entrega |
| GET | `/api/v1/sms/session/{phone}` | Estado da sessão |

### Integração com Provedores

```python
# Exemplo de webhook Twilio/Zenvia
{
    "from": "+5511999999999",
    "to": "28282",
    "body": "1",
    "message_id": "SM123...",
    "timestamp": "2025-01-16T10:30:00Z"
}
```

## Canal 0800 (Voz/URA)

### Arquitetura

O canal de voz utiliza URA (IVR) para navegação por DTMF e TTS para respostas.

```
Usuário liga para 0800-XXX-XXXX
                │
                ▼
┌─────────────────────────────────┐
│ "Bem-vindo ao Tá na Mão.        │
│  Para consultar benefícios,     │
│  digite 1.                      │
│  Para dinheiro esquecido,       │
│  digite 2..."                   │
└─────────────────────────────────┘
                │
    Usuário digita "2"
                │
                ▼
┌─────────────────────────────────┐
│ "Digite seu CPF usando o        │
│  teclado do telefone"           │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ [TTS do agente]:                │
│ "Você tem R$ 1.200 de PIS       │
│  disponível para saque.         │
│  Para instruções de como        │
│  sacar, digite 1..."            │
└─────────────────────────────────┘
```

### Estados de Navegação Voz

```python
class VoiceState(str, Enum):
    """Estados do fluxo de voz."""

    BOAS_VINDAS = "boas_vindas"
    MENU_PRINCIPAL = "menu_principal"
    COLETANDO_CPF = "coletando_cpf"
    PROCESSANDO = "processando"
    RESULTADO = "resultado"
    MENU_OPCOES = "menu_opcoes"
    TRANSFERINDO = "transferindo"
    DESPEDIDA = "despedida"
```

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/voice/webhook` | Recebe chamada (início) |
| POST | `/api/v1/voice/dtmf` | Recebe dígitos DTMF |
| POST | `/api/v1/voice/status` | Status da chamada |
| GET | `/api/v1/voice/session/{call_id}` | Estado da sessão |

### TwiML/VXML de Exemplo

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Camila" language="pt-BR">
        Bem-vindo ao Tá na Mão, seu assistente de benefícios sociais.
    </Say>
    <Gather numDigits="1" action="/api/v1/voice/dtmf" method="POST">
        <Say voice="Polly.Camila" language="pt-BR">
            Para consultar seus benefícios, digite 1.
            Para verificar dinheiro esquecido, digite 2.
            Para Farmácia Popular, digite 3.
            Para encontrar o CRAS mais próximo, digite 4.
        </Say>
    </Gather>
</Response>
```

## Provedores Recomendados

### Comparativo Brasil

| Provedor | SMS | Voice | WhatsApp | Preço SMS | Suporte BR |
|----------|-----|-------|----------|-----------|------------|
| **Zenvia** | ✅ | ✅ | ✅ | R$ 0,06-0,15 | Excelente |
| **Twilio** | ✅ | ✅ | ✅ | R$ 0,08-0,20 | Bom |
| **Infobip** | ✅ | ✅ | ✅ | R$ 0,05-0,12 | Muito bom |
| **Movile** | ✅ | ❌ | ✅ | R$ 0,04-0,10 | Excelente |

### Recomendação

Para o Tá na Mão, recomendamos **Zenvia** ou **Infobip** por:
- Suporte nativo a números curtos brasileiros
- Integração com principais operadoras
- SDKs em Python
- Suporte técnico em português
- Experiência com governo e terceiro setor

## Formato de Mensagem Unificada

Todas as mensagens de diferentes canais são normalizadas para um formato comum:

```python
@dataclass
class UnifiedMessage:
    """Mensagem unificada entre canais."""

    # Identificação
    channel: ChannelType  # whatsapp, sms, voice, web
    message_id: str
    session_id: str

    # Remetente
    user_id: str  # Telefone normalizado ou ID único
    user_phone: Optional[str]

    # Conteúdo
    text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None

    # Contexto
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Estado (para canais stateful como SMS/Voz)
    channel_state: Optional[str] = None
```

## Configuração de Ambiente

### Variáveis de Ambiente (SMS/Voice)

```bash
# Provedor SMS (escolher um)
SMS_PROVIDER=zenvia  # ou twilio, infobip

# Zenvia
ZENVIA_API_TOKEN=seu_token_aqui
ZENVIA_SMS_FROM=28282

# Twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=seu_token
TWILIO_SMS_FROM=+5511999999999
TWILIO_VOICE_FROM=+5508001234567

# Voice/0800
VOICE_PROVIDER=twilio
VOICE_LANGUAGE=pt-BR
VOICE_VOICE=Polly.Camila

# Webhook URLs (para configurar no provedor)
WEBHOOK_BASE_URL=https://api.tanamao.gov.br
```

## Métricas e Monitoramento

### KPIs por Canal

| Métrica | WhatsApp | SMS | Voz |
|---------|----------|-----|-----|
| Taxa de resposta | > 90% | > 80% | > 70% |
| Tempo médio sessão | 3-5 min | 2-4 min | 3-6 min |
| Custo por interação | R$ 0,05 | R$ 0,10-0,20 | R$ 0,50-1,00 |
| NPS esperado | > 70 | > 60 | > 50 |

### Alertas

- Taxa de erro > 5% em qualquer canal
- Tempo de resposta > 5s para SMS
- Chamadas abandonadas > 20%
- Custo diário acima do budget

## Roadmap

### Fase 1: Fundação (Atual)
- [x] WhatsApp via Twilio
- [ ] SMS básico (menu numérico)
- [ ] 0800 com URA simples

### Fase 2: Otimização
- [ ] SMS com fluxos avançados
- [ ] Voz com NLU básico
- [ ] Fallback entre canais

### Fase 3: Expansão
- [ ] Terminais em lotéricas
- [ ] Tablets em CRAS
- [ ] API para prefeituras

## Considerações de Acessibilidade

- **Voz**: Velocidade de fala ajustável, repetição automática
- **SMS**: Mensagens curtas (< 160 chars quando possível)
- **Todos**: Linguagem simples, evitar jargões
- **Escalação**: Sempre oferecer opção de atendente humano

## Integracao com MCPs

O Ta na Mao utiliza MCPs (Model Context Protocol) para integrar ferramentas externas de forma padronizada.

### MCPs Relacionados a Canais

| MCP | Uso | Status |
|-----|-----|--------|
| **Twilio MCP** | SMS, WhatsApp, Voice via MCP padronizado | Configurado |
| **Brasil API MCP** | Validacao de CEP, DDD para identificar regiao | Implementado |
| **Google Maps MCP** | Geolocalizacao e busca de locais | Implementado |

### Beneficios do Twilio MCP

- 20.6% mais rapido que integracao direta
- 19.3% menos chamadas de API
- Retry automatico em falhas
- Logging unificado

### Configuracao

Ver arquivo `.mcp.json` na raiz do projeto e documentacao em `docs/MCP_SETUP.md`.

```json
{
  "mcpServers": {
    "twilio": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-twilio", "--services", "messaging,voice"]
    }
  }
}
```

### Arquitetura com MCP

```
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE CANAIS + MCP                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ WhatsApp │  │   SMS    │  │  Voice   │  │   Web    │    │
│  │ Handler  │  │ Handler  │  │ Handler  │  │ Handler  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │          │
│       └─────────────┴──────┬──────┴─────────────┘          │
│                            │                               │
│                    ┌───────▼───────┐                       │
│                    │  MCP Manager  │                       │
│                    │  (Twilio MCP) │                       │
│                    └───────┬───────┘                       │
│                            │                               │
└────────────────────────────┼───────────────────────────────┘
                             │
                     ┌───────▼───────┐
                     │    Agent      │
                     │ Orchestrator  │
                     └───────────────┘
```

---

## Referencias

- [Twilio SMS/Voice Brazil](https://www.twilio.com/pt-br/sms)
- [Twilio MCP Server](https://www.twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server)
- [Zenvia API Documentation](https://zenvia.github.io/zenvia-openapi-spec/)
- [W3C Voice Browser Working Group](https://www.w3.org/Voice/)
- [WCAG 2.1 - Acessibilidade](https://www.w3.org/WAI/WCAG21/quickref/)
- [MCP Setup Guide](./MCP_SETUP.md)

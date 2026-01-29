# MCP (Model Context Protocol) Setup - Ta na Mao

## Visao Geral

O Ta na Mao utiliza MCP (Model Context Protocol) para integrar ferramentas externas de forma padronizada. Este documento descreve a configuracao e uso dos MCPs no projeto.

## MCPs Configurados

### 1. Brasil API MCP
**Prioridade: ALTA**

APIs brasileiras essenciais para validacao e consultas.

```bash
# Instalacao
npx -y @mauricio-cantu/brasil-api-mcp
```

**Tools disponiveis:**
| Tool | Descricao | Uso no Ta na Mao |
|------|-----------|------------------|
| `cep-lookup` | Busca endereco por CEP | Validacao de localizacao |
| `cnpj-lookup` | Dados publicos de empresas | Verificar farmacias credenciadas |
| `ddd-lookup` | Estado/cidades por DDD | Identificar regiao do usuario |
| `get-banks` | Lista de bancos brasileiros | Orientar saques PIS/FGTS |
| `get-holidays` | Feriados nacionais | Informar horarios de atendimento |

**Exemplo de uso:**
```python
# Buscar endereco por CEP
result = await mcp_client.call_tool("brasil-api", "cep-lookup", {
    "cep": "01310100"
})
# Retorna: {"cep": "01310-100", "logradouro": "Av Paulista", ...}
```

---

### 2. Google Maps MCP
**Prioridade: ALTA**

Geolocalizacao e busca de locais proximos.

```bash
# Instalacao
npx -y @anthropic/mcp-google-maps
```

**Variaveis de ambiente:**
```bash
GOOGLE_MAPS_API_KEY=sua_chave_aqui
```

**Tools disponiveis:**
| Tool | Descricao | Uso no Ta na Mao |
|------|-----------|------------------|
| `search_nearby` | Busca lugares proximos | Farmacias, CRAS, loterias |
| `get_place_details` | Detalhes de estabelecimento | Horarios, telefone, avaliacao |
| `maps_geocode` | Endereco → Coordenadas | Converter CEP em lat/lng |
| `maps_reverse_geocode` | Coordenadas → Endereco | GPS do usuario |
| `maps_distance_matrix` | Distancias e tempos | Ordenar por proximidade |
| `maps_directions` | Rotas passo-a-passo | Direcoes ate a farmacia |

**Exemplo de uso:**
```python
# Buscar farmacias proximas
result = await mcp_client.call_tool("google-maps", "search_nearby", {
    "location": "-23.5505,-46.6333",
    "radius": 2000,
    "type": "pharmacy",
    "keyword": "farmacia popular"
})
```

---

### 3. PDF/OCR MCP
**Prioridade: MEDIA**

Processamento de documentos e receitas medicas.

```bash
# Instalacao (requer Python/uv)
uvx mcp-pdf
```

**Tools disponiveis:**
| Tool | Descricao | Uso no Ta na Mao |
|------|-----------|------------------|
| `extract_text` | Extrair texto de PDF | Processar documentos |
| `extract_images` | Extrair imagens de PDF | Extrair receitas escaneadas |
| `ocr_image` | OCR em imagem | Ler receitas medicas |

**Exemplo de uso:**
```python
# Processar receita medica
result = await mcp_client.call_tool("pdf-ocr", "ocr_image", {
    "image_url": "data:image/jpeg;base64,...",
    "language": "por"
})
# Retorna texto extraido da receita
```

---

### 4. Twilio MCP
**Prioridade: ALTA**

Comunicacao multicanal (SMS, WhatsApp, Voice).

```bash
# Instalacao
npx -y @anthropic/mcp-twilio --services messaging,voice
```

**Variaveis de ambiente:**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Tools disponiveis:**
| Tool | Descricao | Uso no Ta na Mao |
|------|-----------|------------------|
| `send_sms` | Enviar SMS | Notificacoes e menus USSD |
| `send_whatsapp` | Enviar WhatsApp | Canal principal |
| `make_call` | Fazer ligacao | 0800 e URA |
| `get_call_status` | Status de chamada | Monitoramento |

**Beneficios vs integracao direta:**
- 20.6% mais rapido
- 19.3% menos chamadas de API
- Retry automatico
- Logging unificado

---

### 5. Redis MCP
**Prioridade: MEDIA**

Cache e gerenciamento de sessoes.

```bash
# Instalacao
npx -y @redis/mcp
```

**Variaveis de ambiente:**
```bash
REDIS_URL=redis://localhost:6379/0
```

**Recursos:**
- Cache de consultas frequentes
- Sessoes multicanal
- Pub/sub para eventos
- Vector search (LangCache)

---

### 6. Playwright MCP (Microsoft)
**Prioridade: MEDIA**

Automacao de portais web (Gov.br, bancos).

```bash
# Instalacao
npx @playwright/mcp@latest
```

**Uso:**
- Consultas em sistemas sem API
- Scraping de dados publicos
- Automacao de formularios

**Diferencial:**
- Usa accessibility tree (nao visao)
- Mais rapido e confiavel
- Funciona headless

---

### 7. ChromaDB MCP (RAG)
**Prioridade: MEDIA**

Base de conhecimento vetorial para documentacao de beneficios.

```bash
# Instalacao
npx -y @anthropic/mcp-chroma
```

**Variaveis de ambiente:**
```bash
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

**Uso:**
- Armazenar docs de programas sociais
- Busca semantica por beneficios
- Contexto para o agente

---

## Configuracao

### Arquivo: `.mcp.json` (raiz do projeto)

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
    }
  }
}
```

### Variaveis de Ambiente

Adicione ao `.env`:

```bash
# =============================================================================
# MCP - Model Context Protocol
# =============================================================================

# Google Maps
GOOGLE_MAPS_API_KEY=sua_chave_google_maps

# Twilio MCP (se usar API Key em vez de Auth Token)
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma

# MCP Debug
MCP_DEBUG=false
MCP_LOG_LEVEL=info
```

---

## Integracao com o Agente

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENTE TA NA MAO                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            MCP Client (Wrapper Python)              │    │
│  └─────────────┬───────────────────────────────────────┘    │
│                │                                            │
│  ┌─────────────▼───────────────────────────────────────┐    │
│  │              MCP Server Manager                      │    │
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │
│  │   │ Brasil  │ │ Google  │ │  PDF    │ │ Twilio  │   │    │
│  │   │  API    │ │  Maps   │ │  OCR    │ │   MCP   │   │    │
│  │   └─────────┘ └─────────┘ └─────────┘ └─────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator │ Subagents │ Tools │ Context                 │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo de Wrapper Python

```python
# backend/app/agent/mcp/base.py
from typing import Any, Dict, Optional
import subprocess
import json

class MCPClient:
    """Cliente MCP para comunicacao com servidores."""

    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self._process: Optional[subprocess.Popen] = None

    async def start(self):
        """Inicia servidor MCP."""
        cmd = [self.config["command"]] + self.config.get("args", [])
        env = {**os.environ, **self.config.get("env", {})}
        self._process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env=env
        )

    async def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """Chama uma tool do servidor MCP."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": 1
        }
        # Envia request e aguarda resposta
        self._process.stdin.write(json.dumps(request).encode() + b"\n")
        self._process.stdin.flush()
        response = self._process.stdout.readline()
        return json.loads(response)

    async def stop(self):
        """Para servidor MCP."""
        if self._process:
            self._process.terminate()
            self._process = None
```

---

## Debug e Troubleshooting

### Modo Debug

```bash
# Executar Claude Code com debug de MCPs
claude --mcp-debug
```

### Logs

Os MCPs escrevem logs em:
- `~/.claude/logs/mcp/` (user scope)
- `.claude/logs/mcp/` (project scope)

### Problemas Comuns

| Problema | Causa | Solucao |
|----------|-------|---------|
| MCP nao inicia | Node.js nao instalado | `brew install node` |
| Timeout | Servidor lento | Aumentar timeout no config |
| Erro de permissao | Env vars nao setadas | Verificar `.env` |
| Tool nao encontrada | MCP desatualizado | `npx -y @pkg@latest` |

---

## Seguranca

### Protecao de Credenciais

O arquivo `.mcp.json` usa referencias a variaveis de ambiente:

```json
{
  "env": {
    "GOOGLE_MAPS_API_KEY": "${GOOGLE_MAPS_API_KEY}"
  }
}
```

**Nunca** hardcode credenciais no `.mcp.json`.

### Permissoes de Leitura

Configure no `.mcp.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

---

## Integracao no Codigo

### Inicializacao Automatica (main.py)

Os MCPs sao inicializados automaticamente no startup da aplicacao:

```python
# backend/app/main.py
from app.agent.mcp import init_mcp, mcp_manager, BrasilAPIMCP, GoogleMapsMCP, PDFOcrMCP

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.MCP_ENABLED:
        init_mcp(settings.MCP_CONFIG_PATH)

        # Registra wrappers
        mcp_manager.register_wrapper("brasil-api", BrasilAPIMCP)
        mcp_manager.register_wrapper("google-maps", GoogleMapsMCP)
        mcp_manager.register_wrapper("pdf-ocr", PDFOcrMCP)

        # Inicia servidores
        await mcp_manager.start_all()

    yield

    # Shutdown
    if settings.MCP_ENABLED:
        await mcp_manager.stop_all()
```

### Tools Integradas

As tools do agente usam MCPs automaticamente com fallback:

| Tool | MCP Primario | Fallback |
|------|--------------|----------|
| `buscar_cep.py` | BrasilAPIMCP | ViaCEP HTTP |
| `buscar_farmacia.py` | GoogleMapsMCP | Google Places API |
| `processar_receita.py` | PDFOcrMCP | Gemini Vision |

**Exemplo de uso em tool:**
```python
# backend/app/agent/tools/buscar_cep.py
from app.agent.mcp import mcp_manager, BrasilAPIMCP

async def buscar_cep(cep: str) -> dict:
    # Tenta MCP primeiro
    wrapper = mcp_manager.get_wrapper("brasil-api")
    if wrapper and isinstance(wrapper, BrasilAPIMCP):
        resultado = await wrapper.buscar_cep(cep)
        if resultado:
            return resultado.to_dict()

    # Fallback para API direta
    return await _buscar_cep_viacep(cep)
```

### Configuracao (config.py)

```python
# backend/app/config.py
class Settings(BaseSettings):
    # MCP Configuration
    MCP_ENABLED: bool = True
    MCP_CONFIG_PATH: str = ".mcp.json"
    MCP_TIMEOUT: int = 30000  # ms
```

### Desabilitar MCPs

Para usar apenas APIs diretas (fallbacks):

```bash
# .env
MCP_ENABLED=false
```

---

## Roadmap de MCPs

### Fase 1 - Configuracao (CONCLUIDA)
- [x] Wrappers Python para MCPs
- [x] Configuracao `.mcp.json`
- [x] Documentacao

### Fase 2 - Integracao (CONCLUIDA)
- [x] Brasil API MCP em `buscar_cep.py`
- [x] Google Maps MCP em `buscar_farmacia.py`
- [x] PDF/OCR MCP em `processar_receita.py`
- [x] Inicializacao automatica em `main.py`
- [x] Fallbacks para todas as tools

### Fase 3 (Planejada)
- [ ] Twilio MCP - Substituir integracao direta em SMS/Voice
- [ ] Redis MCP - Cache semantico
- [ ] ChromaDB MCP - RAG de beneficios

### Fase 4 (Futura)
- [ ] Playwright MCP - Automacao Gov.br
- [ ] n8n MCP - Workflows complexos
- [ ] Custom MCP - APIs Gov.br

---

## Referencias

### MCPs Oficiais
- [Twilio MCP](https://www.twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server)
- [Google Maps MCP](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Redis MCP](https://redis.io/blog/introducing-model-context-protocol-mcp-for-redis/)

### MCPs Comunitarios
- [Brasil API MCP](https://github.com/mauricio-cantu/brasil-api-mcp)
- [mcp-pdf](https://github.com/rsp2k/mcp-pdf)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

### Documentacao
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [Claude Code MCP Docs](https://code.claude.com/docs/en/settings)

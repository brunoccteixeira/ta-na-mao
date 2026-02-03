# Skill: Proteção de Dados do Cidadão (LGPD+)

Implementação completa de proteção de dados pessoais conforme LGPD, com consentimento granular e portabilidade.

## Contexto

- CPF é dado ultrassensível — base de todo o sistema
- LGPD (Lei 13.709/2018) é obrigatória para qualquer tratamento de dados pessoais
- Confiança do cidadão é pré-requisito para adoção da plataforma
- Dados de saúde e benefícios são dados sensíveis (Art. 5º, II)

## Dados Tratados pelo Tá na Mão

### Classificação por Sensibilidade
```
DADOS PESSOAIS (Art. 5º, I):
├── CPF
├── Nome completo
├── Data de nascimento
├── Endereço / CEP
├── Telefone
├── NIS (Número de Inscrição Social)
└── Composição familiar

DADOS SENSÍVEIS (Art. 5º, II):
├── Dados de saúde (receitas médicas, CID)
├── Condição de deficiência
├── Situação de violência
├── Orientação sexual / gênero
└── Origem racial/étnica (IBGE)

DADOS DE MENORES (Art. 14):
├── Dados de crianças/adolescentes
└── Requer consentimento do responsável

DADOS FINANCEIROS:
├── Renda familiar
├── Valores de benefícios
├── Dados de dinheiro esquecido (PIS/PASEP/FGTS)
└── Histórico de pagamentos
```

## Consentimento Granular

### Tela de Consentimento
```python
# backend/app/models/consentimento.py
class Consentimento(Base):
    __tablename__ = "consentimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cpf_hash: Mapped[str] = mapped_column(index=True)
    finalidade: Mapped[str]           # consulta_beneficio, farmacia, pesquisa
    dados_autorizados: Mapped[list]   # ["cpf", "renda", "composicao_familiar"]
    data_consentimento: Mapped[datetime]
    data_expiracao: Mapped[datetime | None]
    canal: Mapped[str]                # app, whatsapp, web
    revogado: Mapped[bool] = mapped_column(default=False)
    data_revogacao: Mapped[datetime | None]
    ip_hash: Mapped[str | None]
```

### Finalidades de Tratamento
```python
FINALIDADES = {
    "consulta_beneficio": {
        "descricao": "Consultar seus benefícios sociais",
        "dados_necessarios": ["cpf"],
        "dados_opcionais": ["nome", "endereco"],
        "base_legal": "consentimento",  # Art. 7º, I
        "retencao": "durante_sessao",
    },
    "elegibilidade": {
        "descricao": "Verificar quais benefícios você tem direito",
        "dados_necessarios": ["cpf", "renda", "composicao_familiar"],
        "dados_opcionais": ["endereco", "trabalho"],
        "base_legal": "consentimento",
        "retencao": "24_horas",
    },
    "farmacia": {
        "descricao": "Pedir medicamentos na Farmácia Popular",
        "dados_necessarios": ["cpf", "receita_medica"],
        "dados_opcionais": ["localizacao"],
        "base_legal": "consentimento",
        "dados_sensiveis": True,
        "retencao": "30_dias",
    },
    "encaminhamento_cras": {
        "descricao": "Gerar carta de encaminhamento para o CRAS",
        "dados_necessarios": ["cpf", "nome", "endereco"],
        "base_legal": "consentimento",
        "retencao": "90_dias",
    },
    "pesquisa": {
        "descricao": "Responder pesquisa para melhorar o app (anônimo)",
        "dados_necessarios": [],
        "dados_opcionais": ["municipio"],
        "base_legal": "consentimento",
        "retencao": "indefinida_anonimizada",
    },
}
```

### Verificação de Consentimento
```python
# backend/app/middleware/consentimento.py
async def verificar_consentimento(cpf_hash: str, finalidade: str) -> bool:
    """Verifica se cidadão consentiu para esta finalidade."""
    consentimento = await db.query(Consentimento).filter(
        Consentimento.cpf_hash == cpf_hash,
        Consentimento.finalidade == finalidade,
        Consentimento.revogado == False,
        or_(
            Consentimento.data_expiracao == None,
            Consentimento.data_expiracao > datetime.utcnow()
        )
    ).first()
    return consentimento is not None
```

## Portabilidade de Dados (Art. 18, V)

### Export de Dados
```python
# backend/app/routers/lgpd.py
@router.get("/api/v1/meus-dados/exportar")
async def exportar_dados(cpf: str = Depends(auth_cidadao), formato: str = "json"):
    """Exporta todos os dados do cidadão em formato legível."""
    cpf_hash = hash_cpf(cpf)

    dados = {
        "titular": {
            "cpf_parcial": f"***{cpf[3:9]}**",
            "data_export": datetime.utcnow().isoformat(),
        },
        "consentimentos": await buscar_consentimentos(cpf_hash),
        "consultas_realizadas": await buscar_historico_consultas(cpf_hash),
        "beneficios_encontrados": await buscar_beneficios_historico(cpf_hash),
        "atendimentos": await buscar_atendimentos(cpf_hash),
        "dados_armazenados": await listar_dados_armazenados(cpf_hash),
    }

    if formato == "json":
        return JSONResponse(dados)
    elif formato == "pdf":
        return await gerar_pdf_dados(dados)
```

## Direito ao Esquecimento (Art. 18, VI)

### Exclusão de Dados
```python
@router.delete("/api/v1/meus-dados/excluir")
async def excluir_dados(cpf: str = Depends(auth_cidadao), confirmar: bool = False):
    """Exclui todos os dados do cidadão da plataforma."""
    if not confirmar:
        return {
            "aviso": "Isso vai apagar TODOS os seus dados do Tá na Mão. "
                     "Você não vai perder seus benefícios, "
                     "só os dados que estão aqui no app.",
            "confirmar": "Envie novamente com confirmar=true para excluir.",
        }

    cpf_hash = hash_cpf(cpf)

    # Excluir dados de todas as tabelas
    await db.execute(delete(Consentimento).where(Consentimento.cpf_hash == cpf_hash))
    await db.execute(delete(HistoricoConsulta).where(HistoricoConsulta.cpf_hash == cpf_hash))
    await db.execute(delete(Atendimento).where(Atendimento.cpf_hash == cpf_hash))

    # Limpar cache Redis
    await redis.delete(f"session:{cpf_hash}")
    await redis.delete(f"wa_session:{cpf_hash}")

    # Registrar exclusão (sem dados pessoais, só o fato)
    await registrar_log_exclusao(cpf_hash)

    return {"mensagem": "Todos os seus dados foram excluídos com sucesso."}
```

## Auditoria de Acessos

### Log de Acesso a Dados
```python
# backend/app/middleware/auditoria.py
class AuditoriaMiddleware:
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)

        # Registrar acesso a dados pessoais
        if self._acessa_dados_pessoais(request):
            await registrar_acesso(
                endpoint=request.url.path,
                metodo=request.method,
                ip_hash=hash_ip(request.client.host),
                timestamp=datetime.utcnow(),
                status_code=response.status_code,
                # NÃO registrar payload ou dados pessoais
            )

        return response
```

### Simulação de Vazamento
```python
# backend/app/services/incidente.py
PLANO_RESPOSTA_INCIDENTE = {
    "etapas": [
        {
            "passo": 1,
            "acao": "Identificar escopo do vazamento",
            "responsavel": "Equipe técnica",
            "prazo": "2 horas",
        },
        {
            "passo": 2,
            "acao": "Conter o vazamento (revogar tokens, bloquear acesso)",
            "responsavel": "Equipe técnica",
            "prazo": "4 horas",
        },
        {
            "passo": 3,
            "acao": "Notificar ANPD (Autoridade Nacional de Proteção de Dados)",
            "responsavel": "DPO",
            "prazo": "72 horas (obrigatório)",
        },
        {
            "passo": 4,
            "acao": "Notificar titulares afetados",
            "responsavel": "DPO + Comunicação",
            "prazo": "72 horas",
        },
        {
            "passo": 5,
            "acao": "Documentar incidente e medidas tomadas",
            "responsavel": "DPO",
            "prazo": "30 dias",
        },
    ],
    "contatos": {
        "anpd": "https://www.gov.br/anpd/pt-br",
        "dpo_email": "dpo@tanamao.com.br",
    },
}
```

## Mensagens ao Cidadão (Linguagem Simples)

### Consentimento
```
Para consultar seus benefícios, vou precisar do seu CPF.

O que eu faço com ele:
✅ Consulto seus benefícios
✅ Verifico se você tem direito a outros
❌ NÃO guardo seus dados depois
❌ NÃO compartilho com ninguém
❌ NÃO vendo seus dados

Você pode apagar tudo a qualquer momento.

Posso continuar?
```

### Exclusão de Dados
```
Seus dados foram apagados do Tá na Mão.

Isso NÃO afeta seus benefícios — eles continuam normais.
Só apagamos o que estava aqui no app.

Se quiser usar de novo no futuro, é só entrar normalmente.
```

## Arquivos Relacionados
- `backend/app/models/consentimento.py` - Modelo de consentimento
- `backend/app/middleware/consentimento.py` - Verificação de consentimento
- `backend/app/middleware/auditoria.py` - Log de auditoria
- `backend/app/routers/lgpd.py` - Endpoints LGPD
- `backend/app/services/incidente.py` - Plano de resposta
- `.claude/skills/defense-in-depth.md` - Skill de segurança (complementar)

## Referências
- LGPD: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- ANPD: https://www.gov.br/anpd/pt-br
- Guia LGPD para Governo: https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/guias/guia-lgpd

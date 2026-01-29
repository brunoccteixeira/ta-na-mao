# Tá na Mão - Diretrizes de Desenvolvimento

## Contexto do Projeto
Plataforma de acesso a benefícios sociais brasileiros. Público-alvo:
cidadãos de baixa renda/escolaridade. Foco em linguagem simples e acessibilidade.

## Princípio 1: Pensar Antes de Codar
- Declarar suposições antes de implementar
- Se código toca em benefícios/CPF/valores, verificar impacto
- Perguntar quando não tiver certeza (dados sensíveis)
- Ler arquivos existentes antes de modificar

## Princípio 2: Simplicidade Primeiro
- Nenhuma feature além do solicitado
- Sem abstrações "para o futuro"
- Código legível > código "elegante"
- Manter linguagem simples em mensagens ao usuário

## Princípio 3: Mudanças Cirúrgicas
- Tocar apenas código necessário
- Não refatorar código que funciona
- Manter estilo existente (async/await, Pydantic)
- Remover apenas código que suas mudanças tornaram órfão

## Princípio 4: Execução Orientada a Objetivos
- Transformar instruções em critérios verificáveis
- Rodar testes antes de considerar tarefa concluída
- Tarefas multi-passo: verificar cada etapa

## Padrões Técnicos
- Backend: FastAPI, SQLAlchemy 2.0 async, Pydantic v2
- Frontend: React 18, TypeScript, Tailwind CSS
- Testes: pytest-asyncio (backend), Vitest (frontend)
- Agente: Gemini 2.0 Flash, resposta A2UI, MCP

## Regras de Acessibilidade
- Mensagens ao usuário em linguagem simples (5ª série)
- Evitar jargões técnicos/governamentais
- Botões claros com ações óbvias

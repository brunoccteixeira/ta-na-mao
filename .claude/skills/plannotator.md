# Skill: Revisão de Planos

Metodologia para revisar e validar planos de implementação antes de executar.

## Quando Usar

- Antes de implementar features complexas
- Quando mudanças afetam múltiplos arquivos
- Para tarefas que tocam dados sensíveis (CPF, valores)
- Quando há dúvida sobre a abordagem

## Estrutura de um Plano

```markdown
# Plano: [Nome da Feature/Task]

## Objetivo
[O que vamos fazer em 1-2 frases]

## Contexto
[Por que estamos fazendo isso]

## Arquivos Afetados
- `arquivo1.py` - [o que muda]
- `arquivo2.tsx` - [o que muda]

## Passos de Implementação
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

## Riscos e Mitigações
| Risco | Mitigação |
|-------|-----------|
| [risco 1] | [como evitar] |

## Critérios de Verificação
- [ ] Critério 1
- [ ] Critério 2

## Rollback
[Como desfazer se der errado]
```

## Checklist de Revisão

### Clareza
- [ ] O objetivo está claro?
- [ ] Entendo por que estamos fazendo isso?
- [ ] Os passos estão específicos o suficiente?

### Completude
- [ ] Todos os arquivos afetados estão listados?
- [ ] Considerei os casos de borda?
- [ ] Há plano de rollback?

### Segurança
- [ ] Toca em dados sensíveis (CPF, valores)?
- [ ] Há validação de entrada?
- [ ] Logs não expõem dados sensíveis?

### Simplicidade
- [ ] É a solução mais simples possível?
- [ ] Estou adicionando features além do pedido?
- [ ] Posso fazer menos e resolver o problema?

### Verificabilidade
- [ ] Como vou testar que funciona?
- [ ] Testes automatizados cobrem?
- [ ] Critérios de aceite são verificáveis?

## Perguntas para Validação

### Sobre o Problema
- "Qual problema exatamente estamos resolvendo?"
- "Para quem é esse problema?"
- "Como sabemos que é um problema?"

### Sobre a Solução
- "Por que essa abordagem e não outra?"
- "Qual a solução mais simples que funciona?"
- "O que pode dar errado?"

### Sobre a Implementação
- "Quais arquivos vou modificar?"
- "Em que ordem fazer as mudanças?"
- "Como verifico que funcionou?"

## Template de Feedback

```markdown
## Feedback do Plano

### ✅ Pontos Positivos
- [o que está bom]

### ⚠️ Pontos de Atenção
- [o que revisar]

### ❌ Bloqueadores
- [o que impede aprovação]

### Sugestões
- [melhorias propostas]
```

## Fluxo de Aprovação

```
1. Criar plano
2. Auto-revisar com checklist
3. Apresentar ao usuário
4. Incorporar feedback
5. Obter aprovação
6. Executar
```

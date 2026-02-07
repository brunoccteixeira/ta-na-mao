/**
 * Dicas praticas sobre onde/como obter cada documento.
 * Matching case-insensitive por substring — primeira regra vence.
 */

interface HintRule {
  keywords: string[];
  hint: string;
}

const rules: HintRule[] = [
  {
    keywords: ['cpf'],
    hint: 'Tire no site da Receita Federal ou nos Correios. E de graca.',
  },
  {
    keywords: ['nis', 'numero de identificacao social'],
    hint: 'Esta no cartao do Bolsa Familia, Cartao Cidadao ou no comprovante do CadUnico.',
  },
  {
    keywords: ['carteira de trabalho', 'ctps'],
    hint: 'Pode ser a fisica ou a digital (app Carteira de Trabalho Digital).',
  },
  {
    keywords: ['comprovante de renda', 'renda familiar', 'comprovante de rendimento'],
    hint: 'Contracheque, extrato bancario ou declaracao de autonomo assinada.',
  },
  {
    keywords: ['comprovante de residencia', 'comprovante de endereco'],
    hint: 'Conta de luz, agua ou telefone dos ultimos 3 meses no seu nome ou de familiar.',
  },
  {
    keywords: ['certidao de nascimento'],
    hint: 'Original ou segunda via. Peca no cartorio onde foi registrado.',
  },
  {
    keywords: ['certidao de casamento'],
    hint: 'Original ou segunda via. Peca no cartorio onde casou.',
  },
  {
    keywords: ['rg', 'identidade', 'documento de identificacao'],
    hint: 'RG, CNH ou Carteira de Trabalho servem. Leve original e copia.',
  },
  {
    keywords: ['titulo de eleitor'],
    hint: 'Disponivel no app e-Titulo ou no cartorio eleitoral.',
  },
  {
    keywords: ['conta de luz', 'conta de energia'],
    hint: 'Conta recente (ultimos 3 meses) no nome do titular ou familiar.',
  },
  {
    keywords: ['laudo medico', 'laudo'],
    hint: 'Laudo atualizado com descricao da condicao e codigo CID. Pode ser do SUS.',
  },
  {
    keywords: ['foto 3x4', 'foto'],
    hint: 'Foto recente, fundo branco. Papelarias fazem na hora ou use apps gratuitos.',
  },
  {
    keywords: ['receita medica', 'prescricao'],
    hint: 'Do SUS ou particular, legivel, com data recente e carimbo do medico.',
  },
  {
    keywords: ['comprovante de matricula', 'matricula escolar'],
    hint: 'Peca na secretaria da escola ou universidade.',
  },
  {
    keywords: ['cadunico', 'cadastro unico'],
    hint: 'Faca ou atualize no CRAS do seu municipio. Leve documentos de toda a familia.',
  },
  {
    keywords: ['declaracao escolar', 'frequencia escolar'],
    hint: 'Peca na secretaria da escola. Deve ter assinatura e carimbo.',
  },
  {
    keywords: ['comprovante bancario', 'extrato bancario', 'conta bancaria'],
    hint: 'Extrato ou comprovante de abertura de conta. Caixa e Banco do Brasil aceitam conta facil.',
  },
  {
    keywords: ['certidao negativa', 'certidao de debitos'],
    hint: 'Disponivel online nos sites da Receita Federal, PGFN ou prefeitura.',
  },
];

export function getDocumentHint(docText: string): string | undefined {
  const lower = docText.toLowerCase();
  for (const rule of rules) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      return rule.hint;
    }
  }
  return undefined;
}

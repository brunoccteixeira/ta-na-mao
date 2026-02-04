/**
 * Questions data for the eligibility wizard
 *
 * Contains all 20 questions with explanations and options
 */

import { BRAZILIAN_STATES } from '../engine/types';

// Question definition type
export interface QuestionDef {
  id: string;
  title: string;
  subtitle?: string;
  explanation: {
    title: string;
    text: string;
    examples?: string[];
  };
}

// All questions
export const QUESTIONS: Record<string, QuestionDef> = {
  estado: {
    id: 'estado',
    title: 'Em qual estado você mora?',
    subtitle: 'Selecione seu estado',
    explanation: {
      title: 'Por que perguntamos o estado?',
      text: 'Cada estado tem benefícios próprios além dos federais. Por exemplo, São Paulo tem o Renda Cidadã, Bahia tem o Bolsa Presença, e assim por diante.',
      examples: ['Renda SP (São Paulo)', 'Bolsa Presença (Bahia)', 'Vale Gás Bahia'],
    },
  },
  cidade: {
    id: 'cidade',
    title: 'Em qual cidade você mora?',
    subtitle: 'Digite para buscar sua cidade',
    explanation: {
      title: 'Por que perguntamos a cidade?',
      text: 'Muitas prefeituras oferecem benefícios municipais próprios, como auxílio-aluguel, cesta básica, ou descontos em transporte.',
      examples: ['Renda Mínima (Osasco)', 'Auxílio Aluguel Municipal', 'Passe Livre Municipal'],
    },
  },
  nascimento: {
    id: 'nascimento',
    title: 'Qual sua data de nascimento?',
    subtitle: 'Usamos para calcular sua idade',
    explanation: {
      title: 'Por que perguntamos a data de nascimento?',
      text: 'Vários benefícios têm requisitos de idade. O BPC Idoso é para quem tem 65 anos ou mais. Jovens podem ter acesso a programas de primeiro emprego.',
      examples: ['BPC Idoso (65+ anos)', 'Jovem Aprendiz (14-24 anos)', 'Meia-entrada (estudantes)'],
    },
  },
  moradia: {
    id: 'moradia',
    title: 'Como é sua moradia?',
    subtitle: 'Selecione a situação que mais se aproxima',
    explanation: {
      title: 'Por que perguntamos sobre moradia?',
      text: 'Programas de habitação como Minha Casa Minha Vida são para quem não tem casa própria. Quem mora em área rural pode ter acesso a benefícios específicos.',
      examples: ['Minha Casa Minha Vida', 'Auxílio Aluguel', 'Luz para Todos (zona rural)'],
    },
  },
  familia: {
    id: 'familia',
    title: 'Quantas pessoas moram na sua casa?',
    subtitle: 'Conte você e todos que moram junto',
    explanation: {
      title: 'Por que perguntamos o tamanho da família?',
      text: 'A renda per capita (por pessoa) é calculada dividindo a renda total pelo número de moradores. Muitos benefícios usam esse valor como critério.',
      examples: ['Bolsa Família (renda per capita até R$ 218)', 'BPC (renda per capita até 1/4 do salário mínimo)'],
    },
  },
  filhos: {
    id: 'filhos',
    title: 'Sobre crianças e idosos na família',
    subtitle: 'Informe se há dependentes especiais',
    explanation: {
      title: 'Por que perguntamos sobre dependentes?',
      text: 'Famílias com crianças, idosos ou gestantes podem receber valores adicionais no Bolsa Família e ter acesso a outros benefícios específicos.',
      examples: ['Adicional criança 0-6 anos (+R$150)', 'Auxílio gestante (+R$50)', 'BPC Idoso'],
    },
  },
  trabalho: {
    id: 'trabalho',
    title: 'Qual sua situação de trabalho?',
    subtitle: 'Selecione a opção principal',
    explanation: {
      title: 'Por que perguntamos sobre trabalho?',
      text: 'Trabalhadores informais, autônomos e desempregados têm acesso a benefícios diferentes. Quem tem MEI pode receber Bolsa Família sob certas condições.',
      examples: ['Seguro-desemprego', 'Abono salarial PIS/PASEP', 'Auxílio para MEI'],
    },
  },
  renda: {
    id: 'renda',
    title: 'Qual a renda total da família por mês?',
    subtitle: 'Some todos os ganhos de quem mora na casa',
    explanation: {
      title: 'Por que perguntamos a renda?',
      text: 'A maioria dos benefícios sociais tem limite de renda. Quanto menor a renda, mais benefícios você pode acessar.',
      examples: ['Bolsa Família: até R$ 218/pessoa', 'CadÚnico: até 3 salários mínimos', 'MCMV: até R$ 8.000 família'],
    },
  },
  beneficios: {
    id: 'beneficios',
    title: 'Você já recebe algum benefício?',
    subtitle: 'Marque os que você já tem',
    explanation: {
      title: 'Por que perguntamos sobre benefícios atuais?',
      text: 'Evitamos sugerir o que você já recebe e identificamos benefícios complementares. Alguns benefícios são automáticos para quem recebe Bolsa Família.',
      examples: ['Auxílio Gás (automático com BF)', 'Pé-de-Meia (automático para estudantes)', 'Tarifa Social de Energia'],
    },
  },
  especial: {
    id: 'especial',
    title: 'Situações especiais',
    subtitle: 'Marque se alguma se aplica a você ou sua família',
    explanation: {
      title: 'Por que perguntamos sobre situações especiais?',
      text: 'Pessoas com deficiência, gestantes, estudantes e outras situações podem ter acesso a benefícios específicos e prioridade no atendimento.',
      examples: ['BPC/LOAS para PCD', 'Auxílio gestante', 'Passe Livre (PCD)', 'Dignidade Menstrual'],
    },
  },
  interesses: {
    id: 'interesses',
    title: 'O que mais você precisa?',
    subtitle: 'Assim podemos mostrar benefícios relacionados',
    explanation: {
      title: 'Por que perguntamos seus interesses?',
      text: 'Identificamos oportunidades de economia e benefícios que você pode não conhecer, como Tarifa Social de Energia e Farmácia Popular.',
      examples: ['Tarifa Social (até 65% desconto luz)', 'Farmácia Popular (remédios grátis)', 'Passe Livre'],
    },
  },
};

// Estado options (UFs)
export const ESTADO_OPTIONS = Object.entries(BRAZILIAN_STATES).map(([value, label]) => ({
  value,
  label,
}));

// Moradia options
export const MORADIA_OPTIONS = [
  { value: 'propria', label: 'Casa própria', description: 'Quitada ou financiada' },
  { value: 'alugada', label: 'Casa alugada', description: 'Paga aluguel todo mês' },
  { value: 'cedida', label: 'Casa cedida/emprestada', description: 'Não paga aluguel' },
  { value: 'irregular', label: 'Ocupação irregular', description: 'Comunidade, invasão' },
  { value: 'rua', label: 'Em situação de rua', description: 'Sem moradia fixa' },
];

// Work situation options
export const TRABALHO_OPTIONS = [
  { value: 'clt', label: 'Carteira assinada (CLT)', description: 'Trabalho formal' },
  { value: 'mei', label: 'MEI', description: 'Microempreendedor Individual' },
  { value: 'autonomo', label: 'Autônomo / Informal', description: 'Bicos, serviços gerais' },
  { value: 'app', label: 'Aplicativo', description: 'Uber, iFood, 99, Rappi' },
  { value: 'desempregado', label: 'Desempregado', description: 'Procurando emprego' },
  { value: 'aposentado', label: 'Aposentado / Pensionista', description: 'INSS' },
  { value: 'do_lar', label: 'Do lar', description: 'Cuida da casa/família' },
  { value: 'estudante', label: 'Estudante', description: 'Apenas estuda' },
];

// Sectoral options
export const SETORIAL_OPTIONS = [
  { value: 'agricultor', label: 'Agricultor familiar', description: 'Produção rural pequena' },
  { value: 'pescador', label: 'Pescador artesanal', description: 'Pesca de subsistência' },
  { value: 'catador', label: 'Catador de recicláveis', description: 'Coleta e reciclagem' },
  { value: 'domestica', label: 'Trabalhador doméstico', description: 'Empregada, diarista' },
];

// Current benefits options
export const BENEFICIOS_ATUAIS_OPTIONS = [
  { value: 'bolsa_familia', label: 'Bolsa Família' },
  { value: 'bpc', label: 'BPC/LOAS' },
  { value: 'aposentadoria', label: 'Aposentadoria/Pensão INSS' },
  { value: 'seguro_desemprego', label: 'Seguro-Desemprego' },
  { value: 'auxilio_gas', label: 'Auxílio Gás' },
  { value: 'tarifa_social', label: 'Tarifa Social de Energia' },
  { value: 'outro', label: 'Outro benefício' },
  { value: 'nenhum', label: 'Nenhum' },
];

// Interests options
export const INTERESSES_OPTIONS = [
  { value: 'luz', label: 'Economizar na conta de luz', description: 'Tarifa Social de Energia' },
  { value: 'remedio', label: 'Remédios gratuitos', description: 'Farmácia Popular' },
  { value: 'moradia', label: 'Conseguir uma casa', description: 'Minha Casa Minha Vida' },
  { value: 'emprego', label: 'Encontrar emprego', description: 'SINE, cursos gratuitos' },
  { value: 'capacitacao', label: 'Cursos de capacitação', description: 'Qualificação profissional' },
];

// Special situations options
export const SITUACOES_ESPECIAIS_OPTIONS = [
  { value: 'pcd', label: 'Pessoa com deficiência', description: 'Física, mental, intelectual ou sensorial' },
  { value: 'gestante', label: 'Gestante', description: 'Você ou alguém da família' },
  { value: 'idoso65', label: 'Idoso 65+ anos', description: 'Você ou alguém da família' },
  { value: 'estudante', label: 'Estudante', description: 'Escola pública ou particular' },
  { value: 'vitima_violencia', label: 'Vítima de violência doméstica', description: 'Em situação de risco' },
  { value: 'refugiado', label: 'Refugiado / Imigrante', description: 'Situação migratória' },
];

// Money presets for income
export const RENDA_PRESETS = [300, 600, 1000, 1500, 2000, 3000];

// Fetch cities from IBGE API
export async function fetchCitiesByState(uf: string): Promise<{ value: string; label: string; extra: string }[]> {
  try {
    const response = await fetch(
      `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`
    );
    const data = await response.json();

    return data.map((city: { id: number; nome: string }) => ({
      value: city.id.toString(),
      label: city.nome,
      extra: city.id.toString(), // IBGE code
    }));
  } catch (error) {
    console.error('Error fetching cities:', error);
    return [];
  }
}

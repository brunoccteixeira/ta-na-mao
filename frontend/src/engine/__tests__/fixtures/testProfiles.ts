/**
 * Test profiles representing real-world citizen scenarios.
 * Used across evaluator tests with real benefit data.
 */
import { CitizenProfile, DEFAULT_CITIZEN_PROFILE } from '../../types';

/** Helper: merge partial profile over defaults */
export function makeProfile(overrides: Partial<CitizenProfile>): CitizenProfile {
  return { ...DEFAULT_CITIZEN_PROFILE, ...overrides };
}

// ─── 8 canonical profiles ───

/** Família em extrema pobreza com 2 filhos pequenos */
export const extremaPobrezaComFilhos = makeProfile({
  estado: 'MA',
  municipioIbge: '2111300',
  pessoasNaCasa: 4,
  quantidadeFilhos: 2,
  rendaFamiliarMensal: 400,
  cadastradoCadunico: true,
  temCrianca0a6: true,
  temGestante: false,
});

/** Idoso 67 anos morando sozinho, sem renda */
export const idosoSozinho = makeProfile({
  estado: 'SP',
  municipioIbge: '3550308',
  idade: 67,
  pessoasNaCasa: 1,
  rendaFamiliarMensal: 0,
  temIdoso65Mais: true,
  cadastradoCadunico: true,
});

/** PcD com baixa renda, CadÚnico */
export const pcdBaixaRenda = makeProfile({
  estado: 'RJ',
  municipioIbge: '3304557',
  idade: 35,
  pessoasNaCasa: 2,
  rendaFamiliarMensal: 500,
  temPcd: true,
  cadastradoCadunico: true,
});

/** Trabalhador CLT com renda de R$ 2.000 */
export const trabalhadorCLT = makeProfile({
  estado: 'MG',
  municipioIbge: '3106200',
  idade: 30,
  pessoasNaCasa: 3,
  rendaFamiliarMensal: 2000,
  trabalhoFormal: true,
  temCarteiraAssinada: true,
  tempoCarteiraAssinada: 24,
});

/** Estudante de rede pública em SP */
export const estudanteRedePublica = makeProfile({
  estado: 'SP',
  municipioIbge: '3550308',
  idade: 17,
  pessoasNaCasa: 4,
  rendaFamiliarMensal: 3200,
  estudante: true,
  redePublica: true,
});

/** Pescador artesanal no MA */
export const pescadorArtesanal = makeProfile({
  estado: 'MA',
  municipioIbge: '2111300',
  idade: 45,
  pessoasNaCasa: 3,
  rendaFamiliarMensal: 800,
  pescadorArtesanal: true,
  cadastradoCadunico: true,
  moradiaZonaRural: true,
});

/** MEI entregador de app, renda R$ 1.500 */
export const meiEntregador = makeProfile({
  estado: 'SP',
  municipioIbge: '3550308',
  idade: 28,
  pessoasNaCasa: 2,
  rendaFamiliarMensal: 1500,
  temMei: true,
  trabalhaAplicativo: true,
});

/** Família numerosa: 6 pessoas, 4 filhos, gestante */
export const familiaNumerosa = makeProfile({
  estado: 'BA',
  municipioIbge: '2927408',
  idade: 32,
  pessoasNaCasa: 6,
  quantidadeFilhos: 4,
  rendaFamiliarMensal: 1200,
  temGestante: true,
  temCrianca0a6: true,
  cadastradoCadunico: true,
});

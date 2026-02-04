/**
 * shareResult - Serializa perfil do cidadão para compartilhamento via link
 * SEGURANÇA: Nunca inclui CPF, nome ou dados identificáveis
 */

import type { CitizenProfile } from '../components/EligibilityWizard/types';

// Campos seguros para compartilhar (sem PII)
interface ShareableProfile {
  uf?: string;
  m?: string; // municipio
  mi?: string; // municipioIbge
  p: number; // pessoasNaCasa
  f: number; // quantidadeFilhos
  i65: boolean; // temIdoso65Mais
  g: boolean; // temGestante
  pcd: boolean; // temPcd
  c06: boolean; // temCrianca0a6
  r: number; // rendaFamiliarMensal
  tf: boolean; // trabalhoFormal
  bf: boolean; // recebeBolsaFamilia
  bpc: boolean; // recebeBpc
  cad: boolean; // cadastradoCadunico
  cp: boolean; // temCasaPropria
  zr: boolean; // moradiaZonaRural
  mei: boolean;
  app: boolean; // trabalhaAplicativo
  agr: boolean; // agricultorFamiliar
  pes: boolean; // pescadorArtesanal
  cat: boolean; // catadorReciclavel
  est: boolean; // estudante
  rp: boolean; // redePublica
}

export function encodeProfile(profile: CitizenProfile): string {
  const shareable: ShareableProfile = {
    uf: profile.uf,
    m: profile.municipio,
    mi: profile.municipioIbge,
    p: profile.pessoasNaCasa,
    f: profile.quantidadeFilhos,
    i65: profile.temIdoso65Mais,
    g: profile.temGestante,
    pcd: profile.temPcd,
    c06: profile.temCrianca0a6,
    r: profile.rendaFamiliarMensal,
    tf: profile.trabalhoFormal,
    bf: profile.recebeBolsaFamilia,
    bpc: profile.recebeBpc,
    cad: profile.cadastradoCadunico,
    cp: profile.temCasaPropria,
    zr: profile.moradiaZonaRural,
    mei: profile.temMei,
    app: profile.trabalhaAplicativo,
    agr: profile.agricultorFamiliar,
    pes: profile.pescadorArtesanal,
    cat: profile.catadorReciclavel,
    est: profile.estudante,
    rp: profile.redePublica,
  };

  const json = JSON.stringify(shareable);
  return btoa(encodeURIComponent(json));
}

export function decodeProfile(encoded: string): Partial<CitizenProfile> | null {
  try {
    const json = decodeURIComponent(atob(encoded));
    const s: ShareableProfile = JSON.parse(json);

    return {
      uf: s.uf,
      municipio: s.m,
      municipioIbge: s.mi,
      pessoasNaCasa: s.p,
      quantidadeFilhos: s.f,
      temIdoso65Mais: s.i65,
      temGestante: s.g,
      temPcd: s.pcd,
      temCrianca0a6: s.c06,
      rendaFamiliarMensal: s.r,
      trabalhoFormal: s.tf,
      recebeBolsaFamilia: s.bf,
      recebeBpc: s.bpc,
      cadastradoCadunico: s.cad,
      temCasaPropria: s.cp,
      moradiaZonaRural: s.zr,
      temMei: s.mei,
      trabalhaAplicativo: s.app,
      agricultorFamiliar: s.agr,
      pescadorArtesanal: s.pes,
      catadorReciclavel: s.cat,
      estudante: s.est,
      redePublica: s.rp,
      // Explicitly NOT included: cpf, nome
    };
  } catch {
    return null;
  }
}

export function generateShareLink(profile: CitizenProfile): string {
  const encoded = encodeProfile(profile);
  const baseUrl = window.location.origin;
  return `${baseUrl}/descobrir?r=${encoded}`;
}

export function generateWhatsAppLink(profile: CitizenProfile, valorMensal: number): string {
  const shareLink = generateShareLink(profile);
  const valorFormatted = valorMensal.toLocaleString('pt-BR', { maximumFractionDigits: 0 });
  const text = `Descobri que posso receber ate R$ ${valorFormatted}/mes em beneficios sociais! Veja os seus tambem: ${shareLink}`;
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
}

export function generateSmsLink(profile: CitizenProfile, valorMensal: number): string {
  const shareLink = generateShareLink(profile);
  const valorFormatted = valorMensal.toLocaleString('pt-BR', { maximumFractionDigits: 0 });
  const text = `Descubra seus beneficios sociais (ate R$ ${valorFormatted}/mes): ${shareLink}`;
  return `sms:?body=${encodeURIComponent(text)}`;
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

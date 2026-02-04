/**
 * generateCarta - Gera carta de encaminhamento para o CRAS em PDF
 * Usa jspdf para gerar client-side sem servidor
 * SEGURANÇA: Nunca inclui CPF no documento
 */

import { jsPDF } from 'jspdf';
import QRCode from 'qrcode';
import type { CitizenProfile, TriagemResult, EligibilityResult } from '../components/EligibilityWizard/types';
import { generateShareLink } from './shareResult';

export async function generateCarta(
  profile: CitizenProfile,
  result: TriagemResult
): Promise<void> {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;
  let y = margin;

  // --- Header ---
  doc.setFillColor(16, 185, 129); // emerald-500
  doc.rect(0, 0, pageWidth, 35, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('Ta na Mao', margin, 15);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('Carta de Encaminhamento - Beneficios Sociais', margin, 23);

  const today = new Date().toLocaleDateString('pt-BR');
  doc.text(`Data: ${today}`, margin, 30);

  y = 45;

  // --- Dados do cidadao (sem CPF) ---
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('Dados do Cidadao', margin, y);
  y += 8;

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');

  const cidadaoInfo = [
    `Municipio: ${profile.municipio || 'Nao informado'} - ${profile.uf || 'N/A'}`,
    `Pessoas na casa: ${profile.pessoasNaCasa}`,
    `Filhos menores: ${profile.quantidadeFilhos}`,
    `Renda familiar: R$ ${profile.rendaFamiliarMensal.toLocaleString('pt-BR')}`,
    `CadUnico: ${profile.cadastradoCadunico ? 'Sim' : 'Nao'}`,
  ];

  cidadaoInfo.forEach(line => {
    doc.text(line, margin, y);
    y += 6;
  });

  y += 5;

  // --- Resumo de elegibilidade ---
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('Resultado da Triagem', margin, y);
  y += 8;

  // Summary box
  doc.setFillColor(240, 253, 244); // emerald-50
  doc.setDrawColor(16, 185, 129);
  doc.roundedRect(margin, y, contentWidth, 20, 3, 3, 'FD');

  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(5, 150, 105); // emerald-600
  doc.text(
    `${result.beneficiosElegiveis.length} beneficio(s) identificado(s)`,
    margin + 5,
    y + 8
  );

  if (result.valorPotencialMensal > 0) {
    doc.text(
      `Valor estimado: R$ ${result.valorPotencialMensal.toLocaleString('pt-BR')}/mes`,
      margin + 5,
      y + 15
    );
  }

  y += 28;

  // --- Lista de benefícios elegíveis ---
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.text('Beneficios Identificados:', margin, y);
  y += 8;

  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');

  const beneficios: EligibilityResult[] = result.beneficiosElegiveis;
  beneficios.forEach((b, i) => {
    if (y > 250) {
      doc.addPage();
      y = margin;
    }

    doc.setFont('helvetica', 'bold');
    doc.text(`${i + 1}. ${b.programaNome}`, margin + 2, y);
    y += 5;

    doc.setFont('helvetica', 'normal');
    if (b.valorEstimado) {
      doc.text(`   Valor estimado: R$ ${b.valorEstimado.toLocaleString('pt-BR')}/mes`, margin + 2, y);
      y += 5;
    }
    if (b.ondeSolicitar) {
      doc.text(`   Onde solicitar: ${b.ondeSolicitar}`, margin + 2, y);
      y += 5;
    }
    doc.text(`   ${b.motivo}`, margin + 2, y);
    y += 7;
  });

  y += 5;

  // --- Documentos necessários ---
  if (result.documentosNecessarios.length > 0) {
    if (y > 240) {
      doc.addPage();
      y = margin;
    }

    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('Documentos Necessarios:', margin, y);
    y += 7;

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    result.documentosNecessarios.forEach(doc_name => {
      doc.text(`  - ${doc_name}`, margin + 2, y);
      y += 5;
    });
  }

  y += 8;

  // --- QR Code ---
  if (y > 220) {
    doc.addPage();
    y = margin;
  }

  try {
    const shareLink = generateShareLink(profile);
    const qrDataUrl = await QRCode.toDataURL(shareLink, { width: 120, margin: 1 });
    doc.addImage(qrDataUrl, 'PNG', pageWidth - margin - 30, y, 30, 30);

    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    doc.text('Leia o QR Code para ver', pageWidth - margin - 30, y + 33);
    doc.text('o resultado online', pageWidth - margin - 30, y + 37);
  } catch {
    // QR code generation failed, skip
  }

  // --- Footer/Instrucao ---
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(0, 0, 0);
  doc.text('Apresente esta carta no CRAS mais proximo.', margin, y + 5);

  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(120, 120, 120);
  doc.text(
    'Esta carta e uma pre-triagem automatizada e nao garante a concessao dos beneficios.',
    margin,
    y + 12
  );
  doc.text(
    'A elegibilidade final sera confirmada pelo orgao responsavel.',
    margin,
    y + 17
  );

  // --- Page footer ---
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(180, 180, 180);
    doc.text(
      `Ta na Mao - Seus direitos, entregues na sua mao | Pagina ${i}/${pageCount}`,
      margin,
      doc.internal.pageSize.getHeight() - 10
    );
  }

  // Download
  const filename = `carta-encaminhamento-${today.replace(/\//g, '-')}.pdf`;
  doc.save(filename);
}

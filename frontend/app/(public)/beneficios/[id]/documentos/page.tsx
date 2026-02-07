import type { Metadata } from 'next';
import { loadBenefitsCatalogServer, getBenefitByIdServer } from '../../../../../src/engine/catalog.server';
import DocumentsClient from './DocumentsClient';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const catalog = loadBenefitsCatalogServer();
  const benefit = getBenefitByIdServer(catalog, id);

  if (!benefit) {
    return { title: 'Documentos necessarios | Ta na Mao' };
  }

  return {
    title: `Documentos para ${benefit.name} | Ta na Mao`,
    description: `Lista de ${benefit.documentsRequired.length} documentos necessarios para solicitar o ${benefit.name}. Marque o que ja tem.`,
  };
}

export default async function DocumentsPage({ params }: PageProps) {
  const { id } = await params;
  return <DocumentsClient id={id} />;
}

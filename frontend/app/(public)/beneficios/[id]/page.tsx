import type { Metadata } from 'next';
import { loadBenefitsCatalogServer, getBenefitByIdServer } from '../../../../src/engine/catalog.server';
import BenefitDetailClient from './BenefitDetailClient';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const catalog = loadBenefitsCatalogServer();
  const benefit = getBenefitByIdServer(catalog, id);

  if (!benefit) {
    return { title: 'Beneficio nao encontrado | Ta na Mao' };
  }

  return {
    title: `${benefit.name} | Ta na Mao`,
    description: benefit.shortDescription,
  };
}

export default async function BenefitDetailPage({ params }: PageProps) {
  const { id } = await params;
  return <BenefitDetailClient id={id} />;
}

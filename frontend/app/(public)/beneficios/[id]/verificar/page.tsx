import type { Metadata } from 'next';
import { loadBenefitsCatalogServer, getBenefitByIdServer } from '../../../../../src/engine/catalog.server';
import BenefitCheckerClient from './BenefitCheckerClient';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const catalog = loadBenefitsCatalogServer();
  const benefit = getBenefitByIdServer(catalog, id);

  if (!benefit) {
    return { title: 'Verificar elegibilidade | Ta na Mao' };
  }

  return {
    title: `Verificar ${benefit.name} | Ta na Mao`,
    description: `Verifique se voce tem direito ao ${benefit.name}`,
  };
}

export default async function BenefitCheckerPage({ params }: PageProps) {
  const { id } = await params;
  return <BenefitCheckerClient id={id} />;
}

import type { Metadata } from 'next';
import { loadBenefitsCatalogServer, getBenefitByIdServer } from '../../../../../src/engine/catalog.server';
import JourneyClient from './JourneyClient';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const catalog = loadBenefitsCatalogServer();
  const benefit = getBenefitByIdServer(catalog, id);

  if (!benefit) {
    return { title: 'Passo a passo | Ta na Mao' };
  }

  return {
    title: `Como conseguir ${benefit.name} - Passo a passo | Ta na Mao`,
    description: `Guia completo com tudo que voce precisa fazer para conseguir o ${benefit.name}`,
  };
}

export default async function JourneyPage({ params }: PageProps) {
  const { id } = await params;
  return <JourneyClient id={id} />;
}

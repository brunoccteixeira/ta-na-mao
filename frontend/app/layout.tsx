import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Providers from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  metadataBase: new URL('https://tanamao.com.br'),
  title: 'Tá na Mão - Descubra seus direitos sociais',
  description:
    'Plataforma gratuita que ajuda brasileiros a descobrirem quais benefícios sociais podem ter direito. Mais de 1.300 benefícios federais, estaduais, setoriais e municipais em um só lugar.',
  manifest: '/manifest.json',
  keywords: [
    'benefícios sociais',
    'Bolsa Família',
    'BPC',
    'CadÚnico',
    'CRAS',
    'Farmácia Popular',
    'Tarifa Social',
    'Minha Casa Minha Vida',
    'direitos sociais',
    'assistência social',
    'benefícios governo',
  ],
  openGraph: {
    title: 'Tá na Mão - Descubra seus direitos sociais',
    description:
      'Mais de 1.300 benefícios mapeados. Simulação gratuita, sem cadastro, sem senha Gov.br.',
    url: 'https://tanamao.com.br',
    siteName: 'Tá na Mão',
    locale: 'pt_BR',
    type: 'website',
    images: [
      {
        url: '/images/og-cover.png',
        width: 1200,
        height: 630,
        alt: 'Tá na Mão - Descubra seus direitos sociais',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tá na Mão - Descubra seus direitos sociais',
    description:
      'Mais de 1.300 benefícios mapeados. Simulação gratuita, sem cadastro.',
    images: ['/images/og-cover.png'],
  },
  other: {
    'theme-color': '#10b981',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

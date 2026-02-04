import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Providers from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Ta na Mao - Descubra seus direitos sociais',
  description:
    'Plataforma gratuita que ajuda brasileiros a descobrirem quais beneficios sociais podem ter direito. Beneficios federais, estaduais e setoriais em um so lugar.',
  manifest: '/manifest.json',
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

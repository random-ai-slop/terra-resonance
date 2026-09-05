import type { Metadata } from 'next';
import './globals.css';
import { LocaleProvider } from '@/lib/i18n/provider';
export const metadata: Metadata = {
  title: 'Terra Resonance · Earth normal modes',
  description:
    'Explore planetary normal modes through eigenfunctions, interior structure and material motion.',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <LocaleProvider>{children}</LocaleProvider>
      </body>
    </html>
  );
}

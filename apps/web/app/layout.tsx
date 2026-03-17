import './globals.css';
import type { Metadata } from 'next';

import HeaderNav from '@/app/components/HeaderNav';
import { AuthProvider } from '@/lib/auth-context';

export const metadata: Metadata = {
  title: 'Autonomous API Builder',
  description: 'AI-powered API build planning dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <header style={{ borderBottom: '1px solid #e2e8f0', background: '#fff' }}>
            <HeaderNav />
          </header>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

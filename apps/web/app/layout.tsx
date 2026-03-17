import './globals.css';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Autonomous API Builder',
  description: 'AI-powered API build planning dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header style={{ borderBottom: '1px solid #e2e8f0', background: '#fff' }}>
          <nav className="container" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <strong>Autonomous API Builder</strong>
            <Link href="/">Home</Link>
            <Link href="/dashboard">Dashboard</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}

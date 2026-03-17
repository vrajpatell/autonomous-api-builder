'use client';

import Link from 'next/link';
import { useState } from 'react';

import { useAuth } from '@/lib/auth-context';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <main className="container">
      <section className="card" style={{ padding: '1.5rem', maxWidth: 480 }}>
        <h1>Log in</h1>
        <form onSubmit={onSubmit} className="grid" style={{ gap: '0.75rem' }}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email" required />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="Password"
            required
          />
          <button type="submit">Log in</button>
        </form>
        {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
        <p>
          No account? <Link href="/register">Register</Link>
        </p>
      </section>
    </main>
  );
}

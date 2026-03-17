'use client';

import Link from 'next/link';
import { useState } from 'react';

import { useAuth } from '@/lib/auth-context';

export default function RegisterPage() {
  const { register } = useAuth();
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await register({ display_name: displayName || undefined, email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    }
  };

  return (
    <main className="container">
      <section className="card" style={{ padding: '1.5rem', maxWidth: 480 }}>
        <h1>Create account</h1>
        <form onSubmit={onSubmit} className="grid" style={{ gap: '0.75rem' }}>
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            type="text"
            placeholder="Display name"
          />
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email" required />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="Password (min 8 chars)"
            required
            minLength={8}
          />
          <button type="submit">Register</button>
        </form>
        {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
        <p>
          Already have an account? <Link href="/login">Log in</Link>
        </p>
      </section>
    </main>
  );
}

'use client';

import Link from 'next/link';

import { useAuth } from '@/lib/auth-context';

export default function HeaderNav() {
  const { user, logout } = useAuth();

  return (
    <nav className="container" style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '0.75rem 0' }}>
      <strong>Autonomous API Builder</strong>
      <Link href="/">Home</Link>
      {user ? (
        <>
          <Link href="/dashboard">Dashboard</Link>
          <span style={{ marginLeft: 'auto' }}>{user.display_name || user.email}</span>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <span style={{ marginLeft: 'auto' }} />
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </>
      )}
    </nav>
  );
}

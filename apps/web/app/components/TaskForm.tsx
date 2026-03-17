'use client';

import { useState } from 'react';

import { createTask } from '@/lib/api';
import { Task } from '@/lib/types';

type Props = {
  onCreated: (task: Task) => void;
  token: string;
};

export default function TaskForm({ onCreated, token }: Props) {
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const created = await createTask({ title, user_prompt: prompt }, token);
      onCreated(created);
      setTitle('');
      setPrompt('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <h3>Submit Build Request</h3>
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} minLength={3} required />
      </label>
      <label style={{ display: 'block', marginTop: '0.75rem' }}>
        Prompt
        <textarea
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          minLength={10}
          required
        />
      </label>
      {error && <p style={{ color: '#dc2626' }}>{error}</p>}
      <button type="submit" disabled={loading} style={{ marginTop: '0.75rem' }}>
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}

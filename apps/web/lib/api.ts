import { CreateTaskPayload, Task } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || 'Request failed');
  }

  return response.json() as Promise<T>;
}

export function listTasks(): Promise<Task[]> {
  return request<Task[]>('/tasks');
}

export function createTask(payload: CreateTaskPayload): Promise<Task> {
  return request<Task>('/tasks', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getTask(taskId: number): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`);
}

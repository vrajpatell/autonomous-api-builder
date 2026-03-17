import { AuthResponse, CreateTaskPayload, LoginPayload, RegisterPayload, Task, User } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

async function request<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

export function register(payload: RegisterPayload): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginPayload): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function me(token: string): Promise<User> {
  return request<User>('/auth/me', undefined, token);
}

export function listTasks(token: string): Promise<Task[]> {
  return request<Task[]>('/tasks', undefined, token);
}

export function createTask(payload: CreateTaskPayload, token: string): Promise<Task> {
  return request<Task>(
    '/tasks',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function getTask(taskId: number, token: string): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`, undefined, token);
}

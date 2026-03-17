import {
  AuthResponse,
  CreateTaskPayload,
  ListTaskParams,
  LoginPayload,
  PaginatedTaskResponse,
  RegisterPayload,
  Task,
  User,
} from './types';

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

export function listTasks(token: string, params: ListTaskParams = {}): Promise<PaginatedTaskResponse> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value));
    }
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<PaginatedTaskResponse>(`/tasks${suffix}`, undefined, token);
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

export async function downloadArtifact(taskId: number, artifactId: number, token: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/artifacts/${artifactId}/download`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Failed to download artifact');
  }

  return response.blob();
}

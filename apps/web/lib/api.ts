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
import { frontendLog, getCorrelationId } from './observability';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const correlationId = getCorrelationId();
  const requestId = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'x-correlation-id': correlationId,
      'x-request-id': requestId,
      ...(init?.headers || {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const body = await response.text();
    frontendLog('frontend.api_error', { path, status: response.status, body });
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
  const correlationId = getCorrelationId();
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/artifacts/${artifactId}/download`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'x-correlation-id': correlationId,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    frontendLog('frontend.artifact_download_error', { taskId, artifactId, status: response.status });
    throw new Error('Failed to download artifact');
  }

  return response.blob();
}

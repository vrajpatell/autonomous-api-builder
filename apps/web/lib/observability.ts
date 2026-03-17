const CORRELATION_STORAGE_KEY = 'autobuilder-correlation-id';

function newId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function getCorrelationId(): string {
  if (typeof window === 'undefined') {
    return newId();
  }

  const existing = window.localStorage.getItem(CORRELATION_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const created = newId();
  window.localStorage.setItem(CORRELATION_STORAGE_KEY, created);
  return created;
}

export function frontendLog(event: string, details: Record<string, unknown>): void {
  const payload = {
    event,
    correlationId: getCorrelationId(),
    timestamp: new Date().toISOString(),
    ...details,
  };
  console.error(JSON.stringify(payload));
}

import { Task } from '@/lib/types';

export function buildTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 1,
    owner_id: 99,
    title: 'Build task',
    user_prompt: 'Create a robust API generation workflow',
    status: 'pending',
    planner_status: 'pending',
    planner_source: null,
    queue_job_id: null,
    error_message: null,
    created_at: '2026-03-20T10:00:00Z',
    updated_at: null,
    plans: [],
    artifacts: [],
    progress_updates: [],
    orchestration_runs: [],
    agent_runs: [],
    ...overrides,
  };
}

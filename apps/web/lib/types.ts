export type TaskPlan = {
  id: number;
  step_number: number;
  title: string;
  description: string;
};

export type GeneratedArtifact = {
  id: number;
  artifact_type: string;
  file_name: string;
  content: string;
  created_at: string;
};

export type TaskProgressUpdate = {
  id: number;
  status: string;
  message: string;
  created_at: string;
};

export type Task = {
  id: number;
  owner_id: number;
  title: string;
  user_prompt: string;
  status: string;
  planner_status: string;
  planner_source: string | null;
  queue_job_id: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string | null;
  plans: TaskPlan[];
  artifacts: GeneratedArtifact[];
  progress_updates: TaskProgressUpdate[];
};

export type CreateTaskPayload = {
  title: string;
  user_prompt: string;
};

export type User = {
  id: number;
  email: string;
  display_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type AuthResponse = {
  user: User;
  access_token: string;
  token_type: 'bearer';
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload & {
  display_name?: string;
};

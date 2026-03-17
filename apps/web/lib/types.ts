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

export type Task = {
  id: number;
  title: string;
  user_prompt: string;
  status: string;
  created_at: string;
  updated_at: string | null;
  plans: TaskPlan[];
  artifacts: GeneratedArtifact[];
};

export type CreateTaskPayload = {
  title: string;
  user_prompt: string;
};

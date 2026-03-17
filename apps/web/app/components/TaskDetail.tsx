'use client';

import { downloadArtifact } from '@/lib/api';
import { Task } from '@/lib/types';

type Props = {
  task: Task | null;
  token: string | null;
};

export default function TaskDetail({ task, token }: Props) {
  if (!task) {
    return (
      <section className="card">
        <h3>Task Details</h3>
        <p>Select a task to inspect the generated execution plan.</p>
      </section>
    );
  }

  const handleOpenArtifact = async (artifactId: number, fileName: string, openInline: boolean) => {
    if (!token) return;
    const blob = await downloadArtifact(task.id, artifactId, token);
    const url = URL.createObjectURL(blob);
    if (openInline) {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }

    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="card">
      <h3>{task.title}</h3>
      <p>
        <strong>Status:</strong> {task.status}
      </p>
      <p>
        <strong>Planner:</strong> {task.planner_status}
        {task.planner_source ? ` (${task.planner_source})` : ''}
      </p>
      <p>{task.user_prompt}</p>
      <h4>Status History</h4>
      {task.progress_updates.length === 0 ? (
        <p>No status updates recorded.</p>
      ) : (
        <ul>
          {task.progress_updates.map((update) => (
            <li key={update.id}>
              <strong>{update.status}</strong> - {update.message} ({new Date(update.created_at).toLocaleString()})
            </li>
          ))}
        </ul>
      )}
      <h4>Execution Plan</h4>
      {task.plans.length === 0 ? (
        <p>Planner is still preparing plan steps...</p>
      ) : (
        <ol>
          {task.plans.map((step) => (
            <li key={step.id}>
              <strong>
                {step.step_number}. {step.title}
              </strong>
              <p>{step.description}</p>
            </li>
          ))}
        </ol>
      )}

      <h4>Artifacts</h4>
      {task.artifacts.length === 0 ? (
        <p>No generated artifacts yet.</p>
      ) : (
        <ul>
          {task.artifacts.map((artifact) => {
            const inlineViewable =
              artifact.content_type.startsWith('text/') || artifact.content_type === 'application/json';
            return (
              <li key={artifact.id}>
                <strong>{artifact.file_name}</strong> ({artifact.content_type}, {artifact.file_size} bytes)
                {inlineViewable ? (
                  <button type="button" onClick={() => void handleOpenArtifact(artifact.id, artifact.file_name, true)}>
                    View
                  </button>
                ) : null}
                <button type="button" onClick={() => void handleOpenArtifact(artifact.id, artifact.file_name, false)}>
                  Download
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

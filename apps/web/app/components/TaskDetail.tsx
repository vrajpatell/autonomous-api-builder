'use client';

import { Task } from '@/lib/types';

type Props = {
  task: Task | null;
};

export default function TaskDetail({ task }: Props) {
  if (!task) {
    return (
      <section className="card">
        <h3>Task Details</h3>
        <p>Select a task to inspect the generated execution plan.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h3>{task.title}</h3>
      <p>
        <strong>Status:</strong> {task.status}
      </p>
      <p>{task.user_prompt}</p>
      <h4>Execution Plan</h4>
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
    </section>
  );
}

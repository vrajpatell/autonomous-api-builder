'use client';

import { Task } from '@/lib/types';

type Props = {
  tasks: Task[];
  selectedTaskId: number | null;
  onSelect: (taskId: number) => void;
};

export default function TaskList({ tasks, selectedTaskId, onSelect }: Props) {
  return (
    <div className="card">
      <h3>Tasks</h3>
      {tasks.length === 0 ? (
        <p>No tasks yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left' }}>
              <th>Title</th>
              <th>Status</th>
              <th>Planner</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr
                key={task.id}
                onClick={() => onSelect(task.id)}
                style={{
                  cursor: 'pointer',
                  background: selectedTaskId === task.id ? '#eff6ff' : 'transparent',
                }}
              >
                <td>{task.title}</td>
                <td>{task.status}</td>
                <td>{task.planner_status}</td>
                <td>{new Date(task.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

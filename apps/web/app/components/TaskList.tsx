'use client';

import { ListTaskParams, Task, TaskStatus } from '@/lib/types';

const STATUS_OPTIONS: Array<TaskStatus | ''> = ['', 'pending', 'queued', 'planning', 'generating', 'reviewing', 'completed', 'failed', 'cancelled'];

const statusColorMap: Record<string, string> = {
  pending: '#6b7280',
  queued: '#2563eb',
  planning: '#0ea5e9',
  generating: '#7c3aed',
  reviewing: '#d97706',
  completed: '#16a34a',
  failed: '#dc2626',
  cancelled: '#64748b',
};

type Props = {
  tasks: Task[];
  selectedTaskId: number | null;
  onSelect: (taskId: number) => void;
  filters: ListTaskParams;
  onFilterChange: (next: ListTaskParams) => void;
  totalPages: number;
};

export default function TaskList({ tasks, selectedTaskId, onSelect, filters, onFilterChange, totalPages }: Props) {
  return (
    <div className="card">
      <h3>Tasks</h3>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          placeholder="Search title or prompt"
          value={filters.search || ''}
          onChange={(e) => onFilterChange({ ...filters, page: 1, search: e.target.value })}
        />
        <select value={filters.status || ''} onChange={(e) => onFilterChange({ ...filters, page: 1, status: e.target.value as TaskStatus | '' })}>
          {STATUS_OPTIONS.map((status) => (
            <option key={status || 'all'} value={status}>
              {status || 'all statuses'}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={filters.date_from || ''}
          onChange={(e) => onFilterChange({ ...filters, page: 1, date_from: e.target.value })}
        />
        <input
          type="date"
          value={filters.date_to || ''}
          onChange={(e) => onFilterChange({ ...filters, page: 1, date_to: e.target.value })}
        />
        <select
          value={filters.sort_by || 'created_at'}
          onChange={(e) => onFilterChange({ ...filters, sort_by: e.target.value as 'created_at' | 'updated_at' })}
        >
          <option value="created_at">Sort by created</option>
          <option value="updated_at">Sort by updated</option>
        </select>
        <select
          value={filters.sort_order || 'desc'}
          onChange={(e) => onFilterChange({ ...filters, sort_order: e.target.value as 'asc' | 'desc' })}
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>

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
                <td>
                  <span
                    style={{
                      background: `${statusColorMap[task.status]}22`,
                      color: statusColorMap[task.status],
                      borderRadius: '999px',
                      padding: '0.2rem 0.5rem',
                      fontSize: '0.8rem',
                    }}
                  >
                    {task.status}
                  </span>
                </td>
                <td>{task.planner_status}</td>
                <td>{new Date(task.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem' }}>
        <button
          onClick={() => onFilterChange({ ...filters, page: Math.max(1, (filters.page || 1) - 1) })}
          disabled={(filters.page || 1) <= 1}
        >
          Previous
        </button>
        <p>
          Page {filters.page || 1} of {Math.max(totalPages, 1)}
        </p>
        <button
          onClick={() => onFilterChange({ ...filters, page: Math.min(totalPages || 1, (filters.page || 1) + 1) })}
          disabled={(filters.page || 1) >= Math.max(totalPages, 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}

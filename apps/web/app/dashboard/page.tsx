'use client';

import { useEffect, useMemo, useState } from 'react';

import Protected from '@/app/components/Protected';
import TaskDetail from '@/app/components/TaskDetail';
import TaskForm from '@/app/components/TaskForm';
import TaskList from '@/app/components/TaskList';
import { getTask, listTasks } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { ListTaskParams, Task } from '@/lib/types';

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState<ListTaskParams>({
    page: 1,
    page_size: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  useEffect(() => {
    if (!token) return;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await listTasks(token, filters);
        setTasks(data.items);
        setTotalPages(data.meta.total_pages);
        if (data.items.length > 0) {
          setSelectedTaskId((prev) => (prev && data.items.some((item) => item.id === prev) ? prev : data.items[0].id));
        } else {
          setSelectedTaskId(null);
          setSelectedTask(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [token, filters]);

  useEffect(() => {
    if (!selectedTaskId || !token) return;

    const loadDetail = async () => {
      try {
        const detail = await getTask(selectedTaskId, token);
        setSelectedTask(detail);
      } catch {
        setSelectedTask(null);
      }
    };

    void loadDetail();
  }, [selectedTaskId, token]);

  const onCreated = (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
    setSelectedTaskId(newTask.id);
    setSelectedTask(newTask);
  };

  const subtitle = useMemo(
    () => `Track API build requests and generated planning output in one place. Signed in as ${user?.display_name || user?.email}.`,
    [user],
  );

  return (
    <Protected>
      <main className="container grid" style={{ gap: '1.25rem' }}>
        <section>
          <h1>Dashboard</h1>
          <p>{subtitle}</p>
        </section>

        {token ? <TaskForm onCreated={onCreated} token={token} /> : null}

        {loading ? <p>Loading tasks...</p> : error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}

        <section className="grid grid-2">
          <TaskList
            tasks={tasks}
            selectedTaskId={selectedTaskId}
            onSelect={setSelectedTaskId}
            filters={filters}
            onFilterChange={setFilters}
            totalPages={totalPages}
          />
          <TaskDetail task={selectedTask} token={token} />
        </section>
      </main>
    </Protected>
  );
}

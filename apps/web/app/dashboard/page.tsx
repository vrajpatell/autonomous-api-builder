'use client';

import { useEffect, useMemo, useState } from 'react';

import TaskDetail from '@/app/components/TaskDetail';
import TaskForm from '@/app/components/TaskForm';
import TaskList from '@/app/components/TaskList';
import { getTask, listTasks } from '@/lib/api';
import { Task } from '@/lib/types';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await listTasks();
        setTasks(data);
        if (data.length > 0) {
          setSelectedTaskId(data[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  useEffect(() => {
    if (!selectedTaskId) return;

    const loadDetail = async () => {
      try {
        const detail = await getTask(selectedTaskId);
        setSelectedTask(detail);
      } catch {
        setSelectedTask(null);
      }
    };

    void loadDetail();
  }, [selectedTaskId]);

  const onCreated = (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
    setSelectedTaskId(newTask.id);
    setSelectedTask(newTask);
  };

  const subtitle = useMemo(
    () => `Track API build requests and generated planning output in one place.`,
    [],
  );

  return (
    <main className="container grid" style={{ gap: '1.25rem' }}>
      <section>
        <h1>Dashboard</h1>
        <p>{subtitle}</p>
      </section>

      <TaskForm onCreated={onCreated} />

      {loading ? <p>Loading tasks...</p> : error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}

      <section className="grid grid-2">
        <TaskList tasks={tasks} selectedTaskId={selectedTaskId} onSelect={setSelectedTaskId} />
        <TaskDetail task={selectedTask} />
      </section>
    </main>
  );
}

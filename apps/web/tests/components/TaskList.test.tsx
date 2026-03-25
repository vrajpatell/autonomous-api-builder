import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import TaskList from '@/app/components/TaskList';
import { buildTask } from '@/tests/utils/fixtures';

const baseFilters = {
  page: 1,
  page_size: 10,
  sort_by: 'created_at' as const,
  sort_order: 'desc' as const,
};

describe('TaskList', () => {
  it('renders empty state when no tasks exist', () => {
    render(
      <TaskList
        tasks={[]}
        selectedTaskId={null}
        onSelect={vi.fn()}
        filters={baseFilters}
        onFilterChange={vi.fn()}
        totalPages={0}
      />,
    );

    expect(screen.getByText('No tasks yet.')).toBeInTheDocument();
  });

  it('renders tasks and supports selection/filter/pagination actions', async () => {
    const onSelect = vi.fn();
    const onFilterChange = vi.fn();

    render(
      <TaskList
        tasks={[
          buildTask({ id: 1, title: 'Task one', status: 'pending' }),
          buildTask({ id: 2, title: 'Task two', status: 'completed' }),
        ]}
        selectedTaskId={1}
        onSelect={onSelect}
        filters={{ ...baseFilters, search: '', status: '', page: 1 }}
        onFilterChange={onFilterChange}
        totalPages={2}
      />,
    );

    await userEvent.click(screen.getByText('Task two'));
    expect(onSelect).toHaveBeenCalledWith(2);

    await userEvent.type(screen.getByPlaceholderText('Search title or prompt'), 'cache');
    expect(onFilterChange).toHaveBeenLastCalledWith(expect.objectContaining({ search: 'cache', page: 1 }));

    await userEvent.selectOptions(screen.getByDisplayValue('all statuses'), 'completed');
    expect(onFilterChange).toHaveBeenLastCalledWith(expect.objectContaining({ status: 'completed', page: 1 }));

    await userEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(onFilterChange).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }));
  });
});

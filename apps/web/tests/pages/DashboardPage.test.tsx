import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import DashboardPage from '@/app/dashboard/page';
import { getTask, listTasks } from '@/lib/api';
import { buildTask } from '@/tests/utils/fixtures';

vi.mock('@/app/components/Protected', () => ({
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    token: 'test-token',
    user: { email: 'user@example.com', display_name: 'Test User' },
  }),
}));

vi.mock('@/lib/api', () => ({
  listTasks: vi.fn(),
  getTask: vi.fn(),
}));

describe('DashboardPage', () => {
  it('renders loading and then the task list/details', async () => {
    const firstTask = buildTask({ id: 11, title: 'First task' });
    vi.mocked(listTasks).mockResolvedValue({
      items: [firstTask],
      meta: { total_count: 1, current_page: 1, page_size: 10, total_pages: 1 },
    });
    vi.mocked(getTask).mockResolvedValue(firstTask);

    render(<DashboardPage />);

    expect(screen.getByText('Loading tasks...')).toBeInTheDocument();

    expect(await screen.findByText('First task')).toBeInTheDocument();
    await waitFor(() => expect(getTask).toHaveBeenCalledWith(11, 'test-token'));
  });

  it('shows API error when loading tasks fails', async () => {
    vi.mocked(listTasks).mockRejectedValue(new Error('Service unavailable'));

    render(<DashboardPage />);

    expect(await screen.findByText('Service unavailable')).toBeInTheDocument();
  });
});

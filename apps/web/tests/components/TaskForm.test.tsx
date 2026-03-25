import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import TaskForm from '@/app/components/TaskForm';
import { createTask } from '@/lib/api';
import { buildTask } from '@/tests/utils/fixtures';

vi.mock('@/lib/api', () => ({
  createTask: vi.fn(),
}));

describe('TaskForm', () => {
  it('submits the request and resets fields on success', async () => {
    const onCreated = vi.fn();
    vi.mocked(createTask).mockResolvedValue(buildTask({ id: 101, title: 'Generated API' }));

    render(<TaskForm token="token-123" onCreated={onCreated} />);

    await userEvent.type(screen.getByLabelText('Title'), 'Generated API');
    await userEvent.type(screen.getByLabelText('Prompt'), 'Please create an API for issue tracking.');
    await userEvent.click(screen.getByRole('button', { name: 'Create Task' }));

    await waitFor(() => expect(createTask).toHaveBeenCalledWith(
      { title: 'Generated API', user_prompt: 'Please create an API for issue tracking.' },
      'token-123',
    ));

    expect(onCreated).toHaveBeenCalledWith(expect.objectContaining({ id: 101 }));
    expect(screen.getByLabelText('Title')).toHaveValue('');
    expect(screen.getByLabelText('Prompt')).toHaveValue('');
  });

  it('shows an API error message when submission fails', async () => {
    vi.mocked(createTask).mockRejectedValue(new Error('Title is not unique'));

    render(<TaskForm token="token-123" onCreated={vi.fn()} />);

    await userEvent.type(screen.getByLabelText('Title'), 'Duplicate title');
    await userEvent.type(screen.getByLabelText('Prompt'), 'Prompt long enough to satisfy the textarea validation.');
    await userEvent.click(screen.getByRole('button', { name: 'Create Task' }));

    expect(await screen.findByText('Title is not unique')).toBeInTheDocument();
  });
});

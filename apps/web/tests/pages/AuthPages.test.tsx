import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import LoginPage from '@/app/login/page';
import RegisterPage from '@/app/register/page';

const authMock = {
  login: vi.fn(),
  register: vi.fn(),
};

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => authMock,
}));

describe('Auth pages', () => {
  beforeEach(() => {
    authMock.login.mockReset();
    authMock.register.mockReset();
  });

  it('submits login credentials through auth context', async () => {
    render(<LoginPage />);

    await userEvent.type(screen.getByPlaceholderText('Email'), 'qa@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'password123');
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }));

    await waitFor(() => expect(authMock.login).toHaveBeenCalledWith({ email: 'qa@example.com', password: 'password123' }));
  });

  it('surfaces register errors from auth context', async () => {
    authMock.register.mockRejectedValue(new Error('Email is already in use'));

    render(<RegisterPage />);

    await userEvent.type(screen.getByPlaceholderText('Display name'), 'QA');
    await userEvent.type(screen.getByPlaceholderText('Email'), 'qa@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password (min 8 chars)'), 'password123');
    await userEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(await screen.findByText('Email is already in use')).toBeInTheDocument();
  });
});

import { expect, test, type Page } from '@playwright/test';

const user = {
  id: 2,
  email: 'e2e@example.com',
  display_name: 'E2E User',
  is_active: true,
  created_at: '2026-03-21T12:00:00Z',
  updated_at: null,
};

const task = {
  id: 51,
  owner_id: 2,
  title: 'Generated Orders API',
  user_prompt: 'Build an order management API with CRUD and validation.',
  status: 'completed',
  planner_status: 'completed',
  planner_source: 'llm',
  queue_job_id: null,
  error_message: null,
  created_at: '2026-03-21T12:05:00Z',
  updated_at: null,
  progress_updates: [{ id: 1, status: 'completed', message: 'Done', created_at: '2026-03-21T12:06:00Z' }],
  plans: [{ id: 1, step_number: 1, title: 'Model entities', description: 'Create schema for order + line item.' }],
  artifacts: [],
};

async function mockApi(page: Page) {
  await page.route('http://localhost:8000/api/v1/**', async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith('/auth/register') && method === 'POST') {
      return route.fulfill({ json: { user, access_token: 'token-1', token_type: 'bearer' } });
    }
    if (url.endsWith('/auth/login') && method === 'POST') {
      return route.fulfill({ json: { user, access_token: 'token-1', token_type: 'bearer' } });
    }
    if (url.endsWith('/auth/me') && method === 'GET') {
      return route.fulfill({ json: user });
    }
    if (url.includes('/tasks?') && method === 'GET') {
      return route.fulfill({
        json: {
          items: [task],
          meta: { total_count: 11, current_page: 1, page_size: 10, total_pages: 2 },
        },
      });
    }
    if (url.endsWith('/tasks') && method === 'POST') {
      return route.fulfill({ json: { ...task, id: 77, title: 'Created via E2E' } });
    }
    if (url.endsWith('/tasks/51') && method === 'GET') {
      return route.fulfill({ json: task });
    }
    return route.fulfill({ status: 404, body: 'Not mocked' });
  });
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test('user can register and land on dashboard', async ({ page }) => {
  await page.goto('/register');

  await page.getByPlaceholder('Display name').fill('E2E User');
  await page.getByPlaceholder('Email').fill('e2e@example.com');
  await page.getByPlaceholder('Password (min 8 chars)').fill('password123');
  await page.getByRole('button', { name: 'Register' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText('Signed in as E2E User')).toBeVisible();
});

test('user login, create task, view details, and use filters/pagination', async ({ page }) => {
  await page.goto('/login');

  await page.getByPlaceholder('Email').fill('e2e@example.com');
  await page.getByPlaceholder('Password').fill('password123');
  await page.getByRole('button', { name: 'Log in' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByLabel('Title').fill('Created via E2E');
  await page.getByLabel('Prompt').fill('Create an API that tracks invoices and payment status.');
  await page.getByRole('button', { name: 'Create Task' }).click();

  await expect(page.getByRole('heading', { name: 'Created via E2E' })).toBeVisible();

  await page.getByPlaceholder('Search title or prompt').fill('orders');
  await page.getByRole('button', { name: 'Next' }).click();

  await expect(page.getByText('Page 2 of 2')).toBeVisible();

  await page.getByText('Generated Orders API').click();
  await expect(page.getByRole('heading', { name: 'Generated Orders API' })).toBeVisible();
  await expect(page.getByText('Model entities')).toBeVisible();
});

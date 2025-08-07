import { test, expect } from '@playwright/test';

test.use({
  viewport: {
    height: 2000,
    width: 3000
  },
  launchOptions: { slowMo: 300 } 
});

test('test', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  await page.getByRole('button', { name: 'Add Item ⌘K' }).click();
  await expect(page.getByPlaceholder('Search for stage items...')).toBeVisible();
  await page.getByPlaceholder('Search for stage items...').click();
  await page.getByPlaceholder('Search for stage items...').fill('laptop');
  await expect(page.locator('#bits-c395')).toMatchAriaSnapshot(`
    - text: Equipment & Accessories
    - group "Equipment & Accessories":
      - option "Laptop Laptop INPUT" [selected]:
        - img "Laptop"
    `);
  await page.getByRole('option', { name: 'Laptop Laptop INPUT' }).click();
  await page.getByText('DSRDSCDSLUSRUSCUSL').click();
  await expect(page.getByRole('img', { name: 'Laptop' })).toBeVisible();
});
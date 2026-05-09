import { test, expect } from '@playwright/test';

test('Happy Path - Dashboard Prediction and tabs', async ({ page }) => {
  await page.goto('http://localhost:3000/dashboard');
  await page.waitForLoadState('networkidle');

  await expect(page.locator('h1')).toContainText('Credit Risk Dashboard');

  await page.click('button:has-text("Predict Risk")');
  await page.waitForSelector('text=/ML Risk Score|Risk Score/i', { timeout: 15000 });
  await expect(page.locator('text=/ML Risk Score/i')).toBeVisible();

  await page.click('button:has-text("Similar")');
  await page.waitForTimeout(2000);

  await page.click('button:has-text("Groups")');
  await page.waitForTimeout(2000);

  await page.click('button:has-text("Insights")');
  await page.waitForTimeout(2000);

  await page.click('button:has-text("Agents")');
  await page.waitForTimeout(2000);
});

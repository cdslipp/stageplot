import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: {
    command: 'npm run build && npm run preview',
    port: 4173
  },
  testDir: 'e2e',
  // Default browser/device settings for every test and for the recorder
  use: {
    viewport: { width: 3000, height: 2000 }
  }
});

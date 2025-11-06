import { defineConfig } from 'vitest/config'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    viteReact(),
  ],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [],
    coverage: {
      enabled: true,
      provider: 'v8',
      thresholds: {
        branches: 90,
        functions: 90,
        lines: 90,
        statements: 90,
      },
      include: [
        "src/**/*.ts",
        "src/**/*.tsx"
      ],
      exclude: [
        "src/routeTree.gen.ts",
        "src/router.tsx",
      ]
    }
  },
})

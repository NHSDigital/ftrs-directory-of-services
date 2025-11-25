import { defineConfig } from 'vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'
import { nitro } from "nitro/vite"

const config = defineConfig({
  plugins: [
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    tanstackStart(),
    nitro({
      config: {
        preset: "aws-lambda",
        externals: {
          inline: [
            '@aws-lambda-powertools/logger',
            '@aws-lambda-powertools/parameters',
          ],
        },
      }
    }),
    viteReact(),
  ],
  server: {
    host: '127.0.0.1',
    port: 3000,
  },
  ssr: {
    noExternal: [
      '@aws-lambda-powertools/logger',
      '@aws-lambda-powertools/parameters',
    ],
    target: 'node',
  },
})

export default config

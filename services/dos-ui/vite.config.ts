import { defineConfig } from 'vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'
import { nitro } from "nitro/vite"


const config = defineConfig({
  plugins: [
    // this is the plugin that enables path aliases
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    tanstackStart(),
    nitro({
      config: {
        preset: "aws-lambda"
      }
    }),
    viteReact(),
  ],
  ssr: {
    // Don't externalize these packages for SSR builds
    noExternal: [
      '@aws-lambda-powertools/logger',
      '@aws-lambda-powertools/parameters',
    ],
  },
  build: {
    rollupOptions: {
      external: [
        // These should only be used on the server
        'node:crypto',
        'node:console',
      ],
    },
  },
})

export default config

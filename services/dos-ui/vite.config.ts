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
  resolve: {
    alias: {
      // Polyfill Node.js built-ins for browser if needed
      'node:crypto': 'crypto-browserify',
      'node:console': 'console-browserify',
    },
  },
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
        '@aws-lambda-powertools/logger',
        '@aws-lambda-powertools/parameters',
        '@aws-sdk/client-secrets-manager',
        '@aws-sdk/client-ssm',
      ],
    },
  },
})

export default config

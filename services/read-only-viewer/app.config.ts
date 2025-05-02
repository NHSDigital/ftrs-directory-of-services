import { defineConfig } from '@tanstack/react-start/config'
import tsConfigPaths from 'vite-tsconfig-paths'
import { Logger } from 'sass';

export default defineConfig({
  tsr: {
    appDirectory: 'src',
  },
  vite: {
    plugins: [
      tsConfigPaths({
        projects: ['./tsconfig.json'],
      })
    ],
    css: {
      preprocessorOptions: {
        scss: {
          logger: Logger.silent
        }

      }
    }
  },
  server: {
    preset: "aws-lambda",
    awsLambda: {
      streaming: false,
    },
  }
});

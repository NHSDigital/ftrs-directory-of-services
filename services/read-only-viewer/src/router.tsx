import { createRouter as createTanStackRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

export const createRouter = (options?: { scrollRestoration?: boolean }) => {
  const router = createTanStackRouter({
    routeTree,
    ...options,
  })

  return router;
}


declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof createRouter>
  }
}

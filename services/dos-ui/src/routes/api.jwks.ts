import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/jwks')({
  server: {
    handlers: {
      GET: async ({  }) => {
        return new Response('Hello, World!')
      },
    },
  },
})

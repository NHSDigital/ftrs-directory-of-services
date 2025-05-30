import { json } from '@tanstack/react-start'
import { createAPIFileRoute } from '@tanstack/react-start/api'
import { randomUUID } from 'node:crypto';
import { getBaseEndpoint, getSignedHeaders } from '@/utils/authentication';


export const APIRoute = createAPIFileRoute('/api/organisations/query')({
  GET: async () => {
    const correlationId = randomUUID();
    const baseUrl = await getBaseEndpoint();
    const signedHeaders = await getSignedHeaders({
      method: 'GET',
      url: `${baseUrl}/organisation/`,
    });

    const response = await fetch(`${baseUrl}/organisation/`, {
      method: "GET",
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Correlation-ID': correlationId,
        ...signedHeaders
      }
    });

    return json(
      await response.json(),
      {
        headers: {
          'X-Correlation-ID': correlationId,
        }
      }
    )
  },
})

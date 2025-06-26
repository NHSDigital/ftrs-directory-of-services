import { json } from '@tanstack/react-start'
import { createAPIFileRoute } from '@tanstack/react-start/api'
import {makeSignedFetch} from "@/utils/authentication.ts";

export const APIRoute = createAPIFileRoute('/api/healthcareService')({
  GET: async ({ request }) => {
    const response = await makeSignedFetch({
      method: "GET",
      pathname: "/healthcare-service/",
      expectedStatus: [200],
      headers: {
        "X-Correlation-ID": request.headers.get("X-Correlation-ID") || "",
      },
    });

    return json(await response.json(), {
      headers: {
        "X-Correlation-ID": response.headers.get("X-Correlation-ID") || "",
      },
    });
  },
});

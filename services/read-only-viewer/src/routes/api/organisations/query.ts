import { randomUUID } from "node:crypto";
import { getBaseEndpoint, getSignedHeaders } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute("/api/organisations/query")({
  GET: async () => {
    const correlationId = randomUUID();
    const baseEndpoint = await getBaseEndpoint();
    const signedHeaders = await getSignedHeaders({
      method: "GET",
      url: `${baseEndpoint}/organisation/`,
    });

    const response = await fetch(`${baseEndpoint}/organisation/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-Correlation-ID": correlationId,
        ...signedHeaders,
      },
    });

    return json(await response.json(), {
      headers: {
        "X-Correlation-ID": correlationId,
      },
    });
  },
});

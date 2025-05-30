import { randomUUID } from "node:crypto";
import { getBaseEndpoint, getSignedHeaders } from "@/utils/authentication";
import { ResponseError } from "@/utils/errors";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute(
  "/api/organisations/$organisationID/",
)({
  GET: async ({ params }) => {
    const { organisationID } = params;
    const correlationId = randomUUID();
    const baseUrl = await getBaseEndpoint();
    const signedHeaders = await getSignedHeaders({
      method: "GET",
      url: `${baseUrl}/organisation/${organisationID}`,
    });

    const response = await fetch(`${baseUrl}/organisation/${organisationID}/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-Correlation-ID": correlationId,
        ...signedHeaders,
      },
    });
    if (!response.ok) {
      throw new ResponseError(
        `Failed to fetch organisation: ${response.status} ${response.statusText}`,
        response.status,
        Object.fromEntries(response.headers.entries()),
        await response.json(),
      );
    }

    return json(await response.json(), {
      headers: {
        "X-Correlation-ID": correlationId,
      },
    });
  },
});

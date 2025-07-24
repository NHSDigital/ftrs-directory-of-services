import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute("/api/organisation/$organisationID")(
  {
    GET: async ({ params, request }) => {
      const { organisationID } = params;

      const response = await makeSignedFetch({
        method: "GET",
        pathname: `/Organization/${organisationID}`,
        expectedStatus: [200, 404],
        headers: {
          "X-Correlation-ID": request.headers.get("X-Correlation-ID") || "",
        },
      });

      if (response.status === 404) {
        return json(null, {
          status: 404,
          headers: {
            "X-Correlation-ID": response.headers.get("X-Correlation-ID") || "",
          },
        });
      }

      return json(await response.json(), {
        headers: {
          "X-Correlation-ID": response.headers.get("X-Correlation-ID") || "",
        },
      });
    },
  },
);

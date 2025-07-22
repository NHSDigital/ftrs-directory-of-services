import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute("/api/location/$locationID")({
  GET: async ({ params, request }) => {
    const { locationID } = params;

    const response = await makeSignedFetch({
      method: "GET",
      pathname: `/location/${locationID}`,
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
});

import { makeSignedFetch } from "@/utils/authentication.ts";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute("/api/location")({
  GET: async ({ request }) => {
    const response = await makeSignedFetch({
      method: "GET",
      pathname: "/location/",
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

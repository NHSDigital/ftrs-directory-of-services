import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute("/api/organisations")({
  GET: async () => {
    const response = await makeSignedFetch({
      pathname: "/organisation/",
      expectedStatus: [200],
    });

    return json(await response.json(), {
      headers: {
        "X-Correlation-ID": response.headers.get("X-Correlation-ID") || "",
      },
    });
  },
});

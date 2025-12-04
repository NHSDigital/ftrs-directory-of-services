import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/organisation/")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const response = await makeSignedFetch({
          method: "GET",
          pathname: "/Organization/",
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
    }
  }
});

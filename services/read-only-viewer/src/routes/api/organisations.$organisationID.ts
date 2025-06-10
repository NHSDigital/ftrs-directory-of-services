import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute, type StartAPIMethodCallback } from "@tanstack/react-start/api";

export const getOrganisationByID: StartAPIMethodCallback<"/api/organisations/$organisationID"> = async ({ params, request }) => {
  const { organisationID } = params;

  const response = await makeSignedFetch({
    method: "GET",
    pathname: `/organisation/${organisationID}`,
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
}

export const APIRoute = createAPIFileRoute(
  "/api/organisations/$organisationID",
)({ GET: getOrganisationByID });

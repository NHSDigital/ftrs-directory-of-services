import { makeSignedFetch } from "@/utils/authentication";
import { json } from "@tanstack/react-start";
import { createAPIFileRoute } from "@tanstack/react-start/api";

export const APIRoute = createAPIFileRoute(
  "/api/organisations/$organisationID/",
)({
  GET: async ({ params }) => {
    const { organisationID } = params;

    const response = await makeSignedFetch({
      pathname: `/organisation/${organisationID}/`,
      expectedStatus: [200],
    });

    return json(await response.json());
  },
});

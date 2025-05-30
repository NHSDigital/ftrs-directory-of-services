import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoints/$endpointID",
)({
  component: EndpointDetailsPage,
});

function EndpointDetailsPage() {
  const { organisationID, endpointID } = Route.useParams();
  const { data: organisation } = useOrganisationQuery(organisationID);

  return (
    <>
      <PageBreadcrumbs
        backTo="/organisations/$organisationID/endpoints"
        items={[
          { to: "/organisations", label: "Organisations" },
          {
            to: "/organisations/$organisationID",
            label: organisation?.name || "Organisation",
          },
          {
            to: "/organisations/$organisationID/endpoints",
            label: "Endpoints",
            params: { organisationID },
          },
          {
            to: "/organisations/$organisationID/endpoints/$endpointID",
            label: endpointID,
            params: { organisationID, endpointID },
          },
        ]}
      />
    </>
  );
}

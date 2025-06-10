import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoints/$endpointID",
)({
  component: EndpointDetailsPage,
  head: () => ({
    meta: [{ title: "Endpoint Details - FtRS Read Only Viewer" }],
  }),
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
      <span className="nhsuk-caption-l">Organisation Details</span>
      <h1 className="nhsuk-heading-l">Endpoint: {endpointID}</h1>
      <p>This page has not yet been developed.</p>
    </>
  );
}

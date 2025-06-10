import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoints/",
)({
  component: OrganisationEndpointsPage,
  head: () => ({
    meta: [{ title: "Organisation Endpoints - FtRS Read Only Viewer" }],
  }),
});

function OrganisationEndpointsPage() {
  const { organisationID } = Route.useParams();
  const { data: organisation } = useOrganisationQuery(organisationID);

  return (
    <>
      <PageBreadcrumbs
        backTo="/organisations/$organisationID"
        items={[
          { to: "/organisations/", label: "Organisations" },
          {
            to: "/organisations/$organisationID",
            label: organisation?.name || "Organisation",
            params: { organisationID },
          },
          {
            to: "/organisations/$organisationID/endpoints",
            label: "Endpoints",
            params: { organisationID },
          },
        ]}
      />
      <span className="nhsuk-caption-l">Organisation Details</span>
      <h1 className="nhsuk-heading-l">Endpoints for {organisation?.name}</h1>
      <p>This page has not yet been developed.</p>
    </>
  );
}

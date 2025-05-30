import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoints/",
)({
  component: OrganisationEndpointsPage,
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
    </>
  );
}

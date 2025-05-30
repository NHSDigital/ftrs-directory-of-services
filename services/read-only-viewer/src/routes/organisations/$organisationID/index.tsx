import DataTable from "@/components/DataTable";
import KeyValueTable from "@/components/KeyValueTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import type { ResponseError } from "@/utils/errors";
import type { Endpoint, Organisation } from "@/utils/types";
import { Link, createFileRoute } from "@tanstack/react-router";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Card } from "nhsuk-react-components";
import { useMemo } from "react";

export const Route = createFileRoute("/organisations/$organisationID/")({
  component: OrganisationDetailsRoute,
  head: () => ({
    meta: [{ title: "Organisation Details - FtRS Read Only Viewer" }],
  }),
});

const OrganisationOverview: React.FC<{ organisation: Organisation }> = ({
  organisation,
}) => {
  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Overview</h2>
      <KeyValueTable
        items={[
          { key: "ID", value: organisation.id },
          { key: "Name", value: organisation.name },
          { key: "ODS Code", value: organisation.identifier_ODS_ODSCode },
          { key: "Type", value: organisation.type },
          { key: "Active", value: organisation.active ? "Yes" : "No" },
          { key: "Telecom", value: organisation.telecom || "None Provided" },
          {
            key: "Created By",
            value: (
              <>
                {organisation.createdBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({organisation.createdDateTime})
                </span>
              </>
            ),
          },
          {
            key: "Modified By",
            value: (
              <>
                {organisation.modifiedBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({organisation.modifiedDateTime})
                </span>
              </>
            ),
          },
        ]}
      />
    </Card>
  );
};

const useOrganisationEndpointsTable = (endpoints: Endpoint[]) => {
  const sortedEndpoints = useMemo(() => {
    return endpoints.sort((a, b) =>
      a.payloadType === b.payloadType
        ? a.order - b.order
        : a.payloadType?.localeCompare(b.payloadType || "") || 0,
    );
  }, [endpoints]);

  return useReactTable({
    data: sortedEndpoints,
    columns: [
      {
        accessorKey: "payloadType",
        header: "Payload Type",
        cell: (info) => info.getValue().replace("urn:nhs-itk:interaction:", ""),
      },
      {
        accessorKey: "order",
        header: "Order",
      },
      {
        accessorKey: "status",
        header: "Status",
      },
      {
        accessorKey: "id",
        header: "Action",
        cell: (info) => (
          <Link
            to="/organisations/$organisationID/endpoints/$endpointID"
            params={{
              organisationID: info.row.original.managedByOrganisation,
              endpointID: info.getValue(),
            }}
            className="nhsuk-link nhsuk-link--no-visited-state"
          >
            View
          </Link>
        ),
      },
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
  });
};

const OrganisationEndpointsTable: React.FC<{ endpoints: Endpoint[] }> = ({
  endpoints,
}) => {
  const table = useOrganisationEndpointsTable(endpoints);

  if (!endpoints || endpoints.length === 0) {
    return (
      <Card className="nhsuk-u-padding-5">
        <h2 className="nhsuk-heading-m">Endpoints</h2>
        <p>No endpoints available for this organisation.</p>
      </Card>
    );
  }

  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Endpoints</h2>
      <DataTable table={table} />
    </Card>
  );
};

function OrganisationDetailsRoute() {
  const { organisationID } = Route.useParams();
  const {
    data: organisation,
    isLoading,
    error,
  } = useOrganisationQuery(organisationID);

  return (
    <>
      <PageBreadcrumbs
        backTo="/organisations"
        items={[
          { to: "/", label: "Home" },
          { to: "/organisations", label: "Organisations" },
          {
            to: `/organisations/${organisationID}`,
            label: organisation?.name || "Organisation Details",
          },
        ]}
      />
      <span className="nhsuk-caption-l">Organisation Details</span>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {organisation && (
        <>
          <h1 className="nhsuk-heading-l">{organisation.name}</h1>
          <OrganisationOverview organisation={organisation} />
          <OrganisationEndpointsTable endpoints={organisation.endpoints} />
        </>
      )}
    </>
  );
}

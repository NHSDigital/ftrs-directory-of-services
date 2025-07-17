import DataTable from "@/components/DataTable";
import KeyValueTable from "@/components/KeyValueTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import type { ResponseError } from "@/utils/errors";
import type { Endpoint, Organisation } from "@/utils/types";
import { Link, createFileRoute } from "@tanstack/react-router";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { ActionLink, Card, Details } from "nhsuk-react-components";
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
    return endpoints.sort((a, b) => a.order - b.order);
  }, [endpoints]);

  return useReactTable({
    data: sortedEndpoints,
    columns: [
      {
        accessorKey: "order",
        header: "Order",
      },
      {
        accessorKey: "status",
        header: "Status",
      },
      {
        accessorKey: "connectionType",
        header: "Type",
      },
      {
        accessorKey: "address",
        header: "Address",
      },
      {
        accessorKey: "id",
        header: "Action",
        cell: (info) => (
          <Link
            to="/organisations/$organisationID/endpoint/$endpointID"
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

// table of endpoints (this is inside the card)
const OrganisationEndpointsTable: React.FC<{ endpoints: Endpoint[] }> = ({
  endpoints,
}) => {
  const table = useOrganisationEndpointsTable(endpoints);

  return <DataTable table={table} />;
};

// card for each endpoint
const OrganisationEndpointsList: React.FC<{ endpoints: Endpoint[] }> = ({
  endpoints,
}) => {
  if (!endpoints || endpoints.length === 0) {
    return (
      <Card className="nhsuk-u-padding-5">
        <h2 className="nhsuk-heading-m">Endpoints</h2>
        <p>No endpoints available for this organisation.</p>
      </Card>
    );
  }

  const groupedEndpoints = useMemo(
    () =>
      endpoints.reduce<Record<string, Endpoint[]>>((acc, endpoint) => {
        const key = endpoint.payloadType || "Unknown";
        if (key in acc) {
          acc[key].push(endpoint);
        } else {
          acc[key] = [endpoint];
        }
        return acc;
      }, {}),
    [endpoints],
  );

  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Endpoints</h2>
      <Details.ExpanderGroup>
        {Object.entries(groupedEndpoints).map(([interaction, endpoints]) => (
          <Details expander={true} key={interaction}>
            <Details.Summary>{interaction}</Details.Summary>
            <Details.Text>
              <OrganisationEndpointsTable endpoints={endpoints} />
            </Details.Text>
          </Details>
        ))}
      </Details.ExpanderGroup>
    </Card>
  );
};

function OrganisationDetailsRoute() {
  const { organisationID } = Route.useParams();
  const {
    data: organisation,
    isLoading,
    isSuccess,
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
          {/* endpoints listed here */}
          <OrganisationEndpointsList endpoints={organisation.endpoints} />
        </>
      )}
      {isSuccess && !organisation && (
        <>
          <h2 className="nhsuk-heading-l">Organisation not found</h2>
          <p>The organisation you are looking for does not exist.</p>
          <ActionLink
            asElement={Link}
            to="/organisations"
            className="nhsuk-link--no-visited-state"
          >
            Back to Organisations
          </ActionLink>
        </>
      )}
    </>
  );
}

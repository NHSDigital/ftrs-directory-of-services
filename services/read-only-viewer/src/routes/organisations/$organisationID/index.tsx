import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import type { ResponseError } from "@/utils/errors";
import type { Endpoint, Organisation } from "@/utils/types";
import { useQuery } from "@tanstack/react-query";
import { HeadContent, Link, createFileRoute } from "@tanstack/react-router";
import { Meta } from "@tanstack/react-start";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Breadcrumb, Card, SummaryList, Table } from "nhsuk-react-components";
import { useMemo } from "react";

export const Route = createFileRoute("/organisations/$organisationID/")({
  component: RouteComponent,
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
      <SummaryList>
        <SummaryList.Row>
          <SummaryList.Key>ID</SummaryList.Key>
          <SummaryList.Value>{organisation.id}</SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Name</SummaryList.Key>
          <SummaryList.Value>{organisation.name}</SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>ODS Code</SummaryList.Key>
          <SummaryList.Value>
            {organisation.identifier_ODS_ODSCode}
          </SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Type</SummaryList.Key>
          <SummaryList.Value>{organisation.type}</SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Active</SummaryList.Key>
          <SummaryList.Value>
            {organisation.active ? "Yes" : "No"}
          </SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Telecom</SummaryList.Key>
          <SummaryList.Value>
            {organisation.telecom || (
              <span className="nhsuk-caption">None Provided</span>
            )}
          </SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Created By</SummaryList.Key>
          <SummaryList.Value>
            {organisation.createdBy}{" "}
            <i className="nhsuk-u-font-size-16">
              ({organisation.createdDateTime})
            </i>
          </SummaryList.Value>
        </SummaryList.Row>
        <SummaryList.Row>
          <SummaryList.Key>Last Modified By</SummaryList.Key>
          <SummaryList.Value>
            {organisation.modifiedBy}{" "}
            <i className="nhsuk-u-font-size-16">
              ({organisation.modifiedDateTime})
            </i>
          </SummaryList.Value>
        </SummaryList.Row>
      </SummaryList>
    </Card>
  );
};

const columnHelper = createColumnHelper<Endpoint>();

const humanReadableInteraction = (interaction: string) => {
  return interaction.replace("urn:nhs-itk:interaction:", "");
};

const OrganisationEndpoints: React.FC<{ endpoints: Endpoint[] }> = ({
  endpoints,
}) => {
  const sortedEndpoints = useMemo(() => {
    return endpoints.sort((a, b) =>
      a.payloadType === b.payloadType
        ? a.order - b.order
        : a.payloadType?.localeCompare(b.payloadType || "") || 0,
    );
  }, [endpoints]);

  const table = useReactTable({
    data: sortedEndpoints,
    sortingFns: {
      interaction: (rowA, rowB) => {
        const interactionA = rowA.getValue<string>("payloadType") || "";
        const interactionB = rowB.getValue<string>("payloadType") || "";
        return interactionA.localeCompare(interactionB);
      },
    },
    enableSorting: true,
    columns: [
      columnHelper.accessor("payloadType", {
        header: () => "Payload Type",
        cell: (info) => (
          <span style={{ maxWidth: 10, overflow: "scroll" }}>
            {humanReadableInteraction(info.getValue()) || "Not Specified"}
          </span>
        ),
      }),
      columnHelper.accessor("order", {
        header: () => "Order",
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("status", {
        header: () => "Status",
      }),
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
  });

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
      <Table responsive>
        {table.getHeaderGroups().map((headerGroup) => (
          <Table.Head key={headerGroup.id}>
            <Table.Row>
              {headerGroup.headers.map((header) => (
                <Table.Cell key={header.id} colSpan={header.colSpan}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                </Table.Cell>
              ))}
              <Table.Cell>Action</Table.Cell>
            </Table.Row>
          </Table.Head>
        ))}
        <Table.Body>
          {table.getRowModel().rows.map((row) => (
            <Table.Row key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <Table.Cell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </Table.Cell>
              ))}
              <Table.Cell>
                <Link
                  to="/organisations/$organisationID/endpoints/$endpointID"
                  params={{ endpointID: row.id }}
                >
                  View
                </Link>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </Card>
  );
};

function RouteComponent() {
  const { organisationID } = Route.useParams();
  const {
    data: organisation,
    isLoading,
    error,
  } = useOrganisationQuery(organisationID);

  return (
    <>
      <Breadcrumb className="nhsuk-u-margin-bottom-3">
        <Breadcrumb.Back asElement={Link} to="/organisations">
          Back
        </Breadcrumb.Back>
        <Breadcrumb.Item
          asElement={Link}
          to="/"
          className="nhsuk-link--no-visited-state"
        >
          Home
        </Breadcrumb.Item>
        <Breadcrumb.Item
          asElement={Link}
          to="/organisations"
          className="nhsuk-link--no-visited-state"
        >
          Organisations
        </Breadcrumb.Item>
        <Breadcrumb.Item
          asElement={Link}
          to="/organisations/$organisationID"
          // @ts-expect-error - TanStack Router expects params to be an object
          params={{ organisationID }}
          className="nhsuk-link--no-visited-state"
        >
          {isLoading
            ? "Loading"
            : error
              ? "Error loading organisation"
              : organisation?.name || "Organisation Details"}
        </Breadcrumb.Item>
      </Breadcrumb>
      <span className="nhsuk-caption-l">Organisation Details</span>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {organisation && (
        <>
          <h1 className="nhsuk-heading-l">{organisation.name}</h1>
          <OrganisationOverview organisation={organisation} />
          <OrganisationEndpoints endpoints={organisation.endpoints} />
        </>
      )}
    </>
  );
}

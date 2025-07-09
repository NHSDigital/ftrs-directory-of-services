import KeyValueTable from "@/components/KeyValueTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import type { ResponseError } from "@/utils/errors";
import type { Endpoint } from "@/utils/types";
import { Link, createFileRoute } from "@tanstack/react-router";
import { ActionLink, Card } from "nhsuk-react-components";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoint/$endpointID",
)({
  component: EndpointDetailsPage,
  head: () => ({
    meta: [{ title: "Endpoint Details - FtRS Read Only Viewer" }],
  }),
});

const EndpointOverview: React.FC<{
  endpoints: Endpoint[];
  endpointID: string;
}> = ({ endpoints, endpointID }) => {
  let endpoint: Endpoint | null = getEndpoint(endpoints, endpointID);

  if (!endpoint) {
    return (
      <Card className="nhsuk-u-padding-5">
        <h2 className="nhsuk-heading-m">Endpoint</h2>
        <p>No endpoint of id: {endpointID} retrieved for this organisation.</p>
      </Card>
    );
  }
  endpoint = endpoint as Endpoint;
  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Endpoint Overview</h2>
      <KeyValueTable
        items={[
          { key: "ID", value: endpoint.id },
          {
            key: "Identifier Old DOS ID",
            value: endpoint.identifier_oldDoS_id,
          },
          { key: "Status", value: endpoint.status },
          { key: "Connection Type", value: endpoint.connectionType },
          { key: "Name", value: endpoint.name },
          { key: "Description", value: endpoint.description },
          { key: "Payload Type", value: endpoint.payloadType },
          { key: "Address", value: endpoint.address },
          { key: "Order", value: endpoint.order },
          {
            key: "Is Compression Enabled",
            value: endpoint.isCompressionEnabled.toString(),
          },
          { key: "Payload Mime Type", value: endpoint.payloadMimeType },
          {
            key: "Created By",
            value: (
              <>
                {endpoint.createdBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({endpoint.createdDateTime})
                </span>
              </>
            ),
          },
          {
            key: "Modified By",
            value: (
              <>
                {endpoint.modifiedBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({endpoint.modifiedDateTime})
                </span>
              </>
            ),
          },
        ]}
      />
    </Card>
  );
};

function getEndpoint(endpoints: Endpoint[], endpointID: string) {
  let ep = null;

  for (const endpoint of endpoints) {
    if (endpoint.id === endpointID) {
      ep = endpoint;
      break;
    }
  }

  return ep;
}

function EndpointDetailsPage() {
  const { organisationID, endpointID } = Route.useParams();
  const {
    data: organisation,
    isLoading,
    isSuccess,
    error,
  } = useOrganisationQuery(organisationID);

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
            to: "/organisations/$organisationID/$endpointID",
            label: `Endpoint ${endpointID}`,
            params: { organisationID, endpointID },
          },
        ]}
      />
      <span className="nhsuk-caption-l">Endpoint Details</span>
      <h1 className="nhsuk-heading-l">Endpoint: {endpointID}</h1>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {organisation && (
        <EndpointOverview
          endpoints={organisation.endpoints}
          endpointID={endpointID}
        />
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

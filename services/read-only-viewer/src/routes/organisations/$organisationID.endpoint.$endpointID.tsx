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
  endpoint: Endpoint;
}> = ({ endpoint }) => {
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

function getEndpoint() {
  const { organisationID, endpointID } = Route.useParams();
  const {
    data: organisation,
    isLoading,
    isSuccess,
    error,
  } = useOrganisationQuery(organisationID);

  const endpoint = organisation?.endpoints.find(
    (endpoint) => endpoint.id === endpointID,
  );

  return { organisation, endpoint, isLoading, isSuccess, error };
}

function EndpointDetailsPage() {
  const { organisation, endpoint, isLoading, isSuccess, error } = getEndpoint();

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
            label: `Endpoint ${endpoint?.id}`,
            params: {
              organisationID: organisation?.id ?? "",
              endpointID: endpoint?.id ?? "",
            },
          },
        ]}
      />
      <span className="nhsuk-caption-l">Endpoint Details</span>
      <h1 className="nhsuk-heading-l">Endpoint: {endpoint?.id}</h1>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {endpoint && <EndpointOverview endpoint={endpoint} />}
      {isSuccess && !organisation && (
        <>
          <h2 className="nhsuk-heading-l">Organisation not found</h2>
          <p>The organisation for this endpoint does not exist.</p>
          <ActionLink
            asElement={Link}
            to="/organisations"
            className="nhsuk-link--no-visited-state"
          >
            Back to Organisations
          </ActionLink>
        </>
      )}
      {isSuccess && organisation && !endpoint && (
        <>
          <h2 className="nhsuk-heading-l">Endpoint not found</h2>
          <p>The endpoint you are looking for does not exist.</p>
          <ActionLink
            asElement={Link}
            to={`/organisations/${organisation.id}`}
            className="nhsuk-link--no-visited-state"
          >
            Back to Organisation Overview
          </ActionLink>
        </>
      )}
    </>
  );
}

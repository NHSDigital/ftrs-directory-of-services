import KeyValueTable from "@/components/KeyValueTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { useOrganisationQuery } from "@/hooks/queryHooks";
import type { Endpoint } from "@/utils/types";
import { createFileRoute } from "@tanstack/react-router";
import { Card } from "nhsuk-react-components";

export const Route = createFileRoute(
  "/organisations/$organisationID/endpoint/$endpointID",
)({
  component: EndpointDetailsPage,
  head: () => ({
    meta: [{ title: "Endpoint Details - FtRS Read Only Viewer" }],
  }),
});

// TODO: all attributes  of an endpoint in a table (like for organisation details)
// - id
// - identifier_oldDOS_id >> check >> ? identifier_oldDoS_id
// - status
// - connectionType
// - name
// - description
// - payloadType
// - address
// - order
// - isCompressionEnabled
// - payloadMimeType
// - createdBy
// - createdDateTime
// - modifiedBy
// - modifiedDateTime

const EndpointOverview: React.FC<{ endpoints: Endpoint[], endpointID: string }> = ({
  endpoints, endpointID
}) => {
  // error handling for if it actually returns a null because it really should never do that
  var endpoint: Endpoint | null = getEndpoint(endpoints, endpointID)

  if (!endpoint) {
    return (
      <Card className="nhsuk-u-padding-5">
        <h2 className="nhsuk-heading-m">Endpoints</h2>
        <p>No endpoints available for this organisation.</p>
      </Card>
    );
  }
  endpoint = endpoint as Endpoint
  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Endpoint Overview</h2>
      <KeyValueTable
        items={[
          { key: "ID", value: endpoint.id },
          { key: "Identifier Old DOS ID", value: endpoint.identifier_oldDoS_id},
          { key: "Status", value: endpoint.status},
          { key: "Connection Type", value: endpoint.connectionType },
          { key: "Name", value: endpoint.name },
          { key: "Description", value: endpoint.description },
          { key: "Payload Type", value: endpoint.payloadType },
          { key: "Address", value: endpoint.address },
          { key: "Order", value: endpoint.order },
          { key: "Is Compression Enabled", value: endpoint.isCompressionEnabled.toString() },
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
  var ep = null
  endpoints.forEach((endpoint) => {
    if (endpoint.id === endpointID) {
      ep = endpoint
    }
  })

  return ep;
}


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
            to: "/organisations/$organisationID/$endpointID",
            label: `Endpoint ${endpointID}`,
            params: { organisationID, endpointID },
          },
        ]}
      />
      <span className="nhsuk-caption-l">Organisation Details</span>
      <h1 className="nhsuk-heading-l">Endpoint: {endpointID}</h1>
      {organisation && (
        <EndpointOverview endpoints={organisation.endpoints} endpointID={endpointID} />
      )}
    </>
  );
}

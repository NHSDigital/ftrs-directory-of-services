import KeyValueTable from "@/components/KeyValueTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useLocationQuery } from "@/hooks/queryHooks.ts";
import type { ResponseError } from "@/utils/errors";
import type { Location } from "@/utils/types.ts";
import { Link, createFileRoute } from "@tanstack/react-router";
import { ActionLink, Card } from "nhsuk-react-components";

export const Route = createFileRoute("/locations/$locationID/")({
  component: LocationDetailsRoute,
  head: () => ({
    meta: [{ title: "Location Details - FtRS Read Only Viewer" }],
  }),
});

const LocationOverview: React.FC<{
  location: Location;
}> = ({ location }) => {
  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">Location Details</h2>
      <KeyValueTable
        items={[
          { key: "ID", value: location.id },
          { key: "Name", value: location.name },
          { key: "Active", value: location.active ? "Yes" : "No" },
          {
            key: "Address",
            value: (
              <>
                <div>
                  Street: {location.address.street?.replace(/\$/g, ", ")}
                </div>
                <div>Town: {location.address.town}</div>
                <div>Postcode: {location.address.postcode}</div>
              </>
            ),
          },
          {
            key: "Managing Organisation",
            value: location.managingOrganisation ? (
              <Link
                to="/organisations/$organisationID"
                params={{ organisationID: location.managingOrganisation }}
                className="nhsuk-link nhsuk-link--no-visited-state"
              >
                {location.managingOrganisation} (View Managing Organisation)
              </Link>
            ) : (
              "Not Specified"
            ),
          },
          {
            key: "PositionGCS",
            value: (
              <>
                <div>latitude: {location.positionGCS.latitude}</div>
                <div>longitude: {location.positionGCS.longitude}</div>
              </>
            ),
          },
          {
            key: "Position Reference Number UPRN",
            value: location.positionReferenceNumber_UPRN,
          },
          {
            key: "Position Reference Number UBRN",
            value: location.positionReferenceNumber_UBRN,
          },
          {
            key: "Primary Address",
            value: location.primaryAddress ? "Yes" : "No",
          },
          { key: "Part Of", value: location.partOf },
          {
            key: "Created By",
            value: (
              <>
                {location.createdBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({location.createdDateTime})
                </span>
              </>
            ),
          },
          {
            key: "Modified By",
            value: (
              <>
                {location.modifiedBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({location.modifiedDateTime})
                </span>
              </>
            ),
          },
        ]}
      />
    </Card>
  );
};

function LocationDetailsRoute() {
  const { locationID } = Route.useParams();
  const {
    data: location,
    isLoading,
    isSuccess,
    error,
  } = useLocationQuery(locationID);

  return (
    <>
      <PageBreadcrumbs
        backTo="/locations"
        items={[
          { to: "/", label: "Home" },
          { to: "/locations", label: "Locations" },
          {
            to: "/locations/$locationID/",
            label:
              `${location?.address.street?.replace(/\$/g, ", ")}, ${location?.address.town}, ${location?.address.postcode}` ||
              "Location Details",
          },
        ]}
      />
      <span className="nhsuk-caption-l">Location Details</span>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {location && (
        <>
          <h1 className="nhsuk-heading-l">
            {location.address.street?.replace(/\$/g, ", ")},{" "}
            {location.address.town}, {location.address.postcode}
          </h1>
          <LocationOverview location={location} />
        </>
      )}
      {isSuccess && !location && (
        <>
          <h2 className="nhsuk-heading-l">Location not found</h2>
          <p>The location you are looking for does not exist.</p>
          <ActionLink
            asElement={Link}
            to="/locations"
            className="nhsuk-link--no-visited-state"
          >
            Back to Locations
          </ActionLink>
        </>
      )}
    </>
  );
}
